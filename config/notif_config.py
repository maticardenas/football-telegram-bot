import os


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

    # EMAIL
    SMTP_SERVER = os.environ.get("SMTP_SERVER")
    GMAIL_SENDER = os.environ.get("GMAIL_SENDER")
    GMAIL_PASSWD = os.environ.get("GMAIL_PASSWD")

    # DB
    DB_HOST = os.environ.get("DB_HOST")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    POSTGRES_DB_URL = os.environ.get("POSTGRES_DB_URL")
