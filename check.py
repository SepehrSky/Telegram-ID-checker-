from telethon import TelegramClient, functions, errors
import configparser
import os
import asyncio
import sys

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
        return fW.seconds
    except Exception as e:
        print(f"Unhandled error: {e}")
        return False

async def remove_checked_words(checked_words, word_list_path):
    with open(word_list_path, 'r', encoding='utf-8-sig') as file:
        words = file.read().split('\n')

    updated_words = [word for word in words if word not in checked_words]

    with open(word_list_path, 'w', encoding='utf-8-sig') as file:
        file.write('\n'.join(updated_words))

async def get_words():
    path = os.path.join("word_lists", config.get('default', 'wordList'))
    checked_words = []

    if path is not None:
        with open(path, 'r', encoding='utf-8-sig') as file:
            words = file.read().split('\n')

        for name in words:
            rate_limit_seconds = await user_lookup(name)
            if rate_limit_seconds:
                print(f"Rate limit hit. Options after rate limit:")
                await display_options()
                option = input("Select your option: ")

                if option == '3':
                    print(f"Sleeping until rate limit is over ({rate_limit_seconds} seconds)...")
                    await asyncio.sleep(rate_limit_seconds)
                elif option == '4':
                    print("Closing the app.")
                    await close()
                    return  # Return from the function to avoid further execution
                checked_words.append(name)

                # Introduce the 1/30 second delay
                await asyncio.sleep(1/30)

        await remove_checked_words(checked_words, path)

    print("All done")


async def close():
    print("Closing the app.")
    await client.disconnect()
    await asyncio.sleep(1)  # Introduce a small delay
    sys.exit(0)  # Terminate the script
    
async def display_options():
    print('''
    - Username Checker -
    
3 = Sleep until rate limit is over
4 = Close the app
    ''')

async def main():
    print('''
    - Username Checker -
    
1 = Enter username manually
2 = Read a list of usernames from the word_lists folder
    ''')

    while True:
        option = input("Select your option: ")
        if option == '2':
            print("Getting usernames from word_lists...")
            try:
                await get_words()
            except Exception as e:
                print(f"Error: {e}")
        elif option == '1':
            # Implement the case for entering username manually
            pass
        else:
            print("Invalid option. Please enter 1 or 2.")

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.run_until_complete(close())
