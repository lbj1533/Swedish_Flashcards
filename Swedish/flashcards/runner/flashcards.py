import time, sys, random

#define globals
OS = None

def get_OS():
    global OS
    if sys.platform.startswith('win'):
        OS = "windows"
    else:
        OS = "macos"
    return OS

def handle_args():
    if len(sys.argv) > 2:
        print_exception("Usage: python Swedish\\flashcards\\flashcards.py \"filename\"")
        quit()
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
        filename = handle_file_system(filename)
        return [rec_open_file(filename), filename]
    elif len(sys.argv) == 1:
        return False

def display_settings(settings):
    if handle_boolean_input("View Settings?"):
        print_settings(settings)
    else:
        return settings
    if handle_boolean_input("Make Changes?"):
        setting = handle_integer_input("Select a setting to change.", 1, len(settings)+1)-1
        settings[setting][1] = not settings[setting][1]
        print(f"Setting \"{settings[setting][0]}\" changed to {settings[setting][1]}.")
    return display_settings(settings)

def handle_file_system(filename):
    if OS == "windows":
        filename = "Swedish\\flashcards\\" + filename + ".txt"
    elif OS == "macos":
        filename = "Swedish/flashcards/" + filename + ".txt"
    return filename

def rec_open_file(filename):
    try:
        with open(filename, "r", encoding='utf-8') as file:
            parsed_string = parse_file(file)
            print(f"rec_open_file(): {parsed_string}")
            if isinstance(parsed_string, str):
                return parsed_string
            else:
                raise TypeError("Parsed content is not a string.")
    except (FileNotFoundError, TypeError) as e:
        print_exception(f"Error: {str(e)}")
        return None

def get_set():
    while True:
        filename = input("Enter the set to study, do not include the .txt extension: ")
        filename = handle_file_system(filename)
        content = rec_open_file(filename)
        if content:
            return [content, filename]

def parse_file(file):
    lines = file.readlines()
    content = [line for line in lines if (line.strip() != '' and not line.strip().startswith("#"))]
    content = "".join(content)
    return content

def parse_cards(content):
    content = content.split("\n")[:-1]
    cards = []
    for pair in content:
        pair = pair.split(": ")
        cards.append(pair)
    return cards

def display_cards(cards, score, filename):
    global settings
    if settings[0][1]:
        term = 1
        definition = 0
    else:
        term = 0
        definition = 1
    if settings[1][1]:
        random.shuffle(cards)
    wrong_answers = []
    for card in cards:
        try: attempt = input("\r" + card[term] + "\n")
        except IndexError: print_exception("Index error: card: " + str(card))
        if not attempt == card[definition]:
            wrong_answers.append(card)
            att2 = ""
            while att2 != card[definition]:
                print(f"Type the correct answer: {card[definition]} ", end = "")
                att2 = input()
                if att2 != card[definition]:
                    print("\033[F\033[K", end="")
        print("\033[2J")
    if len(wrong_answers) > 0: 
        print("Wrong answers:")
        time.sleep(2)
        display_cards(wrong_answers, calc_last_score(len(wrong_answers), len(cards)), filename)
    if len(wrong_answers) == 0:
        score = calc_last_score(len(wrong_answers), len(cards))
        print(f"Score: {score}%")
        write_last_score_to_file(score, filename)

def calc_last_score(num_wrong, num_total):
    return round((num_total-num_wrong)/num_total * 100)

def write_last_score_to_file(score, filename):
    with open(filename, 'r') as file:
        oc = file.readlines()[1:]
        oc = "".join(oc)
    with open(filename, "w") as file:
        scoreline = f"# Score: {score}"
        file.write(scoreline + "\n" + oc)

def prompt_repeat(cards):
    while True:
        repeat = handle_boolean_input("Repeat?")
        display_cards(cards) if repeat else quit()

def print_exception(message):
    print("\033[31m\n" + message + "\n\033[0m")

def handle_boolean_input(message):
    inp = input(f"{message} [Y/N] ")
    if inp in ["Y","y"]:
        return True
    elif inp in ["N","n"]:
        return False
    else:
        print_exception("Enter Y or N.")
        return handle_boolean_input(message)

def handle_integer_input(message, lower_bound, upper_bound):
    try:
        inp = int(input(f"{message} [{str(lower_bound)} to {str(upper_bound-1)}] "))
        if lower_bound <= inp <= upper_bound-1:
            return inp
        else:
            raise ValueError
    except ValueError:
        print_exception(f"Enter valid input between {lower_bound} and {upper_bound-1}.")
        return handle_integer_input(message, lower_bound, upper_bound)

def print_settings(message):
    for i, setting in enumerate(message):
        print(f"{i+1}. {setting[0]} : {setting[1]}")

def main():
    global settings
    settings = [
        ["Flip term and definition", True],
        ["Shuffle cards", False]
    ]

    OS = get_OS()
    settings = display_settings(settings)

    content_filename = handle_args() or get_set()
    content, filename = content_filename

    cards = parse_cards(content)
    display_cards(cards, 0, filename)
    prompt_repeat(cards)

try:
    main()
except KeyboardInterrupt:
    print_exception("Program terminated by Keyboard Interrupt [Ctrl-C].")
