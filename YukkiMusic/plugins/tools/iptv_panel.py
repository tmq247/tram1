import os
import json
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from config import BANNED_USERS
from YukkiMusic import app, userbot

STREAM_FILE = "streams.json"

# 🧠 Tải danh sách stream từ file JSON
def load_streams():
    if not os.path.exists(STREAM_FILE):
        return []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# 🟢 Lệnh /iptv → hiển thị danh sách kênh dạng nút
@app.on_message(filters.command("iptv") & ~BANNED_USERS)
async def iptv_command(client, message: Message):
    streams = load_streams()
    if not streams:
        return await message.reply("📭 Danh sách IPTV trống.")

    buttons = []
    for stream in streams:
        title = stream["title"].strip()[:32]
        callback_id = f"iptv_stream|{title.lower()[:48]}"
        buttons.append([
            InlineKeyboardButton(text=title, callback_data=callback_id)
        ])

    await message.reply(
        "**📺 Chọn kênh bạn muốn phát vào voice chat:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ⚡ Xử lý khi người dùng nhấn nút chọn kênh
@app.on_callback_query(filters.regex(r"^iptv_stream\|") & ~BANNED_USERS)
async def iptv_play_handler(client, query: CallbackQuery):
    try:
        _, title_key = query.data.split("|", 1)
        streams = load_streams()
        selected = next(
            (s for s in streams if s["title"].strip().lower()[:48] == title_key),
            None
        )

        if not selected:
            return await query.answer("❌ Không tìm thấy kênh!", show_alert=True)

        await query.answer()
        # 🧹 Xóa tin nhắn chứa menu kênh
        await query.message.delete()
        # Gửi lệnh /stream URL như người dùng tự gõ
        first_userbot = userbot.clients[0]

        await first_userbot.send_message(
            chat_id=query.message.chat.id,
            text=f"/stream {selected['url']}",
            reply_to_message_id=query.message.id
        )

    except Exception as e:
        print("⚠️ IPTV callback error:", e)
        await query.answer("Lỗi khi phát kênh!", show_alert=True)
