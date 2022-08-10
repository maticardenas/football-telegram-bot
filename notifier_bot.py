from datetime import date

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

from config.notif_config import NotifConfig
from src.emojis import Emojis
from src.notifier_logger import get_logger
from src.team_fixtures_manager import TeamFixturesManager
from src.telegram_bot.bot_commands_handler import (
    FavouriteLeaguesCommandHandler,
    FavouriteTeamsCommandHandler,
    NextAndLastMatchCommandHandler,
    NextAndLastMatchLeagueCommandHandler,
    NotifierBotCommandsHandler,
    SearchTeamLeagueCommandHandler,
    SurroundingMatchesHandler,
)
from src.telegram_bot.bot_constants import MESSI_PHOTO

logger = get_logger(__name__)


async def start(update: Update, context):
    logger.info(f"'start' command executed - by {update.effective_user.name}")
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=MESSI_PHOTO,
        caption=f"{Emojis.WAVING_HAND.value} Hola {update.effective_user.first_name}, soy FootballNotifier bot!\n\n"
        f"{Emojis.JOYSTICK.value} /help - Chequeá mis comandos disponibles ;) \n\n"
        f"{Emojis.GOAT.value} {Emojis.ARGENTINA.value} Vamos Messi!",
        parse_mode="HTML",
    )


