from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    filters,
)

import requests, json


with open("config.json", "r") as configs_files:
    configs = json.load(configs_files)

WAIT_FOR_TOKEN = range(1)


async def make_req_to_server(
    url: str,
    tg_id: int,
    token_to_buy: str | None = None,
    token_to_sell: str | None = None,
    eth_to_spend: int | None = None,
    amount_to_sell: int | None = None,
    slippage: int | None = None,
) -> dict:
    headers = {"Content-Type": "application/json"}
    eth_to_spend = float(eth_to_spend)
    print(f"make re qeth amount = {eth_to_spend}")
    print(type(eth_to_spend))
    data = {"tg_id": tg_id,"eth_to_spend": eth_to_spend, "token_to_buy": token_to_buy,"token_to_sell": token_to_sell,"amount_to_sell": amount_to_sell,"slippage": slippage}
    print(type(data['eth_to_spend']))

    request = requests.post(url, json=data, headers=headers)

    return request


async def when_token_is_enterd(
    update: Update, context: CallbackContext, message: list[str:str:float] = None
):
    if (
        message is None
    ):  # function is being called from conversation handler instead of /buy_token_with_eth
        message = update.message.text.strip().split()
    print(f"raw message {message}")
    token_address, amount = await disect_message(update, message)
    #@ TODO delete the you forgot to enter token address message on next iteration
    if token_address == False or amount == False:
        await update.message.reply_text(f"you forgot to enter token address or amount ")
        return WAIT_FOR_TOKEN
        # kill = await fall_back(update, context, 1)
        # if kill:
        #     return ConversationHandler.END
    print(f"{token_address} - {float(amount)}")
    response = await make_req_to_server(
        tg_id=update.effective_user.id,
        url=configs["backend_url_buy_tokens_with_eth"],
        token_to_buy=token_address,
        eth_to_spend=amount,
    )
    print(f"printing response {response} -> {response.json()}")
    if response.status_code == 200:
        response = response.json()
        # handle error in case returned with an error of less balance
        if response.get("detail"):
            reply = f"{response['detail']}"
        else:
            reply = f"""
        [TXN HASH](https://etherscan.io/tx/{response['hash']})\n`{response['hash']}`\n\n*From:*\n`{response['from']}`\n\n*To:*\n`{response['to']}`\n\n*Nonce:*\n{response['nonce']}"""
        await update.message.reply_text(reply, parse_mode="Markdown")
    elif response.status_code == 400:
        print(response)
        await update.message.reply_text(response.json()["detail"])
    elif response.status_code == 422:
        print(f"422 code -> {response.json()['detail'][0]['loc']}")
        wrong_input = ""
        if "eth_to_spend" in response.json()["detail"][0]["loc"]:
            wrong_input = "eth amount"
            await update.message.reply_text(f"{wrong_input} must be a number")
            return ConversationHandler.END
        elif "token_to_buy" in response.json()["detail"][0]["loc"]:
            wrong_input = "token address"
            await update.message.reply_text(
                f"{wrong_input} must be a hexadecimal address"
            )
            return ConversationHandler.END
        
        
    # @TODO add custom error codes for different situations (400 means server will not process request bcz of client error
    return ConversationHandler.END


async def disect_message(update: Update, message: list[str, str, float]):
    print(len(message))
    print(message)
    if message is not None and len(message) == 3:
        try:
            _, token_address, amount, *_ = message
            return token_address, amount
        except ValueError as e:
            await update.message.reply_text(
                """*invalid command format*\n`/buy_tokens_with_eth <0xaddress> <amount_of_eth_to_spend>`""",
                parse_mode="Markdown",
            )
    elif len(message) == 2:
        try:
            token_address, amount, *_ = message
            return token_address, amount
        except ValueError as e:
            print(f"line 79 buy_tokens_with_eth {e}")
            await update.message.reply_text(
                """*invalid command format*\n`/buy_tokens_with_eth <0xaddress> <amount_of_eth_to_spend>`""",
                parse_mode="Markdown",
            )
    else:
        return False, False


async def buy_tokens_with_eth(update: Update, context: CallbackContext) -> None:
    # check if message was edited update.message is alwas none if message is edited
    if update.message is None:
        await context.bot.send_message(
            update.effective_chat.id, "Please type in command again editing not allowed"
        )
        return

    if update.message.text is not None:
        message = update.message.text.strip().split()
        if len(message) == 1:
            await update.message.reply_text("enter addrress and amount")
            return WAIT_FOR_TOKEN
        print(f"message : {message}")

        await when_token_is_enterd(update, context, message)
        return ConversationHandler.END


async def fall_back(update: Update, context: CallbackContext, kill: int = None):
    """`arg KILL` is a special arg if set to some integer value returns kill str which can be used to terminate function"""
    # Call the start command handler to show the buttons again
    # await start_command(update, context)
    if kill is not None:
        await buy_tokens_with_eth(update, context)
        return "kill"
    command = update.message.text  # [1:]
    print(f"command = {command}")
    if command == "/buy_tokens_with_eth":
        await buy_tokens_with_eth(update, context)
        return ConversationHandler.END
    elif command.startswith("/"):
        return ConversationHandler.END


buy_tokens_with_eth_convo_handler = ConversationHandler(
    entry_points=[CommandHandler("buy_tokens_with_eth", buy_tokens_with_eth)],
    states={WAIT_FOR_TOKEN: [MessageHandler(filters.TEXT, when_token_is_enterd)]},
    fallbacks=[
        MessageHandler(filters.ALL, fall_back),
        MessageHandler(filters.COMMAND, fall_back),
    ],
    conversation_timeout=60 * 7,
)
