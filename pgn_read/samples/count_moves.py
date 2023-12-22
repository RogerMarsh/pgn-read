# count_movess.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Report time to parse a PGN file, errors detected, and allow correction."""

from ..core.movecount_parser import MoveCount
from ._utilities_moves import main, read_pgn_count_moves


if __name__ == "__main__":
    main(
        game_class=MoveCount,
        read_function=read_pgn_count_moves,
        labels=("Game count", "Move count", "Piece count"),
        samples_title="Sample PGN File Count Tag Pairs Report",
    )
