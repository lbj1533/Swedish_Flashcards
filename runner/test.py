from helper import *
from queue import Queue

settings = [
        ["Flip term and definition", True],
        ["Shuffle cards", True]
    ]
q = Queue()
Runner(q, settings).start()
