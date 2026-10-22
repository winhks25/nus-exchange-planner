"""Start a disposable PostgreSQL catalog and serve the real API for browser tests.

The importer publishes the reviewed source snapshot into a temporary database,
then the read-only runtime role backs uvicorn. Nothing here can target Supabase.
"""

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

from scripts.import_catalog import apply_plan, build_import_plan
from scripts.postgres_validation import PostgresCluster

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18765)
    args = parser.parse_args()

    cluster = PostgresCluster()
    cluster.start()
    child: subprocess.Popen[bytes] | None = None
    try:
        database = cluster.create_database()
        apply_plan(build_import_plan(), database.importer_url)

        # The API inherits only runtime credentials; importer access stays in this process.
        env = {
            **os.environ,
            "CATALOG_BACKEND": "postgres",
            "DATABASE_URL": database.reader_url,
            "CORS_ORIGINS": "http://127.0.0.1:18766",
            "DB_POOL_MIN_SIZE": "0",
            "DB_POOL_MAX_SIZE": "4",
            "DB_CONNECT_TIMEOUT": "2",
            "DB_STATEMENT_TIMEOUT_MS": "5000",
        }
        child = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                args.host,
                "--port",
                str(args.port),
            ],
            cwd=BACKEND_ROOT,
            env=env,
        )

        def stop_child(*_args: object) -> None:
            if child.poll() is None:
                child.terminate()

        for signal_name in (signal.SIGINT, signal.SIGTERM):
            signal.signal(signal_name, stop_child)

        returncode = child.wait()
        if returncode != 0:
            raise SystemExit(returncode)
    except KeyboardInterrupt:
        pass
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        cluster.stop()


if __name__ == "__main__":
    main()
