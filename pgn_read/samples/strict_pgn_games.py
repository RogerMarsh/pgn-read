# strict_pgn_games.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Report time to parse a PGN file and errors detected, and allow correction."""

from ._utilities import main
from ..core.game import GameStrictPGN


if __name__ == '__main__':

    main(game_class=GameStrictPGN,
         samples_title='Sample Strict PGN File Report')
