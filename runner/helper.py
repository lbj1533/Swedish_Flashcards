import sys, time, random

class OSHandler:
    def __init__(self):
        pass

    def get_OS():
        """
        Determines the operating system.
        Returns 'windows' if running on Windows, otherwise returns 'macos'.
        """
        if sys.platform.startswith('win'):
            OS = "windows"
        else:
            OS = "macos"
        return OS
    
class FileHandler:
    def __init__(self):
        pass

    def get_set():
        """
        Prompts the user to enter the set to study.
        Returns the file content and filename.
        """
        while True:
            filename = input("Enter the set to study, do not include the .txt extension: ")
            filename = FileHandler.handle_file_system(filename)
            content = FileHandler.rec_open_file(filename)
            if content:
                return [content, filename]
    
    def handle_args():
        """
        Handles command-line arguments.
        Returns a list with file content and filename if a valid argument is provided, otherwise returns False.
        """
        if len(sys.argv) > 2:
            PrintHandler.print_exception("Usage: python Swedish\\flashcards\\flashcards.py \"filename\"")
            quit()
        elif len(sys.argv) == 2:
            filename = sys.argv[1]
            filename = FileHandler.handle_file_system(filename)
            return [FileHandler.rec_open_file(filename), filename]
        elif len(sys.argv) == 1:
            return False
        
    def handle_file_system(filename):
        """
        Modifies the filename based on the operating system.
        Returns the modified filename.
        """
        OS = OSHandler.get_OS()
        if OS == "windows":
            filename = "Swedish\\flashcards\\" + filename + ".txt"
        elif OS == "macos":
            filename = "Swedish/flashcards/" + filename + ".txt"
        return filename
    
    def rec_open_file(filename):
        """
        Recursively attempts to open a file until successful.
        Returns the parsed content of the file or None if not found.
        """
        try:
            with open(filename, "r", encoding='utf-8') as file:
                parsed_string = FileHandler.parse_file(file)
                if isinstance(parsed_string, str):
                    return parsed_string
                else:
                    raise TypeError("Parsed content is not a string.")
        except (FileNotFoundError, TypeError) as e:
            PrintHandler.print_exception(f"Error: {str(e)}")
            return None
    
    def parse_file(file):
        """
        Parses the content of a file, ignoring empty lines and comments.
        Returns the content as a single string.
        """
        lines = file.readlines()
        content = [line for line in lines if (line.strip() != '' and not line.strip().startswith("#"))]
        content = "".join(content)
        return content
    
class CardHandler:
    
    def parse_cards(content):
        """
        Parses the cards from the content string.
        Returns a list of card pairs.
        """
        content = content.split("\n")
        if content[-1] == "": content = content[:-1]
        cards = []
        for pair in content:
            pair = pair.split(": ")
            cards.append(pair)
        return cards
    
    def display_cards(cards, attempt_number, filename, settings):
        """
        Displays the cards for studying and handles user input.
        Recursively displays wrong answers.
        """
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
            try:
                attempt = input("\r" + card[term] + "\n")
            except IndexError:
                PrintHandler.print_exception("Index error: card: " + str(card))
            if not attempt == card[definition]:
                wrong_answers.append(card)
                att2 = ""
                while att2 != card[definition]:
                    print(f"Type the correct answer: {card[definition]} : ", end="")
                    att2 = input()
                    if att2 != card[definition]:
                        print("\033[F\033[K", end="")
            print("\033[2J")
        if len(wrong_answers) > 0: 
            print("Wrong answers:")
            time.sleep(2)
            CardHandler.display_cards(wrong_answers, attempt_number + 1, filename, settings)
        if attempt_number == 0:
            score = MathHandler.calc_last_score(len(wrong_answers), len(cards))
            print(f"Score: {score}%")
            IOHandler.write_last_score_to_file(score, filename)

class IOHandler:
    def handle_boolean_input(message):
        """
        Handles Yes/No input.
        Returns True for 'Y' or 'y', False for 'N' or 'n'.
        """
        inp = input(f"{message} [Y/N] ")
        if inp in ["Y","y"]:
            return True
        elif inp in ["N","n"]:
            return False
        else:
            PrintHandler.print_exception("Enter Y or N.")
            return IOHandler.handle_boolean_input(message)

    def handle_integer_input(message, lower_bound, upper_bound):
        """
        Handles integer input within a specified range.
        Returns the valid integer input.
        """
        try:
            inp = int(input(f"{message} [{str(lower_bound)} to {str(upper_bound-1)}] "))
            if lower_bound <= inp <= upper_bound-1:
                return inp
            else:
                raise ValueError
        except ValueError:
            PrintHandler.print_exception(f"Enter valid input between {lower_bound} and {upper_bound-1}.")
            return IOHandler.handle_integer_input(message, lower_bound, upper_bound)
        
    def write_last_score_to_file(score, filename):
        """
        Writes the last score to the file.
        """
        with open(filename, 'r') as file:
            oc = file.readlines()[1:]
            oc = "".join(oc)
        with open(filename, "w") as file:
            scoreline = f"# Score: {score}"
            file.write(scoreline + "\n" + oc)

class MenuHandler:


    def display_settings(settings):
        """
        Displays and allows modification of settings.
        Returns the modified settings.
        """
        if IOHandler.handle_boolean_input("View Settings?"):
            PrintHandler.print_settings(settings)
        else:
            return settings
        if IOHandler.handle_boolean_input("Make Changes?"):
            setting = IOHandler.handle_integer_input("Select a setting to change.", 1, len(settings)+1)-1
            settings[setting][1] = not settings[setting][1]
            print(f"Setting \"{settings[setting][0]}\" changed to {settings[setting][1]}.")
        return MenuHandler.display_settings(settings)
    
    def prompt_repeat(cards, filename, settings):
        """
        Prompts the user to repeat the last set studied.
        Repeats indefinitely until the user chooses to quit.
        """
        while True:
            repeat = IOHandler.handle_boolean_input("Repeat?")
            CardHandler.display_cards(cards, 0, filename, settings) if repeat else quit()
            
class PrintHandler:
    def print_exception(message):
        """
        Prints an exception message in red.
        """
        print("\033[31m\n" + message + "\n\033[0m")

    def print_settings(message):
        """
        Prints the settings in a formatted manner.
        """
        for i, setting in enumerate(message):
            print(f"{i+1}. {setting[0]} : {setting[1]}")

    def print_list(list):
        output = ""
        for i, item in enumerate(list):
            output += f"{i}. {item}\n"
        print(output)

class MathHandler:

    def calc_last_score(num_wrong, num_total):
        """
        Calculates the score based on the number of wrong and total cards.
        Returns the score as a percentage.
        """
        return round((num_total-num_wrong)/num_total * 100)








