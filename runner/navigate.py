from pathlib import Path
from helper import *

def list_files(directory="."):
    path = Path(directory)
    files = []
    for file in path.rglob("*"):
        if file.is_file():
            files.append(str(file))
    return files

def main():
    dir = ".\\..\\Swedish"
    PrintHandler.print_list(list_files(dir))
try:
    main()
except KeyboardInterrupt:
    PrintHandler.print_exception("Program terminated by Keyboard Interrupt [Ctrl-C].")
