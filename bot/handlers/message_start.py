import json

import bot.database_client
import bot.telegram_client
from bot.handlers.handler import Handler, HandlerStatus


class MessageStart(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict):
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    def handle(self, update: dict, state: str, order_json: dict):
        telegram_id = update["message"]["from"]["id"]

        bot.database_client.cleare_user_state_and_order(telegram_id)
        bot.database_client.update_user_state(telegram_id, "WHAIT_FOR_PIZZA_NAME")

        bot.telegram_client.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="Whelcome to Pizza shop!",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        bot.telegram_client.sendMessage(
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
