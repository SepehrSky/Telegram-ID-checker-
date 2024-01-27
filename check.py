from telethon import TelegramClient, sync
from telethon import functions, errors
import configparser
import time
import os

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('default', 'api_id')
api_hash = config.get('default', 'api_hash')
bot_token = config.get('default', 'bot_token')  # Added this line

if api_id == 'UPDATE ME' or api_hash == 'UPDATE ME' or bot_token == 'UPDATE ME':
    print("Please read the config.ini and README.md")
    input()
    exit()
else:
    api_id = int(api_id)
    client = TelegramClient('Checker', api_id, api_hash)
    client.start()

def user_lookup(account):
    try: 
        result = client(functions.account.CheckUsernameRequest(username=account))
        if result:
            print("The telegram", account, "is available")
            file = open(output(), 'a')
            file.write("%s\n" % (account))
            file.close()
        else:
            print("The telegram", account, "is not available")
    except errors.FloodWaitError as fW:
        print(f"Hit the rate limit, waiting {fW.seconds} seconds")
        time.sleep(fW.seconds)
        user_lookup(account)
    except errors.UsernameInvalidError as uI:
        print("Username is invalid")
    except errors.rpcbaseerrors.BadRequestError as bR:
        print("Error:", bR.message)

def get_words():
    words = []
    delay = config.get('default', 'delay')
    path = os.path.join("word_lists", config.get('default', 'wordList'))
    
    if path is not None:
        file = open(path, 'r', encoding='utf-8-sig')
        words = file.read().split('\n')
        file.close()
    else:
        print("Word list not found.")
    
    for name in words:
        user_lookup(name)
        time.sleep(int(delay))

    print("All done")
    input("Press enter to exit...")

def output():
    return config.get('default', 'outPut', fallback="Available.txt")

def main():
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
                                   3phrn
    ''')

    print("1 = Enter username manually\n2 = Read a list of usernames from the word_lists folder")
    options = ["1", "2"]
    choice = input("Select your option: ")

    while choice not in options:
        choice = input("1 or 2 ... Please!: ")

    if choice == "1":
        username = input("Enter a username: ")
        user_lookup(username)
    elif choice == "2":
        get_words()

if __name__ == "__main__":
    main()
