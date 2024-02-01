from telethon import TelegramClient, functions, errors
import configparser
import os
import time

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('default', 'api_id')
api_hash = config.get('default', 'api_hash')

if api_id == '28228681' or api_hash == 'b81a9e939de31be895836571119b490a':
    print("Please read the config.ini and README.md")
    input()
    exit()
else:
    api_id = int(api_id)
    client = TelegramClient('Checker', api_id, api_hash)
    client.start()


class RateLimiter:
    def __init__(self, limit_per_second):
        self.limit_per_second = limit_per_second
        self.last_request_time = time.time()

    async def delay_request(self):
        current_time = time.time()
        time_difference = current_time - self.last_request_time
        if time_difference < 1 / self.limit_per_second:
            delay = 1 / self.limit_per_second - time_difference
            await asyncio.sleep(delay)
        self.last_request_time = time.time()


async def user_lookup(account, rate_limiter):
    try:
        await rate_limiter.delay_request()
        result = await client(functions.account.CheckUsernameRequest(username=account))
        if result == True:
            print("The telegram", account, "is available")
            file = open(output(), 'a')
            file.write("%s\n" % (account))
            file.close()
        else:
            print("The telegram", account, "is not available")
    except errors.FloodWaitError as fW:
        print("Hit the rate limit, waiting", fW.seconds, "seconds")
        await asyncio.sleep(fW.seconds)
    except errors.UsernameInvalidError as uI:
        print("Username is invalid")
    except errors.rpcbaseerrors.BadRequestError as bR:
        print("Error:", bR.message)


async def get_words(rate_limiter):
    words = []
    delay = config.get('default', 'delay')
    path = os.path.join("word_lists", config.get('default', 'wordList'))
    if path is not None:
        file = open(path, 'r', encoding='utf-8-sig')
        words = file.read().split('\n')
        file.close()
    else:
        print("Word list not found.")

    for i in range(len(words)):
        name = words[i]
        await user_lookup(name, rate_limiter)
        await asyncio.sleep(int(delay))
    print("All done")
    input("Press enter to exit...")


def output():
    return config.get('default', 'outPut', fallback="AVAILABLE.txt")


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
                                                                         
                                - Username Checker -
            Make sure to read the config.ini and README.md on github
        bulk checking may result in false positives and longer wait times
            ''')
    print("1 = Enter username manually\n2 = Read a list of usernames from the word_lists folder")
    set = ["1", "2"]
    option = input("Select your option: ")
    rate_limiter = RateLimiter(0.5)  # Adjust the rate limit as needed

    while True:
        if str(option) in set:
            if option == set[0]:
                name = input("Enter a username: ")
                await user_lookup(name, rate_limiter)
            else:
                await get_words(rate_limiter)
                break
        else:
            option = input("1 or 2 ... Please!: ")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
