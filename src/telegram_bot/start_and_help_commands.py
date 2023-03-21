from telegram import Update

from src.emojis import Emojis
from src.notifier_logger import get_logger
from src.telegram_bot.commands_utils import send_message

logger = get_logger(__name__)


async def start(update: Update, context):
    logger.info(f"'start' command executed - by {update.effective_user.name}")
    await send_message(
        update=update,
        context=context,
        text=f"{Emojis.WAVING_HAND.value} Hi {update.effective_user.first_name}, I'm FootballNotifier!\n\n"
        f"{Emojis.RIGHT_FACING_FIST.value} /help - my available commands\n\n"
        f"For using me, you can start by configuring your preferences. \n\n"
        f"{Emojis.TELEVISION.value}<u><em>Favourite teams and leagues</em></u>\n\n"
        f"Configuring your <em>favourite teams</em> and"
        f"<em>favourite leagues</em> will give you the possibility to query fixtures by them and "
        f"get more customized information according to your preferences. Add them with /add_favourite_team & /add_favourite_league command. {Emojis.SMILEY_FACE.value}\n\n"
        f"{Emojis.SPEAKING_HEAD.value}<u><em>Language</em></u>\n\n"
        f"You can configure your preferred language through /set_language command. English is the default one, but any language you'd like can be set.\n\n"
        f"{Emojis.GLOBE_WITH_MERIDIANS.value}<u><em>Time Zones</em></u>\n\n"
        f"Configuring your preferred time zone is also very important, as you will get date and times of matches according to it.\n"
        f"You can have a <em>main</em> time zone and <em>additional</em> time zones. Your <em>main</em> is basically what will tell me "
        f"which is your preferred base time to show you when informing matches (you can only have one configured). <em>additional</em> time zones, "
        f"on the other hand, are optional extra that you can have, when informing the matches I will put the time corresponding to your main time zone and "
        f"also the additional ones as well, so that you can share the times that matches will take place with anyone in the world :).\n"
        f"You can add your main time zone with /set_main_time_zone command, whereas for your additional ones you can use /set_add_time_zone.\n\n"
        f"{Emojis.BELL.value}<u><em>Notifications</em></u>\n\n"
        f"You can receive automatic notifications from me! Getting, for example, reminders when there are matches approaching corresponding to your favourite "
        f"teams or leagues, or when a match was just played. First, you need to subscribe to notifications with /subscribe_to_notifications command, then you will"
        f" be able to manage them with the /notif_config command.\n\n"
        f"{Emojis.SOCCER_BALL.value}Enjoy and I hope you are well informed with me!",
    )


async def help_cmd(update: Update, context):
    logger.info(f"'help' command executed - by {update.effective_user.name}")

    text = (
        f"{Emojis.WAVING_HAND.value}Hi {update.effective_user.first_name}!\n\n"
        f" {Emojis.JOYSTICK.value} These are my available commands:\n\n"
        f"• /set_main_time_zone <em>time_zone_id</em> - Sets your main time zone by id. Remember you can have only ONE main time zone.\n"
        f"if you try to add another it will <u>replace</u> the existing main time zone.\n"
        f"• /set_add_time_zone <em>time_zone_id</em> - Sets an additional time zone by id.\n"
        f"• /my_time_zones - List of your configured time zones.\n"
        f"• /set_language - Set your preferred language.\n"
        f"• /delete_time_zone <em>time_zone_id</em> - Removes one of your configured time zones.\n"
        f"• /my_language - Retrieve your configured language.\n"
        f"• /subscribe_to_notifications - Subscribe to existing notification types.\n"
        f"• /notif_config - Get your current notifications configuration.\n"
        f"• /enable_notif_config <em>notif_type_id</em> - Enable a specific notification.\n"
        f"• /disable_notif_config <em>notif_type_id</em> - Disable a specific notification.\n"
        f"• /set_daily_notif_time - Set time for your daily notifications.\n"
        f"• /favourite_teams - List of your favourite teams.\n"
        f"• /favourite_leagues - List of your favourite leagues.\n"
        f"• /add_favourite_team - Adds a team to your favourites.\n"
        f"• /add_favourite_league - Adds a league to your favourites.\n"
        f"• /delete_favourite_team - Removes a team from your favourites.\n"
        f"• /delete_favourite_league - Removes a league from your favourites.\n"
        f"• /next_match - Next match of the specified team.\n"
        f"• /last_match - Last match of the specified team.\n"
        f"• /next_match_league - Next match of the specified league\n"
        f"• /next_matches_league - Search for the next day where there are matches for the "
        f"specified league and informs all the matches of that day\n"
        f"• /last_match_league - Last match of the specified league.\n"
        f"• /available_leagues - All available leagues.\n"
        f"• /today_matches <em>[optional [league_ids] [ft-fteams-favourite_teams] ["
        f"fl-fleagues-favourite_leagues]]</em> - Today's matches.\n"
        f" You can specify optionally specific <em>leagues_id</em> you want to filter for, or just filter by your "
        f"favourite teams or leagues.\n"
        f"• /upcoming_matches - List of upcoming matches of your favourite teams or leagues.\n"
        f"• /tomorrow_matches - Tomorrow's matches of your favourite teams or leagues.\n"
        f"• /last_matches - List of last matches of the specified team.\n"
        f"• /yesterday_matches - Yesterday's matches of your favourite teams or leagues.\n"
        f" You can specify optionally specific <em>leagues_id</em> you want to filter for, or just filter by your "
        f"favourite teams or leagues.\n"
    )
    await send_message(update, context, text)
