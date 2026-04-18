import asyncio
from telebot.async_telebot import AsyncTeleBot
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputReportReasonOther

BOT_TOKEN = "8640729572:AAGtBwSnniRvtknw1YMowvqFufi28ODQNcc"

API_ID = 34928216
API_HASH = "29f66350a892e8b69a83b50d7e99bd27"

# ТВОЯ СТРОКА СЕССИИ (вставь её сюда)
SESSION_STRING = "1BJWap1sBuzBagzaf912aIMOOx3bJL5elg8q3WDkR5tTmPxv_1zYRHVffBaJIg6B1aGgi50zHdqy6C-Ry5kFjH30rWSVpj8QCmoHeyDgnX4cowFnI9ArVOKUxRNSW5uci-PONjksHr7OMOyBpXHi9bkeechrUyw1htV_ueNDzw7u8OBzoNL3ehIFQvwUK336VCOsmn_-7hOkfUjMwWrn_StuITSfjSMMyiWC_2aLQn2aTZaMA3NBpQl-c1K4aH4Pp04aT_Ket2aOSlSib0XMuH10voYx1r90KEOluxc6mPTcr1I8F70f8V3ZFeUIpWkupErXHEYIbbUyaP0pjHgCgLaQ7dxRf2aU="

ALLOWED_USER_ID = 8727723180

REPORT_TEXT = (
    "Открытый доксинг бот. Прописка, паспортные данные, номера телефонов, "
    "ИНН, СНИЛС, фото паспорта, адреса регистрации и проживания, "
    "родственники, кредитная история. Прошу принять меры."
)

REPORTS_PER_BOT = 5
DELAY_BETWEEN_REPORTS = 0.5
DELAY_BETWEEN_BOTS = 3.0

# Используем StringSession вместо файла
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot = AsyncTeleBot(BOT_TOKEN)

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
        print(f"[LOG] {text}")
    except Exception as e:
        print(f"[ERROR] {e}")

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
                await send_log(f"    ✅ Report {i+1}/{REPORTS_PER_BOT} sent")
            except Exception as e:
                await send_log(f"    ❌ Error: {str(e)}")
            if i < REPORTS_PER_BOT - 1:
                await asyncio.sleep(DELAY_BETWEEN_REPORTS)

        await send_log(f"[✅] @{username} — {REPORTS_PER_BOT} reports sent")
    except Exception as e:
        await send_log(f"[-] Error with @{username}: {str(e)}")

@bot.message_handler(commands=['start'])
async def start(message):
    global USER_CHAT_ID
    if message.from_user.id != ALLOWED_USER_ID:
        await bot.reply_to(message, "Access denied.")
        return
    USER_CHAT_ID = message.chat.id
    await send_log(
        "✅ Бот запущен.\n"
        "📋 Отправь список юзернеймов (по одному в строке)\n"
        f"⚡ {REPORTS_PER_BOT} жалоб на бота",
        message.chat.id
    )

@bot.message_handler(func=lambda m: True)
async def handle_list(message):
    global USER_CHAT_ID
    if message.from_user.id != ALLOWED_USER_ID:
        return
    USER_CHAT_ID = message.chat.id
    lines = [line.strip().lstrip('@') for line in message.text.splitlines() if line.strip()]
    if not lines:
        await send_log("❌ Пустой список")
        return
    await send_log(f"🚀 Всего ботов: {len(lines)}")
    for i, username in enumerate(lines, 1):
        await send_log(f"🔄 [{i}/{len(lines)}] @{username}")
        await report_bot(username, message.chat.id)
        if i < len(lines):
            await asyncio.sleep(DELAY_BETWEEN_BOTS)
    await send_log("🎉 ГОТОВО!")

async def main():
    print("=" * 50)
    print("🚀 ЗАПУСК БОТА")
    print("=" * 50)
    await client.start()
    print("✅ Telethon готов (сессия из строки)")
    await bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    asyncio.run(main())
