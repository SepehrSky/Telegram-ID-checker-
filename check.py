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

async def get_words():
    path = os.path.join("word_lists", config.get('default', 'wordList'))

    if path is not None:
        with open(path, 'r', encoding='utf-8-sig') as file:
            words = file.read().split('\n')

        for name in words:
            await user_lookup(name)
            await asyncio.sleep(1/30)  # Introduce the 1/30 second delay

    print("Removing checked words from the word list...")
    # Implement remove_checked_words() as needed
    print("All done")

    try:
        await user_lookup("dummy_user")  # Perform a dummy user_lookup to ensure the rate limit is over
    except errors.FloodWaitError as fW:
        print(f"Hit the rate limit, waiting {fW.seconds} seconds")
        await asyncio.sleep(fW.seconds)
        print("Removing checked words from the word list...")
        # Implement remove_checked_words() as needed
        print("All done")
    except Exception as e:
        print(f"Unhandled error: {e}")


    try:
        await user_lookup("dummy_user")  # Perform a dummy user_lookup to ensure the rate limit is over
    except errors.FloodWaitError as fW:
        print(f"Hit the rate limit, waiting {fW.seconds} seconds")
        await asyncio.sleep(fW.seconds)
    except Exception as e:
        print(f"Unhandled error: {e}")

    print("Removing checked words from the word list...")
    # Implement remove_checked_words() as needed
    print("All done")

async def close():
    print("Closing the app.")
    await client.disconnect()

async def main():
    print('''
    - Username Checker -
    
1 = Enter username manually
2 = Read a list of usernames from the word_lists folder
3 = Sleep until rate limit is over
4 = Close the app
    ''')

    while True:
        option = input("Select your option: ")
        if option == '2':
            print("Getting usernames from word_lists...")
            try:
                await get_words()
            except errors.FloodWaitError as fW:
                print(f"Hit the rate limit, waiting {fW.seconds} seconds")
                await asyncio.sleep(fW.seconds)
                await user_lookup("test_user")  # Perform a dummy user_lookup to ensure the rate limit is over
                await asyncio.sleep(1)  # Introduce a small delay
            except Exception as e:
                print(f"Unhandled error: {e}")
                await asyncio.sleep(5)  # Sleep for 5 seconds before prompting for the next option
                continue  # Continue to the next iteration
        elif option == '1':
            # Implement the case for entering username manually
            pass
        elif option == '3':
            print("Sleeping until rate limit is over...")
            await asyncio.sleep(600)  # Sleep for 10 minutes as an example
        elif option == '4':
            await close()
            break
        else:
            print("Invalid option. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.run_until_complete(close())
