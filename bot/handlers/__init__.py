from bot.handlers.handler import Handler
from bot.handlers.database_logger import DatabaseLogger
from bot.handlers.ensure_user_exists import EnsureUserExists
from bot.handlers.message_start import MessageStart
from bot.handlers.pizza_finish import PizzaFinish
from bot.handlers.pizza_order import PizzaOrder
from bot.handlers.pizza_selection import PizzaSelection
from bot.handlers.pizza_size import PizzaSize


def get_handlers() -> list[Handler]:
    return [
        DatabaseLogger(),
        EnsureUserExists(),
        MessageStart(),
        PizzaSelection(),
        PizzaSize(),
        PizzaOrder(),
        PizzaFinish(),
    ]
