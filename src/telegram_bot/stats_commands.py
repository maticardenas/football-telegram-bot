from telegram import Update

from src.emojis import Emojis
from src.notifier_constants import END_COMMAND_MESSAGE, TEAM_SUMMARY
from src.notifier_logger import get_logger
from src.telegram_bot.command_handlers.statistics_command_handler import (
    TeamStatisticsBotCommandsHandler,
)
from src.telegram_bot.commands_utils import reply_text, send_photo

logger = get_logger(__name__)


async def team_summary(update: Update, context):
    logger.info(f"'team_summary' command executed - by {update.effective_user.name}")

    text = (
        f"Please enter the name of the team you would like the summary of {Emojis.DOWN_FACING_FIST.value}\n\n"
        f"{END_COMMAND_MESSAGE}"
    )

    await reply_text(update, text)

    context.user_data["command"] = "team_summary"

    return TEAM_SUMMARY


async def team_summary_handler(update: Update, context):
    commands_handler = TeamStatisticsBotCommandsHandler(
        context.user_data["team_id"],
        str(update.effective_chat.id),
    )

    text, photo = commands_handler.teams_summary()

    await send_photo(update=update, context=context, photo=photo, caption=text)
