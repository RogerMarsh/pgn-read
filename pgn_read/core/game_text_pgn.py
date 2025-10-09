# game_text_pgn.py
# Copyright 2025 Roger Marsh
# Licence: See LICENCE (BSD licence)
# Code transferred from 2025 version of game.py.

"""Portable Game Notation (PGN) position and game navigation data structures.

GameTextPGN allows Long Algebraic Notation, FIDE pawn promotion and castling
notation, allows and ignores '<...>' sequences, and allows redundant precision
in PGN movetext.  It is a subclass of Game.

GameTextPGN binds _strict_pgn to None.

"""
import re

from .constants import (
    IFG_PIECE_MOVE,
    IFG_PIECE_CAPTURE,
    PGN_CAPTURE_MOVE,
    LAN_MOVE_SEPARATOR,
    PGN_PROMOTION,
    PGN_BISHOP,
    IMPORT_FORMAT,
    TEXT_FORMAT,
    PAWN_MOVE_TOKEN_POSSIBLE_BISHOP,
)
from .game import Game

import_format = re.compile(IMPORT_FORMAT)
text_format = re.compile(TEXT_FORMAT)
possible_bishop_or_bpawn = re.compile(PAWN_MOVE_TOKEN_POSSIBLE_BISHOP)


class GameTextPGN(Game):
    """Data structure derived with adjustments to PGN specification.

    Long algebraic notation is accepted.

    Redundant precision such as 'Nge2' when an 'N' on 'c3' is pinned to the 'K'
    on 'e1' is allowed.

    The FIDE versions of castling using the digit zero, 0-0 and 0-0-0, and pawn
    promotion without the equal symbol, e8Q, are allowed.

    The left and right angle bracket characters, and any characters between a
    ('<', '>') pair, are ignored.  The two characters are reserved for future
    expansion in the PGN specification.  The ignored sequence, '<.*>', happens
    to match the markup sequences of HTML and XHTML.

    """

    _strict_pgn = None
    _bishop_or_bpawn = None

    # bx[a-h][1-8] is ambiguous when case is ignored and always matches as a
    # piece, not a pawn, capturing something.  This method forces 'b' to be a
    # pawn capturing something, and 'B' a bishop capturing something.
    def append_piece_move(self, match):
        """Extend to cope with ambiguity of bxc4, say, when case ignored.

        The regular expression used to generate match treats bxc4 as a bishop
        move when case is ignored.

        If the text is 'bxc4' this method forces interpretation as a pawn move,
        but delegates 'Bxc4' to the superclass version of append_piece_move.

        """
        if match.group(IFG_PIECE_CAPTURE) == PGN_CAPTURE_MOVE:
            if match.group(IFG_PIECE_MOVE) == PGN_BISHOP.lower():
                self.append_token_and_set_error(match)
                self._bishop_or_bpawn = None
                return
        if match.group(IFG_PIECE_CAPTURE) == LAN_MOVE_SEPARATOR:
            if match.group(IFG_PIECE_MOVE) == PGN_BISHOP.lower():
                self.append_token_and_set_error(match)
                self._bishop_or_bpawn = None
                return
            pgn_match = import_format.match(
                "".join((match.group().split(LAN_MOVE_SEPARATOR)))
            )
            if not pgn_match:
                self.append_token_and_set_error(match)
                self._bishop_or_bpawn = None
                return
            super().append_piece_move(pgn_match)
            self._bishop_or_bpawn = None
            return
        super().append_piece_move(match)
        self._bishop_or_bpawn = None

    def append_other_or_disambiguation_pgn(self, match):
        """Delegate to superclass then set _bishop_or_bpawn from match."""
        super().append_other_or_disambiguation_pgn(match)
        self._bishop_or_bpawn = possible_bishop_or_bpawn.match(match.group())

    def append_pawn_move(self, match):
        """Choose method or superclass delegation using bishop_or_bpawn flag.

        The presence of the capture indicator, 'x', or the long algebraic
        move separator, '-', or the current status of the square named in
        match, influence the choice.  The bishop_or_pawn flag is cleared
        if match is processed as a pawn move.

        """
        if self._bishop_or_bpawn:
            bishop = text_format.match(
                self._bishop_or_bpawn.group() + match.group()
            )
            if bishop:
                super().append_piece_move(bishop)
                self._bishop_or_bpawn = None
                return
            self.append_token_and_set_error(match)
            return
        mgl = match.group()

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
            pgn_match = text_format.match(mgl[0] + mgl[-3:])
        elif LAN_MOVE_SEPARATOR in mgl:
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
            self._long_algebraic_notation_pawn_move(match)
            self._bishop_or_bpawn = None
            return
        super().append_pawn_move(pgn_match)
        self._bishop_or_bpawn = None

    def append_pawn_promote_move(self, match):
        """Delegate promotions to superclass then clear bishop_or_bpawn flag.

        Try the match against the strict interpretation of PGN specification
        and treat as an PGN error if it is not seen as a promotion.

        """
        mgl = match.group()
        if PGN_CAPTURE_MOVE in mgl:
            if PGN_PROMOTION in mgl:
                promotion_match = import_format.match(mgl[0] + mgl[-5:])
            else:
                promotion_match = import_format.match(mgl[0] + mgl[-4:])
        elif LAN_MOVE_SEPARATOR in mgl:
            if PGN_PROMOTION in mgl:
                promotion_match = import_format.match(mgl[-4:])
            else:
                promotion_match = import_format.match(mgl[-3:])
        else:
            promotion_match = import_format.match(mgl)
        if promotion_match is None:
            self.append_token_and_set_error(match)
            self._bishop_or_bpawn = None
            return
        super().append_pawn_promote_move(promotion_match)
        self._bishop_or_bpawn = None

    def ignore_reserved(self, match):
        """Ignore reserved sequence of tokens.

        Matching pairs of '<' and '>', and all text between, are ignored.

        In practice that probably means any HTML or XML markup sequences.

        Unlike the ignore_* methods in Game class, the sequence's existence
        does not cause noting detection of the sequence.

        """
        del match
        self._bishop_or_bpawn = None

    def append_comment_to_eol(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_comment_to_eol(match)
        self._bishop_or_bpawn = None

    def append_token(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_token(match)
        self._bishop_or_bpawn = None

    def append_token_and_set_error(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_token_and_set_error(match)
        self._bishop_or_bpawn = None

    def append_token_after_error(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_token_after_error(match)
        self._bishop_or_bpawn = None

    def append_token_after_error_without_separator(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_token_after_error_without_separator(match)
        self._bishop_or_bpawn = None

    def append_comment_after_error(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_comment_after_error(match)
        self._bishop_or_bpawn = None

    def append_bad_tag_and_set_error(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_bad_tag_and_set_error(match)
        self._bishop_or_bpawn = None

    def append_bad_tag_after_error(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_bad_tag_after_error(match)
        self._bishop_or_bpawn = None

    def append_comment_to_eol_after_error(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_comment_to_eol_after_error(match)
        self._bishop_or_bpawn = None

    def append_end_rav_after_error(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_end_rav_after_error(match)
        self._bishop_or_bpawn = None

    def append_escape_after_error(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_escape_after_error(match)
        self._bishop_or_bpawn = None

    def append_start_tag(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_start_tag(match)
        self._bishop_or_bpawn = None

    def append_castles(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_castles(match)
        self._bishop_or_bpawn = None

    def append_start_rav(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        # '(' and ')' may not be spotted in text mode, leading to a later
        # exception on a genuine PGN '('.
        # The '(self._ravstack[-1][2][1] != self._active_color' comparison in
        # super.append_start_rav(match) will raise a TypeError exception if
        # this situation occurs.
        # What is found is certainly nonsense, but pgn_read does not crash.
        try:
            super().append_start_rav(match)
        except TypeError:
            if self._ravstack[-1][2] is not None:
                raise
            self._append_token_and_set_error(match)

        self._bishop_or_bpawn = None

    def append_end_rav(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_end_rav(match)
        self._bishop_or_bpawn = None

    def append_game_termination(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_game_termination(match)
        self._bishop_or_bpawn = None

    def append_glyph_for_traditional_annotation(self, match):
        """Delegate to superclass then clear bishop_or_bpawn flag."""
        super().append_glyph_for_traditional_annotation(match)
        self._bishop_or_bpawn = None

    def _long_algebraic_notation_match(self, long_match, peek_match):
        """Override, return the LAN match or None."""
        del peek_match
        return long_match
