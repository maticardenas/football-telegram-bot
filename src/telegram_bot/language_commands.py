from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from src.emojis import Emojis
from src.notifier_constants import (
    END_COMMAND_MESSAGE,
    LANGUAGES_PAGE_SIZE,
    SEARCH_LANGUAGE,
    TIME_ZONES_PAGE_SIZE,
)
from src.notifier_logger import get_logger
from src.telegram_bot.command_handlers.bot_commands_handler import (
    LanguagesCommandHandler,
)
from src.telegram_bot.commands_utils import reply_text, send_message

logger = get_logger(__name__)


async def set_language(update: Update, context):
    logger.info(f"'set_language' command initialized - by {update.effective_user.name}")

    text = f"Please enter the name of the language you would like set {Emojis.DOWN_FACING_FIST.value}\n\n{END_COMMAND_MESSAGE}"

    await reply_text(update, text)

    context.user_data["command"] = "set_language"

    return SEARCH_LANGUAGE


async def show_languages(update, context, page):
    languages = context.user_data["languages"]
    pages = context.user_data["pages"]

    start = page * TIME_ZONES_PAGE_SIZE
    end = start + TIME_ZONES_PAGE_SIZE

    languages_keyboard = [
        [
            InlineKeyboardButton(
                lang.name.capitalize(),
                callback_data=f"language:{lang.lang_id}:{lang.name}",
            )
        ]
        for lang in languages[start:end]
    ]

    prev_button = (
        InlineKeyboardButton("<< Prev", callback_data=f"lan_page:{page - 1}")
        if page > 0
        else None
    )
    next_button = (
        InlineKeyboardButton("Next >>", callback_data=f"lan_page:{page + 1}")
        if page < pages - 1
        else None
    )

    prev_next_row = []
    if prev_button:
        prev_next_row.append(prev_button)
    if next_button:
        prev_next_row.append(next_button)

    keyboard = [*languages_keyboard, prev_next_row]

    logger.info(f"KEYBOARD: {keyboard}")

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Choose your language: ",
            reply_markup=reply_markup,
        )
    else:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)


async def search_languages_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    data = query.data

    if data.startswith("lang_page:"):
        page = int(data.split(":")[1])
        await show_languages(update, context, page)
    elif data.startswith("language:"):
        lang_data = data.split(":")[1:]
        logger.info(f"LANG_DATA - {lang_data}")
        commands = {"set_language": set_language_handler}
        context.user_data["lang_id"] = lang_data[0]

        await commands.get(context.user_data["command"])(update, context)


async def set_language_handler(update: Update, context):
    commands_handler = LanguagesCommandHandler(
        update.effective_user.first_name,
        str(update.effective_chat.id),
    )

    text = commands_handler.set_language(context.user_data["lang_id"])

    await send_message(update, context, text)


async def my_language(update: Update, context):
    logger.info(f"'my_language' command executed - by {update.effective_user.name}")
    commands_handler = LanguagesCommandHandler(
        update.effective_user.first_name, str(update.effective_chat.id)
    )

    text = commands_handler.get_config_language()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode="HTML"
    )


async def search_language_handler(update: Update, context):
    logger.info(
        f"'search_language {update.message.text}' command executed - by {update.effective_user.name}"
    )
    command_handler = LanguagesCommandHandler(
        [update.message.text], update.effective_user.first_name
    )

    languages = command_handler.search_language(update.message.text)

    page = 0
    pages = len(languages) // LANGUAGES_PAGE_SIZE + (
        1 if len(languages) % LANGUAGES_PAGE_SIZE else 0
    )
    context.user_data["languages"] = languages
    context.user_data["pages"] = pages
    context.user_data["start"] = True

    await show_languages(update, context, page)
