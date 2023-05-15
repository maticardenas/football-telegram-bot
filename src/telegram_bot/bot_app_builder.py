from telegram.ext import ApplicationBuilder
from telegram.ext._application import Application

from src.telegram_bot.notifier_bot_handlers import NOTIFIER_BOT_HANDLERS


class NotifBotAppBuilder:
    def __init__(self, telegram_token: str) -> None:
        self._telegram_token = telegram_token

    def build_application(self) -> Application:
        application = ApplicationBuilder().token(self._telegram_token).build()

        for count, handler in enumerate(NOTIFIER_BOT_HANDLERS):
            application.add_handler(handler, count)

        print(f"JOB QUEUE! -> {application.job_queue}")

        return application
