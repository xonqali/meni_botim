import re
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatType, InlineKeyboardMarkup, InlineKeyboardButton

# ================== SOZLAMALAR ==================
BOT_TOKEN = "8515560975:AAGmRUvORz3gIj39V0HUsAwPdgCYQshlK7o"  # Tokeningni shu yerga yoz
CREATOR_ID = 5800819077

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ================== REKLAMA SO‘ZLAR ==================
BAD_WORDS = [
    r"http", r"https", r"t\.me", r"@", r"instagram", r"reklama", r".net", r".com", r".uz", r".ru",
]

# ================== ADMIN TEKSHIRISH ==================
async def is_admin(message: types.Message):
    if message.from_user.id == CREATOR_ID:
        return True
    member = await message.chat.get_member(message.from_user.id)
    return member.is_chat_admin()

# ================== START ==================
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Yaratuvchi 👤", url="https://t.me/xozyayn2"),
        InlineKeyboardButton("Kanal 📢", url="https://t.me/+8ytWcdHjmmIyNDZi"),
        InlineKeyboardButton(
            "Guruhga qo‘shish ➕",
            url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true"
        )
    )
    await message.reply("✅ Bot ishga tushdi", reply_markup=keyboard)

# ================== MENU ==================
@dp.message_handler(commands=['menu'])
async def menu_cmd(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Yaratuvchi 👤", url="https://t.me/xozyayn2"),
        InlineKeyboardButton("Kanal 📢", url="https://t.me/+8ytWcdHjmmIyNDZi"),
    )
    await message.reply("📋 BOT MENUSI", reply_markup=keyboard)

# ================== ANTIREKLAMA (ENG OXIRIDA) ==================
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def anti_ads(message: types.Message):
    # buyruqlarga tegma
    if message.text and message.text.startswith('/'):
        return

    # faqat guruhda ishlasin
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return

    # adminlarga tegma
    if await is_admin(message):
        return

    text = (message.text or message.caption or "").lower()

    for word in BAD_WORDS:
        if re.search(word, text):
            try:
                await message.delete()
                await message.answer(
                    f"⚠️ {message.from_user.full_name}, reklama taqiqlangan!"
                )
            except:
                pass
            return

# ================== BOT START ==================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)


