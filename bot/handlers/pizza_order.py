import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus


class PizzaOrder(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict):
        if "callback_query" not in update:
            return False

        if state != "WHAIT_FOR_DRINKS":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

    def handle(self, update: dict, state: str, order_json: dict):
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        drink_mapping = {
            "drink_apple_juice": "Apple juice",
            "drink_fanta": "Fanta juice",
            "drink_coke_cola": "Coke-Cola",
            "drink_water": "Water",
            "drink_none": "No drinks",
        }

        drink_type = drink_mapping.get(callback_data)
        order_json["drink"] = drink_type
        bot.database_client.update_user_order(telegram_id, order_json)
        bot.database_client.update_user_state(telegram_id, "WHAIT_FOR_APROVE")
        bot.telegram_client.answerCallbackQuery(update["callback_query"]["id"])
        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )
        new_order_json = bot.database_client.get_user_order(telegram_id)
        if new_order_json:
            order_text = f"Your order:\nPizza: {new_order_json['pizza_name']}\nSize: {new_order_json['pizza_size']}\nDrink: {new_order_json['drink']}"
        else:
            order_text = "No order found"

        bot.telegram_client.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=order_text,
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Order confirm", "callback_data": "order_confirm"},
                            {"text": "Order again", "callback_data": "order_again"},
                        ],
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
