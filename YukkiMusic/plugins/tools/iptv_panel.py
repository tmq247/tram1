# YukkiMusic/modules/iptv_panel.py

import os
import json
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import BANNED_USERS
from YukkiMusic import app

STREAM_FILE = "streams.json"

def load_streams():
    if not os.path.exists(STREAM_FILE):
        return []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

@app.on_message(filters.command("iptv") & ~BANNED_USERS)
async def iptv_command(client, message: Message):
    streams = load_streams()
    if not streams:
        return await message.reply("📭 Danh sách IPTV hiện trống.")

    buttons = []
    for stream in streams:
        command_text = f"/stream {stream['url']}"
        label = stream["title"].strip()[:32]
        buttons.append([
            InlineKeyboardButton(
                text=label,
                switch_inline_query_current_chat=command_text
            )
        ])

    await message.reply(
        "**🎬 Chọn một kênh để gửi lệnh phát:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
