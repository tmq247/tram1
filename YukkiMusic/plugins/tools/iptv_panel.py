import os
import json
from pyrogram import filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import BANNED_USERS
from YukkiMusic import app

STREAM_FILE = "streams.json"

# Load danh sách stream
def load_streams():
    if not os.path.exists(STREAM_FILE):
        return []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# /iptv → gửi danh sách kênh dạng nút
@app.on_message(filters.command("iptv") & ~BANNED_USERS)
async def iptv_command(client, message: Message):
    streams = load_streams()
    if not streams:
        return await message.reply("📭 Danh sách IPTV đang trống.")

    buttons = []
    for stream in streams:
        title = stream["title"].strip()
        callback_id = f"iptvplay|{title[:48].lower()}"
        buttons.append([InlineKeyboardButton(title, callback_data=callback_id)])

    await message.reply(
        "🎬 **Chọn kênh bạn muốn phát:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Xử lý khi nhấn vào nút kênh
@app.on_callback_query(filters.regex(r"^iptvplay\|") & ~BANNED_USERS)
async def iptv_play_handler(client, query: CallbackQuery):
    try:
        _, title_key = query.data.split("|", 1)
        streams = load_streams()
        selected = next(
            (s for s in streams if s["title"].strip().lower()[:48] == title_key),
            None
        )
        if not selected:
            await query.answer("❌ Không tìm thấy kênh.", show_alert=True)
            return

        await query.answer()
        await query.message.reply(f"/stream {selected['url']}")

    except Exception as e:
        print("⚠️ Callback error:", e)
        await query.answer("Lỗi khi phát kênh.", show_alert=True)
