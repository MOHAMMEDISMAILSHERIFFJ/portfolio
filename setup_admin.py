"""Create or reset the single local portfolio admin account."""

from __future__ import annotations

import getpass
import secrets
import sqlite3

from backend import DATABASE_PATH, hash_admin_password


def main() -> None:
    username = input("Admin username: ").strip()
    if not username or len(username) > 100:
        raise SystemExit("Choose a username between 1 and 100 characters.")

    password = getpass.getpass("Admin password (12+ characters): ")
    confirmation = getpass.getpass("Confirm password: ")
    if len(password) < 12:
        raise SystemExit("Use at least 12 characters for the admin password.")
    if password != confirmation:
        raise SystemExit("Passwords did not match. No changes were made.")

    salt = secrets.token_bytes(16)
    password_hash = hash_admin_password(password, salt)
    with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
        connection.execute(
            """INSERT INTO admin_credentials (id, username, salt, password_hash)
               VALUES (1, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                   username = excluded.username,
                   salt = excluded.salt,
                   password_hash = excluded.password_hash""",
            (username, salt, password_hash),
        )
        connection.execute("DELETE FROM admin_sessions")
        connection.commit()
    print("Admin account saved. Sign in from the Admin button in the portfolio header.")


if __name__ == "__main__":
    main()
