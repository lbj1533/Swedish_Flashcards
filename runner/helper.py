import time, random
from pathlib import Path
from typing import List, Any, Tuple, Optional, Union
from io import TextIOWrapper
from queue import Queue  # for typing

from handlers import *


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
        """
        return str(self.basename)

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the object, useful for debugging.

        Returns:
            str: A string that represents the object with its key attributes.

        Notes:
            The string representation should ideally be a valid Python expression that could be used
            to recreate the object.
        """
        content_str = str(self.content).replace("\n", "\n\t\t")

        return (
            f"{self.__class__.__name__}\n"
            f"\t.filepath == {repr(self.filepath)},\n"
            f"\t.basename == {repr(self.basename)},\n"
            f"\t.parent == {repr(self.parent)},\n"
            f"\t.subpath == {repr(self.subpath)},\n"
            f"\t.content == \n\t\t{content_str}\n"
            f"\t.cards == {repr(self.cards)}\n"
        )

    def _open_file(
        self, filename: Path
    ) -> Optional[
        str
    ]:  # str | None: #needed Union[str,None] on mac, could investigate why
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
            with open(filename, "r", encoding="utf-8") as file:
                parsed_string = self._parse_file(file)
                if TypeHandler.check_type_is(parsed_string, str):
                    return parsed_string
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
        if not TypeHandler.check_type_is(file, TextIOWrapper):
            raise TypeError("Expected a file object of type TextIOWrapper")
        lines = file.readlines()
        content = "".join(
            [
                line
                for line in lines
                if (line.strip() != "" and not line.strip().startswith("#"))
            ]
        )
        if not TypeHandler.check_type_is(content, str):
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
        if content[-1] == "":
            content = content[:-1]
        cards = []
        for pair in content:
            pair = pair.split(": ")
            cards.append(pair)
        return cards


class Queue:
    def __init__(self, initial_list: List[File] = []) -> None:
        """
        Initializes an instance of the Queue class.

        Args:
            initial_list (List[File]): An initial list of items to enter into the queue, in a FIFO fashion.
        """
        self.list = []
        self._put_list(initial_list)

    def __sizeof__(self) -> int:
        """
        Returns the size of the queue.

        Returns:
            int: The number of items in the queue.
        """
        return len(self.list)

    def _put(self, item: File) -> None:
        """
        Adds an item to the end of the queue.

        Args:
            item (File): The item to be added to the queue.
        """
        self.list.append(item)

    def _put_list(self, items: List[File]) -> None:
        """
        Adds multiple items to the end of the queue.

        Args:
            items (List[File]): The list of items to be added to the queue.
        """
        for item in items:
            self._put(item)

    def _get(self) -> File:
        """
        Removes and returns the item at the front of the queue.

        Returns:
            File: The item at the front of the queue.
        """
        return self.list.pop(0)

    def _peek(self) -> File:
        """
        Returns the item at the front of the queue without removing it.

        Returns:
            File: The item at the front of the queue.
        """
        return self.list[0]

    def _list(self) -> List[File]:
        """
        Returns all items in the queue as a list.

        Returns:
            List[File]: The list of items in the queue.
        """
        return self.list

    def _print(self, formatting: bool = False) -> None:
        """
        Prints all items in the queue as a list

        Args:
            formatting (bool) Flag for formatting the output. True to format, False to print the list. Defaults to False.
        """
        if formatting and not self._empty():
            for i, item in enumerate(self.list):
                print(f"{i+1}. {item}")
        elif formatting and self._empty():
            print("Queue is empty.")
        else:
            print(self.list)

    def _copy(self) -> Queue[File]:
        """
        Returns a copy of the queue.

        Returns:
            Queue[File]: An identical copy of the queue
        """
        return Queue(self.list)

    def _empty(self) -> bool:
        """
        Returns whether the queue is empty or not

        Returns:
            True if empty, False if not empty
        """
        return self.__sizeof__() == 0


