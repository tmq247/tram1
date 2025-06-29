import asyncio
import traceback
from typing import Optional
from random import randint
from pyrogram.types import Message, ChatPrivileges
from pyrogram import Client, filters
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat, InputPeerUser
from YukkiMusic.utils.database import *
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.errors import (
    ChannelsTooMuch,
    ChatAdminRequired,
    FloodWait,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from YukkiMusic import app, userbot
from typing import List, Union
from pyrogram import filters
from YukkiMusic.core.call import Yukki
from pyrogram.types import VideoChatEnded, Message
from ntgcalls import TelegramServerError
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import (
    ChatUpdate,
    GroupCallConfig,
    MediaStream,
    StreamEnded,
)
from config import BANNED_USERS
async def safe_join_call(assistant, chat_id, audio_path):
   # \"\"\"Safe method to join call with multiple API attempts\"\"\"
    # Prepare audio stream
    if MediaStream != str:
        try:
            stream = MediaStream(audio_path)
        except:
            stream = audio_path
    else:
        stream = audio_path
    
    # Try different join methods
    join_methods = ["join_group_call", "join_call", "play", "start_call"]
    
    for method_name in join_methods:
        if hasattr(assistant, method_name):
            try:
                method = getattr(assistant, method_name)
                await method(chat_id, stream)
                return True
            except Exception as e:
                print(f"⚠️ {method_name} failed: {e}")
                continue
    
    return False

async def safe_leave_call(assistant, chat_id):
   # \"\"\"Safe method to leave call with multiple API attempts\"\"\"
    leave_methods = ["leave_group_call", "leave_call", "stop", "disconnect"]
    
    for method_name in leave_methods:
        if hasattr(assistant, method_name):
            try:
                await getattr(assistant, method_name)(chat_id)
                return True
            except:
                continue
    
    return False

############################################

@app.on_message(filters.command("vcinfo", prefixes=["/", "!"]) & filters.group & ~BANNED_USERS)
async def strcall(client, message):
    assistant = await group_assistant(Yukki, message.chat.id)
    userbot = await get_assistant(message.chat.id)
    userbot_id = userbot.id

    try:
        # Tham gia call bằng assistant
        await safe_join_call(assistant, message.chat.id, "./call.mp3")

        try:
            participants = await assistant.get_participants(message.chat.id)
        except Exception as e:
            await message.reply(f"❌ Không thể lấy danh sách người tham gia: {e}")
            return

        text = "- Những người đang tham gia cuộc gọi nhóm 🫶 :\n\n"
        index = 1

        for participant in participants:
            try:
                user = await userbot.get_users(participant.user_id)
                if user.id == userbot_id:
                    continue

                mic = "Đang mở mic 🗣" if not participant.muted else "Đang tắt mic 🔕"
                try:
                    name = user.mention
                except Exception:
                    name = f"`{user.first_name}`"

                text += f"{index} ➤ {name} ➤ {mic}\n"
                index += 1

            except Exception as e:
                print(f"⚠️ Không thể lấy thông tin user_id {participant.user_id}: {e}")
                continue

        text += f"\nSố người đang tham gia (không tính bot): {index - 1}"
        await message.reply(text)
        await asyncio.sleep(7)
        await safe_leave_call(assistant, message.chat.id)

    except Exception as e:
        error_msg = str(e).lower()
        if "no active" in error_msg or "notincall" in error_msg:
            await message.reply("❌ Hiện không có cuộc gọi nhóm nào đang diễn ra.")
        elif "telegram server" in error_msg:
            await message.reply("⚠️ Máy chủ Telegram đang gặp sự cố, hãy thử lại sau.")
        elif "already joined" in error_msg:
            # Khi đã join rồi thì chỉ cần lấy danh sách
            try:
                participants = await assistant.get_participants(message.chat.id)
                text = "- Những người đang tham gia cuộc gọi nhóm 🫶 :\n\n"
                index = 1
                for participant in participants:
                    try:
                        user = await userbot.get_users(participant.user_id)
                        if user.id == userbot_id:
                            continue
                        mic = "Đang mở mic 🗣" if not participant.muted else "Đang tắt mic 🔕"
                        name = user.mention if hasattr(user, "mention") else f"`{user.full_name}`"
                        text += f"{index} ➤ {name} ➤ {mic}\n"
                        index += 1
                    except Exception as e:
                        print(f"⚠️ Không thể lấy user: {e}")
                        continue
                text += f"\nSố người đang tham gia (không tính bot): {index - 1}"
                await message.reply(text)
            except Exception:
                await message.reply("❌ Không lấy được danh sách người tham gia.")
                print(traceback.format_exc())
        else:
            await message.reply(f"💥 Lỗi không xác định: {str(e)}")
            print(traceback.format_exc())



other_filters = filters.group  & ~filters.via_bot & ~filters.forwarded
other_filters2 = (
    filters.private  & ~filters.via_bot & ~filters.forwarded
)


def command(commands: Union[str, List[str]]):
    return filters.command(commands, "")


  ################################################
async def adminbot(m: Message):
    try:
        bot_id = (await userbot.get_me()).id
        bot_member = await client.get_chat_member(message.chat.id, bot_id)

        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ Bot không phải là quản trị viên trong nhóm này.")

        if not bot_member.privileges or not bot_member.privileges.can_manage_video_chats:
            return await message.reply_text("⚠️ Bot là quản trị viên nhưng không có quyền quản lý video chats.")
    except Exception as e:
        return await message.reply_text(f"Đã xảy ra lỗi khi kiểm tra quyền của bot: {e}")


async def get_group_call(
    client: Client, message: Message, err_msg: str = ""
) -> Optional[InputGroupCall]:
    assistant = await get_assistant(message.chat.id)
    chat_peer = await assistant.resolve_peer(message.chat.id)
    if isinstance(chat_peer, (InputPeerChannel, InputPeerChat)):
        if isinstance(chat_peer, InputPeerChannel):
            full_chat = (
                await assistant.invoke(GetFullChannel(channel=chat_peer))
            ).full_chat
        elif isinstance(chat_peer, InputPeerChat):
            full_chat = (
                await assistant.invoke(GetFullChat(chat_id=chat_peer.chat_id))
            ).full_chat
        if full_chat is not None:
            return full_chat.call
    await app.send_message("**Cuộc gọi nhóm đang bị tắt** {err_msg}")
    return False

@app.on_message(filters.command("mocall", prefixes=["/", "!"]) & filters.group & ~BANNED_USERS)
async def start_group_call(c: Client, m: Message):
    chat_id = m.chat.id
    assistant = await get_assistant(chat_id)
    ass = await assistant.get_me()
    assid = ass.id
    assum = ass.username
    bot_member = await app.get_chat_member(chat_id, assid)
    if assistant is None:
        await app.send_message(chat_id, "Lỗi userbot")
        return
    try:
        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await app.send_message(f"""❌ Userbot không có quyền mở call trong nhóm này. Thêm userbot {assum} làm qtv với quyền quản lý call.""")
        if not bot_member.privileges or not bot_member.privileges.can_manage_video_chats:
            return await app.send_message(f"""⚠️ Userbot {assum} là quản trị viên nhưng không có quyền quản lý call.""")
    except Exception as e:
        return await app.send_message(f"Đã xảy ra lỗi khi kiểm tra quyền của userbot: {e}")

    msg = await app.send_message(chat_id, "Đang mở cuộc gọi nhóm..")
    try:
        if group_call := (await get_group_call(assistant, m)):  
            return await msg.edit_text("Cuộc gọi nhóm đã được mở trước đó.")
    # Nếu chưa có trong storage, thử lấy thông tin chat để lưu vào storage
        await assistant.get_chat(chat_id)
        peer = await assistant.resolve_peer(chat_id)
        await assistant.invoke(
            CreateGroupCall(
                peer=InputPeerChannel(
                    channel_id=peer.channel_id,
                    access_hash=peer.access_hash,
                ),
                random_id=assistant.rnd_id() // 9000000000,
            )
        )
        await msg.edit_text("Cuộc gọi nhóm đã được mở thành công⚡️~!")

    except ChatAdminRequired:
      try:    
        await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=True,
                can_restrict_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_promote_members=False,
        ),)
        peer = await assistant.resolve_peer(chat_id)
        if group_call := (await get_group_call(assistant, m)):  
            return await msg.edit_text("Cuộc gọi nhóm đã được mở trước đó.")
        await assistant.invoke(
            CreateGroupCall(
                peer=InputPeerChannel(
                    channel_id=peer.channel_id,
                    access_hash=peer.access_hash,
                ),
                random_id=assistant.rnd_id() // 9000000000,
            )
        )
        await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_promote_members=False,
            ),
        )                              
        await msg.edit_text("Cuộc gọi nhóm đã được mở thành công⚡️~!")
      except:
         await msg.edit_text("Cấp quyền quản lý cuộc gọi nhóm cho bot, userbot và thử lại⚡")

