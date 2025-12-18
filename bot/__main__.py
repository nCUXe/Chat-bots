import asyncio

from bot.dispatcher import Dispatcher
from bot import get_handlers
from bot.long_polling import start_long_polling
from bot.infrastructure.messenger_telegram import MessengerTelegram
from bot.infrastructure.storage_postgres import StoragePostgres


async def main() -> None:
    storage = StoragePostgres()
    messenger = MessengerTelegram()

    try:
        dispatcher = Dispatcher(storage, messenger)
        dispatcher.add_handlers(*get_handlers())
        await start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        print("\nBye!")
    finally:
        if hasattr(messenger, "close"):
            await messenger.close()
        if hasattr(storage, "close"):
            await storage.close()


if __name__ == "__main__":
    asyncio.run(main())