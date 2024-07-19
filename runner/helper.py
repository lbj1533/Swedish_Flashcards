import sys, time, random, inspect, os
from pathlib import Path
from typing import List, Type, Any, Tuple
from io import TextIOWrapper
from queue import Queue

def check_type_is(obj: Any, expected_type: Type[Any]) -> bool:
    """
    Checks if the given object is of the expected type.

    Args:
        obj (Any): The object to test.
        expected_type (Type[Any]): The type to check against.

    Returns:
        bool: True if the object is of the expected type, False otherwise.
    """
    if isinstance(obj, expected_type):
        return True
    else:
        caller_info = inspect.getframeinfo(inspect.currentframe().f_back)
        PrintHandler.print_exception(
            f"Object: `{obj}` is of incorrect type: {type(obj).__name__} != {expected_type.__name__}.\n"
            f"TypeError from {caller_info.function}() @ Line {caller_info.lineno} in {os.path.basename(caller_info.filename)}."
        )
        return False

def check_types_are(objs: List[Any], expected_types: List[Type[Any]]) -> bool:
    """
    Checks if the given objects are of the expected types.

    Args:
        objs (List[Any]): A list of objects to test.
        expected_types (List[Type[Any]]): A list of types to check against.

    Returns:
        bool: True if all objects are of the expected types, False otherwise.

    Raises:
        ValueError: If the number of types does not match the number of objects.
    """
    if len(expected_types) != len(objs):
        raise ValueError("The number of types must match the number of objects.")

    for obj, expected_type in zip(objs, expected_types):
        if not check_type_is(obj, expected_type):
            return False
    return True

def check_types_are(objects: List[Any], expected_type: Type) -> bool:
    """
    Checks that all objects in the provided list are of the specified type.

    Args:
        objects (List[Any]): A list of objects to be checked.
        expected_type (Type): The type that all objects in the list should be.

    Returns:
        bool: returns True if all elements are of the correct type, and False if they are not

    Raises:
        TypeError: If any object in the list is not of the specified type.
    """
    for obj in objects:
        if not isinstance(obj, expected_type):
            return False
    return True