@app.on_message(filters.command("tatcall", prefixes=["/", "!"]) & filters.group & ~BANNED_USERS)
async def stop_group_call(c: Client, m: Message):
    chat_id = m.chat.id
    assistant = await get_assistant(chat_id)
    ass = await assistant.get_me()
    assid = ass.id
    assum = ass.username
    bot_member = await app.get_chat_member(chat_id, assid)
    if assistant is None:
        await app.send_message(chat_id, "Userbot lỗi")
        return
    try:
        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await app.send_message(f"""❌ Userbot không có quyền mở call trong nhóm này. Thêm userbot {assum} làm qtv với quyền quản lý call.""")
        if not bot_member.privileges or not bot_member.privileges.can_manage_video_chats:
            return await app.send_message(f"""⚠️ Userbot {assum} là quản trị viên nhưng không có quyền quản lý call.""")
    except Exception as e:
        return await app.send_message(f"Đã xảy ra lỗi khi kiểm tra quyền của userbot: {e}")

    msg = await app.send_message(chat_id, "Đang tắt cuộc gọi nhóm..")
    try:
        if not (group_call := (await get_group_call(assistant, m))):  
            return await msg.edit_text("Cuộc gọi nhóm đã được tắt trước đó.")
        await assistant.invoke(DiscardGroupCall(call=group_call))
        await msg.edit_text("Cuộc gọi nhóm đã được tắt thành công⚡️~!")
    except Exception as e:
      if "GROUPCALL_FORBIDDEN" in str(e):
       try:    
         await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=True,
                can_restrict_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_promote_members=False,
             ),
         )
         if not (group_call := (await get_group_call(assistant, m))):  
             return await msg.edit_text("Cuộc gọi nhóm đã được tắt trước đó")
         await assistant.invoke(DiscardGroupCall(call=group_call))
         await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_promote_members=False,
            ),
         )            
         await msg.edit_text("Cuộc gọi nhóm đã được tắt thành công⚡️~!")
       except:
         await msg.edit_text("Bot thiếu quyền quản lý cuộc gọi nhóm")