async def help(update: Update, context):
    logger.info(f"'help' command executed - by {update.effective_user.name}")
    text = (
        f"{Emojis.WAVING_HAND.value}Hi {update.effective_user.first_name}!\n\n"
        f" {Emojis.JOYSTICK.value} These are my available commands:\n\n"
        f"• /search_team <em><team_name></em> - Searches teams by name (or part of it) and retrieves them, if found, with its corresponding <em>team_id</em> \n"
        f"• /search_league <em><league_name></em> - Searches leagues by name (or part of it) and retrieves them, if found, with its corresponding <em>league_id</em>. \n"
        f"• /favourite_teams - List of your favourite teams.\n"
        f"• /favourite_leagues - List of your favourite leagues.\n"
        f"• /add_favourite_team <em><team_id></em> - Adds a team to your favourites.\n"
        f"• /add_favourite_league <em><league_id></em> - Adds a league to your favourites.\n"
        f"• /delete_favourite_team <em><team_id></em> - Removes a team from your favourites.\n"
        f"• /delete_favourite_league <em><league_id></em> - Removes a league from your favourites.\n"
        f"• /next_match <em><team></em> - Next match of the specified team.\n"
        f"• /last_match <em><team></em> - Last match of the specified team.\n"
        f"• /next_match_league <em><league_id></em> - Next match of the specified league\n"
        f"• /next_matches_league <em><league_id></em> - Search for the next day where there are matches for the specified league and informs all the matches of that day\n"
        f"• /last_match_league <em><league_id></em> - Last match of the specified league.\n"
        f"• /available_leagues - All available leagues.\n"
        f"• /today_matches <em>[optional [<league_ids>] [ft-fteams-favourite_teams] [fl-fleagues-favourite_leagues]]</em> - Today's matches.\n"
        f" You can specify optionally specific <em>leagues_id</em> you want to filter for, or just filter by your favourite teams or leagues.\n"
        f"• /upcoming_matches <em><team_id></em> - List of upcoming matches of the specified team.\n"
        f"• /tomorrow_matches <em>[optional [<league_ids>] [ft-fteams-favourite_teams] [fl-fleagues-favourite_leagues]]</em> -  Tomorrow's matches.\n"
        f" You can specify optionally specific <em>leagues_id</em> you want to filter for, or just filter by your favourite teams or leagues.\n"
        f"• /last_matches <em><team_id></em> - List of last matches of the specified team.\n"
        f"• /last_played_matches <em>[optional [<league_ids>] [ft-fteams-favourite_teams] [fl-fleagues-favourite_leagues]]</em> - Yesterday's matches.\n"
        f" You can specify optionally specific <em>leagues_id</em> you want to filter for, or just filter by your favourite teams or leagues.\n"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def available_leagues(update: Update, context):
    logger.info(
        f"'available_leagues' command executed - by {update.effective_user.name}"
    )
    notifier_commands_handler = NotifierBotCommandsHandler()
    text = (
        f"{Emojis.WAVING_HAND.value}Hola {update.effective_user.first_name}!\n\n"
        f" {Emojis.TELEVISION.value} Estos son los torneos disponibles:\n\n"
        f"{notifier_commands_handler.available_leagues_text()}"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
    )


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


async def search_team(update: Update, context):
    logger.info(
        f"'search_team {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = SearchTeamLeagueCommandHandler(
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
    command_handler = SearchTeamLeagueCommandHandler(
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


async def next_match(update: Update, context):
    logger.info(
        f"'next_match {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = NextAndLastMatchCommandHandler(
        context.args, update.effective_user.first_name
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
        f"'last_match {' '.join(context.args)}' command executed - by {update.effective_user.first_name}"
    )
    command_handler = NextAndLastMatchCommandHandler(
        context.args, update.effective_user.first_name
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
    command_handler = NextAndLastMatchLeagueCommandHandler(
        context.args, update.effective_user.first_name
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
        context.args, update.effective_user.first_name
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
        f"'last_match_league {' '.join(context.args)}' command executed - by {update.effective_user.first_name}"
    )
    command_handler = NextAndLastMatchLeagueCommandHandler(
        context.args, update.effective_user.first_name
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


async def today_matches(update: Update, context):
    logger.info(
        f"'today_matches {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = SurroundingMatchesHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    command_handler.validate_command_input()

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
        context.args, update.effective_user.first_name
    )

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
        context.args, update.effective_user.first_name
    )

    texts, photo = command_handler.last_matches()

    for text in texts:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="HTML",
        )


async def last_played_matches(update: Update, context):
    logger.info(
        f"'last_played_matches {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = SurroundingMatchesHandler(
        context.args, update.effective_user.first_name, update.effective_chat.id
    )

    command_handler.validate_command_input()

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

    command_handler.validate_command_input()

    texts, photo = command_handler.tomorrow_games()

    for text in texts:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="HTML",
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(NotifConfig.TELEGRAM_TOKEN).build()
    start_handler = CommandHandler("start", start)
    search_team_handler = CommandHandler("search_team", search_team)
    search_league_handler = CommandHandler("search_league", search_league)
    next_match_handler = CommandHandler("next_match", next_match)
    upcoming_matches_handler = CommandHandler("upcoming_matches", upcoming_matches)
    last_match_handler = CommandHandler("last_match", last_match)
    last_matches_handler = CommandHandler("last_matches", last_matches)
    next_match_league_handler = CommandHandler("next_match_league", next_match_league)
    next_matches_league_handler = CommandHandler(
        "next_matches_league", next_matches_league
    )
    last_match_league_handler = CommandHandler("last_match_league", last_match_league)
    today_matches_handler = CommandHandler("today_matches", today_matches)
    tomorrow_matches_handler = CommandHandler("tomorrow_matches", tomorrow_matches)
    last_played_matches_handler = CommandHandler(
        "last_played_matches", last_played_matches
    )
    available_leagues_handler = CommandHandler("available_leagues", available_leagues)
    favourite_teams_handler = CommandHandler("favourite_teams", favourite_teams)
    favourite_leagues_handler = CommandHandler("favourite_leagues", favourite_leagues)
    add_favourite_team_handler = CommandHandler(
        "add_favourite_team", add_favourite_team
    )
    add_favourite_league_handler = CommandHandler(
        "add_favourite_league", add_favourite_league
    )
    remove_favourite_team_handler = CommandHandler(
        "delete_favourite_team", delete_favourite_team
    )
    remove_favourite_league_handler = CommandHandler(
        "delete_favourite_league", delete_favourite_league
    )

    help_handler = CommandHandler("help", help)

    application.add_handler(start_handler)
    application.add_handler(next_match_handler)
    application.add_handler(upcoming_matches_handler)
    application.add_handler(last_match_handler)
    application.add_handler(last_matches_handler)
    application.add_handler(next_match_league_handler)
    application.add_handler(next_matches_league_handler)
    application.add_handler(last_match_league_handler)
    application.add_handler(help_handler)
    application.add_handler(today_matches_handler)
    application.add_handler(last_played_matches_handler)
    application.add_handler(tomorrow_matches_handler)
    application.add_handler(available_leagues_handler)
    application.add_handler(search_team_handler)
    application.add_handler(search_league_handler)
    application.add_handler(favourite_teams_handler)
    application.add_handler(favourite_leagues_handler)
    application.add_handler(add_favourite_team_handler)
    application.add_handler(add_favourite_league_handler)
    application.add_handler(remove_favourite_team_handler)
    application.add_handler(remove_favourite_league_handler)

    application.run_polling()
