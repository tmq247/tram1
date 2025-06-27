import os
import json
from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS
from YukkiMusic import app
from YukkiMusic.misc import SUDOERS

STREAM_FILE = "streams.json"

# Tải dữ liệu từ file JSON
def load_streams():
    if not os.path.exists(STREAM_FILE):
        return []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# Ghi lại dữ liệu vào file
def save_streams(data):
    with open(STREAM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ✅ /addstream Tiêu đề | URL | Mô tả
@app.on_message(filters.command("addstream") & filters.user(list(SUDOERS)) & ~BANNED_USERS)
async def add_stream_handler(client, message: Message):
    if len(message.command) < 2 or "|" not in message.text:
        return await message.reply_text(
            "📥 Dùng đúng cú pháp:\n`/addstream Tiêu đề | URL | Mô tả`", quote=True
        )
    try:
        raw = message.text.split(" ", 1)[1]
        title, url, description = map(str.strip, raw.split("|"))
    except Exception:
        return await message.reply_text("❌ Không thể phân tích cú pháp.")

    streams = load_streams()
    if any(x["title"].lower() == title.lower() for x in streams):
        return await message.reply_text("⚠️ Stream đã tồn tại.")

    streams.append({
        "title": title,
        "url": url,
        "description": description,
    })

    save_streams(streams)
    await message.reply_text(f"✅ Đã thêm stream: **{title}**")

# 🗑️ /delstream Tên
@app.on_message(filters.command("delstream") & filters.user(list(SUDOERS)) & ~BANNED_USERS)
async def del_stream_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("📤 Dùng cú pháp:\n`/delstream Tên_Stream`", quote=True)

    name = " ".join(message.command[1:]).strip().lower()
    streams = load_streams()
    filtered = [x for x in streams if x["title"].lower() != name]

    if len(filtered) == len(streams):
        return await message.reply_text("❌ Không tìm thấy kênh.")

    save_streams(filtered)
    await message.reply_text(f"🗑️ Đã xóa stream: **{name}**")

# 📋 /liststream
@app.on_message(filters.command("liststream") & filters.user(list(SUDOERS)) & ~BANNED_USERS)
async def list_stream_handler(client, message: Message):
    streams = load_streams()
    if not streams:
        return await message.reply_text("📭 Danh sách stream trống.")

    text = "**📺 Danh sách stream hiện tại:**\n\n"
    for idx, x in enumerate(streams, 1):
        text += f"**{idx}. {x['title']}**\n🔗 `{x['url']}`\n📄 {x['description']}\n\n"
    await message.reply_text(text, disable_web_page_preview=True)

# ✏️ /editstream Tên_cũ | Tên_mới | URL | Mô_tả
@app.on_message(filters.command("editstream") & filters.user(list(SUDOERS)) & ~BANNED_USERS)
async def edit_stream_handler(client, message: Message):
    if len(message.command) < 2 or "|" not in message.text:
        return await message.reply_text(
            "✏️ Dùng đúng cú pháp:\n`/editstream Tên_cũ | Tên_mới | URL | Mô_tả`",
            quote=True
        )
    try:
        raw = message.text.split(" ", 1)[1]
        old_title, new_title, new_url, new_description = map(str.strip, raw.split("|"))
    except Exception:
        return await message.reply_text("❌ Lỗi cú pháp.")

    streams = load_streams()
    found = False
    for stream in streams:
        if stream["title"].lower() == old_title.lower():
            stream["title"] = new_title
            stream["url"] = new_url
            stream["description"] = new_description
            found = True
            break

    if not found:
        return await message.reply_text("⚠️ Không tìm thấy kênh.")

    save_streams(streams)
    await message.reply_text(f"✅ Đã cập nhật stream: **{new_title}**")