class Runner:
    def __init__(
        self,
        filepath: str,
        settings: List[Tuple[str, bool]] = [
            ["Flip term and definition", True],
            ["Shuffle cards", True],
        ],
    ) -> None:
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
        self.filepath = Path(filepath).resolve()
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

        return (
            f"{self.__class__.__name__}\n"
            f"\t.settings == {self.settings}\n"
            f"\t.queue == \n{self.q._list()}"
        )

    def start(self) -> None:
        """
        Helper function to start the menu and display the cards
        """
        while True:
            # get files
            # check type
            # put into queue
            add_files = self._prompt_queue()
            if not TypeHandler.check_types_are(add_files, None):
                for add_file in add_files:
                    self.q._put(add_file)
                # clear screen
                # print sets in the queue, minus the one currently loaded
                print("\033[2J")
                PrintHandler.print_notice("Sets in the queue:")
                copy_q: Queue[File] = self.q._copy()
                copy_q._get()
                copy_q._print(formatting=True)

            # if queue is empty
            # exit
            if self.q._empty():
                PrintHandler.print_notice(f"Exiting...")
                break

            # get the first file in the queue
            # print now studying
            # display cards
            # ask for repeat
            # if ctrlc, exit
            file = self.q._get()
            PrintHandler.print_notice(f"Now Studying: {file.basename}")
            try:
                self._display_cards(file.cards, 0, file.filepath, self.settings)
                self._prompt_repeat(file.cards, file.filepath, self.settings)
            except KeyboardInterrupt:
                PrintHandler.print_notice("Exiting...")
                quit()

    def _display_cards(
        self,
        cards: List[List[str]],
        attempt_number: int,
        filename: Path,
        settings: List[Tuple[str, bool]],
    ) -> None:
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
                    PrintHandler.print_notice(
                        f"Type the correct answer: {card[definition]} : ", end=""
                    )
                    att2 = input()
                    if att2 != card[definition]:
                        print("\033[F\033[K", end="")
            print("\033[2J")
        if len(wrong_answers) > 0:
            PrintHandler.print_notice("Wrong answers:")
            time.sleep(2)
            CardHandler.display_cards(
                wrong_answers, attempt_number + 1, filename, settings
            )
        if attempt_number == 0:
            score = MathHandler.calc_last_score(len(wrong_answers), len(cards))
            PrintHandler.print_notice(f"Score: {score}%")
            IOHandler.write_last_score_to_file(score, filename)

    def _prompt_repeat(
        self, cards: List[List[str]], filename: Path, settings: List[Tuple[str, bool]]
    ) -> None:
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
            if repeat:
                self._display_cards(cards, 0, filename, settings)
            else:
                break

    def _prompt_queue(self) -> List[File]:
        """
        Prompts the user to fill to queue

        Returns:
            set_list (List[File]): A list of files to be put into the queue.
        """
        set_list: List[File] = []
        while True:
            if not self.q._empty():
                PrintHandler.print_notice("Here are the sets in the Queue:")
                self.q._print(formatting=True)
            set_to_add = self._choose_file()
            if set_to_add != None:
                set_list.append(set_to_add)
            else:
                return set_list

    def _list_files(self) -> List[File]:
        """
        Recursively list all files in the Runner's filepath

        Args:
            directory (str): The directory to search.

        Returns:
            list: A list of file paths.
        """
        path = self.filepath
        files = []
        for file in path.rglob("*"):
            if file.is_file():
                files.append(File(file))
        return sorted(files, key=lambda file: file.filepath)

    def _choose_file(self) -> Optional[File]:
        """
        Prompts the user to choose a file to study from a directory.

        Args:
            directory (str): The directory to search for files.

        Returns:
            str: The path to the selected file.
        """
        files: List[File] = self._list_files()
        print("\033[2J")
        self._print_list(files)
        selection = IOHandler.handle_choose_input(
            "Choose file to add to the queue.", 1, len(files) + 1, "Q"
        )
        return None if selection == None else files[selection - 1]

    def _print_list(self, any_list: List[Any]) -> None:
        """
        Prints the items in a list with a numbered format.

        Args:
            any_list (list): The list of items to print.

        Has special formatting for List[File] types
        """
        output = ""
        for i, item in enumerate(any_list):
            if TypeHandler.check_types_are(any_list, File):
                output += f"{i+1}. {item.subpath}\n"
            else:
                output += f"{i+1}. {item}\n"
        print(output, end="")
