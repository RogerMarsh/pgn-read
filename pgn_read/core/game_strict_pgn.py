# game_strict_pgn.py
# Copyright 2025 Roger Marsh
# Licence: See LICENCE (BSD licence)
# Code transferred from 2025 version of game.py.

"""Portable Game Notation (PGN) position and game navigation data structures.

Game expects Import Format PGN, which includes Export Format PGN, and allows
some transgressions which occur in real PGN files that do not stop extraction
of the moves played or given in variations (RAVs).

GameStrictPGN does not allow these transgressions.  It is a subclass of Game.

GameStrictPGN binds _strict_pgn to True.

"""
from .game import Game


class GameStrictPGN(Game):
    """Data structure of game positions derived from a PGN game score.

    Disambiguation is allowed only when necessary.

    Thus 'Nge2' is not accepted when an 'N' on 'c3' is pinned to the 'K' on
    'e1'.

    The definition of strictness may change in future if the Game class is
    modified to allow other transgressions of the PGN specification.

    The strictness is not the distinction between Import and Export Format
    described in the PGN specification.

    """

    _strict_pgn = True
