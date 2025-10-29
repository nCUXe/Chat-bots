from bot.database_client import persist_update
from bot.handlers.handler import Handler, HandlerStatus


class DatabaseLogger(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return True

    def handle(self, update: dict, state: str, order_json: dict):
        persist_update(update)
        return HandlerStatus.CONTINUE
