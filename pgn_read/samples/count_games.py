# count_games.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Report time to parse a PGN file, errors detected, and allow correction."""

from ..core.tagpair_parser import GameCount
from ._utilities_tagpair import main, read_pgn_count_games


if __name__ == "__main__":
    main(
        game_class=GameCount,
        read_function=read_pgn_count_games,
        labels=("Game count",),
        samples_title="Sample PGN File Count Games Report",
    )
