import re

from deep_translator import GoogleTranslator
from telegram import Update

from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import NotifierBotCommandsHandler

logger = get_logger(__name__)


def ignore_parts_of_string(input_string: str) -> tuple:
    not_translate_pattern = r"<not_translate>(.*?)<\/not_translate>"
    logger.info(input_string)
    not_translate_matches = re.findall(not_translate_pattern, input_string)
    not_translate_split_list = re.split(not_translate_pattern, input_string)

    return not_translate_matches, not_translate_split_list


def translate_text(text: str, target_lang: str = "en") -> str:
    translator = GoogleTranslator(source="en", target=target_lang)
    not_translate_matches, not_translate_split_list = ignore_parts_of_string(text)
    final_translated_list = []
    for phrase in not_translate_split_list:
        if phrase not in not_translate_matches:
            final_translated_list.append(translator.translate(phrase))
        else:
            final_translated_list.append(phrase)

    return "".join(final_translated_list)


async def reply_text(update: Update, text, **kwargs) -> None:
    chat_id = update.effective_chat.id
    command_handler = NotifierBotCommandsHandler(update.effective_chat.id)
    user_language = command_handler.get_user_language(str(chat_id)).short_name
    translated_text = translate_text(text=text, target_lang=user_language)

    await update.message.reply_text(translated_text, parse_mode="HTML", **kwargs)


async def send_message(update: Update, context, text: str, **kwargs) -> None:
    chat_id = update.effective_chat.id
    command_handler = NotifierBotCommandsHandler(update.effective_chat.id)
    user_language = command_handler.get_user_language(str(chat_id)).short_name
    translated_text = translate_text(text=text, target_lang=user_language)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=translated_text,
        parse_mode="HTML",
        **kwargs
    )


async def send_photo(
    update: Update, context, photo: str, caption: str, **kwargs
) -> None:
    chat_id = update.effective_chat.id
    command_handler = NotifierBotCommandsHandler(update.effective_chat.id)
    user_language = command_handler.get_user_language(str(chat_id)).short_name
    translated_text = translate_text(text=caption, target_lang=user_language)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo,
        caption=translated_text,
        parse_mode="HTML",
        **kwargs
    )
