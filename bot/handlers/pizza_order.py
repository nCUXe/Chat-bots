import json

from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger


class PizzaOrder(Handler):
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

        if state != "WHAIT_FOR_DRINKS":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:

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
        storage.update_user_order(telegram_id, order_json)
        storage.update_user_state(telegram_id, "WHAIT_FOR_APROVE")
        messenger.answerCallbackQuery(update["callback_query"]["id"])
        messenger.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )
        new_order_json = storage.get_user_order(telegram_id)
        if new_order_json:
            order_text = f"Your order:\nPizza: {new_order_json['pizza_name']}\nSize: {new_order_json['pizza_size']}\nDrink: {new_order_json['drink']}"
        else:
            order_text = "No order found"

        messenger.sendMessage(
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
