from bot.database_client import ensure_user_exists
from bot.handlers.handler import Handler, HandlerStatus


class EnsureUserExists(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict):
        return "message" in update and "from" in update["message"]

    def handle(self, update: dict, state: str, order_json: dict):
        telegram_id = update["message"]["from"]["id"]
        ensure_user_exists(telegram_id)
        return HandlerStatus.CONTINUE
