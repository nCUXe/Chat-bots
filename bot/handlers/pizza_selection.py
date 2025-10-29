import json

from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger


class PizzaSelection(Handler):
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

        if state != "WHAIT_FOR_PIZZA_NAME":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("pizza_")

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

        pizza_name = callback_data.replace("pizza_", "").replace("_", " ").title()

        storage.update_user_order(telegram_id, {"pizza_name": pizza_name})

        storage.update_user_state(telegram_id, "WHAIT_FOR_PIZZA_SIZE")

        messenger.answerCallbackQuery(update["callback_query"]["id"])

        messenger.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messenger.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Good choose! Please select pizza size",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Small (25cm)", "callback_data": "size_small"},
                            {"text": "Medium (30cm)", "callback_data": "size_medium"},
                        ],
                        [
                            {"text": "Large (35 cm)", "callback_data": "size_large"},
                            {
                                "text": "Extra (40cm)",
                                "callback_data": "size_extra_large",
                            },
                        ],
                    ]
                }
            ),
        )
        return HandlerStatus.STOP
