from abc import ABC, abstractmethod


class Messenger(ABC):
    @abstractmethod
    async def send_message(self, chat_id: int, text: str, **param) -> dict: ...

    @abstractmethod
    async def get_updates(self, **param) -> dict: ...

    @abstractmethod
    async def answer_callback_query(self, callback_query_id: str, **param) -> dict: ...

    @abstractmethod
    async def delete_message(self, chat_id: int, message_id: int) -> dict: ...