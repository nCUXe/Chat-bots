import json
import os


import pg8000

from bot.domain.storage import Storage

from dotenv import load_dotenv

load_dotenv()


class StoragePostgres(Storage):
    def _get_connection(self):
        """Create and return a PostgreSQL connection."""
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DATABASE")

        if host is None:
            raise ValueError("POSTGRES_HOST environment variable is not set")
        if port is None:
            raise ValueError("POSTGRES_PORT environment variable is not set")
        if user is None:
            raise ValueError("POSTGRES_USER environment variable is not set")
        if password is None:
            raise ValueError("POSTGRES_PASSWORD environment variable is not set")
        if database is None:
            raise ValueError("POSTGRES_DATABASE environment variable is not set")

        return pg8000.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
        )

    def persist_update(self, update: dict) -> None:
        payload = json.dumps(update, ensure_ascii=False, indent=2)
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO telegram_updates (payload) VALUES (%s)", (payload,)
                )
            conn.commit()

    def ensure_user_exists(self, telegram_id: int) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM users WHERE telegram_id = %s",
                    (telegram_id,),
                )

                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO users (telegram_id) VALUES (%s)",
                        (telegram_id,),
                    )
            conn.commit()

    def recreate_database(self) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS telegram_updates")
                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_updates
                    (
                        id SERIAL PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users
                    (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        state TEXT DEFAULT NULL,
                        order_json TEXT DEFAULT NULL
                    )
                    """
                )
            conn.commit()

    def clear_user_state_and_order(self, telegram_id: int) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = %s",
                    (telegram_id,),
                )
            conn.commit()

    def update_user_state_and_order(self, telegram_id: int, order_json: dict) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET order_json = %s WHERE telegram_id = %s",
                    (json.dumps(order_json, ensure_ascii=False, indent=2), telegram_id),
                )
            conn.commit()

    def update_user_state(self, telegram_id: int, state: str) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = %s WHERE telegram_id = %s",
                    (state, telegram_id),
                )
            conn.commit()

    def get_user(self, telegram_id: int) -> dict | None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = %s",
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
        with self._get_connection() as conn:
            with conn:
                cursor = conn.execute(
                    "SELECT order_json FROM users WHERE telegram_id = ?", (telegram_id,)
                )
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None

    def update_user_order(self, telegram_id: int, data: dict) -> None:
        with self._get_connection() as conn:
            with conn:
                conn.execute(
                    "UPDATE users SET order_json = ? WHERE telegram_id = ?",
                    (json.dumps(data, ensure_ascii=False, indent=2), telegram_id),
                )
            conn.commit()
