import json

from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger


class MessageStart(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:

        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:

        telegram_id = update["message"]["from"]["id"]

        storage.clear_user_state_and_order(telegram_id)
        storage.update_user_state(telegram_id, "WHAIT_FOR_PIZZA_NAME")

        messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="Welcome to Pizza shop!",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="New order\nPlease choose pizza name",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Margarita", "callback_data": "pizza_margarita"},
                            {"text": "Pepperoni", "callback_data": "pizza_pepperoni"},
                        ],
                        [
                            {
                                "text": "Quattro Stagioni",
                                "callback_data": "pizza_quattro_stagioni",
                            },
                            {
                                "text": "Capricciosa",
                                "callback_data": "pizza_capricciosa",
                            },
                        ],
                        [
                            {"text": "Bavarian", "callback_data": "pizza_bavarian"},
                            {"text": "Devils", "callback_data": "pizza_devils"},
                        ],
                    ],
                }
            ),
        )
        return HandlerStatus.STOP
