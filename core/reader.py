# reader.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Portable Game Notation (PGN) file reader.

List of classes

PGNReader

"""

import re

from . import constants
from .parser import PGNUpdate

re_games = re.compile(constants.SPLIT_INTO_GAMES)
    

class PGNReader(PGNUpdate):
    """Read multiple games from a PGN text input and update a database.

    Methods added:

    get_games

    Methods overridden:

    None
    
    Methods extended:

    None
    
    """

    def get_games(self, source, housekeepinghook=lambda:None):
        """Yield tuple(PGN tags, PGN movetext) for each game in source

        source - open file from which to read pgn text
        housekeepinghook - periodic callback when importing many games

        housekeepinghook introduced to commit database updates in DPT while
        code remains unchanged for other database engines

        """
        def read_pgn(source):
            pgntext = source.read(10000000)
            while len(pgntext):
                yield pgntext
                pgntext = source.read(10000000)
            yield pgntext
        
        # The last pair (tags, movetext) are probably incomplete because the
        # source.read() cannot be aligned with a game end.
        # So pick up what was left from previous get_games() call and put back
        # this call's contribution if more text is to come.
        chars = ''
        for pgntext in read_pgn(source):
            games = re_games.split(''.join((chars, pgntext)))
            if len(pgntext):
                chars = games.pop()
                if len(games):
                    chars = ''.join((games.pop(), chars))
            # Text in the first element of games is assumed to be movetext for
            # a game with no tags.  The re_games.split() call puts a '' there
            # if no such text is found.  The not-'' case should occur only for
            # the first get_games() call in a read_pgn() call if at all.
            if len(games[0]):
                self._tag_string = ''
                self._move_string = games.pop(0)
                yield True
            else:
                del games[0]
            while len(games):
                self._tag_string = games.pop(0)
                self._move_string = games.pop(0)
                yield True
            housekeepinghook()
