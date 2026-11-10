"""Export locally stored portfolio inquiries to a private CSV file."""

from __future__ import annotations

import argparse
import csv
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("PORTFOLIO_DB_PATH", ROOT / "data" / "contact_inquiries.sqlite3"))
FIELDS = ("id", "created_at", "name", "email", "phone", "company", "role", "message")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export portfolio contact inquiries to CSV.")
    parser.add_argument("output", nargs="?", default="contact-inquiries.csv", help="private CSV output path")
    args = parser.parse_args()

    if not DATABASE_PATH.exists():
        parser.error(f"No inquiries database found at {DATABASE_PATH}")

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection, output_path.open("w", newline="", encoding="utf-8-sig") as output:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT id, created_at, name, email, phone, company, role, message "
            "FROM contact_inquiries ORDER BY created_at DESC"
        )
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(dict(row) for row in rows)

    print(f"Exported inquiries to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
