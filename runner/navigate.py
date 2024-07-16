
from helper import *



def main():
    dir = ".\\..\\Swedish"
    PrintHandler.print_list(FileHandler.list_files(dir))
    IOHandler.handle_integer_input("Choose file to study: ")
    
try:
    main()
except KeyboardInterrupt:
    PrintHandler.print_exception("Program terminated by Keyboard Interrupt [Ctrl-C].")
