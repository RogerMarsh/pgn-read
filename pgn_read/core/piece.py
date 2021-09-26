# piece.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Portable Game Notation (PGN) position and game navigation pieces."""
from .constants import (
    FEN_PAWNS,
    FEN_WHITE_PAWN,
    PGN_PAWN,
    FEN_WHITE_PIECES,
    FEN_WHITE_ACTIVE,
    FEN_BLACK_ACTIVE,
    FEN_WHITE_KING,
    FEN_BLACK_KING,
)
from .squares import Squares


class Piece:
    """The name of a piece, it's color and square occupied, and identity.

    The name and square or a piece may vary through a game, but color and
    identity are unchanged through a game.  The identity of a piece is defined
    as it's initial square: either from the default starting position or from
    a PGN FEN tag.

    """

    def __init__(self, name, *a):
        """Set the initial name and square of the piece, and it's identity."""
        self.name = name
        self.set_square(*a)
        self.identity = str(self.square.number)
        if self.name in FEN_WHITE_PIECES:
            self.color = FEN_WHITE_ACTIVE
        else:
            self.color = FEN_BLACK_ACTIVE

    def set_square(self, name):
        """Put the piece on a square.

        Provided for moving pieces during a game.

        """
        self.square = Squares.squares[name]

    def promoted_pawn(self, name, *a):
        """Return a new Piece instance for a promoted pawn.

        The Piece instance has the name after promotion but retains the
        identity, unique within a game, assigned to the pawn when the
        containing game was created.

        """
        assert (
            name not in FEN_PAWNS
            and name != FEN_WHITE_KING
            and name != FEN_BLACK_KING
            and self.name in FEN_PAWNS
        )
        promoted_pawn = Piece(name, *a)
        promoted_pawn.identity = self.identity
        assert self.color == promoted_pawn.color
        return promoted_pawn

    # A possible database key, so probably belongs in subclass.
    @property
    def key_str(self):
        """Concatenation of <file>, <name>, and rank.

        <file> is upper case file name for white pawn or file name otherwise.

        <name> is upper case piece name for white pawn or piece name otherwise.

        It is a plausible component of database keys for positions.

        """
        name = self.name
        if name not in FEN_PAWNS:
            return self.square.file.join((name, self.square.rank))
        if name == FEN_WHITE_PAWN:
            return self.square.file.upper().join((PGN_PAWN, self.square.rank))
        return self.square.file.join((PGN_PAWN, self.square.rank))

    def __str__(self):
        """Return concatenation of piece name and square name."""
        return self.name + self.square.name

    # Comparisions for sorting into FEN order.

    def __eq__(self, other):
        """Return True if self.square.number == other.square.number."""
        return self.square.number == other.square.number

    def __ge__(self, other):
        """Return True if self.square.number >= other.square.number."""
        return self.square.number >= other.square.number

    def __gt__(self, other):
        """Return True if self.square.number > other.square.number."""
        return self.square.number > other.square.number

    def __le__(self, other):
        """Return True if self.square.number <= other.square.number."""
        return self.square.number <= other.square.number

    def __lt__(self, other):
        """Return True if self.square.number < other.square.number."""
        return self.square.number < other.square.number
