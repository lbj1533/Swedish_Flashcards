
'''
Todo:
fix bug: why is parse_cards() passed content as a list instead of as a string
have helper functions inside another file
add another script that handles set metadata in general especially score
add score for round
'''

import time, sys, random

#define globals
OS = None

'''
Function to check the OS, was running into issues with colorama
assumes either windows or macos
'''
def get_OS():
    global OS
    # handles which OS this program is being used on
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
    # if used incorrectly as a command line tool
    if len(sys.argv) > 2:
        print_exception("Usage: python Swedish\\flashcards\\flashcards.py \"filename\"")
        quit()

    # if used correctly as a command line tool
    elif len(sys.argv) == 2:
        global OS
        filename = sys.argv[1]

        #determine OS dependent file system
        filename = handle_file_system(filename)
        
        return [rec_open_file(filename, quit), filename]

    # if used as a script
    elif len(sys.argv) == 1:
        return False

'''
Function to alter the settings of the flashcard studier
takes in settings
returns settings
assumes all settings are boolean values
'''
def display_settings(settings):
    
    # ask if user wants to view settings
    if handle_boolean_input("View Settings?"):
        print_settings(settings)
    else:
        return settings
    
    # ask if user wants to change settings
    if handle_boolean_input("Make Changes?"):
        
        # ask which setting to change
        setting = handle_integer_input("Select a setting to change.", 1, len(settings)+1)-1
        # flip true to false and false to true
        settings[setting][1] = not settings[setting][1]
        print(f"Setting \"{settings[setting][0]}\" changed to {settings[setting][1]}.")
    
    # loop
    return display_settings(settings)

'''
Function to return appropriate filename based off of OS
assumes either on windows or macos
'''
def handle_file_system(filename):
    # determine OS dependent file system
    if OS == "windows":
        filename = "Swedish\\flashcards\\" + filename + ".txt"
    elif OS == "macos":
        filename = "Swedish/flashcards/" + filename + ".txt"
    return filename

'''
Function to open a file and recursively repeat an inputted function
takes a filepath and a function
function is what to do when filename is not found
assumes function is valid
'''
def rec_open_file(filename, function):
    # ISSUE LIES IN THIS FUNCTION: RETURNS LIST INSTEAD OF STRING WHEN FILENAME IS FIRST ENTERED WRONG AND THEN RIGHT
    try:
        # try to open file and parse it
        with open(filename, "r", encoding='utf-8') as file:
            return parse_file(file)
    except FileNotFoundError:
        print_exception(f"File {filename} not found.")
        return function()

'''
Function to read in the set of cards from a .txt file
Returns a string containing the whole text file
Asks for input
Assumptions: entire file can be read in one string object, encoding is utf-8
'''
def get_set():
    filename = input("Enter the set to study, do not include the .txt extension: ")
    global OS
    
    # determine appropriate filename
    filename = handle_file_system(filename)

    # open file and recursively repeat if filename not found
    content = rec_open_file(filename, get_set)
    
    return [content, filename]

'''
Function to parse a string from the passed file
takes in a file
'''
def parse_file(file):
    
    # read file line by line
    lines = file.readlines()
    
    # do not read blank lines or lines that start with #
    content = [line for line in lines if (line.strip() != '' and not line.strip().startswith("#"))]
    
    content = "".join(content)

    # return valid lines
    return content
    
'''
Function to parse the cards from the string read in
returns a list of 2-lists, the cards
Assumes formatting is correct
'''
def parse_cards(content):
    
    # split content by lines
    content = content.split("\n")[:-1] # [:-1] needed to avoid blank space
    cards = []
    
    # split lines into 2-lists, and add them to cards list
    for pair in content:
        pair = pair.split(": ")
        cards.append(pair)
    return cards

