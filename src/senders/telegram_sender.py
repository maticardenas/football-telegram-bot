from config.notif_config import NotifConfig
from src.api.telegram_client import TelegramClient
from src.utils.message_utils import translate_text


def send_telegram_message(
    chat_id: str,
    message: str = "",
    photo: str = "",
    video: str = "",
    lang: str = "",
    translate: bool = True,
) -> None:
    message = (
        translate_text(message, lang)
        if lang and lang != "en" and translate is True
        else message.replace("<not_translate>", "").replace("</not_translate>", "")
    )
    telegram_client = TelegramClient(NotifConfig.TELEGRAM_TOKEN)
    if photo:
        response = telegram_client.send_photo(chat_id, photo_url=photo, text=message)
    elif video:
        response = telegram_client.send_video(chat_id, video_url=video, text=message)
    else:
        response = telegram_client.send_message(chat_id, message)

    print(f"TELEGRAM MESSAGE SENT RESPONSE: {response.status_code}\n{response.text}")
