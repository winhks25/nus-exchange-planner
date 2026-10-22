"""Bounded, read-only PostgreSQL access for the catalog runtime."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg_pool import ConnectionPool, PoolClosed, PoolTimeout, TooManyRequests

from .settings import Settings

LOG = logging.getLogger(__name__)

UNAVAILABLE_MESSAGE = "Catalog database is unavailable. Please try again later."


class DatabaseError(Exception):
    """Base class for sanitized database failures."""


class DatabaseUnavailable(DatabaseError):
    """Raised when a database operation cannot be completed safely."""


class DatabaseConfigurationError(DatabaseError):
    """Raised when connection settings cannot produce a usable pool."""


class CatalogDatabase:
    """Owns one synchronous pool and opens no network connections at import time."""

    def __init__(self, settings: Settings) -> None:
        if settings.database_url is None:
            raise DatabaseConfigurationError("DATABASE_URL is required for database mode.")
        self._url = settings.database_url
        self._pool_settings = settings.pool
        self._pool: ConnectionPool | None = None

    def open(self) -> None:
        """Start the pool workers without requiring a successful connection yet."""

        if self._pool is not None:
            return

        # Build the pool with TLS and transaction-pooler-safe connection settings.
        try:
            conninfo = _runtime_conninfo(self._url)
            pool = ConnectionPool(
                conninfo=conninfo,
                min_size=self._pool_settings.min_size,
                max_size=self._pool_settings.max_size,
                timeout=self._pool_settings.timeout,
                max_waiting=self._pool_settings.max_waiting,
                max_lifetime=self._pool_settings.max_lifetime,
                max_idle=self._pool_settings.max_idle,
                check=ConnectionPool.check_connection,
                kwargs=self._connection_kwargs(),
                open=False,
                name="catalog-runtime",
            )
        except DatabaseConfigurationError:
            raise
        except (psycopg.Error, TypeError, ValueError) as exc:
            _log_failure("configure", exc)
            raise DatabaseUnavailable(UNAVAILABLE_MESSAGE) from None

        # Opening with wait=False keeps startup alive while a transient outage is handled as 503.
        try:
            pool.open(wait=False)
        except (psycopg.Error, PoolTimeout, PoolClosed) as exc:
            _log_failure("open", exc)
            self._close_pool(pool)
            raise DatabaseUnavailable(UNAVAILABLE_MESSAGE) from None
        self._pool = pool

    def close(self) -> None:
        """Close the pool without letting shutdown errors escape."""

        pool, self._pool = self._pool, None
        if pool is not None:
            self._close_pool(pool)

    @contextmanager
    def read_transaction(self, operation: str = "query") -> Iterator[psycopg.Connection]:
        """Yield a connection inside a short, read-only transaction."""

        pool = self._pool
        if pool is None:
            raise DatabaseUnavailable(UNAVAILABLE_MESSAGE)

        # Translate driver and pool failures without exposing connection details.
        try:
            with pool.connection() as conn:
                conn.read_only = True
                with conn.transaction():
                    yield conn
        except (psycopg.Error, PoolTimeout, PoolClosed, TooManyRequests) as exc:
            _log_failure(operation, exc)
            raise DatabaseUnavailable(UNAVAILABLE_MESSAGE) from None

    def _close_pool(self, pool: ConnectionPool) -> None:
        """Close a pool, logging operational failures instead of raising them."""

        try:
            pool.close(timeout=self._pool_settings.close_timeout)
        except (psycopg.Error, PoolTimeout, PoolClosed) as exc:
            _log_failure("close", exc)

    def _connection_kwargs(self) -> dict[str, object]:
        """Return settings applied to every pooled connection."""

        timeouts = (
            f"-c statement_timeout={self._pool_settings.statement_timeout_ms} "
            f"-c idle_in_transaction_session_timeout="
            f"{self._pool_settings.idle_in_transaction_timeout_ms} "
            "-c default_transaction_read_only=on"
        )
        return {
            "autocommit": False,
            "prepare_threshold": None,
            "connect_timeout": self._pool_settings.connect_timeout,
            "options": timeouts,
            "application_name": "nus-exchange-planner",
        }


def _runtime_conninfo(url: str) -> str:
    """Force TLS while preserving the caller's host, role, and database."""

    try:
        params = conninfo_to_dict(url)
        if params.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
            params["sslmode"] = "require"
        params.setdefault("application_name", "nus-exchange-planner")
        return make_conninfo(**params)
    except (psycopg.Error, ValueError):
        raise DatabaseConfigurationError("Database connection settings are invalid.") from None


def _log_failure(operation: str, exc: Exception) -> None:
    """Log only the operation and exception class, never conninfo or parameters."""

    LOG.warning("Database %s failed: %s", operation, type(exc).__name__)
