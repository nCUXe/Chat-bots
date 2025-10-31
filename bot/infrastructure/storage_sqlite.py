import json
import os
import sqlite3
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()


class StorageSqlite(Storage):
    def recreate_database(self) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute("DROP TABLE IF EXISTS telegram_updates")
                connection.execute("DROP TABLE IF EXISTS users")
                connection.execute(
                    """
                        CREATE TABLE IF NOT EXISTS telegram_updates
                            (
                                id INTEGER PRIMARY KEY,
                                payload TEXT NOT NULL
                            )
                    """
                )
                connection.execute(
                    """
                        CREATE TABLE IF NOT EXISTS users
                            (
                                id INTEGER PRIMARY KEY,
                                telegram_id INTEGER NOT NULL UNIQUE,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                state TEXT DEFAULT NULL,
                                order_json TEXT DEFAULT NULL
                            )
                    """
                )

    def persist_update(self, update: dict) -> None:
        json_data = json.dumps(update, ensure_ascii=False, indent=2)
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            connection.execute(
                "INSERT INTO telegram_updates (payload) VALUES (?)", (json_data,)
            )

    def ensure_user_exists(self, telegram_id: int) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            cursor = connection.execute(
                "SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            if cursor.fetchone() is None:
                connection.execute(
                    "INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,)
                )

    def cleare_user_state_and_orderee(self, telegram_id: int) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = ?",
                    (telegram_id,),
                )

    def update_user_state(self, telegram_id: int, state: str) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute(
                    "UPDATE users SET state = ? WHERE telegram_id = ?",
                    (
                        state,
                        telegram_id,
                    ),
                )

    def get_user(self, telegram_id: int) -> dict | None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                cursor = connection.execute(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = ?",
                    (telegram_id,),
                )
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "telegram_id": result[1],
                        "created_at": result[2],
                        "state": result[3],
                        "order_json": result[4],
                    }
                return None

    def get_user_order(self, telegram_id: int) -> dict | None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                cursor = connection.execute(
                    "SELECT order_json FROM users WHERE telegram_id = ?", (telegram_id,)
                )
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None

    def update_user_order(self, telegram_id: int, data: dict) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute(
                    "UPDATE users SET order_json = ? WHERE telegram_id = ?",
                    (json.dumps(data, ensure_ascii=False, indent=2), telegram_id),
                )
