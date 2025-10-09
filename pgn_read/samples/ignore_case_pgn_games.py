# ignore_case_pgn_games.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Report time to parse a PGN file, errors detected, and allow correction."""

from ._utilities import main
from ..core.game_ignore_case_pgn import GameIgnoreCasePGN


if __name__ == "__main__":
    main(
        game_class=GameIgnoreCasePGN,
        samples_title="Sample Ignore Case PGN File Report",
    )
