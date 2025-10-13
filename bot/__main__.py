import time
import bot.database_client
import bot.telergam_client

def main() -> None:
    next_update_offset = 0
    try:

        while True:
            updates = bot.telergam_client.getUpdates(next_update_offset)
            bot.database_client.persist_updates(updates)
            for update in updates:
                if "message" in update and "text" in update["message"]:
                    bot.telergam_client.sendMessage(
                        chat_id=update["message"]["chat"]["id"],
                        text=update["message"]["text"],
                    )
                    print(".", end="", flush=True)
                else:
                    print("ONLY TEXT MESSAGE!")
                next_update_offset = max(next_update_offset, update["update_id"] + 1)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()