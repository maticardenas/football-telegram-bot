from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.notifier_constants import (
    ADD_FAVOURITE_LEAGUE,
    ADD_FAVOURITE_TEAM,
    SEARCH_LEAGUE,
    SEARCH_LEAGUES_BY_COUNTRY,
    SEARCH_TEAM,
)
from src.telegram_bot.fav_teams_and_leagues_commands import (
    add_favourite_league,
    add_favourite_league_handler,
    add_favourite_team,
    add_favourite_team_handler,
    available_leagues,
    delete_favourite_league,
    delete_favourite_league_callback_handler,
    delete_favourite_team,
    delete_favourite_team_callback_handler,
    favourite_leagues,
    favourite_teams,
    search_league,
    search_league_handler,
    search_leagues_by_country,
    search_leagues_by_country_handler,
    search_team,
    search_team_handler,
)
from src.telegram_bot.matches_commands import (
    last_match,
    last_match_league,
    last_matches,
    next_match,
    next_match_league,
    next_matches_league,
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
from src.telegram_bot.time_zones_commands import (
    delete_time_zone,
    my_time_zones,
    search_time_zone,
    set_add_time_zone,
    set_main_time_zone,
)


async def cancel(update, context) -> int:
    """Cancels and ends the conversation."""
    # await update.message.reply_text(
    #     f"Finished with {context.user_data['entry_point_command']}",
    # )
    return ConversationHandler.END


NOTIFIER_BOT_HANDLERS = [
    CommandHandler("start", start),
    CommandHandler("next_match", next_match),
    CommandHandler("upcoming_matches", upcoming_matches),
    CommandHandler("last_match", last_match),
    CommandHandler("last_matches", last_matches),
    CommandHandler("next_match_league", next_match_league),
    CommandHandler("next_matches_league", next_matches_league),
    CommandHandler("last_match_league", last_match_league),
    CommandHandler("today_matches", today_matches),
    CommandHandler("tomorrow_matches", tomorrow_matches),
    CommandHandler("yesterday_matches", yesterday_matches),
    CommandHandler("available_leagues", available_leagues),
    CommandHandler("search_time_zone", search_time_zone),
    CommandHandler("my_time_zones", my_time_zones),
    CommandHandler("set_add_time_zone", set_add_time_zone),
    CommandHandler("set_main_time_zone", set_main_time_zone),
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
        notif_config_callback_handler,
        pattern="^.*set_daily_notif_time|enable_notif_config|disable_notif_config.*",
    ),
    ConversationHandler(
        entry_points=[CommandHandler("add_favourite_team", add_favourite_team)],
        states={
            ADD_FAVOURITE_TEAM: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, add_favourite_team_handler
                )
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    ),
    ConversationHandler(
        entry_points=[CommandHandler("add_favourite_league", add_favourite_league)],
        states={
            ADD_FAVOURITE_LEAGUE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, add_favourite_league_handler
                )
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    ),
    ConversationHandler(
        entry_points=[CommandHandler("search_team", search_team)],
        states={
            SEARCH_TEAM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_team_handler)
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    ),
    ConversationHandler(
        entry_points=[CommandHandler("search_league", search_league)],
        states={
            SEARCH_LEAGUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_league_handler)
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancel)],
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
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    ),
]
