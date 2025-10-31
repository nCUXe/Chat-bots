from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def recreate_database() -> None: ...

    @abstractmethod
    def persist_update(update: dict) -> None: ...

    @abstractmethod
    def ensure_user_exists(telegram_id: int) -> None: ...

    @abstractmethod
    def clear_user_state_and_order(telegram_id: int) -> None: ...

    @abstractmethod
    def update_user_state(telegram_id: int, state: str) -> None: ...

    @abstractmethod
    def get_user(telegram_id: int) -> dict | None: ...

    @abstractmethod
    def get_user_order(telegram_id: int) -> dict | None: ...

    @abstractmethod
    def update_user_order(telegram_id: int, data: dict) -> None: ...
