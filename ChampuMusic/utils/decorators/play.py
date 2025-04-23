import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import PLAYLIST_IMG_URL, PRIVATE_BOT_MODE, SUPPORT_GROUP
from strings import get_string
from ChampuMusic import YouTube, app
from ChampuMusic.core.call import _st_ as clean
from ChampuMusic.misc import SUDOERS
from ChampuMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_commanddelete_on,
    is_maintenance,
    is_served_private_chat,
)
from ChampuMusic.utils.inline import botplaylist_markup

links = {}

def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        userbot = await get_assistant(message.chat.id)
        _ = get_string(language)

        if message.sender_chat:
            return await message.reply_text(
                _["general_4"],
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]]
                ),
            )

        if await is_maintenance() and message.from_user.id not in SUDOERS:
            return await message.reply_text(
                text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_GROUP}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a>.",
                disable_web_page_preview=True,
            )

        if PRIVATE_BOT_MODE == str(True):
            if not await is_served_private_chat(message.chat.id):
                await message.reply_text(
                    "**ᴘʀɪᴠᴀᴛᴇ ᴍᴜsɪᴄ ʙᴏᴛ**\n\nᴏɴʟʏ ғᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴄʜᴀᴛs."
                )
                return await app.leave_chat(message.chat.id)

        if await is_commanddelete_on(message.chat.id):
            try: await message.delete()
            except: pass

        audio_telegram = (
            message.reply_to_message.audio or message.reply_to_message.voice
            if message.reply_to_message else None
        )
        video_telegram = (
            message.reply_to_message.video or message.reply_to_message.document
            if message.reply_to_message else None
        )
        url = await YouTube.url(message)

        if not any([audio_telegram, video_telegram, url]) and len(message.command) < 2:
            if "stream" in message.command:
                return await message.reply_text(_["str_1"])
            return await message.reply_photo(
                photo=PLAYLIST_IMG_URL,
                caption=_["playlist_1"],
                reply_markup=InlineKeyboardMarkup(botplaylist_markup(_)),
            )

        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if not chat_id:
                return await message.reply_text(_["setting_12"])
            try: chat = await app.get_chat(chat_id)
            except: return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        try:
            is_call_active = (await app.get_chat(chat_id)).is_call_active
            if not is_call_active:
                return await message.reply_text("**» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ғᴏᴜɴᴅ.**")
        except:
            pass

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)
        if playty != "Everyone" and message.from_user.id not in SUDOERS:
            admins = adminlist.get(message.chat.id)
            if not admins:
                return await message.reply_text(_["admin_18"])
            if message.from_user.id not in admins:
                return await message.reply_text(_["play_4"])

        video = (
            True if message.command[0][0] == "v"
            or "-v" in message.text
            or (len(message.command[0]) > 1 and message.command[0][1] == "v")
            else None
        )
        fplay = True if message.command[0][-1] == "e" and not await is_active_chat(chat_id) else None

        # Ensure userbot is in chat
        try:
            member = await app.get_chat_member(chat_id, userbot.id)
            if member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]:
                try: await app.unban_chat_member(chat_id, userbot.id)
                except: return await message.reply_text(
                    text=_["call_2"].format(userbot.username, userbot.id)
                )
        except UserNotParticipant:
            invitelink = links.get(chat_id)
            if not invitelink:
                if message.chat.username:
                    invitelink = message.chat.username
                else:
                    try:
                        invitelink = await app.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        return await message.reply_text(_["call_1"])
                    except Exception as e:
                        return await message.reply_text(_["call_3"].format(app.mention, type(e).__name__))
                links[chat_id] = invitelink

            myu = await message.reply_text(_["call_5"])
            try:
                await asyncio.sleep(1)
                await userbot.join_chat(invitelink)
            except InviteRequestSent:
                try:
                    await app.approve_chat_join_request(chat_id, userbot.id)
                except Exception as e:
                    return await myu.edit(_["call_3"].format(type(e).__name__))
                await myu.edit(_["call_6"].format(app.mention))
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await myu.edit(_["call_3"].format(type(e).__name__))
            try: await myu.delete()
            except: pass

        # Clean stream if userbot is not present
        try:
            member = await app.get_chat_member(chat_id, userbot.id)
            if await is_active_chat(chat_id) and member.status == ChatMemberStatus.LEFT:
                await clean(chat_id)
        except: pass

        return await command(
            client, message, _, chat_id, video, channel, playmode, url, fplay
        )

    return wrapper
