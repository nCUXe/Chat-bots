import asyncio
import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class MessageStart(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    async def handle(
        self,
        update: dict,
        state: str,
        data: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        await storage.clear_user_state_and_order(telegram_id)
        await storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")
        await asyncio.gather(
            messenger.send_message(
                chat_id=update["message"]["chat"]["id"],
                text="Welcome to Pizza shop!",
                reply_markup=json.dumps({"remove_keyboard": True}),
            ),
            messenger.send_message(
                chat_id=update["message"]["chat"]["id"],
                text="Please, choose Pizza Type",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Margherita",
                                    "callback_data": "pizza_margherita",
                                },
                                {
                                    "text": "Pepperoni",
                                    "callback_data": "pizza_pepperoni",
                                },
                            ],
                            [
                                {
                                    "text": "Quatro Stagioni",
                                    "callback_data": "pizza_stagioni",
                                },
                                {
                                    "text": "Capricciosa",
                                    "callback_data": "pizza_capricciosa",
                                },
                            ],
                        ],
                    },
                ),
            ),
        )
        return HandlerStatus.STOP
