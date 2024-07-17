from helper import *



start_dir = FileHandler.convert_to_current_OS("./../Swedish/flashcards")
print("Converted directory:", start_dir)  # Debug print to check converted directory

filename = MenuHandler.choose_file(start_dir)
print("Chosen filename:", filename)  # Debug print to check chosen filename

