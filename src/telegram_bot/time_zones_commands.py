from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from src.db.notif_sql_models import TimeZone
from src.notifier_constants import (
    SEARCH_TIME_ZONE,
    SET_ADD_TIME_ZONE,
    SET_MAIN_TIME_ZONE,
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
        "Please insert the id of the time zone you would like to set as main.",
    )

    return SET_MAIN_TIME_ZONE


async def set_main_time_zone_handler(update: Update, context):
    commands_handler = TimeZonesCommandHandler(
        [update.message.text],
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
        "Please insert the id of the time zone you would like to set as additional one.",
    )

    return SET_ADD_TIME_ZONE


async def set_add_time_zone_handler(update: Update, context):
    logger.info(
        f"'set_add_time_zone' {update.message.text} command executed - by {update.effective_user.name}"
    )
    commands_handler = TimeZonesCommandHandler(
        [update.message.text],
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
        text = command_handler.search_time_zone_notif()
        logger.info(f"Search Time Zone - text: {text}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )
