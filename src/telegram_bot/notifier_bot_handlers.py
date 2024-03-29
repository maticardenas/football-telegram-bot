from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.notifier_constants import (
    ADD_FAVOURITE_LEAGUE,
    ADD_FAVOURITE_TEAM,
    LAST_MATCH,
    LAST_MATCH_LEAGUE,
    LAST_MATCHES,
    NEXT_MATCH,
    NEXT_MATCH_LEAGUE,
    NEXT_MATCHES_LEAGUE,
    SEARCH_LANGUAGE,
    SEARCH_LEAGUE,
    SEARCH_LEAGUES_BY_COUNTRY,
    SEARCH_TEAM,
    SEARCH_TIME_ZONE,
    TEAM_SUMMARY,
)
from src.notifier_logger import get_logger
from src.telegram_bot.bot_constants import CONVERSATION_TIMEOUT
from src.telegram_bot.fav_teams_and_leagues_commands import (
    add_favourite_league,
    add_favourite_team,
    available_leagues,
    delete_favourite_league,
    delete_favourite_league_callback_handler,
    delete_favourite_team,
    delete_favourite_team_callback_handler,
    favourite_leagues,
    favourite_teams,
    search_league,
    search_league_callback_handler,
    search_league_handler,
    search_leagues_by_country,
    search_leagues_by_country_handler,
    search_team,
    search_team_callback_handler,
    search_team_handler,
)
from src.telegram_bot.language_commands import (
    my_language,
    search_language_handler,
    search_languages_callback_handler,
    set_language,
)
from src.telegram_bot.matches_commands import (
    last_match,
    last_match_league,
    last_matches,
    lineups_callback_handler,
    next_match,
    next_match_league,
    next_matches_league,
    timeline_callback_handler,
    today_matches,
    today_matches_callback_handler,
    tomorrow_matches,
    tomorrow_matches_callback_handler,
    upcoming_matches,
    upcoming_matches_callback_handler,
    yesterday_matches,
    yesterday_matches_callback_handler,
)
from src.telegram_bot.notifications_commands import (
    disable_notif_config,
    enable_notif_config,
    notif_config_callback_handler,
    notif_config_inline_keyboard,
    set_daily_notif_time,
    subscribe_to_notifications,
)
from src.telegram_bot.start_and_help_commands import help_cmd, start
from src.telegram_bot.stats_commands import team_summary
from src.telegram_bot.time_zones_commands import (
    delete_time_zone,
    delete_time_zone_callback_handler,
    my_time_zones,
    search_time_zone,
    search_time_zone_handler,
    search_time_zones_callback_handler,
    set_add_time_zone,
    set_main_time_zone,
)

logger = get_logger(__name__)


async def cancel(update, context) -> int:
    """Cancels and ends the conversation."""
    logger.info("Finishing conversation by command.")
    return ConversationHandler.END


async def timeout(update, context) -> int:
    """Cancels and ends the conversation."""
    logger.info("Finishing conversation by timeout.")
    return ConversationHandler.END


