from config.notif_config import NotifConfig
from src.notifier_logger import get_logger
from src.telegram_bot.bot_app_builder import NotifBotAppBuilder

logger = get_logger(__name__)

if __name__ == "__main__":
    notif_bot_app_builder = NotifBotAppBuilder(NotifConfig.TELEGRAM_TOKEN)
    application = notif_bot_app_builder.build_application()
    application.run_polling()
