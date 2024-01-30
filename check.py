async def get_words():
    path = os.path.join("word_lists", config.get('default', 'wordList'))

    if path is not None:
        with open(path, 'r', encoding='utf-8-sig') as file:
            words = file.read().split('\n')

        for name in words:
            try:
                await user_lookup(name)
                await asyncio.sleep(1/30)  # Introduce the 1/30 second delay
            except errors.FloodWaitError as fW:
                print(f"Hit the rate limit, waiting {fW.seconds} seconds")
                await asyncio.sleep(fW.seconds)
                print_options = False
                break
        else:
            print_options = True

        if print_options:
            await display_options()

    print("Removing checked words from the word list...")
    # Implement remove_checked_words() as needed
    print("All done")
