from telegram import Update

from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import (
    SearchCommandHandler,
    TimeZonesCommandHandler,
)

logger = get_logger(__name__)


async def set_main_time_zone(update: Update, context):
    logger.info(
        f"'set_main_time_zone' command executed - by {update.effective_user.name}"
    )
    commands_handler = TimeZonesCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
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
        f"'set_add_time_zone' command executed - by {update.effective_user.name}"
    )
    commands_handler = TimeZonesCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
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

    validated_input = commands_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        text = commands_handler.delete_time_zone()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def search_time_zone(update: Update, context):
    logger.info(
        f"'search_time_zone {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = SearchCommandHandler(
        context.args, update.effective_user.first_name
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
