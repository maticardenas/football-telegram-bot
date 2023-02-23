from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from src.db.notif_sql_models import TimeZone
from src.emojis import Emojis
from src.notifier_constants import (
    END_COMMAND_MESSAGE,
    SEARCH_TIME_ZONE,
    SET_ADD_TIME_ZONE,
    SET_MAIN_TIME_ZONE,
    TIME_ZONES_PAGE_SIZE,
)
from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import (
    SearchCommandHandler,
    TimeZonesCommandHandler,
)

logger = get_logger(__name__)


async def set_main_time_zone(update: Update, context):
    logger.info(
        f"'set_main_time_zone' command initialized - by {update.effective_user.name}"
    )
    await update.message.reply_text(
        "Please insert the time zone you would like to set as main one.",
    )

    context.user_data["command"] = "set_main_time_zone"

    return SEARCH_TIME_ZONE


async def show_time_zones(update, context, page):
    time_zones = context.user_data["time_zones"]
    pages = context.user_data["pages"]

    start = page * TIME_ZONES_PAGE_SIZE
    end = start + TIME_ZONES_PAGE_SIZE

    time_zones_keyboard = [
        [InlineKeyboardButton(tz.name, callback_data=f"time_zone:{tz.id}:{tz.name}")]
        for tz in time_zones[start:end]
    ]

    prev_button = (
        InlineKeyboardButton("<< Prev", callback_data=f"tz_page:{page - 1}")
        if page > 0
        else None
    )
    next_button = (
        InlineKeyboardButton("Next >>", callback_data=f"tz_page:{page + 1}")
        if page < pages - 1
        else None
    )

    prev_next_row = []
    if prev_button:
        prev_next_row.append(prev_button)
    if next_button:
        prev_next_row.append(next_button)

    keyboard = [*time_zones_keyboard, prev_next_row]

    logger.info(f"KEYBOARD: {keyboard}")

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Choose your time zone: ",
            reply_markup=reply_markup,
        )
    else:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)


async def search_time_zones_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    data = query.data

    if data.startswith("tz_page:"):
        page = int(data.split(":")[1])
        await show_time_zones(update, context, page)
    elif data.startswith("time_zone:"):
        tz_data = data.split(":")[1:]
        logger.info(f"TZ_DATA - {tz_data}")
        commands = {
            "set_add_time_zone": set_add_time_zone_handler,
            "set_main_time_zone": set_main_time_zone_handler,
        }
        context.user_data["time_zone_id"] = tz_data[0]

        await commands.get(context.user_data["command"])(update, context)


async def set_main_time_zone_handler(update: Update, context):
    commands_handler = TimeZonesCommandHandler(
        [context.user_data["time_zone_id"]],
        update.effective_user.first_name,
        str(update.effective_chat.id),
    )

    validated_input = commands_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        text = commands_handler.add_time_zone(main=True)

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def set_add_time_zone(update: Update, context):
    logger.info(
        f"'set_add_time_zone' command initialized - by {update.effective_user.name}"
    )
    await update.message.reply_text(
        f"Please enter the time zone you would like to set as additional one {Emojis.DOWN_FACING_FIST.value}\n\n{END_COMMAND_MESSAGE}",
        parse_mode="HTML",
    )

    context.user_data["command"] = "set_add_time_zone"

    return SEARCH_TIME_ZONE


async def set_add_time_zone_handler(update: Update, context):
    logger.info(
        f"'set_add_time_zone' {context.user_data['time_zone_id']} command executed - by {update.effective_user.name}"
    )
    commands_handler = TimeZonesCommandHandler(
        [context.user_data["time_zone_id"]],
        update.effective_user.first_name,
        str(update.effective_chat.id),
    )

    validated_input = commands_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        text = commands_handler.add_time_zone()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def my_time_zones(update: Update, context):
    logger.info(f"'my_time_zones' command executed - by {update.effective_user.name}")
    commands_handler = TimeZonesCommandHandler(
        context.args,
        update.effective_user.first_name,
        str(update.effective_chat.id),
        is_list=True,
    )

    validated_input = commands_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        text = commands_handler.get_my_time_zones()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def delete_time_zone(update: Update, context):
    logger.info(
        f"'delete_time_zone' command executed - by {update.effective_user.name}"
    )
    commands_handler = TimeZonesCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    if not len(context.args):
        await own_time_zones_inline_keyboard(
            update, context, commands_handler.get_time_zones()
        )
    else:
        validated_input = commands_handler.validate_command_input()

        if validated_input:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=validated_input,
                parse_mode="HTML",
            )
        else:
            text = commands_handler.delete_time_zone()

            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
            )


async def own_time_zones_inline_keyboard(
    update: Update, context, time_zones: List[TimeZone]
):
    keyboard = [
        [
            InlineKeyboardButton(
                time_zones[i].name,
                callback_data=f"delete_time_zone {time_zones[i].id}",
            ),
            InlineKeyboardButton(
                time_zones[i + 1].name,
                callback_data=f"delete_time_zone {time_zones[i+1].id}",
            ),
        ]
        for i in range(0, len(time_zones), 2)
        if i + 1 < len(time_zones)
    ]

    if len(time_zones) % 2 != 0:
        keyboard = [
            *keyboard,
            [
                InlineKeyboardButton(
                    time_zones[-1].name,
                    callback_data=f"delete_time_zone {time_zones[-1].id}",
                )
            ],
        ]

    reply_markup = InlineKeyboardMarkup(list(keyboard))

    text = f"Please choose the league you would like to remove from your favourites:"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def delete_time_zone_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    context.args = [query.data.split()[1]]

    await delete_time_zone(update, context)


async def search_time_zone(update: Update, context):
    logger.info(
        f"'search_time_zone {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    await update.message.reply_text(
        "Please insert the name (or part of the name) of the time zone you are looking for.",
    )

    return SEARCH_TIME_ZONE


async def search_time_zone_handler(update: Update, context):
    logger.info(
        f"'search_time_zone {update.message.text}' command executed - by {update.effective_user.name}"
    )
    command_handler = SearchCommandHandler(
        [update.message.text], update.effective_user.first_name
    )
    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        time_zones = command_handler.search_time_zone(update.message.text)

        page = 0
        pages = len(time_zones) // TIME_ZONES_PAGE_SIZE + (
            1 if len(time_zones) % TIME_ZONES_PAGE_SIZE else 0
        )
        context.user_data["time_zones"] = time_zones
        context.user_data["pages"] = pages
        context.user_data["start"] = True

        await show_time_zones(update, context, page)
