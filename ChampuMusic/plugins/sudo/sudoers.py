from pyrogram import filters
from pyrogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaVideo
)
from ChampuMusic import app
from ChampuMusic.misc import SUDOERS
from ChampuMusic.utils.database import add_sudo, remove_sudo
from config import BANNED_USERS, OWNER_ID

# Example language dictionary for response messages
_ = {
    "general_1": "Please specify a user.",
    "sudo_1": "{} is already a sudo user.",
    "sudo_2": "{} has been added as a sudo user.",
    "sudo_3": "{} is not a sudo user.",
    "sudo_4": "{} has been removed from the sudo list.",
    "sudo_8": "An error occurred.",
}

# Dummy function for extract_user in case it's missing
async def extract_user(message: Message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        user_id = message.command[1]
        return int(user_id) if user_id.isdigit() else None
    return None

# Ensure OWNER_ID is in SUDOERS by default
SUDOERS.add(OWNER_ID)

@app.on_message(
    filters.command(["addsudo"], prefixes=["/", "!", "%", ",", ".", "@", "#"]) & filters.user(OWNER_ID)
)
async def useradd(client, message: Message):
    user = await extract_user(message)
    if isinstance(user, int):
        user_id = user
        user_mention = f"[User](tg://user?id={user_id})"
    elif user:
        user_id = user.id
        user_mention = user.mention
    else:
        return await message.reply_text(_["general_1"])

    if user_id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(user_mention))

    added = await add_sudo(user_id)
    if added:
        SUDOERS.add(user_id)
        await message.reply_text(_["sudo_2"].format(user_mention))
    else:
        await message.reply_text(_["sudo_8"])


@app.on_message(
    filters.command(["delsudo", "rmsudo"], prefixes=["/", "!", "%", ",", ".", "@", "#"]) & filters.user(OWNER_ID)
)
async def userdel(client, message: Message):
    user = await extract_user(message)
    if isinstance(user, int):
        user_id = user
        user_mention = f"[User](tg://user?id={user_id})"
    elif user:
        user_id = user.id
        user_mention = user.mention
    else:
        return await message.reply_text(_["general_1"])

    if user_id not in SUDOERS:
        return await message.reply_text(_["sudo_3"].format(user_mention))

    removed = await remove_sudo(user_id)
    if removed:
        SUDOERS.remove(user_id)
        await message.reply_text(_["sudo_4"].format(user_mention))
    else:
        await message.reply_text(_["sudo_8"])


@app.on_message(
    filters.command(["sudolist", "listsudo", "sudoers"], prefixes=["/", "!", "%", ",", ".", "@", "#"]) & ~BANNED_USERS
)
async def sudoers_list(client, message: Message):
    keyboard = [[InlineKeyboardButton("๏ ᴠɪᴇᴡ sᴜᴅᴏʟɪsᴛ ๏", callback_data="check_sudo_list")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_video(
        video="https://telegra.ph/file/7fceefa2fb3e21f5fd84e.mp4",
        caption="**» ᴄʜᴇᴄᴋ sᴜᴅᴏ ʟɪsᴛ ʙʏ ɢɪᴠᴇɴ ʙᴜᴛᴛᴏɴ.**\n\n**» ɴᴏᴛᴇ:**  ᴏɴʟʏ sᴜᴅᴏ ᴜsᴇʀs ᴄᴀɴ ᴠɪᴇᴡ.",
        reply_markup=reply_markup,
    )


@app.on_callback_query(filters.regex("^check_sudo_list$"))
async def check_sudo_list(client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in SUDOERS:
        return await callback_query.answer("You are not allowed to view the sudo list.", show_alert=True)

    owner = await app.get_users(OWNER_ID)
    owner_mention = owner.mention or owner.first_name
    caption = f"**˹ʟɪsᴛ ᴏғ ʙᴏᴛ ᴍᴏᴅᴇʀᴀᴛᴏʀs˼**\n\n**🌹Oᴡɴᴇʀ** ➥ {owner_mention}\n\n"
    keyboard = [[InlineKeyboardButton("๏ ᴠɪᴇᴡ ᴏᴡɴᴇʀ ๏", url=f"tg://openmessage?user_id={OWNER_ID}")]]

    count = 1
    for user_id in SUDOERS:
        if user_id != OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user_mention = user.mention or f"User {count}"
                caption += f"**🎁 Sᴜᴅᴏ {count}** ➥ {user_mention}\n"
                keyboard.append(
                    [InlineKeyboardButton(f"๏ ᴠɪᴇᴡ Sᴜᴅᴏ {count} ๏", url=f"tg://openmessage?user_id={user_id}")]
                )
                count += 1
            except Exception:
                continue

    keyboard.append([InlineKeyboardButton("๏ ʙᴀᴄᴋ ๏", callback_data="back_to_main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_caption(caption=caption, reply_markup=reply_markup)


@app.on_callback_query(filters.regex("^back_to_main_menu$"))
async def back_to_main_menu(client, callback_query: CallbackQuery):
    keyboard = [[InlineKeyboardButton("๏ ᴠɪᴇᴡ sᴜᴅᴏʟɪsᴛ ๏", callback_data="check_sudo_list")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await callback_query.message.edit_caption(
        caption="**» ᴄʜᴇᴄᴋ sᴜᴅᴏ ʟɪsᴛ ʙʏ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ.**\n\n**» ɴᴏᴛᴇ:**  ᴏɴʟʏ sᴜᴅᴏ ᴜsᴇʀs ᴄᴀɴ ᴠɪᴇᴡ.",
        reply_markup=reply_markup,
    )


@app.on_message(filters.command(["delallsudo"], prefixes=["/", "!", "%", ",", ".", "@", "#"]) & filters.user(OWNER_ID))
async def del_all_sudo(client, message: Message):
    count = 0
    for user_id in SUDOERS.copy():
        if user_id != OWNER_ID:
            removed = await remove_sudo(user_id)
            if removed:
                SUDOERS.remove(user_id)
                count += 1
    await message.reply_text(f"Removed {count} users from the sudo list.")
