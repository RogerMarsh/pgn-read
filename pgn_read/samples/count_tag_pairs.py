# count_tag_pairs.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Report time to parse a PGN file, errors detected, and allow correction."""

from ..core.tagpair_parser import TagPairGame
from ._utilities_tagpair import main, read_pgn_count_tag_pairs


if __name__ == "__main__":
    main(
        game_class=TagPairGame,
        read_function=read_pgn_count_tag_pairs,
        labels=("Game count", "Tag pair count"),
        samples_title="Sample PGN File Count Tag Pairs Report",
    )
