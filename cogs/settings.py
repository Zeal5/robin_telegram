from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from .wallet_cogs.make_server_requests import get_user_settings_server_request
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
import json

with open("config.json", "r") as f:
    configs = json.load(f)


async def enter_settings(update: Update, context: CallbackContext):
    print(context._user_id)
    response = await get_user_settings_server_request(
        url=configs["backend_url_get_user_settings"], tg_id=context._user_id
    )
    reply = response
    await context.bot.send_message(update.effective_chat.id, reply)
    ConversationHandler.END


settings_convo = ConversationHandler(
    entry_points=[
        CommandHandler("enter_settings", enter_settings),
        CallbackQueryHandler(enter_settings, pattern="enter_settings"),
    ],
    states={
        # SHOW_BUTTONS: [CallbackQueryHandler(button_click)],
        # ADD_SECRET: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_keys)],
        # EDIT_BUTTONS: [CallbackQueryHandler(editing_wallets)],
    },
    fallbacks=[],
    allow_reentry=True
    # per_chat=True,
    # per_user=True,
    # per_message=True,
)
