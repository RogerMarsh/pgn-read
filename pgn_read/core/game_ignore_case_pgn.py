# game_ignore_case_pgn.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)
# Code transferred from 2025 version of game.py.

"""Portable Game Notation (PGN) position and game navigation data structures.

GameIgnoreCasePGN extends GameTextPGN by ignoring case where possible.  Some
things allowed in GameTextPGN are not allowed, or will give a non-intuitive
outcome, when ignoring case leads to ambiguity.  The advantage is movetext like
'B4' is accepted as a pawn move and 'bb4' is accepted as a bishop move.  The
problem is processing PGN text takes about 30% longer than the other classes
for typical game scores without variations.

GameIgnoreCasePGN uses the GameTextPGN binding for _strict_pgn.

"""
import re

from .constants import (
    FILE_NAMES,
    FEN_WHITE_ACTIVE,
    FEN_BLACK_ACTIVE,
    FEN_WHITE_PAWN,
    FEN_BLACK_PAWN,
    FEN_BLACK_BISHOP,
    IFG_CASTLES,
    IFG_PIECE_MOVE,
    IFG_PIECE_CAPTURE,
    IFG_PIECE_DESTINATION,
    IFG_PAWN_FROM_FILE,
    IFG_PAWN_TO_RANK,
    IFG_PAWN_PROMOTE_PIECE,
    IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE,
    PGN_CAPTURE_MOVE,
    PGN_O_O,
    PGN_O_O_O,
    DISAMBIGUATE_PROMOTION,
    LAN_MOVE_SEPARATOR,
    PGN_PROMOTION,
    TEXT_PROMOTION,
    TP_MOVE,
    TP_PROMOTE_TO_PIECE,
    PGN_NAMED_PIECES,
)
from .game_text_pgn import (
    GameTextPGN,
    import_format,
    text_format,
    possible_bishop_or_bpawn,
)
from .gamedata import generate_fen_for_position
from .squares import fen_source_squares

disambiguate_promotion_format = re.compile(DISAMBIGUATE_PROMOTION)
text_promotion_format = re.compile(TEXT_PROMOTION)


