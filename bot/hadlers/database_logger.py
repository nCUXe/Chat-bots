from bot.database_client import persist_update
from bot.handler import Handler


class DatabaseLogger(Handler):
    def can_handle(self, update: dict) -> bool:
        if update: return True
    
    def handle(self, update: dict) -> bool:
        persist_update(update)
        return True