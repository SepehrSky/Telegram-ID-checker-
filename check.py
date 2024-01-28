# app.py
import os
import time
from telethon import TelegramClient, sync, functions, errors
import configparser

config = configparser.ConfigParser()
config.read('config.ini')  # Add this line to read the configuration file

def read_checked_words():
    try:
        path = os.path.join("word_lists", "checked_words.txt")
        with open(path, 'r') as file:
            checked_words = file.read().splitlines()
        return checked_words
    except FileNotFoundError:
        return []

def write_checked_words(checked_words):
    path = os.path.join("word_lists", "checked_words.txt")
    with open(path, 'w') as file:
        file.write('\n'.join(checked_words))

def read_word_list():
    path = os.path.join("word_lists", config.get('default', 'wordList'))
    try:
        with open(path, 'r', encoding='utf-8-sig') as file:
            words = file.read().split('\n')
        return words
    except FileNotFoundError:
        return []

def remove_checked_words(word_list, checked_words):
    return [word for word in word_list if word not in checked_words]

def user_lookup(account, checked_words):
    if account in checked_words:
        print("The telegram", account, "has already been checked.")
        return

    try:
        result = client(functions.account.CheckUsernameRequest(username=account))
        if result:
            print("The telegram", account, "is available")
            checked_words.append(account)
            write_checked_words(checked_words)
        else:
            print("The telegram", account, "is not available")
    except errors.FloodWaitError as fW:
        print(f"Hit the rate limit, waiting {fW.seconds} seconds")
        time.sleep(fW.seconds)
        user_lookup(account, checked_words)
    except errors.UsernameInvalidError as uI:
        print("Username is invalid")
    except errors.rpcbaseerrors.BadRequestError as bR:
        print("Error:", bR.message)

def get_words():
    delay = config.get('default', 'delay')
    word_list = read_word_list()
    checked_words = read_checked_words()

    for name in remove_checked_words(word_list, checked_words):
        user_lookup(name, checked_words)
        time.sleep(int(delay))

    print("All done")
    input("Press enter to exit...")

def output():
    return config.get('default', 'outPut', fallback="Available.txt")

def main():
    get_words()  # Adjust this line based on your actual logic

if __name__ == "__main__":
    client = TelegramClient('Checker', config.get('default', 'api_id'), config.get('default', 'api_hash'))
    client.start()

    main()
