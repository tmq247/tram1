# YukkiMusic/__main__.py
# Copyright (C) ...
import asyncio
import os

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

# (tuỳ chọn) tối ưu loop với uvloop nếu có
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except Exception:
    pass

import config
from config import BANNED_USERS
from YukkiMusic import HELPABLE, LOGGER, app, userbot
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import sudo
from YukkiMusic.utils.database import get_banned_users, get_gbanned

logger = LOGGER("YukkiMusic")

async def init():
    if len(config.STRING_SESSIONS) == 0:
        logger.error("No Assistant Clients Vars Defined!.. Exiting Process.")
        return
    if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
        logger.warning(
            "No Spotify Vars defined. Your bot won't be able to play spotify queries."
        )

    # nạp danh sách ban
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    # cấu hình sudoers trước khi khởi động bot
    await sudo()

    # start main client
    await app.start()

    # load core plugins
    for mod in app.load_plugins_from("YukkiMusic/plugins"):
        if mod and getattr(mod, "__MODULE__", None):
            if getattr(mod, "__HELP__", None):
                HELPABLE[mod.__MODULE__.lower()] = mod

    # extra plugins (optional)
    if config.EXTRA_PLUGINS:
        if os.path.exists("xtraplugins"):
            result = await app.run_shell_command(["git", "-C", "xtraplugins", "pull"])
            if result["returncode"] != 0:
                logger.error(f"Error pulling updates for extra plugins: {result['stderr']}")
                raise SystemExit(1)
        else:
            result = await app.run_shell_command(
                ["git", "clone", config.EXTRA_PLUGINS_REPO, "xtraplugins"]
            )
            if result["returncode"] != 0:
                logger.error(f"Error cloning extra plugins: {result['stderr']}")
                raise SystemExit(1)

        req = os.path.join("xtraplugins", "requirements.txt")
        if os.path.exists(req):
            result = await app.run_shell_command(["uv", "pip", "install", "--system", "-r", req])
            if result["returncode"] != 0:
                logger.error(f"Error installing requirements: {result['stderr']}")

        for mod in app.load_plugins_from("xtraplugins"):
            if mod and getattr(mod, "__MODULE__", None):
                if getattr(mod, "__HELP__", None):
                    HELPABLE[mod.__MODULE__.lower()] = mod

    LOGGER("YukkiMusic.plugins").info("Successfully Imported All Modules ")
    await userbot.start()
    await Yukki.start()
    LOGGER("YukkiMusic").info("Assistant Started Sucessfully")

    # test stream vào log group (nếu call đang mở)
    try:
        await Yukki.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("YukkiMusic").error(
            "Please ensure the voice call in your log group is active."
        )
        raise SystemExit(1)

    await Yukki.decorators()
    LOGGER("YukkiMusic").info("YukkiMusic Started Successfully")

    # block đến khi stop
    await idle()

    # graceful shutdown
    await app.stop()
    await userbot.stop()
    await Yukki.stop()

def main():
    # KHÔNG dùng get_event_loop()/run_until_complete nữa
    asyncio.run(init())
    LOGGER("YukkiMusic").info("Stopping YukkiMusic! GoodBye")

if __name__ == "__main__":
    main()    loop.run_until_complete(init())
    LOGGER("YukkiMusic").info("Stopping YukkiMusic! GoodBye")


if __name__ == "__main__":
    main()
