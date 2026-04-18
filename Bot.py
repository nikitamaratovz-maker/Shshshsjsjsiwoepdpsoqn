import asyncio
from telebot.async_telebot import AsyncTeleBot
from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputReportReasonOther

BOT_TOKEN = "8640729572:AAGtBwSnniRvtknw1YMowvqFufi28ODQNcc"

API_ID = 34928216
API_HASH = "29f66350a892e8b69a83b50d7e99bd27"
SESSION_NAME = "IImoderation"

ALLOWED_USER_ID = 8727723180

REPORT_TEXT = (
    "Открытый доксинг бот. Прописка, паспортные данные, номера телефонов, "
    "ИНН, СНИЛС, фото паспорта, адреса регистрации и проживания, "
    "родственники, кредитная история. Прошу принять меры."
)

REPORTS_PER_BOT = 5
DELAY_BETWEEN_REPORTS = 0.5
DELAY_BETWEEN_BOTS = 3.0

bot = AsyncTeleBot(BOT_TOKEN)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

USER_CHAT_ID = None

async def send_log(text: str, chat_id: int = None):
    global USER_CHAT_ID
    if chat_id is None:
        chat_id = USER_CHAT_ID
    if chat_id is None:
        print(f"[LOG] {text}")
        return

    try:
        await bot.send_message(chat_id, text)
        print(f"[LOG → USER] {text}")
    except Exception as e:
        print(f"[ERROR SENDING LOG] {e}")


async def report_bot(username: str, chat_id: int):
    try:
        await send_log(f"[+] Starting reports on @{username}")

        entity = await client.get_entity(username)
        peer = await client.get_input_entity(entity)

        await send_log(f"[+] Entity received: @{username} (ID: {entity.id})")

        for i in range(REPORTS_PER_BOT):
            try:
                await client(ReportPeerRequest(
                    peer=peer,
                    reason=InputReportReasonOther(),
                    message=REPORT_TEXT
                ))
                await send_log(f"    ✅ Report {i+1}/{REPORTS_PER_BOT} successfully sent")
            except Exception as e:
                await send_log(f"    ❌ Error on report {i+1}/{REPORTS_PER_BOT}: {str(e)}")

            if i < REPORTS_PER_BOT - 1:
                await asyncio.sleep(DELAY_BETWEEN_REPORTS)

        await send_log(f"[✅ OK] Completed on @{username} — all {REPORTS_PER_BOT} reports sent")

    except Exception as e:
        await send_log(f"[-] Critical error with @{username}: {str(e)}")


@bot.message_handler(commands=['start'])
async def start(message):
    global USER_CHAT_ID
    if message.from_user.id != ALLOWED_USER_ID:
        await bot.reply_to(message, "Access denied.")
        return

    USER_CHAT_ID = message.chat.id
    await send_log(
        "✅ Bot is launched and ready.\n"
        "Send the list of bot usernames (one per line)",
        message.chat.id
    )


@bot.message_handler(func=lambda m: True)
async def handle_list(message):
    global USER_CHAT_ID
    if message.from_user.id != ALLOWED_USER_ID:
        return

    USER_CHAT_ID = message.chat.id

    lines = [line.strip() for line in message.text.splitlines() if line.strip()]
    if not lines:
        await send_log("❌ Empty list.", message.chat.id)
        return

    valid_usernames = [line.strip().lstrip('@') for line in lines if line.strip()]

    if not valid_usernames:
        await send_log("❌ No valid @username found", message.chat.id)
        return

    await send_log(f"🚀 Starting processing. Total bots: {len(valid_usernames)}")

    for i, username in enumerate(valid_usernames, 1):
        await send_log(f"🔄 Processing {i}/{len(valid_usernames)} → @{username}")
        await report_bot(username, message.chat.id)

        if i < len(valid_usernames):
            await asyncio.sleep(DELAY_BETWEEN_BOTS)

    await send_log("🎉 ALL DONE. All reports have been sent.")


async def main():
    print("Launching bot...")
    await client.start()
    print("Telethon session ready")
    await send_log("🟢 Telethon session started. Bot ready.", ALLOWED_USER_ID)
    await bot.infinity_polling(skip_pending=True)


if __name__ == '__main__':
    asyncio.run(main())
