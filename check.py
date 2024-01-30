from telethon import TelegramClient, functions, errors
from telegram.ext import CommandHandler, Updater
import configparser
import os
import asyncio

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('default', 'api_id')
api_hash = config.get('default', 'api_hash')
bot_token = config.get('default', 'bot_token')

if api_id == 'UPDATE ME' or api_hash == 'UPDATE ME' or bot_token == 'UPDATE ME':
    print("Please read the config.ini and README.md")
    input()
    exit()
else:
    api_id = int(api_id)
    client = TelegramClient('Checker', api_id, api_hash)
    client.start()

updater = Updater(bot_token, use_context=True)
dispatcher = updater.dispatcher

async def user_lookup(account, context):
    try:
        result = await client(functions.account.CheckUsernameRequest(username=account))
        log_word(account, "checked_words.txt")  # Log all checked usernames

        if result:
            message = f"The telegram {account} is available"
            context.bot.send_message(chat_id=context.message.chat_id, text=message)
            log_word(account, "Available.txt")  # Log available usernames
        else:
            message = f"The telegram {account} is not available"
            context.bot.send_message(chat_id=context.message.chat_id, text=message)
    except errors.FloodWaitError as fW:
        message = f"Hit the rate limit, waiting {fW.seconds} seconds"
        context.bot.send_message(chat_id=context.message.chat_id, text=message)
        await asyncio.sleep(fW.seconds)
        await user_lookup(account, context)
    except errors.UsernameInvalidError as uI:
        message = "Username is invalid"
        context.bot.send_message(chat_id=context.message.chat_id, text=message)
    except errors.rpcbaseerrors.BadRequestError as bR:
        message = f"Error: {bR.message}"
        context.bot.send_message(chat_id=context.message.chat_id, text=message)
        if "USERNAME_INVALID" in bR.message:
            message = f"The telegram {account} is invalid"
            context.bot.send_message(chat_id=context.message.chat_id, text=message)
        elif "USERNAME_OCCUPIED" in bR.message:
            message = f"The telegram {account} is already taken"
            context.bot.send_message(chat_id=context.message.chat_id, text=message)
        elif "USERNAME_NOT_OCCUPIED" in bR.message:
            message = f"The telegram {account} is available"
            context.bot.send_message(chat_id=context.message.chat_id, text=message)
        elif "FLOOD_WAIT" in bR.message:
            message = f"Hit the rate limit, waiting {bR.seconds} seconds"
            context.bot.send_message(chat_id=context.message.chat_id, text=message)
            await asyncio.sleep(bR.seconds)
            await user_lookup(account, context)
        else:
            message = f"Unhandled error: {bR.message}"
            context.bot.send_message(chat_id=context.message.chat_id, text=message)

def log_word(word, filename):
    with open(filename, 'a') as file:
        file.write(f"{word}\n")

def remove_checked_words():
    checked_path = os.path.join("word_lists", "checked_words.txt")
    word_list_path = os.path.join("word_lists", config.get('default', 'wordList'))

    if os.path.exists(checked_path) and os.path.exists(word_list_path):
        with open(checked_path, 'r', encoding='utf-8-sig') as checked_file:
            checked_words = checked_file.read().split('\n')

        with open(word_list_path, 'r', encoding='utf-8-sig') as word_list_file:
            word_list = word_list_file.read().split('\n')

        remaining_words = [word for word in word_list if word not in checked_words]

        with open(word_list_path, 'w', encoding='utf-8-sig') as updated_file:
            updated_file.write('\n'.join(remaining_words))

async def get_words():
    delay = config.get('default', 'delay')
    path = os.path.join("word_lists", config.get('default', 'wordList'))

    if path is not None:
        with open(path, 'r', encoding='utf-8-sig') as file:
            words = file.read().split('\n')

        for name in words:
            await user_lookup(name, context)
            await asyncio.sleep(1/30)  # Introduce the 1/30 second delay

    print("Removing checked words from the word list...")
    remove_checked_words()
    print("All done")

async def close():
    print("Closing the app.")
    await client.disconnect()

async def main():
    print('''
    ▄▄▄█████▓▓█████  ██▓    ▓█████   ▄████  ██▀███   ▄▄▄       ███▄ ▄███▓
    ▓  ██▒ ▓▒▓█   ▀ ▓██▒    ▓█   ▀  ██▒ ▀█▒▓██ ▒ ██▒▒████▄    ▓██▒▀█▀ ██▒
    ▒ ▓██░ ▒░▒███   ▒██░    ▒███   ▒██░▄▄▄░▓██ ░▄█ ▒▒██  ▀█▄  ▓██    ▓██░
    ░ ▓██▓ ░ ▒▓█  ▄ ▒██░    ▒▓█  ▄ ░▓█  ██▓▒██▀▀█▄  ░██▄▄▄▄██ ▒██    ▒██ 
    ▒██▒ ░ ░▒████▒░██████▒░▒████▒░▒▓███▀▒░██▓ ▒██▒ ▓█   ▓██▒▒██▒   ░██▒
    ▒ ░░   ░░ ▒░ ░░ ▒░▓  ░░░ ▒░ ░ ░▒   ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒░   ░  ░
      ░     ░ ░  ░░ ░ ▒  ░ ░ ░  ░  ░   ░   ░▒ ░ ▒░  ▒   ▒▒ ░░  ░      ░
    ░         ░     ░ ░      ░   ░ ░   ░   ░░   ░   ░   ▒   ░      ░   
                ░  ░    ░  ░   ░  ░      ░    ░           ░  ░       ░   
    - Username Checker - From 3phrn
    
1 = Enter username manually
2 = Read a list of usernames from the word_lists folder
Select your option: 2
''')

    while True:
        print("Getting usernames from word_lists...")
        try:
            await get_words()
        except errors.FloodWaitError as fW:
            print(f"Hit the rate limit, waiting {fW.seconds} seconds")
            await asyncio.sleep(fW.seconds)
        except Exception as e:
            print(f"Unhandled error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.run_until_complete(close())
