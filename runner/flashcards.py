'''
Todo:
program to check if sets are formatted correctly?
dotfile to manage metadata, would probably include a script to create sets
add average score? or rolling average?
implement folders and get rid of directory traversal vuln
'''

from helper import *

def main():
    """
    Main function to run the flashcard program.
    """
    global settings
    settings = [
        ["Flip term and definition", True],
        ["Shuffle cards", True]
    ]

    settings = MenuHandler.display_settings(settings)

    content_filename = FileHandler.handle_args() or FileHandler.get_set()
    content, filename = content_filename

    cards = CardHandler.parse_cards(content)
    CardHandler.display_cards(cards, 0, filename, settings)
    MenuHandler.prompt_repeat(cards, filename, settings)

# ctrl-c exception handling
try:
    main()
except KeyboardInterrupt:
    PrintHandler.print_exception("Program terminated by Keyboard Interrupt [Ctrl-C].")
