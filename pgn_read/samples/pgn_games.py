# pgn_games.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Report time to parse a PGN file and errors detected, and allow correction."""

from ..core.game import Game
from ._utilities import main


if __name__ == '__main__':

    main(game_class=Game, samples_title='Sample PGN File Report')
