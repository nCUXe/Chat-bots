import asyncio
import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class DrinkSelectionHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_PIZZA_SIZE":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")

    async def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        pizza_size = callback_data.replace("size_", "").replace("_", " ").title()
        order_json["pizza_size"] = pizza_size

        await asyncio.gather(
            storage.update_user_state_and_order(telegram_id, order_json),
            storage.update_user_state(telegram_id, "WAIT_FOR_DRINK"),
            messenger.answer_callback_query(update["callback_query"]["id"]),
        )

        await asyncio.gather(
            messenger.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            ),
            messenger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="Please select Drink",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {"text": "Cola", "callback_data": "drink_cola"},
                                {"text": "Juice", "callback_data": "drink_juice"},
                            ],
                            [
                                {
                                    "text": "Mineral Water",
                                    "callback_data": "drink_water",
                                },
                                {"text": "Tea", "callback_data": "drink_tea"},
                            ],
                        ],
                    },
                ),
            ),
        )
        return HandlerStatus.STOP
