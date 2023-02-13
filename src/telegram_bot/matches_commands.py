from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from src.notifier_constants import NEXT_MATCH, LAST_MATCH, NEXT_MATCH_LEAGUE, LAST_MATCH_LEAGUE
from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import (
    NextAndLastMatchCommandHandler,
    NextAndLastMatchLeagueCommandHandler,
    SurroundingMatchesHandler,
)

logger = get_logger(__name__)


async def next_match(update: Update, context):
    logger.info(
        f"'next_match initialized - by {update.effective_user.name}"
    )
    await update.message.reply_text(
        "Please insert the id of the team for which you would like to get the next match:",
    )

    return NEXT_MATCH

async def next_match_handler(update: Update, context):
    logger.info(
        f"'next_match {update.message.text}' command executed - by {update.effective_user.name}"
    )
    command_handler = NextAndLastMatchCommandHandler(
        [update.message.text], update.effective_user.first_name, str(update.effective_chat.id)
    )

    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input
        )
    else:
        text, photo = command_handler.next_match_team_notif()
        logger.info(f"Fixture - text: {text} - photo: {photo}")
        if photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=text,
                parse_mode="HTML",
            )
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def last_match(update: Update, context):
    logger.info(
        f"'last_match initialized - by {update.effective_user.name}"
    )
    await update.message.reply_text(
        "Please insert the id of the team for which you would like to get the last match.",
    )

    return LAST_MATCH


async def last_match_handler(update: Update, context):
    logger.info(
        f"'last_match {update.message.text}' command executed - by {update.effective_user.first_name}"
    )
    command_handler = NextAndLastMatchCommandHandler(
        [update.message.text], update.effective_user.first_name, str(update.effective_chat.id)
    )
    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input
        )
    else:
        text, photo = command_handler.last_match_team_notif()
        logger.info(f"Fixture - text: {text} - photo: {photo}")
        if photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=text,
                parse_mode="HTML",
            )
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def next_match_league(update: Update, context):
    logger.info(
        f"'next_match_league {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )

    await update.message.reply_text(
        "Please insert the id of the league for which you would like to get the next match.",
    )

    return NEXT_MATCH_LEAGUE

async def next_match_league_handler(update: Update, context):
    logger.info(
        f"'next_match_league {update.message.text}' command executed - by {update.effective_user.name}"
    )
    command_handler = NextAndLastMatchLeagueCommandHandler(
        [update.message.text], update.effective_user.first_name, update.effective_chat.id
    )

    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input
        )
    else:
        text, photo = command_handler.next_match_league_notif()
        logger.info(f"Fixture - text: {text} - photo: {photo}")
        if photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=text,
                parse_mode="HTML",
            )
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def next_matches_league(update: Update, context):
    logger.info(
        f"'next_matches_league {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = NextAndLastMatchLeagueCommandHandler(
        context.args, update.effective_user.first_name, update.effective_chat.id
    )

    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input
        )
    else:
        texts = command_handler.next_matches_league_notif()
        logger.info(f"Fixture - texts: {texts}")
        for text in texts:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
            )



async def last_match_league(update: Update, context):
    logger.info(
        f"/last_match_league initialized - by {update.effective_user.first_name}"
    )
    await update.message.reply_text(
        "Please insert the id of the league for which you would like to get the last match.",
    )

    return LAST_MATCH_LEAGUE


async def last_match_league(update: Update, context):
    logger.info(
        f"'last_match_league {update.message.text}' command executed - by {update.effective_user.first_name}"
    )
    command_handler = NextAndLastMatchLeagueCommandHandler(
        [update.message.text], update.effective_user.first_name, update.effective_chat.id
    )
    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input
        )
    else:
        text, photo = command_handler.last_match_league_notif()
        logger.info(f"Fixture - text: {text} - photo: {photo}")
        if photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=text,
                parse_mode="HTML",
            )
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def today_matches_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    context.args = [query.data.split()[1]]

    await today_matches(update, context)


async def tomorrow_matches_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    context.args = [query.data.split()[1]]

    await tomorrow_matches(update, context)


async def upcoming_matches_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    context.args = [query.data.split()[1]]

    await upcoming_matches(update, context)


async def yesterday_matches_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    context.args = [query.data.split()[1]]

    await yesterday_matches(update, context)


async def favourite_teams_and_leagues_inline_keyboard(
    update: Update, context, command: str
):
    keyboard = [
        [
            InlineKeyboardButton("Favourite Leagues", callback_data=f"{command} fl"),
            InlineKeyboardButton("Favourite Teams", callback_data=f"{command} ft"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Please choose the option you'd like to get <strong>{' '.join(command.split('_'))}</strong> for:"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def today_matches(update: Update, context):
    logger.info(
        f"/today_matches {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = SurroundingMatchesHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    if not len(context.args):
        await favourite_teams_and_leagues_inline_keyboard(
            update, context, "today_matches"
        )
    else:
        validated_input = command_handler.validate_command_input()

        if validated_input:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=validated_input,
                parse_mode="HTML",
            )
        else:
            texts, photo = command_handler.today_games()

            for text in texts:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode="HTML",
                )


async def upcoming_matches(update: Update, context):
    logger.info(
        f"'upcoming_matches {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = NextAndLastMatchCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    if not len(context.args):
        await favourite_teams_and_leagues_inline_keyboard(
            update, context, "upcoming_matches"
        )
    else:
        validated_input = command_handler.validate_command_input()

        if validated_input:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=validated_input,
                parse_mode="HTML",
            )
        else:
            texts, photo = command_handler.upcoming_matches()

            for text in texts:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode="HTML",
                )


async def last_matches(update: Update, context):
    logger.info(
        f"'last_matches {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = NextAndLastMatchCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input
        )
    else:
        texts, photo = command_handler.last_matches()

        for text in texts:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="HTML",
            )


async def yesterday_matches(update: Update, context):
    logger.info(
        f"'yesterday_matches {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = SurroundingMatchesHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    if not len(context.args):
        await favourite_teams_and_leagues_inline_keyboard(
            update, context, "yesterday_matches"
        )
    else:
        validated_input = command_handler.validate_command_input()

        if validated_input:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=validated_input,
                parse_mode="HTML",
            )
        else:
            texts, photo = command_handler.yesterday_games()

            for text in texts:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode="HTML",
                )


async def tomorrow_matches(update: Update, context):
    logger.info(
        f"'tomorrow_matches {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = SurroundingMatchesHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    if not len(context.args):
        await favourite_teams_and_leagues_inline_keyboard(
            update, context, "tomorrow_matches"
        )
    else:
        validated_input = command_handler.validate_command_input()

        if validated_input:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=validated_input,
                parse_mode="HTML",
            )
        else:
            texts, photo = command_handler.tomorrow_games()

            for text in texts:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode="HTML",
                )
