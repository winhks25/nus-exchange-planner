"""Environment-backed settings for the catalog runtime."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import urlsplit

CatalogBackend = Literal["json", "postgres"]

BACKENDS: tuple[CatalogBackend, ...] = ("json", "postgres")


class SettingsError(ValueError):
    """Raised for invalid configuration without echoing secret values."""


@dataclass(frozen=True)
class PoolSettings:
    """Bounded pool and timeout values used by the synchronous runtime pool."""

    min_size: int = 0
    max_size: int = 1
    timeout: float = 5.0
    max_waiting: int = 16
    close_timeout: float = 5.0
    max_lifetime: float = 1800.0
    max_idle: float = 300.0
    connect_timeout: int = 5
    statement_timeout_ms: int = 5000
    idle_in_transaction_timeout_ms: int = 5000


@dataclass(frozen=True)
class Settings:
    """Validated application settings; connection URLs are never printed in reprs."""

    catalog_backend: CatalogBackend = "json"
    database_url: str | None = field(default=None, repr=False)
    pool: PoolSettings = field(default_factory=PoolSettings)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        values = env if env is not None else os.environ

        # Select the catalog source explicitly; unknown values must not silently fall back.
        backend = values.get("CATALOG_BACKEND", "json").strip().lower() or "json"
        if backend not in BACKENDS:
            raise SettingsError(
                f"CATALOG_BACKEND must be one of {', '.join(BACKENDS)}; got an unknown value"
            )
        catalog_backend: CatalogBackend = backend

        # Validate URLs when provided and require the runtime URL only in postgres mode.
        database_url = _optional_url(values.get("DATABASE_URL"), "DATABASE_URL")
        if catalog_backend == "postgres" and database_url is None:
            raise SettingsError("DATABASE_URL is required when CATALOG_BACKEND=postgres")

        # Parse and bound every pool/timeout setting before the pool is constructed.
        pool = PoolSettings(
            min_size=_int(values, "DB_POOL_MIN_SIZE", 0, 0, 10),
            max_size=_int(values, "DB_POOL_MAX_SIZE", 1, 1, 10),
            timeout=_float(values, "DB_POOL_TIMEOUT", 5.0, 0.1, 30.0),
            max_waiting=_int(values, "DB_POOL_MAX_WAITING", 16, 1, 100),
            close_timeout=_float(values, "DB_POOL_CLOSE_TIMEOUT", 5.0, 0.1, 30.0),
            max_lifetime=_float(values, "DB_POOL_MAX_LIFETIME", 1800.0, 60.0, 86400.0),
            max_idle=_float(values, "DB_POOL_MAX_IDLE", 300.0, 0.0, 3600.0),
            connect_timeout=_int(values, "DB_CONNECT_TIMEOUT", 5, 1, 60),
            statement_timeout_ms=_int(
                values, "DB_STATEMENT_TIMEOUT_MS", 5000, 100, 60000
            ),
            idle_in_transaction_timeout_ms=_int(
                values, "DB_IDLE_IN_TRANSACTION_TIMEOUT_MS", 5000, 100, 60000
            ),
        )
        if pool.min_size > pool.max_size:
            raise SettingsError("DB_POOL_MIN_SIZE must not exceed DB_POOL_MAX_SIZE")

        return cls(
            catalog_backend=catalog_backend,
            database_url=database_url,
            pool=pool,
        )


def _optional_url(value: str | None, name: str) -> str | None:
    """Return a trimmed PostgreSQL URL or None, raising a secret-free error."""

    if value is None or not value.strip():
        return None
    candidate = value.strip()
    try:
        parsed = urlsplit(candidate)
    except ValueError:
        raise SettingsError(f"{name} is not a valid PostgreSQL URL") from None
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise SettingsError(f"{name} must use the postgres:// or postgresql:// scheme")
    try:
        hostname = parsed.hostname
    except ValueError:
        raise SettingsError(f"{name} is not a valid PostgreSQL URL") from None
    if not hostname:
        raise SettingsError(f"{name} must include a database host")
    return candidate


def _int(
    env: Mapping[str, str], name: str, default: int, minimum: int, maximum: int
) -> int:
    raw = env.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError:
        raise SettingsError(f"{name} must be an integer") from None
    if not minimum <= value <= maximum:
        raise SettingsError(f"{name} must be between {minimum} and {maximum}")
    return value


def _float(
    env: Mapping[str, str], name: str, default: float, minimum: float, maximum: float
) -> float:
    raw = env.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = float(raw)
    except ValueError:
        raise SettingsError(f"{name} must be a number") from None
    if not minimum <= value <= maximum:
        raise SettingsError(f"{name} must be between {minimum} and {maximum}")
    return value
