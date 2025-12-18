import logging
import os
import time

import aiohttp

from bot.domain.messenger import Messenger

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s.%(msecs)03d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class MessengerTelegram(Messenger):
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    def _get_telegram_base_uri(self) -> str:
        return f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def make_request(self, method: str, **param) -> dict:
        url = f"{self._get_telegram_base_uri()}/{method}"
        start_time = time.time()

        logger.info(f"[HTTP] → POST {method}")

        try:
            session = await self._get_session()
            async with session.post(
                url,
                json=param,
                headers={"Content-Type": "application/json"},
            ) as response:
                response_json = await response.json()
                assert response_json["ok"] == True  # noqa: E712

                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[HTTP] ← POST {method} - {duration_ms:.2f}ms")

                return response_json["result"]
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[HTTP] ✗ POST {method} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_updates(self, **param) -> dict:
        return await self.make_request("getUpdates", **param)

    async def send_message(self, chat_id: int, text: str, **param) -> dict:
        return await self.make_request(
            "sendMessage", chat_id=chat_id, text=text, **param
        )

    async def answer_callback_query(self, callback_query_id: str, **param) -> dict:
        return await self.make_request(
            "answerCallbackQuery",
            callback_query_id=callback_query_id,
            **param,
        )

    async def delete_message(self, chat_id: int, message_id: int) -> dict:
        return await self.make_request(
            "deleteMessage",
            chat_id=chat_id,
            message_id=message_id,
        )
