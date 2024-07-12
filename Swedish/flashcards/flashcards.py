
'''
Todo:
add support for color (colorama doesn't seem to work on macos, use ANSI codes)
add handling for when an answer is wrong
Add support for folders
Make sure flashcards.py works in a subfolder
add another script that handles metadata in general especially score
'''

import time, sys, random

OS = None

'''
Function to check the OS, was running into issues with colorama
assumes either windows or macos
'''
def get_OS():
    global OS
    if sys.platform.startswith('win'):
        OS = "windows"
    else:
        OS = "macos"
    return OS


'''
Function to handle if this script is being used as a command line tool
returns False if not being used as command line tool
returns the string of the file if it is being used as a command line tool
'''
def handle_args():
    if len(sys.argv) > 2:
        print_exception("Usage: python Swedish\flashcards\flashcards.py \"filename\"")
        quit()
    elif len(sys.argv) == 2:
        global OS
        if OS == "windows":
            filename = "Swedish\\flashcards\\" + filename + ".txt"
        elif OS == "macos":
            filename = "Swedish/flashcards/" + filename + ".txt"
        try:
            with open(filename, "r", encoding='utf-8') as file:
                return parse_file(file)
        except FileNotFoundError:
            print_exception(f"File {filename} not found.")
            quit()
    elif len(sys.argv) == 1:
        return False

'''
Function to alter the settings of the flashcard studier
takes in settings
returns settings
'''
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


'''
Function to read in the set of cards from a .txt file
Returns a string containing the whole text file
Asks for input
Assumptions: entire file can be read in one string object, encoding is utf-8
'''
def get_set():
    filename = input("Enter the set to study, do not include the .txt extension: ")
    global OS
    if OS == "windows":
        filename = "Swedish\\flashcards\\" + filename + ".txt"
    elif OS == "macos":
        filename = "Swedish/flashcards/" + filename + ".txt"
    try:
        with open(filename, "r", encoding='utf-8') as file:
            return parse_file(file)
    except FileNotFoundError:
        print_exception(f"File {filename} not found.")
        return get_set()

'''
Function to parse a string from the passed file
takes in a file
'''
def parse_file(file):
    lines = file.readlines()
    content = [line for line in lines if (line.strip() != '' and not line.strip().startswith("#"))]
    return "".join(content)
    
'''
Function to parse the cards from the string read in
returns a list of 2-lists, the cards
Assumes formatting is correct
'''
def parse_cards(content):
    content = content.split("\n")
    cards = []
    for pair in content:
        pair = pair.split(": ")
        cards.append(pair)
    return cards

'''
Function to run through the cards, displaying them for studying
takes in cards and returns nothing
Assumes ANSI codes will clear the screen, and that cards have length 2, and that whitespace is correct
'''
def display_cards(cards):
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
        attempt = input("\r" + card[term] + "\n")
        if not attempt == card[definition]:
            wrong_answers.append(card)
            print("Correct answer: " + card[definition])
            time.sleep(5)
        print("\033[2J")
    if len(wrong_answers) > 0: 
        print("Wrong answers:")
        time.sleep(2)
        display_cards(wrong_answers)

'''
Prompts the user to repeat the last set studied
Takes in previous set, returns nothing
Asks for input
Assumes last set was valid, and that the input is either y or n
'''
def prompt_repeat(cards):
    while True:
        repeat = handle_boolean_input("Repeat?")
        display_cards(cards) if repeat else quit()
        

'''
Function to print exceptions
Takes in message, returns nothing
'''
def print_exception(message):
    print("\n" + message + "\n")

'''
Function to handle all Y/N input
Takes in message, returns boolean
'''
def handle_boolean_input(message):
    inp = input(f"{message} [Y/N] ")
    if inp in ["Y","y"]:
        return True
    elif inp in ["N","n"]:
        return False
    else:
        print_exception("Enter Y or N.")
        return handle_boolean_input(message)
    
'''
Function to handle integer input
Takes in a message, a lower bound (inclusive) and a upper bound (exclusive)
Returns integer inserted
'''
def handle_integer_input(message, lower_bound, upper_bound):
    inp = int(input(f"{message} [{str(lower_bound)} to {str(upper_bound-1)}] "))
    if type(inp) != isinstance(inp, int) and inp >= lower_bound and inp <= upper_bound-1:
        return int(inp)
    else:
        print_exception(f"Enter valid input between {lower_bound} and {upper_bound-1}.")
        return handle_integer_input(message, upper_bound, lower_bound)
    
'''
Function to print the settings menu
Takes in a list of 2 lists and prints them in an organized manner
Assumes settings are a list of 2 lists
'''
def print_settings(message):
    for i,setting in enumerate(message):
        print(f"{i+1}. {setting[0]} : {setting[1]}")


'''
Main function to run program
'''
def main():
    global settings, Fore
    settings = [
        ["Flip term and definition", True],
        ["Shuffle cards", True]
    ]

    OS = get_OS()

    settings = display_settings(settings)
    if not handle_args():
        content = get_set()
    else:
        content = handle_args()
    
    cards = parse_cards(content)
    display_cards(cards)
    prompt_repeat(cards)


try:
    main()
except KeyboardInterrupt:
    print_exception("Program terminated by Keyboard Interrupt [Ctrl-C].")