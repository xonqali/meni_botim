import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatType

# ================== SOZLAMALAR ==================
BOT_TOKEN = "8515560975:AAGmRUvORz3gIj39V0HUsAwPdgCYQshlK7o"
CREATOR_ID = 5800819077

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Reklama so'zlari
BAD_WORDS = {"http", "https", "t.me", "@", "instagram", "promo", "reklama"}

# Ogohlantirishlar
WARNINGS = {}

# Oxirgi o‘chirgan xabarlar logi
DELETED_LOG = []
MAX_LOG = 10

# ================== ADMIN TEKSHIRISH ==================
async def is_admin(message: types.Message):
    if message.from_user.id == CREATOR_ID:
        return True
    admins = await message.chat.get_administrators()
    return message.from_user.id in [admin.user.id for admin in admins]

# ================== ADMIN PANEL ==================
@dp.message_handler(commands=["addword"])
async def add_word(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Siz admin emassiz!")
        return
    word = message.get_args().lower()
    if not word:
        await message.reply("❗ Iltimos, qo'shmoqchi bo'lgan so'zni kiriting: /addword reklama")
        return
    BAD_WORDS.add(word)
    await message.reply(f"✅ `{word}` reklama so'zlariga qo‘shildi", parse_mode="Markdown")

@dp.message_handler(commands=["delword"])
async def del_word(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Siz admin emassiz!")
        return
    word = message.get_args().lower()
    if word in BAD_WORDS:
        BAD_WORDS.remove(word)
        await message.reply(f"❌ `{word}` reklama so'zlaridan o‘chirildi", parse_mode="Markdown")
    else:
        await message.reply("⚠️ Bunday so‘z yo‘q")

@dp.message_handler(commands=["listwords"])
async def list_words(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Siz admin emassiz!")
        return
    await message.reply("Reklama so'zlari:\n" + "\n".join(BAD_WORDS))

@dp.message_handler(commands=["log"])
async def show_log(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Siz admin emassiz!")
        return
    if not DELETED_LOG:
        await message.reply("🔹 Hozircha o‘chirgan xabarlar yo‘q.")
        return
    log_text = "\n\n".join(DELETED_LOG[-MAX_LOG:])
    await message.reply(f"📝 Oxirgi o‘chirgan xabarlar:\n{log_text}")

# ================== ANTIREKLAMA ==================
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def anti_ads(message: types.Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return

    member = await message.chat.get_member(message.from_user.id)
    if member.is_chat_admin or message.from_user.id == CREATOR_ID:
        return

    text = ""
    if message.text:
        text = message.text.lower()
    elif message.caption:
        text = message.caption.lower()

    for word in BAD_WORDS:
        if word in text:
            try:
                await message.delete()
            except:
                return

            user_id = message.from_user.id
            WARNINGS[user_id] = WARNINGS.get(user_id, 0) + 1

            log_entry = f"{message.from_user.full_name} ({user_id}): {text[:50]}..."
            DELETED_LOG.append(log_entry)
            if len(DELETED_LOG) > MAX_LOG:
                DELETED_LOG.pop(0)

            if WARNINGS[user_id] == 1:
                await message.answer(f"⚠️ {message.from_user.full_name}\nReklama taqiqlangan!")
            elif WARNINGS[user_id] == 2:
                await bot.kick_chat_member(message.chat.id, user_id)
                await bot.unban_chat_member(message.chat.id, user_id)
                await message.answer(f"👢 {message.from_user.full_name} kick qilindi")
            elif WARNINGS[user_id] >= 3:
                await bot.kick_chat_member(message.chat.id, user_id)
                await message.answer(f"⛔ {message.from_user.full_name} BAN qilindi")
            return

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatType

BOT_TOKEN = "8515560975:AAGmRUvORz3gIj39V0HUsAwPdgCYQshlK7o"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BAD_WORDS = [
    "http", "https", "t.me", "@", "instagram", "reklama", "promo"
]

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("✅ Antireklama bot ishga tushdi")

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def anti_ads(message: types.Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return

    text = message.text.lower()

    for word in BAD_WORDS:
        if word in text:
            try:
                await message.delete()
                await message.answer(
                    f"⚠️ {message.from_user.full_name}, reklama taqiqlangan!"
                )
            except:
                pass
            return

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)