'''
Function to run through the cards, displaying them for studying
takes in cards and returns nothing
Assumes ANSI codes will clear the screen, and that cards have length 2, and that whitespace is correct
'''
def display_cards(cards, score, filename):
    
    #reads settings and determines term and definition
    global settings
    if settings[0][1]:
        term = 1
        definition = 0
    else:
        term = 0
        definition = 1
    
    # shuffles cards if need be
    if settings[1][1]:
        random.shuffle(cards)
    wrong_answers = []

    
    # goes through all cards
    for card in cards:
        try: attempt = input("\r" + card[term] + "\n")
        except IndexError: print_exception("Index error: card: " + str(card))
        # if wrong
        if not attempt == card[definition]:
            wrong_answers.append(card)
            att2 = ""
            
            # continue to ask until it is right
            while att2 != card[definition]:
                print(f"Type the correct answer: {card[definition]} ", end = "")
                att2 = input()
                if att2 != card[definition]:
                    # clears line and resets cursor
                    print("\033[F\033[K", end="")


        print("\033[2J") #clears the screen
    
    # runs through wrong answers as above
    if len(wrong_answers) > 0: 
        print("Wrong answers:")
        time.sleep(2)
        display_cards(wrong_answers, calc_last_score(len(wrong_answers), len(cards)), filename)

    # handles score
    if len(wrong_answers) == 0:
        score = calc_last_score(len(wrong_answers), len(cards))
        print(f"Score: {score}%")
        write_last_score_to_file(score, filename)

'''
Function to calculate last score from # wrong vs # total.
'''
def calc_last_score(num_wrong, num_total):
    return round((num_total-num_wrong)/num_total * 100)



'''
Function to write the last score to the set file
takes score
'''
def write_last_score_to_file(score, filename):
    with open (filename, 'r') as file:
        oc = file.readlines()[1:]
        oc = "".join(oc)
    with open(filename, "w") as file:
        scoreline = f"# Score: {score}"
        file.write(scoreline + "\n" + oc)

'''
Prompts the user to repeat the last set studied
Takes in previous set, returns nothing
Asks for input
Assumes last set was valid, and that the input is either y or n
'''
def prompt_repeat(cards):
    # asks if user wants to repeat indefinitely
    while True:
        repeat = handle_boolean_input("Repeat?")
        display_cards(cards) if repeat else quit()
        

'''
Function to print exceptions
Takes in message, returns nothing
assumes ansi codes work
'''
def print_exception(message):
    # ansi codes to make it red and then reset color
    # avoids using external libraries
    print("\033[31m\n" + message + "\n\033[0m")

'''
Function to handle all Y/N input
Takes in message, returns boolean
'''
def handle_boolean_input(message):
    # takes input from crafted message
    inp = input(f"{message} [Y/N] ")
    
    # determines true or false, or other
    if inp in ["Y","y"]:
        return True
    elif inp in ["N","n"]:
        return False
    else:
        print_exception("Enter Y or N.")
        # recursively repeats until Y or N is entered
        return handle_boolean_input(message)
    
'''
Function to handle integer input
Takes in a message, a lower bound (inclusive) and a upper bound (exclusive)
Returns integer inserted
'''
def handle_integer_input(message, lower_bound, upper_bound):
    # takes input from crafted message
    inp = int(input(f"{message} [{str(lower_bound)} to {str(upper_bound-1)}] "))
    # checks type is integer and that it is within bounds
    if type(inp) != isinstance(inp, int) and inp >= lower_bound and inp <= upper_bound-1:
        return int(inp)
    else:
        print_exception(f"Enter valid input between {lower_bound} and {upper_bound-1}.")
        # recursively repeats until valid input is entered
        return handle_integer_input(message, upper_bound, lower_bound)
    
'''
Function to print the settings menu
Takes in a list of 2 lists and prints them in an organized manner
Assumes settings are a list of 2 lists
'''
def print_settings(message):
    # prints the settings nicely
    for i,setting in enumerate(message):
        print(f"{i+1}. {setting[0]} : {setting[1]}")


'''
Main function to run program
'''
def main():
    # define settings as global
    global settings
    settings = [
        ["Flip term and definition", True],
        ["Shuffle cards", False]
    ]

    # define OS here
    OS = get_OS()

    # display and return settings
    settings = display_settings(settings)

    # handle if being used in command line or not
    if not handle_args(): #if not being used in command line
        content_filename = get_set()
        content = content_filename[0]
        filename = content_filename[1]
    else: # if being used in command line
        content_filename = handle_args()
        content = content_filename[0]
        filename = content_filename[1]

    
    
    # parse and display cards, repeat with user approval
    cards = parse_cards(content)
    display_cards(cards, 0, filename)
    prompt_repeat(cards)


# ctrl-c exception handling
try:
    main()
except KeyboardInterrupt:
    print_exception("Program terminated by Keyboard Interrupt [Ctrl-C].")