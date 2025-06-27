# YukkiMusic/modules/inline_m3u8.py

import os
import json
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
    CallbackQuery,
)

from config import BANNED_USERS
from YukkiMusic import app

STREAM_FILE = "streams.json"

# Load danh sách stream từ file
def load_streams():
    if not os.path.exists(STREAM_FILE):
        return []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# 👉 Inline query trả danh sách stream
@app.on_inline_query(~BANNED_USERS)
async def inline_query_handler(client, query):
    streams = load_streams()
    if not streams:
        await query.answer(
            results=[],
            switch_pm_text="📭 Danh sách stream đang trống.",
            switch_pm_parameter="empty",
            cache_time=5,
        )
        return

    answers = []
    for stream in streams:
        caption = f"""🎬 **{stream['title']}**

📺 [Xem trực tiếp tại đây]({stream['url']})

ℹ️ {stream['description']}

👉 _Bấm nút bên dưới để phát trực tiếp vào voice chat bằng lệnh_ `/stream {stream['url']}`

⚡️ _Nguồn phát do quản trị viên định nghĩa_"""

        answers.append(
            InlineQueryResultPhoto(
                photo_url=stream["thumb"],
                title=stream["title"],
                description=stream["description"],
                caption=caption,
                thumb_url=stream["thumb"],
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("▶️ Phát trong nhóm", callback_data=f"stream_now|{stream['url']}")]]
                ),
            )
        )

    try:
        await client.answer_inline_query(query.id, results=answers, cache_time=60)
    except Exception as e:
        print(f"⚠️ Inline query error: {e}")

# ✅ Xử lý khi bấm nút "Phát trong nhóm"
@app.on_callback_query(filters.regex(r"^stream_now\|") & ~BANNED_USERS)
async def stream_now_handler(client, query: CallbackQuery):
    try:
        _, url = query.data.split("|", 1)
        chat_id = query.message.chat.id

        await query.answer()
        await query.message.delete()

        # Gửi lệnh /stream như thể người dùng vừa gõ tay
        await client.send_message(
            chat_id=chat_id,
            text=f"/stream {url}",
            reply_to_message_id=query.message.id  # hoặc None nếu không muốn reply
        )

    except Exception as e:
        print("❌ Callback error:", e)
        await query.answer("Lỗi khi xử lý phát stream.", show_alert=True)
