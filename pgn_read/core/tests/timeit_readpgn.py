# timeit_readpgn.py
# Copyright 2024 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Time several ways of reading a file and counting characters found.

Get a baseline, time and character count, then try a variety of ways to read
a file so the last text in each block is a PGN Tag Pair if possible.

The important condition is a PGN Tag Pair does not start in one block and
finish in the next.

A PGN Tag Pair is supposed to be in a line by itself so reading to a
newline is reasonable, but using a regular expression to find the last
'[<name>"<value>"]' does not take much longer compared with the time
needed too fully parse the games.

"""
import tkinter.filedialog
import re

CHARS = 10000000
STEP = 1000
endtag = re.compile(r"]")
tagpair = re.compile(r'\[\s*[A-Za-z0-9_]+\s*"(?:[^\\"]|\\.)*"\s*\]')


def block():
    """Print count of characters read.

    Text is read from file in fixed length blocks.

    """
    count = 0
    with open(pgn, mode="r", encoding="iso-8859-1") as file:
        while True:
            text = file.read(CHARS)
            if not text:
                break
            count += len(text)
    print(count)


def warm():
    """Do initial pass through file by calling block().

    The following pass, calling block() directly, is then done after a
    pass through the file, like the rest.

    """
    block()


def eol():
    """Print count of characters read.

    Text is read from file in fixed length blocks plus one readline to
    terminate the block on a newline.

    """
    count = 0
    with open(pgn, mode="r", encoding="iso-8859-1") as file:
        while True:
            text = file.read(CHARS) + file.readline()
            if not text:
                break
            count += len(text)
    print(count)


def lines():
    """Print count of characters read.

    Text is read from file by readlines quoting a fixed size.

    """
    count = 0
    with open(pgn, mode="r", encoding="iso-8859-1") as file:
        while True:
            text = "".join(file.readlines(CHARS))
            if not text:
                break
            count += len(text)
    print(count)


def right():
    """Print count of characters read and find last ']' in each block.

    Text is read from file in fixed length blocks.

    """
    count = 0
    with open(pgn, mode="r", encoding="iso-8859-1") as file:
        while True:
            text = file.read(CHARS)
            if not text:
                break
            count += len(text)
            step = STEP
            match_ = None
            while True:
                for found in endtag.finditer(text[-step:]):
                    match_ = found
                if match_:
                    textpos = match_.start() - step
                    if text[textpos - 1 : textpos] != "\\":
                        break
                elif len(text) < step:
                    break
                step += step
    print(count)


def tag():
    """Print count of characters read and find last PGN tag in each block.

    Text is read from file in fixed length blocks.

    """
    count = 0
    with open(pgn, mode="r", encoding="iso-8859-1") as file:
        while True:
            text = file.read(CHARS)
            if not text:
                break
            count += len(text)
            step = STEP
            match_ = None
            while True:
                for found in tagpair.finditer(text[-step:]):
                    match_ = found
                if match_ or len(text) < step:
                    break
                step += step
    print(count)


def read():
    """Print count of characters read and yield text ending with PGN tag.

    Text is read from file in fixed length blocks.

    """
    count = 0
    tail = ""
    with open(pgn, mode="r", encoding="iso-8859-1") as file:
        while True:
            text = file.read(CHARS)
            if not text:
                yield tail
                break
            count += len(text)
            step = STEP
            match_ = None
            while True:
                for found in tagpair.finditer(text[-step:]):
                    match_ = found
                if match_ or len(text) < step:
                    break
                step += step
            if match_ is None:
                tail += text
                continue
            end = match_.end() - step
            tail += text[:end]
            text = text[end:]
            yield tail
            tail = text
    print(count, "read")


def parsestub():
    """Print count of characters read via read() method."""
    count = 0
    for text in read():
        count += len(text)
    print(count, "parsestub")


if __name__ == "__main__":
    import timeit

    pgn = tkinter.filedialog.askopenfilename()
    if pgn:
        print("Warm")
        print(
            timeit.timeit(
                "warm()", setup="from __main__ import warm", number=1
            )
        )
        print("Block")
        print(
            timeit.timeit(
                "block()", setup="from __main__ import block", number=1
            )
        )
        print("Lines")
        print(
            timeit.timeit(
                "lines()", setup="from __main__ import lines", number=1
            )
        )
        print("Eol")
        print(
            timeit.timeit("eol()", setup="from __main__ import eol", number=1)
        )
        print("Right")
        print(
            timeit.timeit(
                "right()", setup="from __main__ import right", number=1
            )
        )
        print("Tag")
        print(
            timeit.timeit("tag()", setup="from __main__ import tag", number=1)
        )
        print("Parsestub")
        print(
            timeit.timeit(
                "parsestub()", setup="from __main__ import parsestub", number=1
            )
        )
