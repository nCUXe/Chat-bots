import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class PizzaSize(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict):
        if "callback_query" not in update:
            return False

        if state != "WHAIT_FOR_PIZZA_SIZE":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")

    def handle(self, update: dict, state: str, order_json: dict):
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        size_mapping = {
            "size_small": "Small (25cm)",
            "size_medium": "Medium (30cm)",
            "size_large": "Large (35 cm)",
            "size_extra_large": "Extra (40cm)",
        }

        pizza_size = size_mapping.get(callback_data)
        order_json["pizza_size"] = pizza_size
        bot.database_client.update_user_order(telegram_id, order_json)
        bot.database_client.update_user_state(telegram_id, "WHAIT_FOR_DRINKS")
        bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )
        bot.telegram_client.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Please choose some drinks",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Apple juice",
                                "callback_data": "drink_apple_juice",
                            },
                            {"text": "Fanta", "callback_data": "drink_fanta"},
                        ],
                        [
                            {"text": "Coke-Cola", "callback_data": "drink_coke_cola"},
                            {"text": "Water", "callback_data": "drink_water"},
                        ],
                        [
                            {"text": "No drinks", "callback_data": "drink_none"},
                        ],
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
