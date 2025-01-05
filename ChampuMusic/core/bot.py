import uvloop

uvloop.install()

import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

import config

from ..logging import LOGGER


class ChampuBot(Client):
    def __init__(self):
        LOGGER(__name__).info(f"sᴛᴀʀᴛɪɴɢ ʙᴏᴛ...")
        super().__init__(
            "ChampuMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )
    async def start(self):
    await super().start()
    get_me = await self.get_me()
    self.username = get_me.username
    self.id = get_me.id
    self.name = f"{get_me.first_name} {get_me.last_name or ''}".strip()
    self.mention = get_me.mention

    # Create the button
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="๏ ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ๏",
                    url=f"https://t.me/{self.username}?startgroup=true",
                )
            ]
        ]
    )

    # Try to send a message to the logger group
    if config.LOGGER_ID:
        try:
            await self.send_photo(
                chat_id=config.LOGGER_ID,
                photo=config.START_IMG_URL,
                caption=f"""
𖣐 {self.name} ɪs ᴀʟɪᴠᴇ ʙᴀʙʏ 𖣐
━━━━━━━━ ⊱◈◈◈⊰ ━━━━━━━━

● ɪᴅ ➠ `{self.id}`
● ᴜsᴇʀɴᴀᴍᴇ ➠ @{self.username}

◈ ᴛʜᴀɴᴋs ғᴏʀ ᴜsɪɴɢ
━━━━━━━━ ⊱◈◈◈⊰ ━━━━━━━━
""",
                reply_markup=button,
            )
        except pyrogram.errors.ChatWriteForbidden as e:
            LOGGER(__name__).error(f"Bot cannot write to the log group: {e}")
        except Exception as e:
            LOGGER(__name__).error(f"Unexpected error while sending to log group: {e}")
    else:
        LOGGER(__name__).warning("LOGGER_ID is not set, skipping log group notifications.")

    # Setting commands
    if config.SET_CMDS:
        try:
            await self.set_bot_commands(
                commands=[
                    BotCommand("start", "sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
                    BotCommand("help", "ɢᴇᴛ ᴛʜᴇ ʜᴇʟᴘ ᴍᴇɴᴜ"),
                    BotCommand("ping", "ᴄʜᴇᴄᴋ ʙᴏᴛ ɪs ᴀʟɪᴠᴇ ᴏʀ ᴅᴇᴀᴅ"),
                ],
                scope=BotCommandScopeAllPrivateChats(),
            )
            await self.set_bot_commands(
                commands=[
                    BotCommand("play", "Start playing requested song"),
                    BotCommand("stop", "Stop the current song"),
                    BotCommand("pause", "Pause the current song"),
                    BotCommand("resume", "Resume the paused song"),
                    BotCommand("queue", "Check the queue of songs"),
                    BotCommand("skip", "Skip the current song"),
                    BotCommand("volume", "Adjust the music volume"),
                    BotCommand("lyrics", "Get lyrics of the song"),
                ],
                scope=BotCommandScopeAllGroupChats(),
            )
        except Exception as e:
            LOGGER(__name__).error(f"Failed to set bot commands: {e}")

    # Check if bot is an admin in the logger group
    if config.LOGGER_ID:
        try:
            chat_member_info = await self.get_chat_member(
                config.LOGGER_ID, self.id
            )
            if chat_member_info.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "Please promote Bot as Admin in Logger Group"
                )
        except Exception as e:
            LOGGER(__name__).error(f"Error occurred while checking bot status: {e}")

    LOGGER(__name__).info(f"MusicBot Started as {self.name}")
