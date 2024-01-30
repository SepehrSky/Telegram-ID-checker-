from telethon import TelegramClient, functions, errors
import configparser
import time
import os
import logging

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('default', 'api_id')
api_hash = config.get('default', 'api_hash')
bot_token = config.get('default', 'bot_token')

if api_id == 'UPDATE ME' or api_hash == 'UPDATE ME' or bot_token == 'UPDATE ME':
    logging.error("Please read the config.ini and README.md")
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
            logging.info(f"The telegram {account} is available")
            log_word(account, "Available.txt")  # Log available usernames
        else:
            logging.info(f"The telegram {account} is not available")
    except errors.FloodWaitError as fW:
        logging.warning(f"Hit the rate limit, waiting {fW.seconds} seconds")
        time.sleep(fW.seconds)
        user_lookup(account)
    except errors.UsernameInvalidError as uI:
        logging.error("Username is invalid")
    except errors.rpcbaseerrors.BadRequestError as bR:
        logging.error(f"Error: {bR.message}")

def log_word(word, filename):
    with open(filename, 'a') as file:
        file.write(f"{word}\n")

def remove_checked_words():
    checked_path = os.path.join("word_lists", "checked_words.txt")
    word_list_path = os.path.join("word_lists", config.get('default', 'wordList'))

    logging.info("Checking path: {}".format(checked_path))
    logging.info("Word list path: {}".format(word_list_path))

    if os.path.exists(checked_path) and os.path.exists(word_list_path):
        with open(checked_path, 'r', encoding='utf-8-sig') as checked_file:
            checked_words = checked_file.read().split('\n')

        with open(word_list_path, 'r', encoding='utf-8-sig') as word_list_file:
            word_list = word_list_file.read().split('\n')

        logging.info("Checked Words: {}".format(checked_words))
        logging.info("Original Word List: {}".format(word_list))

        remaining_words = [word for word in word_list if word not in checked_words]

        logging.info("Remaining Words: {}".format(remaining_words))

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

    logging.info("Removing checked words from the word list...")
    remove_checked_words()
    logging.info("All done")

def main():
    logging.info('''
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
                logging.info("Getting usernames from word_lists...")
                get_words()
                break
        else:
            logging.warning("1 or 2 ... Please!")

if __name__ == "__main__":
    main()
