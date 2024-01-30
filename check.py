from telethon import TelegramClient, functions, errors
import configparser
import time
import os

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('default', 'api_id')
api_hash = config.get('default', 'api_hash')

if api_id == 'UPDATE ME' or api_hash == 'UPDATE ME':
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
        log_word(account, "checked_words.txt")  # Log all checked usernames

        if result:
            print("The telegram", account, "is available")
            log_word(account, "Available.txt")  # Log available usernames
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

def close():
    print("Closing the app.")

if __name__ == "__main__":
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
    ''')

    print("1 = Enter username manually\n2 = Read a list of usernames from the word_lists folder")
    set_options = ["1", "2"]

    while True:
        option = input("Select your option: ")
        if option in set_options:
            if option == set_options[0]:
                name = input("Enter a username: ")
                user_lookup(name)
            else:
                print("Getting usernames from word_lists...")
                get_words()
                close()  # Close the app
                break
        else:
            print("1 or 2 ... Please!")
