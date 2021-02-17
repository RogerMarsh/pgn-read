# squares.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""The squares on a chessboard: defining for each square it's name, file, rank,
diagonals, and castling rights lost when activity occurs on a square.

This module provides an instance of the class Squares.

"""
from . import constants


class _Square:
    """Name, file, rank, diagonals, and castling rights, attached to a square.

    Castling rights are those lost when activity occurs on square.  On most
    squares activity causes no loss, but for a1, e1, h1, a8, e8, and h8, one or
    two of 'KQkq' are lost if they are held.

    Squares compare equal if they are not identical and occupy the same file,
    rank, left-to-right-down diagonal, or right-to-left-down diagonal.

    The __eq__ method is intended to assist testing if a piece on one square
    attacks another square in the same line.  A piece does not attack the
    square currently occupied.  A square is attacked if the squares on the line
    between the two squares are empty.

    Each square has a number and a bit value, a8 is (0, 1 << (63 - 63) and h1
    is (63, 1 << (63 - 0).  The number is used to sort the pieces on the board
    into FEN string order.  The bit value can be used as part of position key
    generation for databases: perhaps bit string concatenated with piece names
    in bit order.  Bit values should allow the bit string to be read left to
    right in FEN order but the existing mapping in previous versions happens
    to read right to left.

    Instances of this class should be accessed via the Squares class.

    """
    castling_rights_lost = ''

    def __init__(self, file, rank):
        self.name = file + rank
        self.file = file
        self.rank = rank
        self.number = (constants.FILE_NAMES.index(file) +
                       8 * constants.RANK_NAMES.index(rank))
        self.bit = 1 << self.number
        self.left_to_right_down_diagonal = ord(file) + ord(rank)
        self.right_to_left_down_diagonal = ord(file) - ord(rank)
        castling_rights = constants.CASTLING_RIGHTS.get(file + rank)
        if castling_rights is not None:
            self.castling_rights_lost = castling_rights

    # Comparisions for deciding if squares occupy the same line.

    def __eq__(self, other):
        """Return True if squares occupy same line, False otherwise."""
        return (
            id(self) != id(other) and
            (self.file == other.file or
             self.rank == other.rank or
             (self.left_to_right_down_diagonal ==
              other.left_to_right_down_diagonal) or
             (self.right_to_left_down_diagonal ==
              other.right_to_left_down_diagonal)))


class Squares:
    """The squares on a chessboard."""

    def __init__(self):
        self.squares = {}
        squares = self.squares
        ranks = constants.RANK_NAMES
        for f in constants.FILE_NAMES:
            for r in ranks:
                squares[f+r] = _Square(f, r)


Squares = Squares()
