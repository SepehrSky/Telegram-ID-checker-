from telethon import TelegramClient, functions, errors
import configparser
import os
import asyncio

config = configparser.ConfigParser()
config.read('config.ini')

api_id = int(config.get('default', 'api_id'))
api_hash = config.get('default', 'api_hash')
bot_token = config.get('default', 'bot_token')

client = TelegramClient('Checker', api_id, api_hash)
client.start()

async def user_lookup(account):
    try:
        result = await client(functions.account.CheckUsernameRequest(username=account))
        if result:
            print(f"The telegram {account} is available")
        else:
            print(f"The telegram {account} is not available")
    except errors.FloodWaitError as fW:
        print(f"Hit the rate limit, waiting {fW.seconds} seconds")
        await asyncio.sleep(fW.seconds)
        await user_lookup(account)
    except errors.UsernameInvalidError as uI:
        print("Username is invalid")
    except errors.rpcbaseerrors.BadRequestError as bR:
        print("Error:", bR.message)
        if "USERNAME_INVALID" in bR.message:
            print(f"The telegram {account} is invalid")
        elif "USERNAME_OCCUPIED" in bR.message:
            print(f"The telegram {account} is already taken")
        elif "USERNAME_NOT_OCCUPIED" in bR.message:
            print(f"The telegram {account} is available")
        elif "FLOOD_WAIT" in bR.message:
            print(f"Hit the rate limit, waiting {bR.seconds} seconds")
            await asyncio.sleep(bR.seconds)
            await user_lookup(account)
        else:
            print("Unhandled error:", bR.message)

async def remove_checked_words():
    # Implement this function as needed
    pass

async def get_words():
    path = os.path.join("word_lists", config.get('default', 'wordList'))

    if path is not None:
        with open(path, 'r', encoding='utf-8-sig') as file:
            words = file.read().split('\n')

        for name in words:
            await user_lookup(name)
            await asyncio.sleep(1/30)  # Introduce the 1/30 second delay

        print("Removing checked words from the word list...")
        await remove_checked_words()
        print("All done")

    while True:
        try:
            await display_options()
            option = input("Select your option: ")
            if option == '3':
                print(f"Hit the rate limit, waiting {fW.seconds} seconds")
                await asyncio.sleep(fW.seconds)
            elif option == '4':
                await close()
                return
            else:
                print("Invalid option. Please enter 3 or 4.")
        except errors.FloodWaitError as fW:
            print(f"Hit the rate limit, waiting {fW.seconds} seconds")
            await asyncio.sleep(fW.seconds)

async def close():
    print("Closing the app.")
    await client.disconnect()

async def display_options():
    print('''
    - Username Checker -
    
1 = Enter username manually
2 = Read a list of usernames from the word_lists folder
3 = Sleep until rate limit is over
4 = Close the app
    ''')

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(display_options())
        option = input("Select your option: ")
        if option == '1' or option == '2':
            loop.run_until_complete(get_words())
        elif option == '3':
            print(f"Hit the rate limit, waiting {fW.seconds} seconds")
            await asyncio.sleep(fW.seconds)
        elif option == '4':
            loop.run_until_complete(close())
        else:
            print("Invalid option. Please enter 1, 2, 3, or 4.")
    except KeyboardInterrupt:
        loop.run_until_complete(close())