NOTIFIER_BOT_HANDLERS = [
    CommandHandler("start", start),
    CommandHandler("upcoming_matches", upcoming_matches),
    CommandHandler("today_matches", today_matches),
    CommandHandler("tomorrow_matches", tomorrow_matches),
    CommandHandler("yesterday_matches", yesterday_matches),
    CommandHandler("available_leagues", available_leagues),
    CommandHandler("my_time_zones", my_time_zones),
    CommandHandler("delete_time_zone", delete_time_zone),
    CommandHandler("favourite_teams", favourite_teams),
    CommandHandler("favourite_leagues", favourite_leagues),
    CommandHandler("delete_favourite_team", delete_favourite_team),
    CommandHandler("delete_favourite_league", delete_favourite_league),
    CommandHandler("notif_config", notif_config_inline_keyboard),
    CommandHandler("enable_notif_config", enable_notif_config),
    CommandHandler("disable_notif_config", disable_notif_config),
    CommandHandler("subscribe_to_notifications", subscribe_to_notifications),
    CommandHandler("set_daily_notif_time", set_daily_notif_time),
    CommandHandler("my_language", my_language),
    CommandHandler("help", help_cmd),
    CallbackQueryHandler(today_matches_callback_handler, pattern="^.*today_matches.*"),
    CallbackQueryHandler(
        tomorrow_matches_callback_handler, pattern="^.*tomorrow_matches.*"
    ),
    CallbackQueryHandler(
        upcoming_matches_callback_handler, pattern="^.*upcoming_matches.*"
    ),
    CallbackQueryHandler(
        yesterday_matches_callback_handler, pattern="^.*yesterday_matches.*"
    ),
    CallbackQueryHandler(
        delete_favourite_team_callback_handler, pattern="^.*delete_favourite_team.*"
    ),
    CallbackQueryHandler(
        delete_favourite_league_callback_handler, pattern="^.*delete_favourite_league.*"
    ),
    CallbackQueryHandler(
        delete_time_zone_callback_handler, pattern="^.*delete_time_zone.*"
    ),
    CallbackQueryHandler(
        notif_config_callback_handler,
        pattern="^.*set_daily_notif_time|enable_notif_config|disable_notif_config.*",
    ),
    CallbackQueryHandler(
        search_time_zones_callback_handler,
        pattern="^.*time_zone|tz_page.*",
    ),
    CallbackQueryHandler(
        search_team_callback_handler,
        pattern="^.*team|team_page.*",
    ),
    CallbackQueryHandler(
        search_league_callback_handler,
        pattern="^.*league|league_page.*",
    ),
    CallbackQueryHandler(
        search_languages_callback_handler,
        pattern="^.*language|lang_page.*",
    ),
    CallbackQueryHandler(timeline_callback_handler, pattern="^.*timeline.*"),
    CallbackQueryHandler(lineups_callback_handler, pattern="^.*lineups.*"),
    ConversationHandler(
        entry_points=[CommandHandler("add_favourite_team", add_favourite_team)],
        states={
            ADD_FAVOURITE_TEAM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_team_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/add_favourite_team$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("add_favourite_league", add_favourite_league)],
        states={
            ADD_FAVOURITE_LEAGUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_league_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/add_favourite_league$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("search_team", search_team)],
        states={
            SEARCH_TEAM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_team_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/search_team$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("search_league", search_league)],
        states={
            SEARCH_LEAGUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_league_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/search_league$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[
            CommandHandler("search_leagues_by_country", search_leagues_by_country)
        ],
        states={
            SEARCH_LEAGUES_BY_COUNTRY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, search_leagues_by_country_handler
                )
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[
            MessageHandler(~filters.Regex("^/search_leagues_by_country$"), cancel)
        ],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("next_match", next_match)],
        states={
            NEXT_MATCH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_team_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/next_match$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("last_match", last_match)],
        states={
            LAST_MATCH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_team_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/last_match$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("last_matches", last_matches)],
        states={
            LAST_MATCHES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_team_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/last_matches$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("next_match_league", next_match_league)],
        states={
            NEXT_MATCH_LEAGUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_league_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/next_match_league$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("next_matches_league", next_matches_league)],
        states={
            NEXT_MATCHES_LEAGUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_league_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/next_matches_league$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("last_match_league", last_match_league)],
        states={
            LAST_MATCH_LEAGUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_league_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/last_match_league$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("set_main_time_zone", set_main_time_zone)],
        states={
            SEARCH_TIME_ZONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, search_time_zone_handler
                )
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/set_main_time_zone$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("set_add_time_zone", set_add_time_zone)],
        states={
            SEARCH_TIME_ZONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, search_time_zone_handler
                )
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[
            MessageHandler(~filters.Regex("^/set_add_time_zone$"), cancel),
        ],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("search_time_zone", search_time_zone)],
        states={
            SEARCH_TIME_ZONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, search_time_zone_handler
                )
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[
            MessageHandler(~filters.Regex("^/search_time_zone$"), cancel),
        ],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("set_language", set_language)],
        states={
            SEARCH_LANGUAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_language_handler)
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[
            MessageHandler(~filters.Regex("^/set_language"), cancel),
        ],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
    ConversationHandler(
        entry_points=[CommandHandler("team_summary", team_summary)],
        states={
            TEAM_SUMMARY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_team_handler),
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timeout)],
        },
        fallbacks=[MessageHandler(~filters.Regex("^/team_summary$"), cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    ),
]
