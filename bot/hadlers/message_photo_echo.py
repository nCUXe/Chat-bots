from bot.handler import Handler
from bot.telergam_client import sendPhoto


class MessagePhotoEcho(Handler):
    def can_handle(self, update: dict) -> bool:
        return "message" in update and "photo" in update["message"]
    
    def handle(self, update: dict) -> bool:
        photos = update["message"]["photo"]

        best_photo = max(photos, key=lambda x: x.get("file_size", 0))
        file_id = best_photo["file_id"]

        if "caption" in update["message"]:
            sendPhoto(
                chat_id=update["message"]["chat"]["id"],
                photo=file_id,
                caption=update["message"]["caption"],
            )
        else:
            sendPhoto(
                chat_id=update["message"]["chat"]["id"],
                photo=file_id,
            )

        return False