# GameIgnoreCasePGN uses many GameTextPGN methods without extending them.
# Where a method is extended the appropriate superclass call must often
# start it's search from GameTextPGN not GameIgnoreCasePGN.
class GameIgnoreCasePGN(GameTextPGN):
    """Data structure of game positions derived while ignoring case.

    The game score follows PGN specification principles but is assumed to
    ignore case and adopt aspects of long algebraic notation at times.

    Upper and lower case alphabetic characters are accepted as piece and file
    names in addition to what is accepted in GameTextPGN.

    Thus 'nGE2', 'o-o', and 'E8q', and so forth, are accepted as movetext.

    However 'bxc8q' will not be seen as a pawn promotion because of ambiguity
    with 'Bxc8 <Q move>': the pawn promotion must be expressed 'bxc8=q' in this
    case, denying the FIDE version of promotion.

    """

    # Defaults for GameIgnoreCasePGN instance state.
    _promotion_disambiguation_detected = False

    # Introduced so self.append_token_after_error() can process possible
    # bishop moves detected by self.append_pawn_move().
    def undo_pgn_error_notification(self):
        """Do nothing.  Subclasses should override to fit requirements.

        This method should be overridden if self.pgn_error_notification() is
        overridden and should undo whatever was done.

        """

    def _undo_append_token_and_set_error(self):
        self._state = None
        self._state_stack[-1] = self._state
        self._error_list.pop()
        self.undo_pgn_error_notification()
        self._text.pop()
        try:
            self._position_deltas.pop()
        except IndexError:
            pass

    def append_token_after_error(self, match):
        """See if match converts preceeding error token into a move.

        If the preceeding token could be a bishop or pawn move, or could be
        the start of a piece move where both source and destination square
        are given, combine match with previous token and see if a legal move
        is created.  If so undo the error and apply the move with the
        appropriate superclass method.

        Otherwise delegate to superclass to apply the token in error context.

        """
        if self._bishop_or_bpawn:
            if self._append_recovered_bishop_or_bpawn_move(match):
                if self._full_disambiguation_detected:
                    del self._full_disambiguation_detected
                self._bishop_or_bpawn = None
                return
        if self._full_disambiguation_detected:
            del self._full_disambiguation_detected
            mgl = match.group().lower()
            if text_format.match(
                LAN_MOVE_SEPARATOR.join((self._text[-1], mgl)).strip()
            ):
                if PGN_PROMOTION not in mgl:
                    pgn_match = import_format.match(
                        self._text[-1].strip() + mgl
                    )
                    if pgn_match and pgn_match.lastindex == IFG_PAWN_TO_RANK:
                        self._undo_append_token_and_set_error()
                        # Ignore method in GameTextPGN class.
                        # Pylint reports bad-super-call.
                        super(GameTextPGN, self).append_pawn_move(pgn_match)
                        return
                else:
                    mgls = mgl.split(PGN_PROMOTION, 1)
                    pgn_match = import_format.match(
                        PGN_PROMOTION.join((mgls[0], mgls[1].upper()))
                    )
                    if (
                        pgn_match
                        and pgn_match.lastindex == IFG_PAWN_PROMOTE_PIECE
                    ):
                        self._undo_append_token_and_set_error()
                        # Ignore method in GameTextPGN class.
                        # Pylint reports bad-super-call.
                        super(GameTextPGN, self).append_pawn_promote_move(
                            pgn_match
                        )
                        return
        # Ignore method in GameTextPGN class.  Pylint reports bad-super-call.
        super(GameTextPGN, self).append_token_after_error(match)

    def append_other_or_disambiguation_pgn(self, match):
        """Delegate non-promotion indicator lower case match to superclass.

        A '=[QRBNqrbn]' at start of match when already processed by peek-ahead
        is ignored.

        A match that is not also a match when converted to lower case is an
        error, even if the superclass would accept it, except when it means
        a bishop capture on ranks 1 or 8 with bishop symbol in lower case.

        Otherwise delegate to superclass.

        """
        if self._promotion_disambiguation_detected:
            del self._promotion_disambiguation_detected
            if disambiguate_promotion_format.match(match.group()):
                return
        pgn_match = text_format.match(match.group().lower())
        if pgn_match is None:
            self.append_token_and_set_error(match)
            return
        mgt = match.group()
        mgt = mgt[0] + mgt[1:].lower()
        if (
            pgn_match.lastindex == IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE
            and mgt.startswith("bx")
        ):
            bishop = import_format.match(mgt[0].upper() + mgt[1:])
            if bishop and bishop.lastindex == IFG_PIECE_DESTINATION:
                # Ignore method in GameTextPGN class.
                # Pylint reports bad-super-call.
                super(GameTextPGN, self).append_piece_move(bishop)
                return
        super().append_other_or_disambiguation_pgn(pgn_match)

    def append_castles(self, match):
        """Translate FIDE style castling to PGN and delegate to superclass.

        FIDE style castling uses zero, 0, rather than capital-o, 'O'.

        """
        group = match.group
        if len(group(IFG_CASTLES)) == 3:
            castles = PGN_O_O + group()[3:]
        else:
            castles = PGN_O_O_O + group()[5:]
        pgn_match = text_format.match(castles)
        if pgn_match is None:
            self.append_token_and_set_error(match)
            return
        super().append_castles(pgn_match)

    def append_piece_move(self, match):
        """Process match as piece move unless it fits better as a b-pawn move.

        bx[ac][1-8] is ambiguous when case is ignored.  The board state is
        examined to decide if 'b' or 'B' means bishop or pawn.  Sometimes
        the only way to decide is by taking case into account.

        """
        group = match.group
        pml = group().lower()
        piece_match = text_format.match(
            pml[0].upper()
            + pml[1:]
            + match.string[match.end() : match.end() + 10]
        )
        if (
            pml[0] in "kqrn"
            or group(IFG_PIECE_DESTINATION)[0].lower() in "defgh"
            or (
                PGN_CAPTURE_MOVE in pml
                and group(IFG_PIECE_DESTINATION)[0].lower() == "b"
            )
            or (
                PGN_CAPTURE_MOVE not in pml
                and group(IFG_PIECE_DESTINATION)[0].lower() in "ac"
            )
        ):
            if piece_match.group(IFG_PIECE_MOVE) is None:
                self.append_token_and_set_error(match)
                return
            # Ignore method in GameTextPGN class.
            # Pylint reports bad-super-call.
            super(GameTextPGN, self).append_piece_move(piece_match)
            self._bishop_or_bpawn = None
            return
        pawn_match = text_format.match(pml)
        if pawn_match and pawn_match.lastindex != IFG_PAWN_TO_RANK:
            pawn_match = None
        if group(IFG_PIECE_DESTINATION)[1] in "18":
            peek_start = match.span(match.lastindex)[-1]
            if peek_start == len(match.string):
                pawn_promotion_match = None
            elif match.string[peek_start] != PGN_PROMOTION:
                pawn_promotion_match = None
            else:
                pawn_promotion_match = text_promotion_format.match(
                    pml + match.string[peek_start : peek_start + 6].lower()
                )
                if pawn_promotion_match:
                    pawn_promotion_match = text_format.match(
                        "".join(
                            (
                                pawn_promotion_match.group(TP_MOVE),
                                pawn_promotion_match.group(
                                    TP_PROMOTE_TO_PIECE
                                ).upper(),
                            )
                        )
                    )
                    if pawn_promotion_match and (
                        pawn_promotion_match.lastindex
                        != IFG_PAWN_PROMOTE_PIECE
                    ):
                        pawn_promotion_match = None
        else:
            pawn_promotion_match = None
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                return
            self._movetext_offset = len(self._text)
        fen = generate_fen_for_position(
            self._piece_placement_data.values(),
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        )
        setup = import_format.match('[SetUp"1"]')
        fen = import_format.match(fen.join(('[FEN"', '"]')))
        bishop_move = GameTextPGN()
        bishop_move.append_start_tag(setup)
        bishop_move.append_start_tag(fen)
        bishop_move.append_piece_move(piece_match)
        if pawn_match:
            pawn_move = GameTextPGN()
            pawn_move.append_start_tag(setup)
            pawn_move.append_start_tag(fen)
            pawn_move.append_pawn_move(pawn_match)
        if pawn_promotion_match:
            pawn_promotion_move = GameTextPGN()
            pawn_promotion_move.append_start_tag(setup)
            pawn_promotion_move.append_start_tag(fen)
            pawn_promotion_move.append_pawn_promote_move(pawn_promotion_match)
        if bishop_move.state is None:
            if not (pawn_match or pawn_promotion_match):
                # Ignore method in GameTextPGN class.
                # Pylint reports bad-super-call.
                super(GameTextPGN, self).append_piece_move(piece_match)
                self._bishop_or_bpawn = None
                return
            if match[0].isupper():
                # Ignore method in GameTextPGN class.
                # Pylint reports bad-super-call.
                super(GameTextPGN, self).append_piece_move(piece_match)
                self._bishop_or_bpawn = None
                return
            # else:

            # All tests passed with this commented code.
            # However I am not convinced it is safe to collapse the
            # conditionals under 'if bishop_move.state is None:' yet,
            # nor that the original code below is sound in the new
            # more limited scope.
            # super(GameTextPGN, self).append_piece_move(piece_match)
            # self._bishop_or_bpawn = None
            # return

            # pass
        else:
            if pawn_match and pawn_match.lastindex == IFG_PAWN_TO_RANK:
                # Ignore method in GameTextPGN class.
                # Pylint reports bad-super-call.
                super(GameTextPGN, self).append_pawn_move(pawn_match)
                self._bishop_or_bpawn = None
            elif (
                pawn_promotion_match
                and pawn_promotion_match.lastindex == IFG_PAWN_PROMOTE_PIECE
            ):
                # Ignore method in GameTextPGN class.
                # Pylint reports bad-super-call.
                super(GameTextPGN, self).append_pawn_promote_move(
                    pawn_promotion_match
                )
                self._bishop_or_bpawn = None
            else:
                self.append_token_and_set_error(match)
            return

        # Following code is mostly not used at version 2.1 compared with
        # previous version.  One route above falls through to here but it
        # seems 'self.is_move_interpreted_as_piece_move(match)' always
        # evalutes True.
        # Implication might be that move is always a bishop move, never a
        # pawn move, if bishop_move.state is None in the code above.
        if self.is_move_interpreted_as_piece_move(match):
            if piece_match.group(IFG_PIECE_MOVE) is None:
                self.append_token_and_set_error(match)
                return
            # Ignore method in GameTextPGN class.
            # Pylint reports bad-super-call.
            super(GameTextPGN, self).append_piece_move(piece_match)
            self._bishop_or_bpawn = None
            return
        if match.group(IFG_PIECE_DESTINATION)[1] in "18":
            peek_start = match.span(match.lastindex)[-1]
            if peek_start == len(match.string):
                self.append_token_and_set_error(match)
            elif match.string[peek_start] != PGN_PROMOTION:
                self.append_token_and_set_error(match)
            else:
                promotion_match = text_promotion_format.match(
                    pml + match.string[peek_start : peek_start + 6].lower()
                )
                if promotion_match is None:
                    self.append_token_and_set_error(match)
                    return
                promotion_match = text_format.match(
                    "".join(
                        (
                            promotion_match.group(TP_MOVE),
                            promotion_match.group(TP_PROMOTE_TO_PIECE).upper(),
                        )
                    )
                )
                if promotion_match is None:
                    self.append_token_and_set_error(match)
                    return
                # Ignore method in GameTextPGN class.
                # Pylint reports bad-super-call.
                super(GameTextPGN, self).append_pawn_promote_move(
                    promotion_match
                )
                self._promotion_disambiguation_detected = True
                self._bishop_or_bpawn = None
            return
        piece_match = text_format.match(pml)
        if piece_match.group(IFG_PAWN_FROM_FILE) is None:
            self.append_token_and_set_error(match)
            return
        # Ignore method in GameTextPGN class.  Pylint reports bad-super-call.
        super(GameTextPGN, self).append_pawn_move(piece_match)
        self._bishop_or_bpawn = None

    def is_move_interpreted_as_piece_move(self, match):
        """Return True if move is not a pawn move, and None otherwise.

        is_move_interpreted_as_piece_move is called when deciding if a
        movetext item starting 'b' or'B' should be treated as a pawn move
        or a bishop move.

        """
        group = match.group
        piece = group(IFG_PIECE_MOVE).lower()
        i = FILE_NAMES.find(piece)
        if i < 0:
            return True
        square = group(IFG_PIECE_DESTINATION).lower()
        file = square[0]
        if file == piece:
            return True
        if file not in FILE_NAMES[i - 1 : i + 2]:
            return True
        if not group(IFG_PIECE_CAPTURE):
            return True
        if self._active_color == FEN_WHITE_ACTIVE:
            pawn = FEN_WHITE_PAWN
        else:
            pawn = FEN_BLACK_PAWN
        source_squares = fen_source_squares[pawn].get(square)

        # In case this is done for first movetext element after tags.
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                return None

        piece_placement_data = self._piece_placement_data
        if source_squares:
            for ssq in source_squares:
                if ssq[0] == piece:
                    if ssq in piece_placement_data:
                        if piece_placement_data[ssq].name != pawn:
                            return True
        for pgn_np in PGN_NAMED_PIECES:
            if group(IFG_PIECE_MOVE) == pgn_np:
                for pobsq in self._pieces_on_board[
                    (
                        pgn_np.lower()
                        if self._active_color == FEN_BLACK_ACTIVE
                        else pgn_np
                    )
                ]:
                    if pobsq.square.point_to_point.get(
                        pobsq.square.name, square
                    ):
                        return True
        return None

    def append_pawn_move(self, match):
        """Delegate lower case match to superclass."""
        # self._state is None and self._bishop_or_bpawn will have been set
        # by self.append_other_or_disambiguation_pgn().
        assert self._state is None
        if self._bishop_or_bpawn:
            bishop = text_format.match(
                self._bishop_or_bpawn.group().upper() + match.group().lower()
            )
            if bishop:
                # Ignore method in GameTextPGN class.
                # Pylint reports bad-super-call.
                super(GameTextPGN, self).append_piece_move(bishop)
                self._bishop_or_bpawn = None
                return
            self.append_token_and_set_error(match)
            return

        mgl = match.group().lower()

        # So the test on self._piece_placement_data gives a helpful answer.
        # Cannot wait till it's done in 'super().append_pawn_move(pgn_match)'.
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                self._bishop_or_bpawn = None
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)

        if PGN_CAPTURE_MOVE in mgl:
            if mgl.startswith(FEN_BLACK_BISHOP):
                self._append_bishop_or_bpawn_capture(match)
                return
            pgn_match = text_format.match(mgl[0] + mgl[-3:])
        elif LAN_MOVE_SEPARATOR in mgl:
            if mgl.startswith(FEN_BLACK_BISHOP):
                self._append_bishop_or_bpawn_move(match)
                return
            for source_rank, destination_rank, ep_rank in ("243", "756"):
                if mgl[1] == source_rank and mgl[4] == destination_rank:
                    if mgl[0] != mgl[3]:
                        self.append_token_and_set_error(match)
                        self._bishop_or_bpawn = None
                        return
                    if mgl[0] + ep_rank in self._piece_placement_data:
                        self.append_token_and_set_error(match)
                        self._bishop_or_bpawn = None
                        return
            pgn_match = text_format.match(mgl[-2:])
        elif mgl not in self._piece_placement_data:
            pgn_match = text_format.match(mgl)
        elif self._full_disambiguation_detected:
            del self._full_disambiguation_detected
            self._bishop_or_bpawn = None
            return
        else:
            self._long_algebraic_notation_pawn_move(text_format.match(mgl))
            if self._state is not None:
                piece = self._piece_placement_data[mgl]
                if self._active_color == piece.color:
                    if self._active_color == FEN_WHITE_ACTIVE:
                        if piece.name == FEN_WHITE_PAWN:
                            self._full_disambiguation_detected = True
                    elif self._active_color == FEN_BLACK_ACTIVE:
                        if piece.name == FEN_BLACK_PAWN:
                            self._full_disambiguation_detected = True
                self._bishop_or_bpawn = possible_bishop_or_bpawn.match(
                    match.group()
                )
                if (
                    self._full_disambiguation_detected
                    and self._bishop_or_bpawn
                ):
                    del self._full_disambiguation_detected
            else:
                self._bishop_or_bpawn = None
            return
        if pgn_match is None:
            self.append_token_and_set_error(match)
            self._bishop_or_bpawn = None
            return
        # Ignore method in GameTextPGN class.  Pylint reports bad-super-call.
        super(GameTextPGN, self).append_pawn_move(pgn_match)
        if self._state is None:
            self._bishop_or_bpawn = None
            return

        # self._state is not None so self.append_token_after_error() will
        # process next token.
        assert self._state is not None
        self._bishop_or_bpawn = possible_bishop_or_bpawn.match(match.group())

    def append_pawn_promote_move(self, match):
        """Delegate lower case move with upper case promotion to superclass."""
        mgl = match.group().lower()
        if mgl.startswith(FEN_BLACK_BISHOP):
            # So the test on self._piece_placement_data gives a helpful answer.
            # Cannot wait for 'super().append_pawn_move(pgn_match)'.
            if self._movetext_offset is None:
                if not self.set_initial_position():
                    self.append_token_and_set_error(match)
                    self._bishop_or_bpawn = None
                    return
                self._ravstack.append([0])
                self._movetext_offset = len(self._text)

        if PGN_CAPTURE_MOVE in mgl:
            if PGN_PROMOTION in mgl:
                promotion_match = text_promotion_format.match(
                    mgl[0] + mgl[-5:]
                )
            else:
                promotion_match = text_promotion_format.match(
                    mgl[0] + mgl[-4:]
                )
        elif LAN_MOVE_SEPARATOR in mgl:
            if PGN_PROMOTION in mgl:
                promotion_match = text_promotion_format.match(mgl[-4:])
            else:
                promotion_match = text_promotion_format.match(mgl[-3:])
        else:
            promotion_match = text_promotion_format.match(mgl)
        if promotion_match is None:
            self.append_token_and_set_error(match)
            self._bishop_or_bpawn = None
            return
        pmg = promotion_match.group()
        promotion_match = import_format.match(pmg[:-1] + pmg[-1].upper())
        if promotion_match is None:
            self.append_token_and_set_error(match)
            self._bishop_or_bpawn = None
            return
        # Ignore method in GameTextPGN class.  Pylint reports bad-super-call.
        super(GameTextPGN, self).append_pawn_promote_move(promotion_match)
        self._bishop_or_bpawn = None

    def _append_recovered_bishop_or_bpawn_move(self, match):
        """Return True if match is resolved to a bishop or b-pawn move."""
        mgt = match.group().lower()
        promotion_match = text_format.match(
            LAN_MOVE_SEPARATOR.join(
                (
                    self._bishop_or_bpawn.group().lower(),
                    mgt[:-1] + mgt[-1].upper(),
                )
            )
        )
        promotion_lastindex = (
            promotion_match
            and promotion_match.lastindex == IFG_PAWN_PROMOTE_PIECE
        )
        if not (
            mgt.startswith(LAN_MOVE_SEPARATOR)
            or mgt.startswith(PGN_CAPTURE_MOVE)
        ):
            mgt = LAN_MOVE_SEPARATOR + mgt
        bishop_match = text_format.match(
            "".join((self._bishop_or_bpawn.group().upper(), mgt))
        )
        pawn_match = text_format.match(
            "".join((self._bishop_or_bpawn.group().lower(), mgt))
        )
        bishop_lastindex = (
            bishop_match and bishop_match.lastindex == IFG_PIECE_DESTINATION
        )
        pawn_lastindex = pawn_match and (
            pawn_match.lastindex in (IFG_PAWN_TO_RANK, IFG_PAWN_PROMOTE_PIECE)
        )

        # Try the available matches.
        if promotion_lastindex:
            self._undo_append_token_and_set_error()
            super().append_pawn_promote_move(promotion_match)
            self._bishop_or_bpawn = None
        elif bishop_lastindex and pawn_lastindex:
            fen = generate_fen_for_position(
                self._piece_placement_data.values(),
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            )
            setup = import_format.match('[SetUp"1"]')
            fen = import_format.match(fen.join(('[FEN"', '"]')))
            bishop_move = GameTextPGN()
            bishop_move.append_start_tag(setup)
            bishop_move.append_start_tag(fen)
            bishop_move.append_piece_move(bishop_match)
            pawn_move = GameTextPGN()
            pawn_move.append_start_tag(setup)
            pawn_move.append_start_tag(fen)
            pawn_move.append_pawn_move(pawn_match)
            if bishop_move.state is None and pawn_move.state is None:
                if match.group()[0].isupper():
                    self._undo_append_token_and_set_error()
                    super().append_piece_move(bishop_match)
                else:
                    self._undo_append_token_and_set_error()
                    self._append_pawn_move(pawn_match)
            elif bishop_move.state is None:
                self._undo_append_token_and_set_error()
                super().append_piece_move(bishop_match)
            elif pawn_move.state is None:
                self._undo_append_token_and_set_error()
                self._append_pawn_move(pawn_match)

            # This looks equivalent to doing nothing, but if removed leads to
            # an exception in _append_pawn_move at 'if mgl[0] != mgl[3]:'.
            # Without the adjustment to self._text[-1] the text from match
            # appears in two adjacent self._text elements.
            else:
                error_text = self._text[-1]
                self._undo_append_token_and_set_error()
                self.append_token_and_set_error(match)
                self._text[-1] = error_text

        elif pawn_lastindex:
            self._undo_append_token_and_set_error()
            self._append_pawn_move(pawn_match)
        elif bishop_lastindex:
            self._undo_append_token_and_set_error()
            super().append_piece_move(bishop_match)
        else:
            self.append_token_and_set_error(match)
        return bool(self._state is None)

    def _append_pawn_move(self, match):
        mgl = match.group()
        try:
            different_file = mgl[0] != mgl[3]
        except IndexError:
            self.append_token_and_set_error(match)
            return
        if different_file:
            self.append_token_and_set_error(match)
            return
        for source_rank, destination_rank, ep_rank in ("243", "756"):
            if mgl[1] == source_rank and mgl[4] == destination_rank:
                if mgl[0] + ep_rank in self._piece_placement_data:
                    self.append_token_and_set_error(match)
                    return
        pawn_match = import_format.match(mgl[-2:])
        if pawn_match is None:
            self.append_token_and_set_error(match)
            return
        # Ignore method in GameTextPGN class.  Pylint reports bad-super-call.
        super(GameTextPGN, self).append_pawn_move(pawn_match)

    # B[1-8][xX] and b[1-8xX] are intended targets.
    # Others seem covered already.
    def _append_bishop_or_bpawn_capture(self, match):
        fen = generate_fen_for_position(
            self._piece_placement_data.values(),
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        )
        mgt = match.group().lower()
        bishop_match = text_format.match("".join((mgt[0].upper(), mgt[1:])))
        if PGN_PROMOTION in mgt:
            pawn_match = text_format.match(
                "".join((mgt[0].lower(), mgt[1:-1], mgt[-1].upper()))
            )
        else:
            pawn_match = text_format.match("".join((mgt[0].lower(), mgt[1:])))
        setup = import_format.match('[SetUp"1"]')
        fen = import_format.match(fen.join(('[FEN"', '"]')))
        bishop_move = GameTextPGN()
        bishop_move.append_start_tag(setup)
        bishop_move.append_start_tag(fen)
        bishop_move.append_piece_move(bishop_match)
        pawn_move = GameTextPGN()
        pawn_move.append_start_tag(setup)
        pawn_move.append_start_tag(fen)
        if PGN_PROMOTION in mgt:
            pawn_move.append_pawn_promote_move(pawn_match)
        else:
            pawn_move.append_pawn_move(pawn_match)
        if bishop_move.state is None and pawn_move.state is None:
            if match.group()[0].isupper():
                super().append_piece_move(bishop_match)
            else:
                if PGN_PROMOTION in mgt:
                    super().append_pawn_promote_move(pawn_match)
                else:
                    super().append_pawn_move(pawn_match)
        elif bishop_move.state is None:
            super().append_piece_move(bishop_match)
        elif pawn_move.state is None:
            if PGN_PROMOTION in mgt:
                super().append_pawn_promote_move(pawn_match)
            else:
                super().append_pawn_move(pawn_match)
        else:
            self.append_token_and_set_error(match)

    def _append_bishop_or_bpawn_move(self, match):
        fen = generate_fen_for_position(
            self._piece_placement_data.values(),
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        )
        mgt = match.group().lower()
        bishop_match = text_format.match(
            "".join((mgt[0].upper(), mgt[1:].replace(LAN_MOVE_SEPARATOR, "")))
        )
        if PGN_PROMOTION in mgt:
            pawn_match = text_format.match(
                "".join((mgt[0].lower(), mgt[1:-1], mgt[-1].upper()))
            )
        else:
            pawn_match = text_format.match("".join((mgt[0].lower(), mgt[1:])))
        setup = import_format.match('[SetUp"1"]')
        fen = import_format.match(fen.join(('[FEN"', '"]')))
        bishop_move = GameTextPGN()
        bishop_move.append_start_tag(setup)
        bishop_move.append_start_tag(fen)
        bishop_move.append_piece_move(bishop_match)
        pawn_move = GameTextPGN()
        pawn_move.append_start_tag(setup)
        pawn_move.append_start_tag(fen)
        if PGN_PROMOTION in mgt:
            pawn_move.append_pawn_promote_move(pawn_match)
        else:
            pawn_move.append_pawn_move(pawn_match)
        if bishop_move.state is None and pawn_move.state is None:
            if match.group()[0].isupper():
                super().append_piece_move(bishop_match)
            else:
                if PGN_PROMOTION in mgt:
                    super().append_pawn_promote_move(pawn_match)
                else:
                    super().append_pawn_move(pawn_match)
        elif bishop_move.state is None:
            super().append_piece_move(bishop_match)
        elif pawn_move.state is None:
            if PGN_PROMOTION in mgt:
                super().append_pawn_promote_move(pawn_match)
            else:
                super().append_pawn_move(pawn_match)
        else:
            self.append_token_and_set_error(match)
