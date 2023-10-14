# from wallet_manager import (
#     wallet_manager_convo_handler,
#     enter_wallet_manager,
# )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# import requests, json

WALLET_MANAGER, MENU_BUTTONS = range(2)


async def menu_button_pressed(update: Update, context: CallbackContext):
    query = update.callback_query
    button_choice = query.data
    if button_choice == "wallet_manager":
        # CommandHandler(enter_wallet_manager(update, context))
        print("wallet manager button pressed")
        # return WALLET_MANAGER
        # await enter_wallet_manager(update,context)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=context.user_data["menu_button"],
        )
    else:
        print("pressed extra button")
    print("ending convo")
    return ConversationHandler.END


async def main_menu_interface(update: Update, context: CallbackContext):
    wallet_manager = InlineKeyboardButton(
        "\u2699 Wallet Manger", callback_data="wallet_manager"
    )
    extra = InlineKeyboardButton("Settings", callback_data="enter_settings")

    keyboard = [[wallet_manager], [extra]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    menu_buttons = await update.message.reply_text("Menu", reply_markup=reply_markup)
    context.user_data["menu_button"] = menu_buttons.id

    return MENU_BUTTONS


async def fall_back(update: Update, context: CallbackContext):
    print("fallback main menu")
    return ConversationHandler.END


main_menu_convo_handler = ConversationHandler(
    entry_points=[CommandHandler("main_menu", main_menu_interface)],
    states={
        MENU_BUTTONS: [CallbackQueryHandler(menu_button_pressed)],
        # WALLET_MANAGER: [CallbackQueryHandler(enter_wallet_manager)]
    },
    fallbacks=[
        MessageHandler(filters.ALL, fall_back),
        MessageHandler(filters.Command, fall_back),
    ]
)
