# squares.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""The squares on a chessboard.

Define for each square it's name, file, rank, diagonals, and castling rights
lost when activity occurs on a square.

This module provides two dicts:
fen_squares, which maps square names like 'a1' to a _Square instance.
fen_square_names, which maps square number in Forsyth Edwards Notation
order to square name.

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
    """

    castling_rights_lost = ""

    def __init__(self, file, rank):
        self.name = file + rank
        self.file = file
        self.rank = rank
        self.number = constants.FILE_NAMES.index(
            file
        ) + 8 * constants.RANK_NAMES.index(rank)
        self.bit = 1 << self.number
        self.left_to_right_down_diagonal = ord(file) + ord(rank)
        self.right_to_left_down_diagonal = ord(file) - ord(rank)
        castling_rights = constants.CASTLING_RIGHTS.get(file + rank)
        if castling_rights is not None:
            self.castling_rights_lost = castling_rights

        # For square d4 the squares a4 b4 c4 and [a-h][1-3] are low squares
        # and e4 f4 g4 h4 and [a-h][5-8] are high squares.
        # Square d4 is on the a7 to g1 lrd diagonal (down from left to right).
        # Square d4 is on the h8 to a1 rld diagonal (down from right to left).
        self.low_file_attacks = None
        self.high_file_attacks = None
        self.low_rank_attacks = None
        self.high_rank_attacks = None
        self.low_lrd_attacks = None
        self.high_lrd_attacks = None
        self.low_rld_attacks = None
        self.high_rld_attacks = None
        self.highlow = constants.FILE_NAMES.index(file) + 8 * (
            7 - constants.RANK_NAMES.index(rank)
        )

        # The squares between this square and each square in the *_attacks
        # attributes.  Thus for square "a3" point_to_point["c5"] is ("b4",)
        # and point["b5"] does not exist.
        self.point_to_point = {}

    # Comparisions for deciding which of high_* and low_* is relevant when
    # deciding attacks between squares.

    def higher_than(self, other):
        """Return (self.highlow > other.highlow)."""
        return self.highlow > other.highlow

    def lower_than(self, other):
        """Return (self.highlow < other.highlow)."""
        return self.highlow < other.highlow

    # Comparisions for deciding if squares occupy the same line.

    def is_in_same_line(self, other):
        """Return True if squares occupy same line, False otherwise."""
        return id(self) != id(other) and (
            self.file == other.file
            or self.rank == other.rank
            or (
                self.left_to_right_down_diagonal
                == other.left_to_right_down_diagonal
            )
            or (
                self.right_to_left_down_diagonal
                == other.right_to_left_down_diagonal
            )
        )

    def attack_line(self, other):
        """Return squares in line if squares occupy same line or None.

        other is the square from which the attack originates, or is behind
        or in front of the attcking square.

        """
        if id(self) == id(other):
            return None
        if self.file == other.file:
            return self.low_file_attacks, self.high_file_attacks
        if self.rank == other.rank:
            return self.low_rank_attacks, self.high_rank_attacks
        if (
            self.left_to_right_down_diagonal
            == other.left_to_right_down_diagonal
        ):
            return self.low_lrd_attacks, self.high_lrd_attacks
        if (
            self.right_to_left_down_diagonal
            == other.right_to_left_down_diagonal
        ):
            return self.low_rld_attacks, self.high_rld_attacks
        return None

    def attack_lines(self):
        """Return the eight lines of attack on a square."""
        return (
            self.low_file_attacks,
            self.high_file_attacks,
            self.low_rank_attacks,
            self.high_rank_attacks,
            self.low_lrd_attacks,
            self.high_lrd_attacks,
            self.low_rld_attacks,
            self.high_rld_attacks,
        )


def _point_to_point(e, sq1, line):
    """Populate point_to_point for sq1 paired with line squares."""
    for es, sq2 in enumerate(line[e + 1 :]):
        fen_squares[sq1].point_to_point[sq2] = tuple(line[e + 1 : e + 1 + es])
        fen_squares[sq2].point_to_point[sq1] = fen_squares[sq1].point_to_point[
            sq2
        ]


def _create_squares():
    """Populate fen_squares and fen_square_names with _Square instances.

    fen_squares maps square names (a8, b8, ..., a7, ..., h2, ..., g1, h1)
    to instances of _Square.

    fen_square_names maps square numbers in FEN piece placement field
    order to square names {0: "a8", 1: "b8", ..., 63: "h1"}.

    """
    files = {}
    ranks = {}
    file_names = constants.FILE_NAMES
    rank_names = constants.RANK_NAMES
    for file_number, file in enumerate(file_names):
        files[file] = {file + r for r in rank_names}
        for rank_number, rank in enumerate(rank_names):
            fen_squares[file + rank] = _Square(file, rank)
            fen_square_names[rank_number * 8 + file_number] = file + rank
    for rank in rank_names:
        ranks[rank] = {f + rank for f in file_names}
    left_to_right = []
    right_to_left = []
    for e in range(len(file_names)):
        left_to_right.append(set())
        for x, y in zip(file_names[e:], rank_names):
            left_to_right[-1].add(x + y)
        right_to_left.append(set())
        for x, y in zip(reversed(file_names[: e + 1]), rank_names[: e + 2]):
            right_to_left[-1].add(x + y)
    for e in range(len(rank_names) - 1):
        left_to_right.append(set())
        for x, y in zip(file_names[: -e - 1], rank_names[e + 1 :]):
            left_to_right[-1].add(x + y)
        right_to_left.append(set())
        for x, y in zip(reversed(file_names[-e - 1 :]), rank_names[-e - 1 :]):
            right_to_left[-1].add(x + y)
    for v in files.values():
        line = tuple(sorted(v))
        for e, sq1 in enumerate(line):
            fen_squares[sq1].low_file_attacks = tuple(list(reversed(line[:e])))
            fen_squares[sq1].high_file_attacks = tuple(line[e + 1 :])
            _point_to_point(e, sq1, line)
    for v in ranks.values():
        line = tuple(sorted(v))
        for e, sq1 in enumerate(line):
            fen_squares[sq1].low_rank_attacks = tuple(list(reversed(line[:e])))
            fen_squares[sq1].high_rank_attacks = tuple(line[e + 1 :])
            _point_to_point(e, sq1, line)
    for v in left_to_right:
        line = tuple(sorted(v))
        for e, sq1 in enumerate(line):
            fen_squares[sq1].high_lrd_attacks = tuple(list(reversed(line[:e])))
            fen_squares[sq1].low_lrd_attacks = tuple(line[e + 1 :])
            _point_to_point(e, sq1, line)
    for v in right_to_left:
        line = tuple(sorted(v))
        for e, sq1 in enumerate(line):
            fen_squares[sq1].low_rld_attacks = tuple(list(reversed(line[:e])))
            fen_squares[sq1].high_rld_attacks = tuple(line[e + 1 :])
            _point_to_point(e, sq1, line)
    rook_moves = {}
    for f, file in files.items():
        for r, rank in ranks.items():
            rook_moves[f + r] = file.union(rank)
            rook_moves[f + r].remove(f + r)
    bishop_moves = {}
    for f in file_names:
        for r in rank_names:
            sq = f + r
            for x in left_to_right:
                if sq in x:
                    for y in right_to_left:
                        if sq in y:
                            bishop_moves[sq] = x.union(y)
                            bishop_moves[sq].remove(sq)
                            break
                    break
    knight_moves = {}
    for ef, f in enumerate(file_names):
        for er, r in enumerate(rank_names):
            sq = f + r
            knight_moves[sq] = set()
            for h, v in (
                (2, 1),
                (2, -1),
                (1, -2),
                (1, 2),
                (-2, -1),
                (-2, 1),
                (-1, 2),
                (-1, -2),
            ):
                h += ef
                v += er
                if h < 0 or h > 7 or v < 0 or v > 7:
                    continue
                knight_moves[sq].add(file_names[h] + rank_names[v])
    king_moves = {}
    for ef, f in enumerate(file_names):
        for er, r in enumerate(rank_names):
            sq = f + r
            king_moves[sq] = set()
            for h, v in (
                (1, 1),
                (1, 0),
                (1, -1),
                (0, 1),
                (-1, 1),
                (-1, 0),
                (-1, -1),
                (0, -1),
            ):
                h += ef
                v += er
                if h < 0 or h > 7 or v < 0 or v > 7:
                    continue
                king_moves[sq].add(file_names[h] + rank_names[v])
    queen_moves = {k: set() for k in rook_moves}
    for k, v in queen_moves.items():
        v.update(rook_moves[k])
        v.update(bishop_moves[k])

    # The square names on each file need to be in sorted order for pawn
    # move calculations.
    for f in files:
        files[f] = sorted(files[f])

    white_pawn_moves = {}
    for sqs in files.values():
        for e, sq in enumerate(sqs[2:]):
            white_pawn_moves[sq] = {sqs[e + 1]}
        white_pawn_moves[sqs[3]].add(sqs[1])
        en_passant_target_squares[constants.FEN_BLACK_ACTIVE][
            sqs[3], sqs[1]
        ] = sqs[2]
    black_pawn_moves = {}
    for sqs in files.values():
        sqs = list(reversed(sqs))
        for e, sq in enumerate(sqs[2:]):
            black_pawn_moves[sq] = {sqs[e + 1]}
        black_pawn_moves[sqs[3]].add(sqs[1])
        en_passant_target_squares[constants.FEN_WHITE_ACTIVE][
            sqs[3], sqs[1]
        ] = sqs[2]
    white_pawn_captures = {}
    for ef, f in enumerate(file_names):
        for er, r in enumerate(files[f][2:]):
            white_pawn_captures[r] = set()
            if ef < 7:
                white_pawn_captures[r].add(files[file_names[ef + 1]][er + 1])
            if ef > 0:
                white_pawn_captures[r].add(files[file_names[ef - 1]][er + 1])
        if ef < 7:
            en_passant_target_squares[
                constants.PGN_CAPTURE_MOVE.join(
                    (f, files[file_names[ef + 1]][5])
                )
            ] = files[file_names[ef + 1]][4]
        if ef > 0:
            en_passant_target_squares[
                constants.PGN_CAPTURE_MOVE.join(
                    (f, files[file_names[ef - 1]][5])
                )
            ] = files[file_names[ef - 1]][4]
    black_pawn_captures = {}
    for ef, f in enumerate(file_names):
        for er, r in enumerate(files[f][:-2]):
            black_pawn_captures[r] = set()
            if ef < 7:
                black_pawn_captures[r].add(files[file_names[ef + 1]][er + 1])
            if ef > 0:
                black_pawn_captures[r].add(files[file_names[ef - 1]][er + 1])
        if ef < 7:
            en_passant_target_squares[
                constants.PGN_CAPTURE_MOVE.join(
                    (f, files[file_names[ef + 1]][-6])
                )
            ] = files[file_names[ef + 1]][-5]
        if ef > 0:
            en_passant_target_squares[
                constants.PGN_CAPTURE_MOVE.join(
                    (f, files[file_names[ef - 1]][-6])
                )
            ] = files[file_names[ef - 1]][-5]

    # For testing moves in PGN.
    source_squares[constants.PGN_KING] = king_moves
    source_squares[constants.PGN_QUEEN] = queen_moves
    source_squares[constants.PGN_ROOK] = rook_moves
    source_squares[constants.PGN_BISHOP] = bishop_moves
    source_squares[constants.PGN_KNIGHT] = knight_moves
    source_squares[constants.FEN_WHITE_PAWN] = white_pawn_moves
    source_squares[constants.FEN_BLACK_PAWN] = black_pawn_moves
    source_squares[constants.FEN_WHITE_PAWN + constants.PGN_CAPTURE_MOVE] = (
        white_pawn_captures
    )
    source_squares[constants.FEN_BLACK_PAWN + constants.PGN_CAPTURE_MOVE] = (
        black_pawn_captures
    )

    # For testing if a square is attacked by a piece.
    fen_source_squares[constants.FEN_WHITE_KING] = king_moves
    fen_source_squares[constants.FEN_WHITE_QUEEN] = queen_moves
    fen_source_squares[constants.FEN_WHITE_ROOK] = rook_moves
    fen_source_squares[constants.FEN_WHITE_BISHOP] = bishop_moves
    fen_source_squares[constants.FEN_WHITE_KNIGHT] = knight_moves
    fen_source_squares[constants.FEN_WHITE_PAWN] = white_pawn_captures
    fen_source_squares[constants.FEN_BLACK_KING] = king_moves
    fen_source_squares[constants.FEN_BLACK_QUEEN] = queen_moves
    fen_source_squares[constants.FEN_BLACK_ROOK] = rook_moves
    fen_source_squares[constants.FEN_BLACK_BISHOP] = bishop_moves
    fen_source_squares[constants.FEN_BLACK_KNIGHT] = knight_moves
    fen_source_squares[constants.FEN_BLACK_PAWN] = black_pawn_captures


fen_squares = {}
fen_square_names = {}
en_passant_target_squares = {
    constants.FEN_WHITE_ACTIVE: {},
    constants.FEN_BLACK_ACTIVE: {},
}

# The squares a piece can move to from this square.
source_squares = {}

# The squares attacked by a piece on this square.
fen_source_squares = {}

_create_squares()
del _create_squares
del _point_to_point
