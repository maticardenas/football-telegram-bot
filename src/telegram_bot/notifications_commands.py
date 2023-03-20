from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from src.notifier_logger import get_logger
from src.telegram_bot.bot_commands_handler import NotifConfigCommandHandler
from src.telegram_bot.commands_utils import send_message

logger = get_logger(__name__)


async def subscribe_to_notifications(update: Update, context):
    logger.info(
        f"'subscribe_to_notifications' command executed - by {update.effective_user.name}"
    )
    command_handler = NotifConfigCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    text = command_handler.subscribe_to_notifications()

    await send_message(update, context, text)


async def enable_notif_config(update: Update, context):
    logger.info(
        f"'enable_notif_config {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )

    if not len(context.args):
        await enable_or_disable_notif_config_inline_keyboard(update, context)
    else:
        command_handler = NotifConfigCommandHandler(
            context.args,
            update.effective_user.first_name,
            str(update.effective_chat.id),
        )

        validated_input = command_handler.validate_command_input()

        if validated_input:
            await send_message(update, context, validated_input)
        else:
            text = command_handler.enable_notification()

            await send_message(update, context, text)


async def disable_notif_config(update: Update, context):
    logger.info(
        f"'disable_notif_config {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )

    if not len(context.args):
        await enable_or_disable_notif_config_inline_keyboard(
            update, context, enable=False
        )
    else:
        command_handler = NotifConfigCommandHandler(
            context.args,
            update.effective_user.first_name,
            str(update.effective_chat.id),
        )

        validated_input = command_handler.validate_command_input()

        if validated_input:
            await send_message(update, context, validated_input)
        else:
            text = command_handler.disable_notification()

            await send_message(update, context, text)


async def set_daily_notif_time(update: Update, context):
    logger.info(
        f"'set_daily_notif_time {' '.join(context.args)}' command executed - by {update.effective_user.name}"
    )
    command_handler = NotifConfigCommandHandler(
        context.args, update.effective_user.first_name, str(update.effective_chat.id)
    )

    if not len(context.args):
        await set_daily_notification_times_inline_keyboard(update, context)
    else:
        text = command_handler.set_daily_notification_time()

        await send_message(update, context, text)


async def notif_config_callback_handler(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    commands = {
        "set_daily_notif_time": set_daily_notif_time,
        "enable_notif_config": enable_notif_config,
        "disable_notif_config": disable_notif_config,
    }

    split_query = query.data.split()
    command = split_query[0]

    try:
        context.args = [split_query[1]]
    except:
        context.args = []

    await commands[command](update, context)


async def set_daily_notification_times_inline_keyboard(
    update: Update,
    context,
):
    morning_times = ["5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00"]
    keyboard = [
        [
            InlineKeyboardButton(
                morning_time, callback_data=f"set_daily_notif_time {morning_time}"
            )
            for morning_time in morning_times
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Please choose the time you'd like to set for your daily notifications:"

    await send_message(
        update=update, context=context, text=text, reply_markup=reply_markup
    )


async def notif_config_inline_keyboard(
    update: Update,
    context,
):
    logger.info(f"'notif_config' command executed - by {update.effective_user.name}")
    command_handler = NotifConfigCommandHandler(
        context.args,
        update.effective_user.first_name,
        str(update.effective_chat.id),
        is_list=True,
    )

    text = command_handler.notif_config()

    keyboard = [
        [
            InlineKeyboardButton("Enable notif.", callback_data=f"enable_notif_config"),
            InlineKeyboardButton(
                "Disable notif.", callback_data=f"disable_notif_config"
            ),
        ],
        [
            InlineKeyboardButton(
                "Set daily notif. time", callback_data=f"set_daily_notif_time"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await send_message(
        update=update, context=context, text=text, reply_markup=reply_markup
    )


async def enable_or_disable_notif_config_inline_keyboard(
    update: Update, context, enable: bool = True
):
    command_handler = NotifConfigCommandHandler(
        context.args,
        update.effective_user.first_name,
        str(update.effective_chat.id),
        is_list=True,
    )

    all_notif_types = command_handler._fixtures_db_manager.get_all_notif_types()

    action = "enable" if enable else "disable"

    keyboard = [
        [
            InlineKeyboardButton(
                notif_type.name, callback_data=f"{action}_notif_config {notif_type.id}"
            )
            for notif_type in all_notif_types[:2]
        ],
        [
            InlineKeyboardButton(
                notif_type.name, callback_data=f"{action}_notif_config {notif_type.id}"
            )
            for notif_type in all_notif_types[2:]
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"Please select the notification type you would like to {action}:"

    await send_message(
        update=update, context=context, text=text, reply_markup=reply_markup
    )
