from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler

from src.db.notif_sql_models import FavouriteTeam, Team
from src.emojis import Emojis
from src.notifier_constants import (
    ADD_FAVOURITE_LEAGUE,
    ADD_FAVOURITE_TEAM,
    SEARCH_LEAGUE,
    SEARCH_LEAGUES_BY_COUNTRY,
    SEARCH_TEAM,
    TEAMS_PAGE_SIZE,
)
from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import (
    FavouriteLeaguesCommandHandler,
    FavouriteTeamsCommandHandler,
    NotifierBotCommandsHandler,
    SearchCommandHandler,
)
from src.telegram_bot.matches_commands import (
    last_match_handler,
    last_match_league_handler,
    last_matches_handler,
    next_match_handler,
    next_match_league_handler,
)

logger = get_logger(__name__)


async def add_favourite_team(update: Update, context):
    logger.info(
        f"'add_favourite_team' command executed - by {update.effective_user.name}"
    )

    await update.message.reply_text(
        f"Please enter the id of the team you would like me to add as your favourite {Emojis.DOWN_FACING_FIST.value}",
    )

    context.user_data["command"] = "add_favourite_team"

    return ADD_FAVOURITE_TEAM


async def add_favourite_team_handler(update: Update, context):
    commands_handler = FavouriteTeamsCommandHandler(
        [context.user_data["team_id"]],
        update.effective_user.first_name,
        str(update.effective_chat.id),
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
        text = commands_handler.get_favourite_teams_response()

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

    if not len(context.args):
        await own_favourite_teams_inline_keyboard(
            update, context, commands_handler.get_favourite_teams()
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
            text = commands_handler.delete_favourite_team()

            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
            )


async def delete_favourite_team_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    context.args = [query.data.split()[1]]

    await delete_favourite_team(update, context)


async def own_favourite_teams_inline_keyboard(
    update: Update, context, teams: List[Team]
):
    keyboard = [
        [
            InlineKeyboardButton(
                teams[i].name, callback_data=f"delete_favourite_team {teams[i].id}"
            ),
            InlineKeyboardButton(
                teams[i + 1].name,
                callback_data=f"delete_favourite_team {teams[i+1].id}",
            ),
        ]
        for i in range(0, len(teams), 2)
        if i + 1 < len(teams)
    ]

    if len(teams) % 2 != 0:
        keyboard = [
            *keyboard,
            [
                InlineKeyboardButton(
                    teams[-1].name,
                    callback_data=f"delete_favourite_team {teams[-1].id}",
                )
            ],
        ]

    reply_markup = InlineKeyboardMarkup(list(keyboard))

    text = f"Please choose the team you would like to remove from your favourites:"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def delete_favourite_league_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    context.args = [query.data.split()[1]]

    await delete_favourite_league(update, context)


async def own_favourite_leagues_inline_keyboard(
    update: Update, context, leagues: List[Team]
):
    keyboard = [
        [
            InlineKeyboardButton(
                leagues[i].name,
                callback_data=f"delete_favourite_league {leagues[i].id}",
            ),
            InlineKeyboardButton(
                leagues[i + 1].name,
                callback_data=f"delete_favourite_league {leagues[i+1].id}",
            ),
        ]
        for i in range(0, len(leagues), 2)
        if i + 1 < len(leagues)
    ]

    if len(leagues) % 2 != 0:
        keyboard = [
            *keyboard,
            [
                InlineKeyboardButton(
                    leagues[-1].name,
                    callback_data=f"delete_favourite_league {leagues[-1].id}",
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


async def add_favourite_league(update: Update, context):
    logger.info(
        f"'add_favourite_league' command executed - by {update.effective_user.name}"
    )

    await update.message.reply_text(
        "Please the league you would like me to add as your favourite.",
    )

    context.user_data["command"] = "add_favourite_league"

    return ADD_FAVOURITE_LEAGUE


async def add_favourite_league_handler(update: Update, context):
    commands_handler = FavouriteLeaguesCommandHandler(
        [context.user_data["league_id"]],
        update.effective_user.first_name,
        str(update.effective_chat.id),
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

    if not len(context.args):
        await own_favourite_leagues_inline_keyboard(
            update, context, commands_handler.get_favourite_leagues()
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
        text = commands_handler.get_favourite_leagues_response()

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

    await update.message.reply_text(
        f"Please enter the name (or part of the name) of the team you would like to search {Emojis.DOWN_FACING_FIST.value}",
    )

    return SEARCH_TEAM


async def search_team_handler(update, context):
    command_handler = SearchCommandHandler(
        [update.message.text], update.effective_user.first_name
    )
    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        teams = command_handler.search_team(update.message.text)

        page = 0
        pages = len(teams) // TEAMS_PAGE_SIZE + (
            1 if len(teams) % TEAMS_PAGE_SIZE else 0
        )
        context.user_data["teams"] = teams
        context.user_data["pages"] = pages
        context.user_data["start"] = True

        await show_teams(update, context, page)


async def show_teams(update, context, page: int):
    teams = context.user_data["teams"]
    pages = context.user_data["pages"]

    start = page * TEAMS_PAGE_SIZE
    end = start + TEAMS_PAGE_SIZE

    teams_keyboard = [
        [InlineKeyboardButton(team.name, callback_data=f"team:{team.id}:{team.name}")]
        for team in teams[start:end]
    ]

    prev_button = (
        InlineKeyboardButton("<< Prev", callback_data=f"team_page:{page - 1}")
        if page > 0
        else None
    )
    next_button = (
        InlineKeyboardButton("Next >>", callback_data=f"team_page:{page + 1}")
        if page < pages - 1
        else None
    )

    prev_next_row = []
    if prev_button:
        prev_next_row.append(prev_button)
    if next_button:
        prev_next_row.append(next_button)

    keyboard = [*teams_keyboard, prev_next_row]

    logger.info(f"KEYBOARD: {keyboard}")

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query is None:
        team_text = (
            "Select team"
            if len(teams)
            else f"There were no teams found. Please enter another value {Emojis.DOWN_FACING_FIST.value}"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=team_text,
            reply_markup=reply_markup,
        )
    else:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)


async def show_leagues(update, context, page: int):
    leagues = context.user_data["leagues"]
    pages = context.user_data["pages"]

    start = page * TEAMS_PAGE_SIZE
    end = start + TEAMS_PAGE_SIZE

    leagues_keyboard = [
        [
            InlineKeyboardButton(
                league.name, callback_data=f"league:{league.id}:{league.name}"
            )
        ]
        for league in leagues[start:end]
    ]

    prev_button = (
        InlineKeyboardButton("<< Prev", callback_data=f"league_page:{page - 1}")
        if page > 0
        else None
    )
    next_button = (
        InlineKeyboardButton("Next >>", callback_data=f"league_page:{page + 1}")
        if page < pages - 1
        else None
    )

    prev_next_row = []
    if prev_button:
        prev_next_row.append(prev_button)
    if next_button:
        prev_next_row.append(next_button)

    keyboard = [*leagues_keyboard, prev_next_row]

    logger.info(f"KEYBOARD: {keyboard}")

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query is None:
        league_text = (
            "Select league"
            if len(leagues)
            else f"There were no leagues found. Please enter another value {Emojis.DOWN_FACING_FIST.value}"
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=league_text,
            reply_markup=reply_markup,
        )
    else:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)


async def search_team_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    data = query.data

    if data.startswith("team_page:"):
        page = int(data.split(":")[1])
        await show_teams(update, context, page)
    elif data.startswith("team:"):
        team_data = data.split(":")[1:]
        logger.info(f"TEAM DATA - {team_data}")
        commands = {
            "add_favourite_team": add_favourite_team_handler,
            "next_match": next_match_handler,
            "last_match": last_match_handler,
            "last_matches": last_matches_handler,
        }
        context.user_data["team_id"] = team_data[0]

        await commands.get(context.user_data["command"])(update, context)


async def search_league_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    data = query.data

    if data.startswith("page:"):
        page = int(data.split(":")[1])
        await show_leagues(update, context, page)
    elif data.startswith("league:"):
        league_data = data.split(":")[1:]
        logger.info(f"LEAGUE DATA - {league_data}")
        commands = {
            "add_favourite_league": add_favourite_league_handler,
            "next_match_league": next_match_league_handler,
            "last_match_league": last_match_league_handler,
        }
        context.user_data["league_id"] = league_data[0]

        await commands.get(context.user_data["command"])(update, context)


async def search_league(update: Update, context):
    logger.info(
        f"'search_league {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )

    await update.message.reply_text(
        f"Please enter the name (or part of the name) of the league you would like to search {Emojis.DOWN_FACING_FIST.value}",
    )

    return SEARCH_LEAGUE


async def search_league_handler(update, context):
    command_handler = SearchCommandHandler(
        [update.message.text], update.effective_user.first_name
    )
    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
        leagues = command_handler.search_league(update.message.text)

        page = 0
        pages = len(leagues) // TEAMS_PAGE_SIZE + (
            1 if len(leagues) % TEAMS_PAGE_SIZE else 0
        )
        context.user_data["leagues"] = leagues
        context.user_data["pages"] = pages
        context.user_data["start"] = True

        await show_leagues(update, context, page)


async def search_leagues_by_country(update: Update, context):
    logger.info(
        f"'search_leagues_by_country {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )

    await update.message.reply_text(
        f"Please enter the name (or part of the name) of the of the country you would like to search leagues for {Emojis.DOWN_FACING_FIST.value}",
    )

    return SEARCH_LEAGUES_BY_COUNTRY


async def search_leagues_by_country_handler(update: Update, context):
    command_handler = SearchCommandHandler(
        [update.message.text], update.effective_user.first_name
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