class File:
    def __init__(self, filepath: str) -> None:
        """
        Initializes an instance of the class with the specified file path.

        Args:
            filepath (str): The path to the file to be processed.

        Attributes:
            filepath (Path): The path to the file.
            basename (Path): The base name of the file, extracted from the file path.
            parent (Path): The parent directory of the file.
            subpath (Path): A subpath formed by combining the parent directory with the file's base name.
            content (str): The content of the file, parsed from its contents.
            cards (List[List[str]]) The content of the file parsed into cards

        Raises:
            FileNotFoundError: If the file specified by `filepath` does not exist.
            TypeError: If the content parsed from the file is not a string.
        """
        self.filepath: Path = Path(filepath)
        self.basename: Path = Path(self.filepath.name)
        self.parent: Path = Path(self.filepath.parent.name)
        self.subpath: Path = Path(self.parent / self.basename)
        self.content: str = self._open_file(filepath)
        self.cards: List[List[str]] = self._parse_cards(self.content)

    def __str__(self) -> str:
        """
        Provides a human-readable string representation of the object.

        Returns:
            str: A formatted string that represents the object.
        
        Notes:
            This method currently returns the same value as `__repr__()`.
        """
        return self.__repr__()

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the object, useful for debugging.

        Returns:
            str: A string that represents the object with its key attributes.

        Notes:
            The string representation should ideally be a valid Python expression that could be used 
            to recreate the object.
        """
        content_str = str(self.content).replace("\n","\n\t\t")
        
        return (f"{self.__class__.__name__}\n"
                f"\t.filepath == {repr(self.filepath)},\n"
                f"\t.basename == {repr(self.basename)},\n"
                f"\t.parent == {repr(self.parent)},\n"
                f"\t.subpath == {repr(self.subpath)},\n"
                f"\t.content == \n\t\t{content_str}\n"
                f"\t.cards == {repr(self.cards)}\n"
        )
                

    def _open_file(self, filename: Path) -> str | None:
        """
        Attempts to open a file and return its content.

        Args:
            filename (Path): The path to the file.

        Returns:
            str or None: The parsed content of the file or None if not found.

        Raises:
            FileNotFoundError: If the file is not found.
            TypeError: If the parsed content is not a string.
        """
        try:
            with open(filename, "r", encoding='utf-8') as file:
                parsed_string = self._parse_file(file)
                if check_type_is(parsed_string, str):
                    return parsed_string
                else:
                    raise TypeError("Parsed content is not a string.")
        except (FileNotFoundError, TypeError) as e:
            PrintHandler.print_exception(f"Error: {str(e)}")
            return None

    def _parse_file(self, file: TextIOWrapper) -> str:
        """
        Parses the content of a file, ignoring empty lines and comments.

        Args:
            file (TextIOWrapper): The file object.

        Returns:
            str: The content as a single string.

        Raises:
            TypeError: If the file argument is not of type TextIOWrapper.
        """
        if not check_type_is(file, TextIOWrapper):
            raise TypeError("Expected a file object of type TextIOWrapper")
        lines = file.readlines()
        content = "".join([line for line in lines if (line.strip() != '' and not line.strip().startswith("#"))])
        if not check_type_is(content, str):
            raise TypeError("Parsed content is not a string.")
        return content
    
    def _parse_cards(self, content):
        """
        Parses the cards from the content string.

        Args:
            content (str): The content string with cards.

        Returns:
            list: A list of length 2 lists of strings.
        """
        content = content.split("\n")
        if content[-1] == "": content = content[:-1]
        cards = []
        for pair in content:
            pair = pair.split(": ")
            cards.append(pair)
        return cards

class Runner:
    def __init__(self, q: Queue[File], settings: List[Tuple[str, bool]]) -> None:
        """
        Initializes an instance of the class with the specified file path.

        Args:
            current_set (File): The file object whose cards are to be processed.
            settings (List[List[str, bool]]): Settings for the displaying of cards.

        Attributes:
            current_set (File): Stores the file object with the card data.
            settings (List[Tuple[str, bool]]): Stores the settings for how cards should be displayed.

        Raises:
            ValueError: If the settings list is empty or not properly formatted.
        """
        self.q: Queue[File] = Queue()
        self.settings: List[Tuple[str, bool]] = settings

    def __str__(self) -> str:
        """
        Provides a human-readable string representation of the object.

        Returns:
            str: A formatted string that represents the object.
        
        Notes:
            This method currently returns the same value as `__repr__()`.
        """
        return self.__repr__()

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the object, useful for debugging.

        Returns:
            str: A string that represents the object with its key attributes.

        Notes:
            The string representation should ideally be a valid Python expression that could be used 
            to recreate the object.
        """
       
        return (f"{self.__class__.__name__}\n"
                f"\t.settings == {self.settings}\n"
                f"\t.queue == \n{self._print_queue(self.q)}"
        )
    
    def start(self):
        """
        Helper function to start the menu and display the cards
        """
        while True:
            add_file = self._prompt_queue(self.q)
            if add_file != None: self.q.put(add_file)
            self._print_queue(self.q)
            if not self.q.empty():
                file = self.q.get(timeout=1)
                print(f"Studying: set {file.basename}")
                self._display_cards(file.cards, 0, file.filepath, self.settings)
                self._prompt_repeat(file.cards, file.filepath, self.settings)
            else:
                print(f"Exiting...")
                break;

    def _display_cards(self, cards:List[List[str]], attempt_number:int, filename:Path, settings:List[Tuple[str,bool]]) -> None:
        """
        Displays the cards for studying and handles user input.

        Args:
            cards (list): The list of card pairs.
            attempt_number (int): The current attempt number.
            filename (str): The filename of the card set.
            settings (List[Tuple[str,bool]]): The list of settings.

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
        
    def _prompt_repeat(self, cards:List[List[str]], filename:Path, settings:List[Tuple[str,bool]]) -> None:
        """
        Prompts the user to repeat the last set studied.

        Args:
            cards (list): The list of card pairs.
            filename (str): The filename of the card set.
            settings (list): The list of settings.

        Repeats indefinitely until the user chooses to quit.
        """
        while True:
            repeat = IOHandler.handle_boolean_input("Repeat set?")
            if repeat: self._display_cards(cards, 0, filename, settings)
            else: break

    def _prompt_queue(self, q:Queue[File]) -> File:
        """
        Prompts the user to fill to queue

        Args:
            q (Queue[File]): The queue of files.
        """
        print("Here are the items in the Queue:")
        self._print_queue(q)
        if IOHandler.handle_boolean_input("Would you like to add more?"):
            return self._choose_file()

    def _print_queue(self, q:Queue[File]) -> None:
        """
        Prints each element of the queue
        """
        if q.empty(): print("Queue is empty.")
        else:
            temp_list: List[File] = []
            while not q.empty():
                item: File = q.get()
                temp_list.append(item)
            for item in temp_list: print(item.basename)
            for item in temp_list: q.put(item)

    def _list_files(self, directory:str) -> List[File]:
        """
        Recursively list all files in the given directory.

        Args:
            directory (str): The directory to search.

        Returns:
            list: A list of file paths.
        """
        path = Path(directory)
        files = []
        for file in path.rglob("*"):
            if file.is_file():
                files.append(File(file))
        return files
    
    def _choose_file(self, directory:str = "Swedish/flashcards") -> File:
        """
        Prompts the user to choose a file to study from a directory.

        Args:
            directory (str): The directory to search for files.

        Returns:
            str: The path to the selected file.
        """
        files:List[File] = self._list_files(directory)
        self._print_list(files)
        selection = IOHandler.handle_integer_input("Choose file to add to the queue (pick 0 to exit): ", 0, len(files)+1)
        if selection == 0: raise NotImplementedError
        return files[selection-1]
    
    def _print_list(self, any_list:List[Any]) -> None:
        """
        Prints the items in a list with a numbered format.

        Args:
            any_list (list): The list of items to print.

        Has special formatting for List[File] types
        """
        output = ""
        for i, item in enumerate(any_list):
            if check_types_are(any_list, File):
                output += f"{i+1}. {item.basename}\n"
            else:
                output += f"{i+1}. {item}\n"
        print(output)

class OSHandler:

    def get_OS():
        """
        Determines the operating system.

        Returns:
            str: 'windows' if running on Windows, otherwise 'macos'.
        """
        if sys.platform.startswith('win'):
            OS = "windows"
        else:
            OS = "macos"
        return OS
    
class FileHandler:
    
    def file_exists(filename:Path):
        """
        Checks if a file exists.

        Args:
            filename (str or Path): The path to the file.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return filename.exists()

    def list_files(directory="."):
        """
        Recursively list all files in the given directory.

        Args:
            directory (str): The directory to search. Defaults to the current directory.

        Returns:
            list: A list of file paths.
        """
        if directory is None: raise ValueError("The directory is None")
        path = Path(directory)
        files = []
        for file in path.rglob("*"):
            if file.is_file():
                files.append(str(file))
        return files
        
    def get_set():
        """
        Prompts the user to enter the set to study.

        Returns:
            list: The file content and filename.
        """
        while True:
            filename = input("Enter the set to study, do not include the .txt extension: ")
            filename = FileHandler.handle_file_system(filename)
            content = FileHandler.open_file(filename)
            if content:
                return [content, filename]
    
    def handle_args():
        """
        Handles command-line arguments.

        Returns:
            list or bool: A list with file content and filename if a valid argument is provided, otherwise returns False.
        """
        if len(sys.argv) > 2:
            PrintHandler.print_exception("Usage: python Swedish\\flashcards\\flashcards.py \"filename\"")
            quit()
        elif len(sys.argv) == 2:
            filename = sys.argv[1]
            filename = FileHandler.handle_file_system(filename)
            return [FileHandler.open_file(filename), filename]
        elif len(sys.argv) == 1:
            return False
        
    def convert_to_windows(filename):
        """
        Converts filename to use Windows convention.

        Args:
            filename (str): The original filename.

        Returns:
            str: The filename with Windows path convention.
        """
        return filename.replace("/","\\")
    
    def convert_to_macos(filename):
        """
        Converts filename to use macOS or Linux convention.

        Args:
            filename (str): The original filename.

        Returns:
            str: The filename with macOS/Linux path convention.
        """
        return filename.replace("\\","/")
    
    def convert_to_current_OS(filename):
        """
        Converts filename to use the current OS's filepath convention.

        Args:
            filename (str): The original filename.

        Returns:
            str: The filename with current OS path convention.
        """
        OS = OSHandler.get_OS()
        if OS == "windows": return FileHandler.convert_to_windows(filename)
        elif OS == "macos": return FileHandler.convert_to_macos(filename)
        
    def handle_file_system(filename):
        """
        Modifies the filename based on the operating system.

        Args:
            filename (str): The original filename.

        Returns:
            str: The modified filename.
        """
        OS = OSHandler.get_OS()
        if OS == "windows":
            filename = "Swedish\\flashcards\\" + filename + ".txt"
        elif OS == "macos":
            filename = "Swedish/flashcards/" + filename + ".txt"
        return filename
    
    def open_file(filename):
        """
        Attempts to open a file.

        Args:
            filename (str): The path to the file.

        Returns:
            str or None: The parsed content of the file or None if not found.

        Raises:
            FileNotFoundError: If the file is not found.
            TypeError: If the parsed content is not a string.
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

        Args:
            file (TextIO): The file object.

        Returns:
            str: The content as a single string.
        """
        lines = file.readlines()
        content = [line for line in lines if (line.strip() != '' and not line.strip().startswith("#"))]
        content = "".join(content)
        return content
    
    def resolve_path(filepath):
        """
        Resolves the absolute path of the given filepath.

        Args:
            filepath (str or Path): The path to resolve.

        Returns:
            str: The absolute path.
        """
        return str(Path(filepath).resolve())

