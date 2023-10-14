import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)

# import custom pakages
from cogs.main_menu import main_menu_convo_handler
from cogs.wallet_manager import wallet_manager_convo_handler 
from cogs.buy_tokens_with_eth import buy_tokens_with_eth_convo_handler
from cogs.get_token_balance import get_token_balance, get_eth_balance
from cogs.settings import settings_convo
from typing import Optional
load_dotenv()
token = os.getenv("TOKEN")


async def callback(update: Optional[object], context: CallbackContext):
    print(f"error = {context.error}")
    await update.message.reply_text(
                f"Something went wrong this is error"
            )
#@TODO make making request to server modular (create a seperate moduel for this purpose only
def main():
    print("bot started")
    app = Application.builder().token(token).build()
    app.add_handler(main_menu_convo_handler,5)
    app.add_handler(wallet_manager_convo_handler,4)
    app.add_handler(buy_tokens_with_eth_convo_handler,2)
    app.add_handler(CommandHandler("eth_balance",get_eth_balance),3)
    app.add_handler(get_token_balance)
    app.add_handler(settings_convo,6)
    app.add_error_handler(callback)
    # app.add_handler(MessageHandler(filters.Command,command_handler))


    # polling
    app.run_polling(0, allowed_updates=Update.ALL_TYPES)

"""
main_menu - Main menu for bot
manage_wallets - create new wallet, add wallet, check all wallets
buy_tokens_with_eth - token address , amount eth
change_wallet - change active wallet ???
token_balance - get token balance
eth_balance - get eth balance for active address
"""


if __name__ == "__main__":
    main()
