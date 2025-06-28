#
# Copyright (C) 2024-2025 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#
from datetime import datetime

from pyrogram.types import Message

from config import BANNED_USERS, PING_IMG_URL
from strings import command
from YukkiMusic import app
from YukkiMusic.core.call import Yukki
from YukkiMusic.utils import bot_sys_stats
from YukkiMusic.utils.decorators.language import language
from YukkiMusic.utils.inline import support_group_markup

import asyncio

async def ping_telegram_server():
    proc = await asyncio.create_subprocess_shell(
        "ping -c 1 telegram.org",  # Hoặc thay bằng IP cụ thể nếu bạn biết
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    output = stdout.decode()

    if "time=" in output:
        try:
            # Trích xuất giá trị time
            time_ms = output.split("time=")[-1].split(" ")[0]
            return f"{time_ms} ms"
        except Exception:
            return "Không xác định"
    return "Ping thất bại"

@app.on_message(command("PING_COMMAND") & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    tg_ping = await ping_telegram_server()
    response = await message.reply_photo(
        photo=PING_IMG_URL,
        caption=_["ping_1"].format(app.mention),
    )
    start = datetime.now()
    pytgping = await Yukki.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        _["ping_2"].format(
            resp,
            app.mention,
            UP,
            RAM,
            CPU,
            DISK,
            pytgping,
            tg_ping,
        ),
        reply_markup=support_group_markup(_),
    )
