import asyncio
import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class ApprovalHandler(Handler):
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

        if state != "WAIT_FOR_DRINK":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

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

        drink = callback_data.replace("drink_", "").replace("_", " ").title()
        order_json["drink"] = drink
        await asyncio.gather(
            storage.update_user_state_and_order(telegram_id, order_json),
            storage.update_user_state(telegram_id, "WAIT_FOR_APPROVAL"),
            messenger.answer_callback_query(update["callback_query"]["id"]),
        )
        pizza_name = order_json.get("pizza_name", "Unknown")
        pizza_size = order_json.get("pizza_size", "Unknown")
        drink = order_json.get("drink", "Unknown")
        order_summary = f"""**Your Order:**

    **Pizza:** {pizza_name}
    **Size:** {pizza_size}
    **Drink:** {drink}

    Is everything OK?"""

        await asyncio.gather(
            messenger.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            ),
            messenger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=order_summary,
                parse_mode="Markdown",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {"text": "Yes", "callback_data": "approval_yes"},
                            ],
                            [
                                {"text": "No", "callback_data": "approval_no"},
                            ],
                        ],
                    },
                ),
            ),
        )
        return HandlerStatus.STOP
