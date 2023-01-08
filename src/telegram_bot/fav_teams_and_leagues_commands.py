from telegram import Update

from src.emojis import Emojis
from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import (
    FavouriteLeaguesCommandHandler,
    FavouriteTeamsCommandHandler,
    NotifierBotCommandsHandler,
    SearchCommandHandler,
)

logger = get_logger(__name__)


async def add_favourite_team(update: Update, context):
    logger.info(
        f"'add_favourite_team' command executed - by {update.effective_user.name}"
    )
    commands_handler = FavouriteTeamsCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    validated_input = commands_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        text = commands_handler.add_favourite_team()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def favourite_teams(update: Update, context):
    logger.info(f"'favourite_teams' command executed - by {update.effective_user.name}")
    commands_handler = FavouriteTeamsCommandHandler(
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
        text = commands_handler.get_favourite_teams()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def delete_favourite_team(update: Update, context):
    logger.info(
        f"'delete_favourite_team' command executed - by {update.effective_user.name}"
    )
    commands_handler = FavouriteTeamsCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    validated_input = commands_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        text = commands_handler.delete_favourite_team()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def add_favourite_league(update: Update, context):
    logger.info(
        f"'add_favourite_league' command executed - by {update.effective_user.name}"
    )
    commands_handler = FavouriteLeaguesCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    validated_input = commands_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        text = commands_handler.add_favourite_league()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def delete_favourite_league(update: Update, context):
    logger.info(
        f"'delete_favourite_league' command executed - by {update.effective_user.name}"
    )
    commands_handler = FavouriteLeaguesCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    validated_input = commands_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        text = commands_handler.delete_favourite_league()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def favourite_leagues(update: Update, context):
    logger.info(
        f"'favourite_leagues' command executed - by {update.effective_user.name}"
    )
    commands_handler = FavouriteLeaguesCommandHandler(
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
        text = commands_handler.get_favourite_leagues()

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def available_leagues(update: Update, context):
    logger.info(
        f"'available_leagues' command executed - by {update.effective_user.name}"
    )
    notifier_commands_handler = NotifierBotCommandsHandler()
    texts = notifier_commands_handler.available_leagues_texts()

    intrductory_text = (
        f"{Emojis.WAVING_HAND.value}Hi {update.effective_user.first_name}!\n\n"
        f" {Emojis.TELEVISION.value} These are the available leagues:\n\n"
    )
    texts[0] = f"{intrductory_text}{texts[0]}"

    for text in texts:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def search_team(update: Update, context):
    logger.info(
        f"'search_team {' '.join(context.args)}' command executed - by {update.effective_user.name}"
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
        text = command_handler.search_team_notif()
        logger.info(f"Search Team - text: {text}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def search_league(update: Update, context):
    logger.info(
        f"'search_league {' '.join(context.args)}' command executed - by {update.effective_user.name}"
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
        text = command_handler.search_league_notif()
        logger.info(f"Search League - text: {text}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )


async def search_leagues_by_country(update: Update, context):
    logger.info(
        f"'search_leagues_by_country {' '.join(context.args)}' command executed - by {update.effective_user.name}"
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
        text = command_handler.search_leagues_by_country_notif()
        logger.info(f"Search Leagues by Country - text: {text}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
        )
