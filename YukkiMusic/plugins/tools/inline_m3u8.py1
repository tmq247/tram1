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

# 🔄 Tải danh sách stream
def load_streams():
    if not os.path.exists(STREAM_FILE):
        return []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# 📥 Inline query hiển thị stream
@app.on_inline_query(~BANNED_USERS)
async def inline_query_handler(client, query):
    streams = load_streams()
    if not streams:
        await query.answer(
            results=[],
            switch_pm_text="📭 Danh sách stream trống.",
            switch_pm_parameter="empty",
            cache_time=5,
        )
        return

    answers = []
    for stream in streams:
        title = stream["title"].strip()
        callback_id = title[:48].lower()  # An toàn dưới 64 ký tự

        caption = f"""🎬 **{stream['title']}**

📺 [Xem trực tiếp tại đây]({stream['url']})

ℹ️ {stream['description']}

👉 _Bấm nút bên dưới để phát vào voice chat bằng lệnh_ `/stream {stream['url']}`

⚡️ _Nguồn phát do quản trị viên định nghĩa_"""

        answers.append(
            InlineQueryResultPhoto(
                photo_url=stream["thumb"],
                title=stream["title"],
                description=stream["description"],
                caption=caption,
                thumb_url=stream["thumb"],
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("▶️ Phát trong nhóm", callback_data=f"stream_now|{callback_id}")]]
                ),
            )
        )

    try:
        await client.answer_inline_query(query.id, results=answers, cache_time=60)
    except Exception as e:
        print(f"⚠️ Inline query error: {e}")

# 🎯 Xử lý khi nhấn nút callback
@app.on_callback_query(filters.regex(r"^stream_now\|") & ~BANNED_USERS)
async def stream_now_handler(client, query: CallbackQuery):
    try:
        _, title_raw = query.data.split("|", 1)
        title_key = title_raw.strip().lower()

        streams = load_streams()
        selected = next(
            (s for s in streams if s["title"].strip().lower()[:48] == title_key),
            None
        )

        if not selected:
            await query.answer("❌ Không tìm thấy stream.", show_alert=True)
            return

        await query.answer()
        await query.message.delete()

        await client.send_message(
            chat_id=query.message.chat.id,
            text=f"/stream {selected['url']}",
            reply_to_message_id=query.message.id
        )

    except Exception as e:
        print(f"❌ Callback handler error: {e}")
        await query.answer("Lỗi khi xử lý stream.", show_alert=True)
