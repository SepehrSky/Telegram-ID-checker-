from telethon import TelegramClient, sync, functions, errors
from telegram import Bot
from telegram.ext import ChatBot, MessageHandler, Filters
import configparser
import time
import os

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

    # Initialize the ChatBot for rate limit handling
    chatbot = ChatBot(token=bot_token)

def user_lookup(account):
    try:
        result = client(functions.account.CheckUsernameRequest(username=account))
        if result:
            print("The telegram", account, "is available")
            log_word(account, "Available.txt")
            log_word(account, "Checked_words.txt")
        else:
            print("The telegram", account, "is not available")
            log_word(account, "Checked_words.txt")
    except errors.FloodWaitError as fW:
        print(f"Hit the rate limit, waiting {fW.seconds} seconds")
        time.sleep(fW.seconds)
        user_lookup(account)
    except errors.UsernameInvalidError as uI:
        print("Username is invalid")
    except errors.rpcbaseerrors.BadRequestError as bR:
        print("Error:", bR.message)

def log_word(word, filename):
    with open(filename, 'a') as file:
        file.write(f"{word}\n")

def remove_checked_words():
    checked_path = os.path.join("word_lists", "Checked_words.txt")
    word_list_path = os.path.join("word_lists", config.get('default', 'wordList'))

    if os.path.exists(checked_path) and os.path.exists(word_list_path):
        with open(checked_path, 'r', encoding='utf-8-sig') as checked_file:
            checked_words = checked_file.read().split('\n')

        with open(word_list_path, 'r', encoding='utf-8-sig') as word_list_file:
            word_list = word_list_file.read().split('\n')

        remaining_words = [word for word in word_list if word not in checked_words]

        with open(word_list_path, 'w', encoding='utf-8-sig') as updated_file:
            updated_file.write('\n'.join(remaining_words))

def get_words():
    delay = config.get('default', 'delay')
    path = os.path.join("word_lists", config.get('default', 'wordList'))

    if path is not None:
        with open(path, 'r', encoding='utf-8-sig') as file:
            words = file.read().split('\n')

        for name in words:
            user_lookup(name)
            time.sleep(int(delay))

    print("Removing checked words from the word list...")
    remove_checked_words()
    print("All done")
    input("Press enter to exit...")

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
        Make sure to read the config.ini and README.md on github
    bulk checking may result in false positives and longer wait times
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
