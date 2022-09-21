from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

from config.notif_config import NotifConfig
from src.emojis import Emojis
from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import (
    FavouriteLeaguesCommandHandler,
    FavouriteTeamsCommandHandler,
    NextAndLastMatchCommandHandler,
    NextAndLastMatchLeagueCommandHandler,
    NotifierBotCommandsHandler,
    SearchCommandHandler,
    SurroundingMatchesHandler,
    TimeZonesCommandHandler,
)
from src.telegram_bot.bot_constants import MESSI_PHOTO

logger = get_logger(__name__)


async def start(update: Update, context):
    logger.info(f"'start' command executed - by {update.effective_user.name}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{Emojis.WAVING_HAND.value} Hi {update.effective_user.first_name}, I'm FootballNotifier!\n\n"
        f"{Emojis.RIGHT_FACING_FIST.value} /help - my available commands\n\n"
        f"For using me, you can start by configuring your preferences. \n\n"
        f"{Emojis.TELEVISION.value}<u><em>Favourite teams and leagues</em></u>\n\n"
        f"Configuring your <em>favourite teams</em> and"
        f"<em>favourite leagues</em> will give you the possibility to query fixtures by them and "
        f"get more customized information according to your preferences. You can search teams and leagues with /search_team & /search_league commands, take the id "
        f"of your favourite team or league and add them with /add_favourite_team & /add_favourite_league command.\n\n"
        f"{Emojis.GLOBE_WITH_MERIDIANS.value}<u><em>Time Zones</em></u>\n\n"
        f"Configuring your preferred time zone is also very important, as you will get date and times of matches according to it.\n"
        f"You can have a <em>main</em> time zone and <em>additional</em> time zones. Your <em>main</em> is basically what will tell me "
        f"which is your preferred base time to show you when informing matches (you can only have one configured). <em>additional</em> time zones, "
        f"on the other hand, are optional extra that you can have, when informing the matches I will put the time corresponding to your main time zone and "
        f"also the additional ones as well, so that you can share the times that matches will take place with anyone in the world :).\n"
        f"You can add you main time zone with /set_main_time_zone command, whereas for your additional ones you can use /set_add_time_zone.\n\n"
        f"{Emojis.SOCCER_BALL.value}Enjoy and I hope you are well informed with me!",
        parse_mode="HTML",
    )


