# ignore_case_pgn_games.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Report time to parse a PGN file and errors detected, and allow correction."""

from ._utilities import main
from ..core.game import GameIgnoreCasePGN


if __name__ == '__main__':

    main(game_class=GameIgnoreCasePGN,
         samples_title='Sample Ignore Case PGN File Report')
