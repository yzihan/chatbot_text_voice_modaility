import argparse
from datetime import datetime, timezone
from pathlib import Path

from database_sql import init_database
from sql_repository import export_database_zip


def main() -> None:
    parser = argparse.ArgumentParser(description="Export all chatbot SQL data as CSV files in a ZIP.")
    parser.add_argument("--output", type=Path, help="Output ZIP path")
    args = parser.parse_args()

    init_database()
    output = args.output or Path(
        f"chatbot-data-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.zip"
    )
    output.write_bytes(export_database_zip())
    print(output.resolve())


if __name__ == "__main__":
    main()