async def help(update: Update, context):
    logger.info(f"'help' command executed - by {update.effective_user.name}")

    text = (
        f"{Emojis.WAVING_HAND.value}Hi {update.effective_user.first_name}!\n\n"
        f" {Emojis.JOYSTICK.value} These are my available commands:\n\n"
        f"• /search_time_zone <em>timezone name</em> - Searches time zones by name (or part of it) and retrieves them, if found, "
        f"with its corresponding <em>time_zone_id</em>\n"
        f"• /set_main_time_zone <em>time_zone_id</em> - Sets your main time zone by id. Remember you can have only ONE main time zone.\n"
        f"if you try to add another it will <u>replace</u> the existing main time zone.\n"
        f"• /set_add_time_zone <em>time_zone_id</em> - Sets an additional time zone by id.\n"
        f"• /my_time_zones - List of your configured time zones.\n"
        f"• /delete_time_zone <em>time_zone_id</em> - Removes one of your configured time zones.\n"
        f"• /search_team <em>team_name</em> - Searches teams by name (or part of it) and retrieves them, if found, "
        f"with its corresponding <em>team_id</em> \n"
        f"• /search_league <em>league_name</em> - Searches leagues by name (or part of it) and retrieves them, "
        f"if found, with its corresponding <em>league_id</em>. \n"
        f"• /search_leagues_by_country <em>country_name</em> - Searches leagues by country name (or part of it) and retrieves them, "
        f"if found, with its corresponding <em>league_id</em>. \n"
        f"• /favourite_teams - List of your favourite teams.\n"
        f"• /favourite_leagues - List of your favourite leagues.\n"
        f"• /add_favourite_team <em>team_id</em> - Adds a team to your favourites.\n"
        f"• /add_favourite_league <em>league_id</em> - Adds a league to your favourites.\n"
        f"• /delete_favourite_team <em>team_id</em> - Removes a team from your favourites.\n"
        f"• /delete_favourite_league <em>league_id</em> - Removes a league from your favourites.\n"
        f"• /next_match <em>team</em> - Next match of the specified team.\n"
        f"• /last_match <em>team</em> - Last match of the specified team.\n"
        f"• /next_match_league <em>league_id</em> - Next match of the specified league\n"
        f"• /next_matches_league <em>league_id</em> - Search for the next day where there are matches for the "
        f"specified league and informs all the matches of that day\n"
        f"• /last_match_league <em>league_id</em> - Last match of the specified league.\n"
        f"• /available_leagues - All available leagues.\n"
        f"• /today_matches <em>[optional [league_ids] [ft-fteams-favourite_teams] ["
        f"fl-fleagues-favourite_leagues]]</em> - Today's matches.\n"
        f" You can specify optionally specific <em>leagues_id</em> you want to filter for, or just filter by your "
        f"favourite teams or leagues.\n"
        f"• /upcoming_matches <em>[optional [team_id] [ft-fteams-favourite_teams] ["
        f"fl-fleagues-favourite_leagues]]</em> - List of upcoming matches.\n"
        f" You can specify optionally specific <em>team_id</em> you want to filter for, or just filter by your "
        f"favourite teams or leagues.\n"
        f"• /tomorrow_matches <em>[optional [league_ids] [ft-fteams-favourite_teams] ["
        f"fl-fleagues-favourite_leagues]]</em> -  Tomorrow's matches.\n"
        f" You can specify optionally specific <em>leagues_id</em> you want to filter for, or just filter by your "
        f"favourite teams or leagues.\n"
        f"• /last_matches <em>team_id</em> - List of last matches of the specified team.\n"
        f"• /last_played_matches <em>[optional [league_ids] [ft-fteams-favourite_teams] ["
        f"fl-fleagues-favourite_leagues]]</em> - Yesterday's matches.\n"
        f" You can specify optionally specific <em>leagues_id</em> you want to filter for, or just filter by your "
        f"favourite teams or leagues.\n"
    )
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


async def next_match(update: Update, context):
    logger.info(
        f"'next_match {' '.join(context.args)}' command executed - by {update.effective_user.name}"
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
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
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
        context.args, update.effective_user.first_name, update.effective_chat.id
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
        f"'last_match_league {' '.join(context.args)}' command executed - by {update.effective_user.first_name}"
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

    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
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

    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
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
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
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

    validated_input = command_handler.validate_command_input()

    if validated_input:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=validated_input, parse_mode="HTML"
        )
    else:
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
    search_leagues_by_country_handler = CommandHandler(
        "search_leagues_by_country", search_leagues_by_country
    )
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
    search_time_zone_handler = CommandHandler("search_time_zone", search_time_zone)
    my_time_zones_handler = CommandHandler("my_time_zones", my_time_zones)
    set_add_time_zone_handler = CommandHandler("set_add_time_zone", set_add_time_zone)
    set_main_time_zone_handler = CommandHandler(
        "set_main_time_zone", set_main_time_zone
    )
    remove_time_zone_handler = CommandHandler("delete_time_zone", delete_time_zone)
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
    application.add_handler(search_leagues_by_country_handler)
    application.add_handler(favourite_teams_handler)
    application.add_handler(favourite_leagues_handler)
    application.add_handler(add_favourite_team_handler)
    application.add_handler(add_favourite_league_handler)
    application.add_handler(remove_favourite_team_handler)
    application.add_handler(remove_favourite_league_handler)
    application.add_handler(search_time_zone_handler)
    application.add_handler(set_main_time_zone_handler)
    application.add_handler(set_add_time_zone_handler)
    application.add_handler(my_time_zones_handler)
    application.add_handler(remove_time_zone_handler)

    application.run_polling()
