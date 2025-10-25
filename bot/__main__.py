from bot.dispatcher import Dispatcher
from bot.hadlers.message_text_echo import MessageTextEcho
from bot.hadlers.database_logger import DatabaseLogger
from bot.hadlers.message_photo_echo import MessagePhotoEcho
from bot.long_polling import start_long_polling


if __name__ == "__main__":
    try:
        dispatcher = Dispatcher()
        dispatcher.add_handler(DatabaseLogger())
        dispatcher.add_handler(MessageTextEcho())
        dispatcher.add_handler(MessagePhotoEcho())
        start_long_polling(dispatcher)
    except KeyboardInterrupt:
        print("\nBye!")
