import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from config.notif_config import NotifConfig
from src.emojis import Emojis
from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import (
    FavouriteLeaguesCommandHandler,
    FavouriteTeamsCommandHandler,
    NextAndLastMatchCommandHandler,
    NextAndLastMatchLeagueCommandHandler,
    NotifConfigCommandHandler,
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
        f"{Emojis.BELL.value}<u><em>Notifications</em></u>\n\n"
        f"You can receive automatic notifications from me! Getting, for example, reminders when there are matches approaching corresponding to your favourite "
        f"teams or leagues, or when a match was just played. First, you need to subscribe to notifications with /subscribe_to_notifications command, then you will"
        f" be able to check them and their status with /notif_config and don't worry, you can enable/disable them as you please, with /enable_notif_config and /disable_notif_config commands.\n\n"
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
        f"• /subscribe_to_notifications - Subscribe to existing notification types.\n"
        f"• /notif_config - Get your current notifications configuration.\n"
        f"• /enable_notif_config <em>notif_type_id</em> - Enable a specific notification.\n"
        f"• /disable_notif_config <em>notif_type_id</em> - Disable a specific notification.\n"
        f"• /set_daily_notif_time - Set time for your daily notifications.\n"
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
        f"• /yesterday_matches <em>[optional [league_ids] [ft-fteams-favourite_teams] ["
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


async def subscribe_to_notifications(update: Update, context):
    logger.info(
        f"'subscribe_to_notifications' command executed - by {update.effective_user.name}"
    )
    command_handler = NotifConfigCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    text = command_handler.subscribe_to_notifications()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="HTML",
    )


async def enable_notif_config(update: Update, context):
    logger.info(
        f"'enable_notif_config {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )

    if not len(context.args):
        await enable_or_disable_notif_config_inline_keyboard(update, context)
    else:
        command_handler = NotifConfigCommandHandler(
            context.args,
            update.effective_user.first_name,
            str(update.effective_chat.id),
        )

        validated_input = command_handler.validate_command_input()

        if validated_input:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=validated_input,
                parse_mode="HTML",
            )
        else:
            text = command_handler.enable_notification()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="HTML",
            )


async def disable_notif_config(update: Update, context):
    logger.info(
        f"'disable_notif_config {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )

    if not len(context.args):
        await enable_or_disable_notif_config_inline_keyboard(
            update, context, enable=False
        )
    else:
        command_handler = NotifConfigCommandHandler(
            context.args,
            update.effective_user.first_name,
            str(update.effective_chat.id),
        )

        validated_input = command_handler.validate_command_input()

        if validated_input:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=validated_input,
                parse_mode="HTML",
            )
        else:
            text = command_handler.disable_notification()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="HTML",
            )


async def set_daily_notif_time(update: Update, context):
    logger.info(
        f"'set_daily_notif_time {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = NotifConfigCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    if not len(context.args):
        await set_daily_notification_times_inline_keyboard(update, context)
    else:
        text = command_handler.set_daily_notification_time()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="HTML",
        )


async def notif_config_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    commands = {
        "set_daily_notif_time": set_daily_notif_time,
        "enable_notif_config": enable_notif_config,
        "disable_notif_config": disable_notif_config,
    }

    split_query = query.data.split()
    command = split_query[0]

    try:
        context.args = [split_query[1]]
    except:
        context.args = []

    await commands[command](update, context)


async def set_daily_notification_times_inline_keyboard(
    update: Update,
    context,
):
    morning_times = ["5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00"]
    keyboard = [
        [
            InlineKeyboardButton(
                morning_time, callback_data=f"set_daily_notif_time {morning_time}"
            )
            for morning_time in morning_times
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Please choose the time you'd like to set for your daily notifications:"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def notif_config_inline_keyboard(
    update: Update,
    context,
):
    logger.info(f"'notif_config' command executed - by {update.effective_user.name}")
    command_handler = NotifConfigCommandHandler(
        context.args,
        update.effective_user.first_name,
        str(update.effective_chat.id),
        is_list=True,
    )

    text = command_handler.notif_config()

    keyboard = [
        [
            InlineKeyboardButton("Enable notif.", callback_data=f"enable_notif_config"),
            InlineKeyboardButton(
                "Disable notif.", callback_data=f"disable_notif_config"
            ),
        ],
        [
            InlineKeyboardButton(
                "Set daily notif. time", callback_data=f"set_daily_notif_time"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


async def enable_or_disable_notif_config_inline_keyboard(
    update: Update, context, enable: bool = True
):
    command_handler = NotifConfigCommandHandler(
        context.args,
        update.effective_user.first_name,
        str(update.effective_chat.id),
        is_list=True,
    )

    all_notif_types = command_handler._fixtures_db_manager.get_all_notif_types()

    action = "enable" if enable else "disable"

    keyboard = [
        [
            InlineKeyboardButton(
                notif_type.name, callback_data=f"{action}_notif_config {notif_type.id}"
            )
            for notif_type in all_notif_types[:2]
        ],
        [
            InlineKeyboardButton(
                notif_type.name, callback_data=f"{action}_notif_config {notif_type.id}"
            )
            for notif_type in all_notif_types[2:]
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Please select the notification type you would like to {action}:"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
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
    yesterday_matches_handler = CommandHandler("yesterday_matches", yesterday_matches)
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
    notif_config_handler = CommandHandler("notif_config", notif_config_inline_keyboard)
    enable_notif_handler = CommandHandler("enable_notif_config", enable_notif_config)
    disable_notif_handler = CommandHandler("disable_notif_config", disable_notif_config)
    subscribe_to_notifications_handler = CommandHandler(
        "subscribe_to_notifications", subscribe_to_notifications
    )
    set_daily_notif_time_handler = CommandHandler(
        "set_daily_notif_time", set_daily_notif_time
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
    application.add_handler(yesterday_matches_handler)
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
    application.add_handler(notif_config_handler)
    application.add_handler(enable_notif_handler)
    application.add_handler(disable_notif_handler)
    application.add_handler(subscribe_to_notifications_handler)
    application.add_handler(set_daily_notif_time_handler)
    application.add_handler(
        CallbackQueryHandler(
            today_matches_callback_handler, pattern="^.*today_matches.*"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            tomorrow_matches_callback_handler, pattern="^.*tomorrow_matches.*"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            upcoming_matches_callback_handler, pattern="^.*upcoming_matches.*"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            yesterday_matches_callback_handler, pattern="^.*yesterday_matches.*"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            notif_config_callback_handler,
            pattern="^.*set_daily_notif_time|enable_notif_config|disable_notif_config.*",
        )
    )

    application.run_polling()
