# game_indicate_check.py
# Copyright 2025 Roger Marsh
# Licence: See LICENCE (BSD licence)
# Code transferred from 2025 version of game.py.

"""Portable Game Notation (PGN) position and game navigation data structures.

GameIndicateCheck extends Game by adding check indicators, '+' and '#', to
movetext from games stored on the database.

"""
from .constants import (
    FEN_WHITE_ACTIVE,
    FEN_NULL,
    FEN_WHITE_PAWN,
    FEN_BLACK_PAWN,
    FEN_WHITE_KNIGHT,
    FEN_BLACK_KNIGHT,
    PGN_CAPTURE_MOVE,
    FEN_PAWNS,
    SIDE_TO_MOVE_KING,
    PIECE_TO_KING,
    PGN_KING,
    PGN_KNIGHT,
)
from .game import Game
from .squares import (
    fen_squares,
    source_squares,
    fen_source_squares,
    en_passant_target_squares,
)


class GameIndicateCheck(Game):
    """Add check and checkmate indicators to games extracted from database.

    Append check and checkmate indicators, '+' and '#', to movetext where the
    move gives check or checkmate by overriding _append_check_indicator()
    method.

    Note the methods in this class are not needed to determine legality of a
    move.  Their purpose is to decide if a move needs a check indicator to
    comply with the Export Format defined in the PGN standard.

    """

    def _append_decorated_text(self, movetext):
        """Append movetext plus appropriate check indicator to self._text."""
        self._text.append(movetext)
        self._append_check_indicator()

    def _append_decorated_castles_text(self, movetext):
        """Append movetext plus appropriate check indicator to self._text."""
        self._text.append(movetext)
        self._append_check_indicator()

    def _append_check_indicator(self):
        """Append correct check indicator, '+' and '#', suffix to movetext.

        This method is used after the move in self._text[-1] has been applied
        to the board, but before processing the next token starts.

        '#' indicators are replaced by '+' because checkmate is not validated
        explicitly unless the move is not followed by a valid move in the game
        or variation.  This is done later, and the positions to test must be
        set here but is not implemented yet.

        """
        # The move will be legal, so is_square_attacked_by_other_side tests
        # too much.  Only need to consider direct attacks from destination
        # square of knight move, through the source and destination squares,
        # and through the square of a pawn captured en-passant.
        if self.is_check_given_by_move():
            self._text[-1] += "#" if self._is_position_checkmate() else "+"

    def _is_position_checkmate(self):
        """Return True if the side to move is checkmated."""
        piece_placement_data = self._piece_placement_data.copy()
        pieces_on_board = self._pieces_on_board
        side_to_move_king = SIDE_TO_MOVE_KING[self._active_color]
        king_square = pieces_on_board[side_to_move_king][0].square.name
        escape_squares = source_squares[PGN_KING][king_square]
        active_color = self._active_color

        # Be sure to put king back!
        del self._piece_placement_data[king_square]

        # Can king avoid check by moving?
        # Test all possible destination squares without putting king on them.
        for sqr in escape_squares:
            if sqr not in piece_placement_data:
                if not self.is_square_attacked_by_other_side(
                    sqr, active_color
                ):
                    self._piece_placement_data[king_square] = (
                        piece_placement_data[king_square]
                    )
                    return False
            elif (
                PIECE_TO_KING[piece_placement_data[sqr].name]
                != side_to_move_king
            ):
                if not self.is_square_attacked_by_other_side(
                    sqr, active_color
                ):
                    self._piece_placement_data[king_square] = (
                        piece_placement_data[king_square]
                    )
                    return False

        # Put king back.
        self._piece_placement_data[king_square] = piece_placement_data[
            king_square
        ]

        # Can side to move block the check?
        attack_lines = self._get_attacks_on_square_by_other_side(king_square)
        if len(attack_lines) > 1:
            return True
        if len(attack_lines) == 0:
            return False
        if self._legal_move_to_square_exists(
            attack_lines[0], PGN_CAPTURE_MOVE, king_square
        ):
            return False
        ptp = fen_squares[attack_lines[0]].point_to_point.get(king_square)
        if ptp is not None:
            for sqr in ptp:
                if self._legal_move_to_square_exists(sqr, "", king_square):
                    return False
            return True
        ptp = source_squares[PGN_KNIGHT].get(attack_lines[0])
        if ptp is not None:
            for sqr in ptp:
                if self._legal_move_to_square_exists(sqr, "", king_square):
                    return False
            return True
        return False

    def _get_attacks_on_square_by_other_side(self, square):
        """Return list of attacking squares.

        This method is intended for deciding if a check is checkmate, so the
        list is returned early if it's length reaches two because a single
        move cannot block checks from two squares.

        It is assumed the king cannot escape check by moving itself.

        """
        piece_placement_data = self._piece_placement_data
        active_color = self._active_color
        attacking_squares = []

        for square_list in fen_squares[square].attack_lines():
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = fen_source_squares.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                attacking_squares.append(sqr)
                if len(attacking_squares) > 1:
                    return attacking_squares
                break

        if active_color == FEN_WHITE_ACTIVE:
            knight_search = FEN_BLACK_KNIGHT
        else:
            knight_search = FEN_WHITE_KNIGHT
        square_list = fen_source_squares[knight_search]
        # pylint message C0206 'Consider iterating with .items()'.
        # Evaluating 'square_list[sqr]' is not considered frequent enough.
        # Changing to 'square_list.keys()' attracts extra C0201 message
        # 'Consider iterating dictionary directly instead of calling .keys()'.
        for sqr in square_list:
            if sqr not in piece_placement_data:
                continue
            piece = piece_placement_data[sqr]
            if piece.color == active_color:
                break
            if piece.name == knight_search:
                if square in square_list[sqr]:
                    attacking_squares.append(sqr)
                    if len(attacking_squares) > 1:
                        return attacking_squares

        return attacking_squares

    def _legal_move_to_square_exists(self, square, capture, king_square):
        """Return True if a legal move to square exists.

        This method is intended for deciding if a check is checkmate, and it
        is assumed the king cannot move.

        En-passant captures cannot block a check but they can remove a pawn
        giving check.  Test if en-passant prevents checkmate as last thing
        because it seems least likely case and the algorithm is unlike any of
        the other line and point-to-point cases.

        """
        ppd = self._piece_placement_data
        checked_king = ppd[king_square].name
        active_color = self._active_color
        for from_square, piece in ppd.copy().items():
            if piece.color != active_color:
                continue
            name = piece.name
            if name == checked_king:
                continue
            if name in FEN_PAWNS:
                name += capture
                if square in source_squares[name]:
                    if from_square not in source_squares[name][square]:
                        continue
                    ppd_to = ppd.pop(square, None)
                    ppd_from = ppd.pop(from_square)
                    ppd[square] = ppd_from
                    check = self.is_square_attacked_by_other_side(
                        king_square, active_color
                    )
                    del ppd[square]
                    if ppd_to is not None:
                        ppd[square] = ppd_to
                    ppd[from_square] = ppd_from
                    if not check:
                        return True
                continue
            if from_square in fen_source_squares[name][square]:
                if name in (FEN_WHITE_KNIGHT, FEN_BLACK_KNIGHT):
                    ppd_to = ppd.pop(square, None)
                    ppd_from = ppd.pop(from_square)
                    ppd[square] = ppd_from
                    check = self.is_square_attacked_by_other_side(
                        king_square, active_color
                    )
                    del ppd[square]
                    if ppd_to is not None:
                        ppd[square] = ppd_to
                    ppd[from_square] = ppd_from
                    if not check:
                        return True
                    continue
                ptp = fen_squares[from_square].point_to_point[square]
                for line_sq in ptp:
                    if line_sq in ppd:
                        break
                else:
                    ppd_to = ppd.pop(square, None)
                    ppd_from = ppd.pop(from_square)
                    ppd[square] = ppd_from
                    check = self.is_square_attacked_by_other_side(
                        king_square, active_color
                    )
                    del ppd[square]
                    if ppd_to is not None:
                        ppd[square] = ppd_to
                    ppd[from_square] = ppd_from
                    if not check:
                        return True
        if capture and self._en_passant_target_square != FEN_NULL:
            for k, value in en_passant_target_squares[active_color].items():
                if value != self._en_passant_target_square:
                    continue
                if k[0] != square:
                    continue
                if active_color == FEN_WHITE_ACTIVE:
                    pawn = FEN_WHITE_PAWN
                else:
                    pawn = FEN_BLACK_PAWN
                for from_square in fen_source_squares[pawn][
                    self._en_passant_target_square
                ]:
                    piece = ppd.get(from_square)
                    if piece is None:
                        continue
                    if piece.name != pawn:
                        continue
                    ppd_to = ppd.pop(square, None)
                    ppd_from = ppd.pop(from_square)
                    ppd[self._en_passant_target_square] = ppd_from
                    check = self.is_square_attacked_by_other_side(
                        king_square, active_color
                    )
                    del ppd[self._en_passant_target_square]
                    if ppd_to is not None:
                        ppd[square] = ppd_to
                    ppd[from_square] = ppd_from
                    if not check:
                        return True
        return False
