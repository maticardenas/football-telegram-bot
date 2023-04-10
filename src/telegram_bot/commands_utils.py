from telegram import Update

from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import NotifierBotCommandsHandler
from src.utils.message_utils import translate_text

logger = get_logger(__name__)


async def reply_text(update: Update, text, **kwargs) -> None:
    chat_id = update.effective_chat.id
    command_handler = NotifierBotCommandsHandler(update.effective_chat.id)
    user_language = command_handler.get_user_language(str(chat_id)).short_name
    text_to_send = (
        translate_text(text=text, target_lang=user_language)
        if user_language != "en"
        else text.replace("<not_translate>", "")
        .replace("</not_translate>", "")
    )

    await update.message.reply_text(text_to_send, parse_mode="HTML", **kwargs)


async def send_message(update: Update, context, text: str, **kwargs) -> None:
    chat_id = update.effective_chat.id
    command_handler = NotifierBotCommandsHandler(update.effective_chat.id)
    user_language = command_handler.get_user_language(str(chat_id)).short_name
    text_to_send = (
        translate_text(text=text, target_lang=user_language)
        if user_language != "en"
        else text.replace("<not_translate>", "")
        .replace("</not_translate>", "")
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text_to_send, parse_mode="HTML", **kwargs
    )


async def send_photo(
    update: Update, context, photo: str, caption: str, **kwargs
) -> None:
    chat_id = update.effective_chat.id
    command_handler = NotifierBotCommandsHandler(update.effective_chat.id)
    user_language = command_handler.get_user_language(str(chat_id)).short_name
    text_to_send = (
        translate_text(text=caption, target_lang=user_language)
        if user_language != "en"
        else caption.replace("<not_translate>", "")
        .replace("</not_translate>", "")
    )

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo,
        caption=text_to_send,
        parse_mode="HTML",
        **kwargs
    )
