import sqlite3
import os
import json

from dotenv import load_dotenv

load_dotenv()

def recreate_database() -> None:
    connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))
    with connection:
        connection.execute("DROP TABLE IF EXISTS telegram_uptades")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS telegram_updates
            (
                id INTEGER PRIMARY KEY,
                payload TEXT NOT NULL
            )
        """
        )
    connection.close()

def persist_update(update: dict) -> None:
    connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))
    with connection:
        connection.execute(
            "INSERT INTO telegram_updates (payload) VALUES (?)",
            (json.dumps(update, ensure_ascii=False, indent=2),),
        )
    connection.close()