class CardHandler:
    
    def parse_cards(content):
        """
        Parses the cards from the content string.

        Args:
            content (str): The content string with cards.

        Returns:
            list: A list of card pairs.
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

        Args:
            cards (list): The list of card pairs.
            attempt_number (int): The current attempt number.
            filename (str): The filename of the card set.
            settings (list): The list of settings.

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

        Args:
            message (str): The message to display.

        Returns:
            bool: True for 'Y' or 'y', False for 'N' or 'n'.

        Raises:
            KeyboardInterrupt: If the user interrupts the input with Ctrl+C.
        """
        while True:
            try:
                inp = input(f"{message} [Y/N] ").strip().lower()
                if inp in ["y", "n"]:
                    return inp == "y"
                else:
                    PrintHandler.print_exception("Enter Y or N.")
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)



    def handle_integer_input(message, lower_bound, upper_bound):
        """
        Handles integer input within a specified range.

        Args:
            message (str): The message to display.
            lower_bound (int): The lower bound of the valid range (inclusive).
            upper_bound (int): The upper bound of the valid range (exclusive).

        Returns:
            int: The valid integer input.

        Raises:
            ValueError: If the input is not within the specified range.
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

        Args:
            score (int): The score to write.
            filename (str): The filename to write to.
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
        Displays the current settings and allows the user to modify them.

        Args:
            settings (list): A list of settings where each setting is a tuple with the setting name and value.

        Returns:
            list: The possibly modified settings.
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

        Args:
            cards (list): The list of card pairs.
            filename (str): The filename of the card set.
            settings (list): The list of settings.

        Repeats indefinitely until the user chooses to quit.
        """
        while True:
            repeat = IOHandler.handle_boolean_input("Repeat?")
            CardHandler.display_cards(cards, 0, filename, settings) if repeat else quit()

    def choose_file(directory):
        """
        Prompts the user to choose a file to study from a directory.

        Args:
            directory (str): The directory to search for files.

        Returns:
            str: The path to the selected file.
        """
        files = FileHandler.list_files(directory)
        PrintHandler.print_list(files)
        selection = IOHandler.handle_integer_input("Choose file to study: ", 1, len(files)+1)
        return files[selection-1]

class PrintHandler:
    def print_exception(message):
        """
        Prints exception messages.

        Args:
            exception_message (str): The exception message to print.
        """
        print("\033[31m\n" + message + "\n\033[0m")

    def print_settings(message):
        """
        Prints the settings in a formatted manner.

        Args:
            message (list): A list of settings where each setting is a tuple with the setting name and value.
        """
        for i, setting in enumerate(message):
            print(f"{i+1}. {setting[0]} : {setting[1]}")

    def print_list(list):
        """
        Prints the items in a list with a numbered format.

        Args:
            list (list): The list of items to print.
        """
        output = ""
        for i, item in enumerate(list):
            output += f"{i+1}. {item}\n"
        print(output)

class MathHandler:

    def calc_last_score(num_wrong, num_total):
        """
        Calculates the last score based on wrong answers and total cards.

        Args:
            wrongs (int): The number of wrong answers.
            total_cards (int): The total number of cards.

        Returns:
            int: The score as a percentage.
        """
        return round((num_total-num_wrong)/num_total * 100)








