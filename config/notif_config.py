import os

from config.config_utils import (
    get_telegram_recipients_config,
    get_email_recipients_config,
)


class NotifConfig:
    # RAPID API
    X_RAPIDAPI_HOST = os.environ.get("X_RAPIDAPI_HOST")
    X_RAPIDAPI_IMG_SEARCH_HOST = os.environ.get("X_RAPIDAPI_IMG_SEARCH_HOST")
    X_RAPIDAPI_VIDEO_SEARCH_HOST = os.environ.get("X_RAPIDAPI_VIDEO_SEARCH_HOST")
    X_YOUTUBE_SEARCH_HOST = os.environ.get("X_YOUTUBE_SEARCH_HOST")
    X_WORLDOMETERS_HOST = os.environ.get("X_WORLDOMETERS_HOST")
    X_RAPIDAPI_KEY = os.environ.get("X_RAPIDAPI_KEY")

    # NOTIF THRESHOLDS
    NEXT_MATCH_THRESHOLD = int(os.environ.get("NEXT_MATCH_THRESHOLD"))
    LAST_MATCH_THRESHOLD_DAYS = int(os.environ.get("LAST_MATCH_THRESHOLD_DAYS"))

    # TELEGRAM
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    TELEGRAM_RECIPIENTS = get_telegram_recipients_config()

    # EMAIL
    SMTP_SERVER = os.environ.get("SMTP_SERVER")
    GMAIL_SENDER = os.environ.get("GMAIL_SENDER")
    GMAIL_PASSWD = os.environ.get("GMAIL_PASSWD")
    EMAIL_RECIPIENTS = get_email_recipients_config()