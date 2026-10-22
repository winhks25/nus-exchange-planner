"""Serve a preview-seeded disposable database for local browser checks.

The database is temporary validation tooling, never the production project. The
script writes its URL to a file and waits until the process receives SIGINT or
SIGTERM, so a shell can start PostgreSQL and the API around one shared URL.
"""

import argparse
import signal
import threading
from pathlib import Path

from scripts.catalog_preview import build_preview
from scripts.catalog_seed import seed_preview
from scripts.postgres_validation import PostgresCluster


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url-file",
        required=True,
        type=Path,
        help="File that receives the disposable database URL when it is ready.",
    )
    args = parser.parse_args()

    stop = threading.Event()

    def request_stop(*_args: object) -> None:
        stop.set()

    for signal_name in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signal_name, request_stop)

    cluster = PostgresCluster()
    cluster.start()
    try:
        database = cluster.create_database()
        seed_preview(database, build_preview())
        args.url_file.write_text(f"{database.url}\n")
        print(f"Validation database ready; URL written to {args.url_file}", flush=True)
        while not stop.wait(0.5):
            pass
    finally:
        args.url_file.unlink(missing_ok=True)
        cluster.stop()


if __name__ == "__main__":
    main()
