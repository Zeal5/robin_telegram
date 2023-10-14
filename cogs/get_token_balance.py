from telegram import Update, ForceReply
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    filters,
)
from dataclasses import dataclass
import json
from cogs.wallet_cogs.make_server_requests import get_token_balance_server_request

with open("config.json", "r") as configs_files:
    configs = json.load(configs_files)

WAIT_FOR_TOKEN_ADDRESS = 1


@dataclass
class TokenBalance:
    balance: float
    symbol: str


async def check_token_balance_when_token_address_is_enterd(
    update: Update, context: CallbackContext
) -> None:
    # If this message is a reply to another message...
    tg_id = update.effective_user.id
    if update.message.reply_to_message:
        message = update.message.text.strip().split()
        print(f"message reply => {message}")
        response = await get_token_balance_server_request(
            configs["backend_url_get_token_balance"],
            tg_id,
            message[0],  #   token_address,
        )
        if isinstance(response, str):
            await update.message.reply_text(response)
            print(f"res => {response}")

        elif isinstance(response, dict):
            await update.message.reply_text(
                f"{response['symbol']}  {response['balance']}"
            )

    return ConversationHandler.END


async def get_balance(update: Update, context: CallbackContext):
    tg_id = update.effective_user.id
    # token_address: str = (update.effective_message.text)[1]
    print(context.user_data)
    message = update.message.text.strip().split()
    print(f"message => {message}")
    if len(message) == 2:
        response = await get_token_balance_server_request(
            configs["backend_url_get_token_balance"],
            tg_id,
            message[1],  #   token_address,
        )
        # await update.message.reply_text(f"{response['symbol']}  {response['balance']} ")
        if isinstance(response, str):
            await update.message.reply_text(response)
            print(f"res => {response}")

        elif isinstance(response, dict):
            await update.message.reply_text(
                f"{response['symbol']}  {response['balance']}"
            )

        return ConversationHandler.END
    if len(message) == 1:
        await update.message.reply_text(
            f"Reply to this message with token address to check balance",
            reply_markup=ForceReply(),
        )
        return WAIT_FOR_TOKEN_ADDRESS
    else:
        await update.message.reply_text(f"Invalid command used")
        return ConversationHandler.END


get_token_balance = ConversationHandler(
    entry_points=[CommandHandler("token_balance", get_balance)],
    states={
        WAIT_FOR_TOKEN_ADDRESS: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                check_token_balance_when_token_address_is_enterd,
            )
        ],
    },
    fallbacks=[],
    allow_reentry=True,
)


async def get_eth_balance(update: Update, context: CallbackContext):
    tg_id = update.effective_user.id
    print("checking eth balance")
    response = await get_token_balance_server_request(
        configs["backend_url_get_eth_balance"], tg_id  #   token_address,
    )
    # await update.message.reply_text(f"{response['symbol']}  {response['balance']} ")
    if isinstance(response, str):
        await update.message.reply_text(response)
        print(f"res => {response}")

    elif isinstance(response, dict):
        await update.message.reply_text(f"{response['symbol']}  {response['balance']}")
        
    return ConversationHandler.END
