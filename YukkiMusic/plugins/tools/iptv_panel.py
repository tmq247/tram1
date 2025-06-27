# YukkiMusic/modules/iptv_panel.py

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

# ✅ Import hàm xử lý phát stream (bạn cần tạo hàm này)
from YukkiMusic.modules.stream_handler import stream_execute

STREAM_FILE = "streams.json"

# Tải danh sách stream
def load_streams():
    if not os.path.exists(STREAM_FILE):
        return []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# Lệnh /iptv: hiển thị danh sách nút chọn
@app.on_message(filters.command("iptv") & ~BANNED_USERS)
async def iptv_command(client, message: Message):
    streams = load_streams()
    if not streams:
        return await message.reply("📭 Danh sách IPTV hiện đang trống.")

    buttons = []
    for stream in streams:
        title = stream["title"].strip()
        key = f"iptv_run|{title[:48].lower()}"
        buttons.append(
            [InlineKeyboardButton(text=title[:32], callback_data=key)]
        )

    await message.reply(
        "**📡 Chọn kênh bạn muốn phát vào voice chat:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Xử lý khi người dùng nhấn nút
@app.on_callback_query(filters.regex(r"^iptv_run\|") & ~BANNED_USERS)
async def iptv_callback_handler(client, query: CallbackQuery):
    try:
        _, title_key = query.data.split("|", 1)
        streams = load_streams()

        selected = next(
            (s for s in streams if s["title"].strip().lower()[:48] == title_key),
            None
        )

        if not selected:
            return await query.answer("❌ Không tìm thấy kênh!", show_alert=True)

        await query.answer("🚀 Đang phát...", show_alert=False)

        # Gọi hàm phát
        await stream_execute(client, query.message.chat.id, selected["url"])

    except Exception as e:
        print("❌ IPTV callback error:", e)
        await query.answer("Đã xảy ra lỗi khi phát kênh.", show_alert=True)
