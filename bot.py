import os
import re
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatType, InlineKeyboardMarkup, InlineKeyboardButton

# ================== SOZLAMALAR ==================
BOT_TOKEN = "8515560975:AAGmRUvORz3gIj39V0HUsAwPdgCYQshlK7o"
CREATOR_ID = 5800819077

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ================== BAD WORDS (regex) ==================
BAD_WORDS = [
    r"http", r"https", r"t\.me", r"@", r"instagram", r"reklama", r"promo"
]

# ================== WARNINGS VA LOG ==================
WARNINGS = {}  # user_id : count
LOG_FILE = "log.txt"
DELETED_LOG = []
MAX_LOG = 10
stats = {"warnings": 0, "kicks": 0, "bans": 0}

# ================== ADMIN TEKSHIRISH ==================
async def is_admin(message: types.Message):
    if message.from_user.id == CREATOR_ID:
        return True
    member = await message.chat.get_member(message.from_user.id)
    return member.is_chat_admin

# ================== START VA INLINE TUGMALAR ==================
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Yaratuvchisi 👤", url="https://t.me/xozyayn2"),
        InlineKeyboardButton(text="Shaxsiy Kanal 📢", url="https://t.me/+8ytWcdHjmmIyNDZi"),
        InlineKeyboardButton(text="Botni Guruhga Qo'shish ➕", url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true")
    )
    await message.reply("✅ Antireklama bot ishga tushdi", reply_markup=keyboard)

# ================== ADMIN PANEL ==================
@dp.message_handler(commands=['panel'])
async def admin_panel(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Siz admin emassiz!")
        return

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="📋 So‘zlar", callback_data="panel_words"),
        InlineKeyboardButton(text="♻️ Reset Warnings", callback_data="panel_reset"),
        InlineKeyboardButton(text="📊 Stats", callback_data="panel_stats"),
        InlineKeyboardButton(text="📝 Log", callback_data="panel_log"),
        InlineKeyboardButton(text="⏳ 1 Soat Ban", callback_data="ban_1h"),
        InlineKeyboardButton(text="⏳ 1 Kun Ban", callback_data="ban_1d")
    )
    await message.reply("🛠 ADMIN PANEL", reply_markup=keyboard)

# ================== SO'Z QO'SHISH ==================
@dp.message_handler(commands=['addword'])
async def add_word(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Siz admin emassiz!")
        return
    word = message.get_args().lower()
    if not word:
        await message.reply("❗ Misol: /addword reklama")
        return
    if word not in BAD_WORDS:
        BAD_WORDS.append(word)
        await message.reply(f"✅ `{word}` qo‘shildi", parse_mode="Markdown")

# ================== SO'Z O'CHIRISH ==================
@dp.message_handler(commands=['delword'])
async def del_word(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Siz admin emassiz!")
        return
    word = message.get_args().lower()
    if word in BAD_WORDS:
        BAD_WORDS.remove(word)
        await message.reply(f"❌ `{word}` o‘chirildi", parse_mode="Markdown")
    else:
        await message.reply("⚠️ Bunday so‘z yo‘q")

# ================== WARN RESET ==================
@dp.message_handler(commands=['resetwarn'])
async def reset_warn(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Siz admin emassiz!")
        return
    if not message.reply_to_message:
        await message.reply("❗ User xabariga reply qilib yoz")
        return
    user_id = message.reply_to_message.from_user.id
    WARNINGS[user_id] = 0
    await message.reply("♻️ Ogohlantirishlar tozalandi")

# ================== ANTIREKLAMA ==================
@dp.message_handler(content_types=types.ContentTypes.ANY)
async def anti_ads(message: types.Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return
    if await is_admin(message):
        return

    text = ""
    if message.text:
        text = message.text.lower()
    elif message.caption:
        text = message.caption.lower()

    for pattern in BAD_WORDS:
        if re.search(pattern, text):
            try:
                await message.delete()
            except:
                return

            user_id = message.from_user.id
            WARNINGS[user_id] = WARNINGS.get(user_id, 0) + 1
            stats["warnings"] += 1

            # Log yozish
            log_entry = f"[{datetime.now()}] ⚠️ {message.from_user.full_name} ({user_id}): {text[:50]}..."
            DELETED_LOG.append(log_entry)
            if len(DELETED_LOG) > MAX_LOG:
                DELETED_LOG.pop(0)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")

            # Ogohlantirish / kick / ban
            if WARNINGS[user_id] == 1:
                await message.answer(f"⚠️ {message.from_user.full_name}, reklama taqiqlangan!")
            elif WARNINGS[user_id] == 2:
                await bot.kick_chat_member(message.chat.id, user_id)
                await bot.unban_chat_member(message.chat.id, user_id)
                stats["kicks"] += 1
                await message.answer(f"👢 {message.from_user.full_name} kick qilindi")
            elif WARNINGS[user_id] >= 3:
                await bot.kick_chat_member(message.chat.id, user_id)
                stats["bans"] += 1
                await message.answer(f"⛔ {message.from_user.full_name} BAN qilindi")
            return

# ================== VAQTINCHALIK BAN ==================
async def temp_ban(user_id, chat_id, duration_seconds):
    await bot.kick_chat_member(chat_id, user_id, until_date=datetime.now() + timedelta(seconds=duration_seconds))
    stats["bans"] += 1
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] ⛔ {user_id} - temporary ban {duration_seconds} sek\n")

@dp.message_handler(commands=['start', 'menu'])
async def start_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Bot Funksiyalari ℹ️", callback_data="func_info"),
        InlineKeyboardButton(text="Admin Panel 🛠", callback_data="open_panel")
    )
    await message.reply("📌 Bot menyusi:", reply_markup=keyboard)

# CALLBACKS
@dp.callback_query_handler(lambda c: c.data)
async def handle_callbacks(callback_query: types.CallbackQuery):
    await callback_query.answer()
    data = callback_query.data

    if data == "func_info":
        await callback_query.message.reply(
            "🤖 Bot funksiyalari:\n1️⃣ Antireklama\n2️⃣ Ogohlantirish\n3️⃣ Kick\n4️⃣ Ban\n5️⃣ Admin Panel\n6️⃣ /addword /delword\n7️⃣ /resetwarn\n8️⃣ /menu"
        )
    elif data == "open_panel":
        if not await is_admin(callback_query.message):
            await callback_query.message.reply("❌ Siz admin emassiz!")
            return
        await admin_panel(callback_query.message)

# ================== BOT START ==================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

