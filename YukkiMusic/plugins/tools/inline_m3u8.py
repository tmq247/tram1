import os
import json
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
)

from config import BANNED_USERS
from YukkiMusic import app
from YukkiMusic.misc import SUDOERS

STREAM_FILE = "streams.json"

def load_streams():
    if not os.path.exists(STREAM_FILE):
        return []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

@app.on_inline_query(~BANNED_USERS)
async def inline_query_handler(client, query):
    user_id = query.from_user.id
    if user_id not in SUDOERS:
        await query.answer(
            results=[],
            switch_pm_text="🚫 Bạn không có quyền sử dụng tính năng inline này.",
            switch_pm_parameter="no_access",
            cache_time=5,
        )
        return

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

👉 _Trả lời tin nhắn này bằng lệnh_ `/stream {stream['url']}` _để phát trực tiếp trong voice chat._

⚡️ _Nguồn phát do quản trị viên định nghĩa_"""
        answers.append(
            InlineQueryResultPhoto(
                photo_url=stream["thumb"],
                title=stream["title"],
                description=stream["description"],
                caption=caption,
                thumb_url=stream["thumb"],
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("▶️ Xem ngay", url=stream["url"])]]
                ),
            )
        )

    try:
        await client.answer_inline_query(query.id, results=answers, cache_time=60)
    except Exception as e:
        print(f"⚠️ Lỗi khi trả inline query: {e}")
