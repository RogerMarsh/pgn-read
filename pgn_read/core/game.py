# game.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)
# Code transferred from 2016 version of parser.py and modified.

"""Portable Game Notation (PGN) position and game navigation data structures.

Five classes are provided:

Game expects Import Format PGN, which includes Export Format PGN, and allows
some transgressions which occur in real PGN files that do not stop extraction
of the moves played or given in variations (RAVs).

GameStrictPGN does not allow these transgressions.  It is a subclass of Game.

GameTextPGN allows Long Algebraic Notation, FIDE pawn promotion and castling
notation, allows and ignores '<...>' sequences, and allows redundant precision
in PGN movetext.  It is a subclass of Game.

GameIgnoreCasePGN extends GameTextPGN by ignoring case where possible.  Some
things allowed in GameTextPGN are not allowed, or will give a non-intuitive
outcome, when ignoring case leads to ambiguity.  The advantage is movetext like
'B4' is accepted as a pawn move and 'bb4' is accepted as a bishop move.  The
problem is processing PGN text takes about 30% longer than the other classes
for typical game scores without variations.

GameIndicateCheck extends Game by adding check indicators, '+' and '#', to
movetext from games stored on the database.

Some differences are implemented by redefining methods in subclasses.  The rest
are implemented by reference to the class attribute _strict_pgn.

Game binds _strict_pgn to False.

GameStrictPGN binds _strict_pgn to True.

GameTextPGN binds _strict_pgn to None.

GameIgnoreCasePGN uses the GameTextPGN binding for _strict_pgn.

"""
import re

from .constants import (
    IFG_TAG_NAME,
    IFG_TAG_VALUE,
    TAG_FEN,
    TAG_SETUP,
    SETUP_VALUE_FEN_ABSENT,
    SETUP_VALUE_FEN_PRESENT,
    FILE_NAMES,
    RANK_NAMES,
    FEN_PIECE_NAMES,
    FEN_INITIAL_CASTLING,
    FEN_WHITE_KING,
    FEN_BLACK_KING,
    FEN_WHITE_ACTIVE,
    FEN_BLACK_ACTIVE,
    FEN_FIELD_DELIM,
    FEN_RANK_DELIM,
    FEN_NULL,
    FEN_WHITE_PAWN,
    FEN_BLACK_PAWN,
    FEN_WHITE_QUEEN,
    FEN_WHITE_ROOK,
    FEN_WHITE_BISHOP,
    FEN_WHITE_KNIGHT,
    FEN_BLACK_QUEEN,
    FEN_BLACK_ROOK,
    FEN_BLACK_BISHOP,
    FEN_BLACK_KNIGHT,
    IFG_CASTLES,
    IFG_PIECE_MOVE,
    IFG_PIECE_MOVE_FROM_FILE_OR_RANK,
    IFG_PIECE_CAPTURE,
    IFG_PIECE_DESTINATION,
    IFG_PAWN_FROM_FILE,
    IFG_PAWN_CAPTURE_TO_FILE,
    IFG_PAWN_TO_RANK,
    IFG_PAWN_PROMOTE_TO_RANK,
    IFG_PAWN_PROMOTE_PIECE,
    IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE,
    FEN_FIELD_COUNT,
    FEN_PIECE_PLACEMENT_FIELD_INDEX,
    FEN_ACTIVE_COLOR_FIELD_INDEX,
    FEN_CASTLING_AVAILABILITY_FIELD_INDEX,
    FEN_EN_PASSANT_TARGET_SQUARE_FIELD_INDEX,
    FEN_HALFMOVE_CLOCK_FIELD_INDEX,
    FEN_FULLMOVE_NUMBER_FIELD_INDEX,
    PGN_CAPTURE_MOVE,
    POINT_TO_POINT,
    EN_PASSANT_TARGET_SQUARES,
    FEN_TO_PGN,
    PGN_ROOK,
    CASTLING_RIGHTS,
    CASTLING_PIECE_FOR_SQUARE,
    CASTLING_MOVE_RIGHTS,
    FEN_PAWNS,
    RANK_ATTACKS,
    FILE_ATTACKS,
    LRD_DIAGONAL_ATTACKS,
    RLD_DIAGONAL_ATTACKS,
    PGN_O_O,
    PGN_O_O_O,
    SOURCE_SQUARES,
    FEN_SOURCE_SQUARES,
    OTHER_SIDE,
    PIECE_TO_KING,
    PROMOTED_PIECE_NAME,
    DISAMBIGUATE_TEXT,
    DG_CAPTURE,
    DG_DESTINATION,
    DISAMBIGUATE_PGN,
    DISAMBIGUATE_PROMOTION,
    LAN_FORMAT,
    LAN_MOVE_SEPARATOR,
    PGN_PROMOTION,
    PGN_BISHOP,
    IMPORT_FORMAT,
    TEXT_FORMAT,
    TEXT_PROMOTION,
    TP_MOVE,
    TP_PROMOTE_TO_PIECE,
    PAWN_MOVE_TOKEN_POSSIBLE_BISHOP,
    WHITE_PAWN_CAPTURES,
    BLACK_PAWN_CAPTURES,
    PGN_NAMED_PIECES,
    TAG_EVENT,
    TAG_SITE,
    TAG_DATE,
    TAG_ROUND,
    TAG_WHITE,
    TAG_BLACK,
    TAG_RESULT,
    SEVEN_TAG_ROSTER,
    SUPPLEMENTAL_TAG_ROSTER,
    DEFAULT_TAG_VALUE,
    DEFAULT_TAG_DATE_VALUE,
    DEFAULT_TAG_RESULT_VALUE,
    DEFAULT_SORT_TAG_VALUE,
    DEFAULT_SORT_TAG_RESULT_VALUE,
    SEVEN_TAG_ROSTER_DEFAULTS,
    PGN_MAXIMUM_LINE_LENGTH,
    PGN_LINE_SEPARATOR,
    PGN_TOKEN_SEPARATOR,
    PGN_DOT,
    SUFFIX_ANNOTATION_TO_NAG,
    KING_MOVES,
    KNIGHT_MOVES,
)
from .piece import Piece
from .squares import Squares

import_format = re.compile(IMPORT_FORMAT)
text_format = re.compile(TEXT_FORMAT)
disambiguate_pgn_format = re.compile(DISAMBIGUATE_PGN)
disambiguate_text_format = re.compile(DISAMBIGUATE_TEXT)
disambiguate_promotion_format = re.compile(DISAMBIGUATE_PROMOTION)
lan_format = re.compile(LAN_FORMAT)
text_promotion_format = re.compile(TEXT_PROMOTION)
possible_bishop_or_bpawn = re.compile(PAWN_MOVE_TOKEN_POSSIBLE_BISHOP)
white_black_tag_value_format = re.compile(r"\s*([^,.\s]+)")
suffix_annotations = re.compile(r"(!!|!\?|!|\?\?|\?!|\?)$")
SIDE_TO_MOVE_KING = {
    FEN_WHITE_ACTIVE: FEN_WHITE_KING,
    FEN_BLACK_ACTIVE: FEN_BLACK_KING,
}


class GameError(Exception):
    """Exceptions raised manipulating Game state."""


class Game:
    """Data structure of game positions derived from a PGN game score.

    Input is a token which is potentially a valid token, as defined in the PGN
    specification, in the current game state.

    Move number indications and dots are detected but completely ignored while
    the input is valid.  The PGN specification states move number indications
    are optional but must be correct if present.  Thus games with incorrect
    move number indications are accepted if the game is valid otherwise.

    Movetext like 'Nge2' is accepted when 'Ne2' is unambiguous: typically the
    'N' on 'c3' is pinned against the 'K' on 'e1'.  Class GameStrictPGN insists
    on 'Ne2' because it sets _strict_pgn True rather than False.

    Invalid tokens between the first valid movetext and the game termination
    marker are not allowed when _strict_pgn is False.  This may be changed in
    future to ignore these invalid tokens.

    The left and right angle bracket characters, and any characters between a
    ('<', '>') pair, are treated as an error because the two characters are
    reserved for future expansion in the PGN specification.  The sequence
    '<.*>' happens to match the markup sequences of HTML and XHTML.

    Comparison operators implement the PGN collating sequence, except in
    ascending str order rather than ascending ASCII order.

    """

    # Overridden in some subclasses to change behaviour for non-standard PGN.
    _strict_pgn = False

    # Defaults for Game instance state.
    _full_disambiguation_detected = False
    _state = None
    _movetext_offset = None
    _initial_position = None
    _fullmove_number = None
    _halfmove_clock = None
    _en_passant_target_square = None
    _castling_availability = None
    _active_color = None

    def __init__(self):
        """Create empty data structure for a game presented in PGN format."""
        # There is 1:1 between self._text and self._position_deltas.
        # self._movetext_offset is offset of first non-tag item in self._text,
        # usually the first movetext item but ';...\n', '<...>', and others
        # are possible too.
        self._text = []
        self._position_deltas = []

        self._tags = {}
        self._error_list = []
        self._state_stack = [None]

        # This attribute, with the relevant five items defaulted in the class
        # definition, correspond to the six fields in a FEN desription of a
        # position.  It contains a dict of Piece instances, at most 32 items
        # which reduces as pieces are captured.
        self._piece_placement_data = {}

        # Keys are FEN pieces, and files suffixed by the FEN value for the
        # relevant pawn.
        # Values are lists of Piece instances with the same value in the name
        # attribute.
        # Normally a maximum of two pieces are in each list.  Pawn promotion
        # and tripled, or more, pawns are the ways the normal maximum can be
        # exceeded.
        self._pieces_on_board = {}

        # Track and label Recursive Annotation Variations (RAV).
        self._ravstack = []

    def set_game_error(self):
        """Declare parsing of game text has failed.

        set_game_error() allows an instance of parser.PGN to declare the game
        invalid in cases where the Game class instance cannot do so: such as
        when input text ends without a game termination marker but is valid up
        to that point.

        set_game_error() sets _state to 'False' if _state does not
        indicate the offset in _text of the token which caused the text to be
        deemed invalid PGN.  _state is None initially and is set 'True'
        when the first valid PGN Tag is found, or to the offset of the token
        which makes the PGN text invalid.

        set_game_error() should not be used within the Game class or any
        subclass.

        """
        if self._state is None:
            self._state = len(self._text)
            self._state_stack[-1] = self._state

    @property
    def game_ok(self):
        """Return True if game and all variations have no PGN errors."""
        return bool(self._state is None and not self._error_list)

    @property
    def game_ok_with_variation_errors(self):
        """Return True if game has no PGN errors: variations are ignored."""
        return bool(self._state is None and self._error_list)

    @property
    def game_has_errors(self):
        """Return True if game has PGN errors: variations are ignored."""
        return bool(self._state is not None)

    @property
    def state(self):
        """Return the token offset where PGN error in game occured."""
        return self._state

    @property
    def movetext_offset(self):
        """Return the token offset where PGN movetext begins."""
        return self._movetext_offset

    # May be removed in future, or converted to property.
    # Property game_has_errors is equivalent but meaning of True and False is
    # reversed.
    def is_movetext_valid(self):
        """Return True if there are no error_tokens in the collected game."""
        return self._state is None

    # May be overridden in subclasses.
    def is_tag_roster_valid(self):
        """Return True if the game's tag roster is valid."""
        tags = self._tags
        for str_tag in SEVEN_TAG_ROSTER:
            if str_tag not in tags:
                # A mandatory tag is missing.
                return False
            if len(tags[str_tag]) == 0:
                # Mandatory tags must have a non-null value.
                return False
        for str_tag in SUPPLEMENTAL_TAG_ROSTER:
            if str_tag in tags:
                if len(tags[str_tag]) == 0:
                    return False
        return True

    def is_pgn_valid(self):
        """Return True if the tags and movetext in the game are valid.

        Movetext with no PGN errors in the main line but errors in one or more
        RAVs will cause this method to return True.

        """
        return self.is_movetext_valid() and self.is_tag_roster_valid()

    def is_pgn_valid_export_format(self):
        """Return True if the tags and movetext meet PGN export format rules.

        This method always returns False if is_pgn_valid returns False, but
        may return False if is_pgn_valid returns True.

        """
        if not self.is_pgn_valid():
            return False
        return self._tags.get(TAG_RESULT) == self._text[-1]

    def add_board_state_none(self, position_delta):
        """Append placeholder, None, for token being processed.

        Subclasses may extend this method as needed: it is used when a PGN Tag,
        or a game termination token, is found.

        """
        self._position_deltas.append(position_delta)

    def repeat_board_state(self, position_delta):
        """Copy preceding board state for token being processed.

        Subclasses may extend this method as needed: it is used when various
        non-move tokens such as comments, but not start and end RAV markers,
        are found.

        """
        self._position_deltas.append(position_delta)

    def set_board_state(self, position_delta):
        """Set board state for token being processed.

        Subclasses may extend this method as needed: it is used when setting
        the board state after the end of a RAV.

        """
        self._position_deltas.append(position_delta)

    def set_initial_board_state(self, position_delta):
        """Set board state for token being processed.

        Subclasses may extend this method as needed: it is used when a PGN FEN
        Tag is found or the first move token is found.

        """
        self._initial_position = position_delta

    def reset_board_state(self, position_delta):
        """Set board state for token being processed.

        Subclasses may extend this method as needed: it is used when setting
        the board state at the start of a RAV.

        """
        self._position_deltas.append(position_delta)

    def modify_board_state(self, position_delta):
        """Modify board state for token being processed.

        Subclasses may extend this method as needed: it is used when setting
        the board state for a move played in the game or a RAV.

        """
        self._position_deltas.append(position_delta)

    def append_comment_to_eol(self, match):
        r"""Append ';...\n' token from gamescore.

        The '\n' termination for the comment is not captured because it may
        start an escaped line, '\n%...\n', and is explicitly added to the
        token.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(match.group() + "\n")
        try:
            self.repeat_board_state(self._position_deltas[-1])
        except IndexError:
            self.add_board_state_none(None)

    def append_token(self, match):
        """Append valid non-tag token from game score.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(match.group())
        try:
            self.repeat_board_state(self._position_deltas[-1])
        except IndexError:
            self.add_board_state_none(None)

    append_reserved = append_token

    # '--' is a non-standard, and not rare, extension to PGN meaning side with
    # move does not make a move but the other side is now to move.
    # Some subclasses of Game ignore anything which is not PGN.  These two
    # methods ensure '--' is always captured because the associated moves will
    # not make sense, when eyeballed, if the '--' is missing.
    # '--' has been seen as the first or only move after the tags, where it
    # makes no sense, and is therefore treated as legal as the first movetext
    # token.  However it is not allowed as the first token of a game score, in
    # PGN files the first token after a game termination token, to minimise
    # the risk of swallowing valid games from it's use in PGN files: the
    # Craftynn.pgn series for example.
    def append_pass_and_set_error(self, match):
        """Append '--' token and set PGN error found."""
        if self._movetext_offset is None and self._text:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        self.append_token_and_set_error(match)

    def append_pass_after_error(self, match):
        """Append '--' token found after detection of PGN error."""
        self.append_token_after_error(match)

    def pgn_error_notification(self):
        """Do nothing.  Subclasses should override to fit requirements.

        When not overridden the game_ok or game_ok_with_variation_errors
        properties should be used to test for errors rather than the state
        or game_has_errors properties.  self._state can be None even if there
        are errors in recursive annotation variations.  The detail of the
        subclass will determine if this is still the case.

        One possibility is to wrap the error in a '{...}' comment.

        """

    def pgn_error_recovery(self):
        """Do nothing.  Subclasses should override to fit requirements.

        When not overridden the game_ok or game_ok_with_variation_errors
        properties should be used to test for errors rather than the state
        or game_has_errors properties.  self._state can be None even if there
        are errors in recursive annotation variations.  The detail of the
        subclass will determine if this is still the case.

        One possibility is to wrap the error in a '{...}' comment.

        """

    def pgn_mark_comment_in_error(self, comment):
        """Return comment.  Subclasses should override to fit requirements.

        When not overridden the game_ok or game_ok_with_variation_errors
        properties should be used to test for errors rather than the state
        or game_has_errors properties.  self._state can be None even if there
        are errors in recursive annotation variations.  The detail of the
        subclass will determine if this is still the case.

        One possibility is to wrap the error in a '{...}' comment.  The '}'
        token in any wrapped commment would end the comment wrapping the error
        prematurely, so some action may be needed.

        """
        return comment

    def append_token_and_set_error(self, match):
        """Append first invalid token in main line or variation to game score.

        The game error state is adjusted so the error condition can be removed
        at the end of the variation in which it occured.

        """
        if self._state is None:
            self._state = len(self._text)
            self._state_stack[-1] = self._state
            self._error_list.append(self._state)
            self.pgn_error_notification()
            # Activate to stop at first error; beware this catches end of
            # buffer errors too, so be sure the error to be seen is in first
            # buffer.  The method raises an AssertionError.
            # self.display_placement_and_board_and_fen_then_assert_false(match)
        self._text.append(PGN_TOKEN_SEPARATOR + match.group())

        # len(self._position_deltas) will be 0 if end of buffer reached while
        # collecting PGN Tags.
        try:
            self.repeat_board_state(self._position_deltas[-1])
        except IndexError:
            if self._position_deltas:
                raise

    def append_token_after_error(self, match):
        """Append token to game score after an error has been found."""
        self._text.append(PGN_TOKEN_SEPARATOR + match.group())

    def append_token_after_error_without_separator(self, match):
        """Append token without separator from game score after PGN error.

        Sequences of dots after an error are kept together, there is not a
        space before each dot.  When there is no error dots are ignored.

        Check indicators are not prefixed with a separator.

        """
        self._text.append(match.group())

    def append_comment_after_error(self, match):
        """Append comment token to game score after an error has been found."""
        self._text.append(
            PGN_TOKEN_SEPARATOR + self.pgn_mark_comment_in_error(match.group())
        )

    def append_bad_tag_and_set_error(self, match):
        r"""Append incomplete or badly formed tag to game score and set error.

        The tag is formed like '[ Tagname "Tagvalue" ]' with extra, or
        less, whitespace allowed.  In particular there is at least one '\' or
        '"' without the '\' escape prefix.  If _state and _movetext_offset
        allow and the rules do not state _strict_pgn the escape prefix is
        added as needed, rather than declare an error and terminate the game.

        The tag is wrapped in a comment, '{}' and the game is terminated with
        the unknown result symbol '*'.

        """
        if (
            self._strict_pgn
            or self._state is not None
            or self._movetext_offset is not None
        ):
            if self._state is None:
                self._state = len(self._text)
                self._state_stack[-1] = self._state
                self._error_list.append(self._state)
            self._text.append(
                match.group().join(("{::Bad Tag::", "::Bad Tag::}"))
            )
            # self._text.append('*')
            try:
                self.repeat_board_state(self._position_deltas[-1])
            except IndexError:
                if self._position_deltas:
                    raise
                self.add_board_state_none(None)
            return
        bad_tag = match.group().split('"')
        val = (
            '"'.join(bad_tag[1:-1])
            .replace('"', '"')
            .replace("\\\\", "\\")
            .replace("\\", "\\\\")
            .replace('"', r"\"")
        )

        # Copy from append_start_tag() to apply correctly formatted PGN tag,
        # which must not be duplicated.
        self.add_board_state_none(None)
        tag_name = bad_tag[0].lstrip("[").strip()
        self._text.append("".join(("[", tag_name, '"', val, '"]')))
        if tag_name in self._tags:
            if self._state is None:
                self._state = len(self._tags) - 1
                self._state_stack[-1] = self._state
            return
        self._tags[tag_name] = val
        return

    def append_bad_tag_after_error(self, match):
        """Append token to game score after an error has been found."""
        self._text.append(match.group())
        if self._state is not None or self._movetext_offset is not None:
            self.add_board_state_none(None)

    def append_game_termination_after_error(self, match):
        """Delegate action to append_token_after_error method.

        append_game_termination_after_error exists to provide explicit default
        action when a game termination token to found when in game error state.

        """
        self.pgn_error_recovery()
        self.append_token_after_error(match)

    def append_comment_to_eol_after_error(self, match):
        r"""Append ';...\n' token to game score after an error has been found.

        The '\n' termination for the comment is not captured because it may
        start an escaped line, '\n%...\n', and is explicitly added to the
        token.

        """
        self._text.append(match.group() + "\n")

    def append_start_rav_after_error(self, match):
        """Append start RAV token from game score after PGN error found."""
        self.append_token_after_error(match)
        self._state_stack.append(self._state)

    def append_end_rav_after_error(self, match):
        """Append end RAV token from game score after PGN error found."""
        if len(self._state_stack) > 1:
            if self._state_stack[-2] == self._state_stack[-1]:
                self.append_token_after_error(match)
                del self._state_stack[-1]
                self._state = self._state_stack[-1]
            else:

                # Cannot call append_end_rav() method because it tests some
                # conditions that should be true when errors are absent.
                if self._movetext_offset is None:
                    self.append_token_and_set_error(match)
                    return
                if len(self._ravstack) == 1:
                    self.append_token_and_set_error(match)
                    return
                del self._ravstack[-1]
                del self._state_stack[-1]
                self._state = self._state_stack[-1]
                if self._ravstack[-1][2] is None:
                    self.set_position_to_play_prior_right_nested_rav_at_move()
                else:
                    self.set_position_to_play_main_line_at_move()
                self.pgn_error_recovery()
                self._text.append(match.group())

        else:
            self.append_token_after_error(match)

    def append_escape_after_error(self, match):
        r"""Append escape token to game score after an error has been found.

        The '\n' termination for the escaped line is not captured because it
        may start an escaped line.

        The '\n' is appended to the token.

        """
        self._text.append(match.group() + "\n")

    def append_other_or_disambiguation_pgn(self, match):
        """Ignore token previously used for disambiguation, or set PGN error.

        'Qb3c2' can mean move the queen on b3 to c2 when all whitespace is
        removed from PGN movetext.  This method processes the 'c2' when it is
        consumed from the input: 'c2' is processed by peeking at the input when
        processing the 'Qb3'.

        """
        # The pawn-like capture destination has been processed as part of a
        # fully disambiguated piece move.
        # There is no need to do anything for long algebraic notation moves
        # because these are allowed only when unrecognized tokens are ignored.
        # In other words when 'if self._strict_pgn' evaluates False.
        if self._full_disambiguation_detected:
            del self._full_disambiguation_detected
            if disambiguate_pgn_format.match(match.group()):
                return

        if self._strict_pgn is not None:
            self.append_token_and_set_error(match)

    def append_start_tag(self, match):
        """Append tag token to game score and update game tags.

        Put game in error state if a duplicate tag name is found.

        """
        if self._state is not None or self._movetext_offset is not None:
            self.append_token_and_set_error(match)
            return
        group = match.group
        tag_name = group(IFG_TAG_NAME)
        tag_value = group(IFG_TAG_VALUE)
        self._text.append("".join(("[", tag_name, '"', tag_value, '"]')))
        self.add_board_state_none(None)

        # Iniitialized None and set True when first valid match is applied.
        # Parser detects when a tag is out-of-sequence and sets _game_ok False.
        # if self._state is None:
        #    self._state = 'True'
        #    self._state_stack[-1] = self._state

        # Tag names must not be duplicated.
        if tag_name in self._tags:
            # if self._state == 'True':
            if self._state is None:
                self._state = len(self._tags) - 1
                self._state_stack[-1] = self._state
            return

        self._tags[tag_name] = tag_value
        return

    def append_castles(self, match):
        """Append castling move token to game score and update board state.

        Put game in error state if the token represents an illegal move.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        piece_placement_data = self._piece_placement_data
        if self._active_color == FEN_WHITE_ACTIVE:
            king_square = FILE_NAMES[4] + RANK_NAMES[-1]
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            king_square = FILE_NAMES[4] + RANK_NAMES[0]
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        if king_square not in piece_placement_data:
            self.append_token_and_set_error(match)
            return
        castling_move = match.group(IFG_CASTLES)
        if (
            CASTLING_MOVE_RIGHTS[self._active_color, castling_move]
            not in self._castling_availability
        ):
            self.append_token_and_set_error(match)
            return
        if castling_move == PGN_O_O:
            if self._active_color == FEN_WHITE_ACTIVE:
                rook_square = FILE_NAMES[7] + RANK_NAMES[-1]
                king_destination = FILE_NAMES[6] + RANK_NAMES[-1]
                rook_destination = FILE_NAMES[5] + RANK_NAMES[-1]
            else:
                rook_square = FILE_NAMES[7] + RANK_NAMES[0]
                king_destination = FILE_NAMES[6] + RANK_NAMES[0]
                rook_destination = FILE_NAMES[5] + RANK_NAMES[0]
        elif self._active_color == FEN_WHITE_ACTIVE:
            rook_square = FILE_NAMES[0] + RANK_NAMES[-1]
            king_destination = FILE_NAMES[2] + RANK_NAMES[-1]
            rook_destination = FILE_NAMES[3] + RANK_NAMES[-1]
        else:
            rook_square = FILE_NAMES[0] + RANK_NAMES[0]
            king_destination = FILE_NAMES[2] + RANK_NAMES[0]
            rook_destination = FILE_NAMES[3] + RANK_NAMES[0]
        if rook_square not in piece_placement_data:
            self.append_token_and_set_error(match)
            return
        if not self.line_empty(king_square, rook_square):
            self.append_token_and_set_error(match)
            return

        # Cannot castle if king is in check, king would be in check if move
        # completed, or the square between the source and destination is
        # attacked by the other side.
        # No need to test if king is in check after applying remove and place
        # instructions to board.
        ptp = POINT_TO_POINT[king_square, king_destination]
        for square in (
            king_square,
            king_destination,
            ptp[2][ptp[0] : ptp[1]][0],
        ):
            if self.is_square_attacked_by_other_side(square):
                self.append_token_and_set_error(match)
                return

        king = piece_placement_data[king_square]
        rook = piece_placement_data[rook_square]
        remove = ((king_square, king), (rook_square, rook))
        self.remove_piece_on_square(remove[0])
        self.remove_piece_on_square(remove[1])
        place = ((king_destination, king), (rook_destination, rook))
        self.place_piece_on_square(place[0])
        self.place_piece_on_square(place[1])
        self._text.append(match.group())
        self.modify_board_state(
            (
                (
                    remove,
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ),
                (
                    place,
                    OTHER_SIDE[self._active_color],
                    self.get_castling_options_after_move_applied(remove),
                    FEN_NULL,
                    self._halfmove_clock + 1,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = self._position_deltas[-1][1][1:]
        self.append_check_indicator()

    def append_piece_move(self, match):
        """Append piece move token to game score and update board state.

        Put game in error state if the token represents an illegal move.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        group = match.group
        if self._active_color == FEN_WHITE_ACTIVE:
            piece_name = group(IFG_PIECE_MOVE)
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            piece_name = group(IFG_PIECE_MOVE).lower()
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        destination = group(IFG_PIECE_DESTINATION)
        try:
            source_squares = SOURCE_SQUARES[group(IFG_PIECE_MOVE)][destination]
        except KeyError:
            self.append_token_and_set_error(match)
            return
        piece_placement_data = self._piece_placement_data

        # Piece move and capture.

        if group(IFG_PIECE_CAPTURE):
            if destination not in piece_placement_data:
                self.append_token_and_set_error(match)
                return
            candidates = []
            for piece in self._pieces_on_board[piece_name]:
                if piece.square.name in source_squares:
                    candidates.append(piece)
            if len(candidates) == 1:
                piece = candidates[0]
                if not self.line_empty(piece.square.name, destination):
                    self.append_token_and_set_error(match)
                    return
                remove = (
                    (destination, piece_placement_data[destination]),
                    (piece.square.name, piece),
                )
                self.remove_piece_from_board(remove[0])
                self.remove_piece_on_square(remove[1])
                place = destination, piece
                self.place_piece_on_square(place)
                if self.is_square_attacked_by_other_side(
                    self._pieces_on_board[PIECE_TO_KING[piece.name]][
                        0
                    ].square.name
                ):
                    self.remove_piece_on_square(place)
                    self.place_piece_on_board(remove[0])
                    self.place_piece_on_square(remove[1])
                    self.append_token_and_set_error(match)
                    return

                # Allow acceptance of superfluous precision in movetext, even
                # though it may be too lenient as there is only one piece that
                # could make the move.
                # For example Ngxe2 when Nxe2 is unambiguous.
                # But Ng1xe2 is not accepted at this point.
                if group(IFG_PIECE_MOVE_FROM_FILE_OR_RANK):
                    if self._strict_pgn:
                        self.append_token_and_set_error(match)
                        return
                    self._text.append(group()[:1] + group()[2:])
                else:
                    self._text.append(group())

                self.modify_board_state(
                    (
                        (
                            remove,
                            self._active_color,
                            self._castling_availability,
                            self._en_passant_target_square,
                            self._halfmove_clock,
                            self._fullmove_number,
                        ),
                        (
                            (place,),
                            OTHER_SIDE[self._active_color],
                            self.get_castling_options_after_move_applied(
                                remove
                            ),
                            FEN_NULL,
                            0,
                            fullmove_number_for_next_halfmove,
                        ),
                    )
                )
                (
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ) = self._position_deltas[-1][1][1:]
                self.append_check_indicator()
                return
            from_file_or_rank = group(IFG_PIECE_MOVE_FROM_FILE_OR_RANK)
            if from_file_or_rank:
                can_move = []
            fit_count = 0
            chosen_move = None
            for piece in candidates:
                if not self.line_empty(piece.square.name, destination):
                    continue
                remove = (
                    (destination, piece_placement_data[destination]),
                    (piece.square.name, piece),
                )
                self.remove_piece_from_board(remove[0])
                self.remove_piece_on_square(remove[1])
                place = destination, piece
                self.place_piece_on_square(place)
                if not self.is_square_attacked_by_other_side(
                    self._pieces_on_board[PIECE_TO_KING[piece.name]][
                        0
                    ].square.name
                ):
                    if from_file_or_rank:
                        if from_file_or_rank in remove[-1][0]:
                            chosen_move = remove, place
                            fit_count += 1
                        can_move.append(piece)
                    else:
                        chosen_move = remove, place
                        fit_count += 1
                self.remove_piece_on_square(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_square(remove[1])
            if chosen_move is None or fit_count != 1:
                self.append_token_and_set_error(match)
                return

            # Acceptance of superfluous precision in movetext is allowed.
            # For example Ngxe2 when Nxe2 is unambiguous.
            # But Ng1xe2 is not accepted at this point.
            if from_file_or_rank:
                if len(can_move) == 1:
                    if self._strict_pgn:
                        self.append_token_and_set_error(match)
                        return
                    self._text.append(group()[:1] + group()[2:])
                elif from_file_or_rank in RANK_NAMES:
                    pfile = chosen_move[0][1][0][0]
                    if (
                        len([p for p in can_move if p.square.file == pfile])
                        < 2
                    ):
                        self.append_token_and_set_error(match)
                        return
                    self._text.append(group())
                else:
                    self._text.append(group())
            else:
                self._text.append(group())

            remove, place = chosen_move
            self.remove_piece_from_board(remove[0])
            self.remove_piece_on_square(remove[1])
            self.place_piece_on_square(place)
            self.modify_board_state(
                (
                    (
                        remove,
                        self._active_color,
                        self._castling_availability,
                        self._en_passant_target_square,
                        self._halfmove_clock,
                        self._fullmove_number,
                    ),
                    (
                        (place,),
                        OTHER_SIDE[self._active_color],
                        self.get_castling_options_after_move_applied(remove),
                        FEN_NULL,
                        0,
                        fullmove_number_for_next_halfmove,
                    ),
                )
            )
            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._position_deltas[-1][1][1:]
            self.append_check_indicator()
            return

        # Piece move without capture.

        if destination in piece_placement_data:

            # IMPORT_FORMAT regular expression treats 'Qe3c6' as 'Qe3' and 'c6',
            # and 'Qe3xc6' as 'Qe3' and the unexpected 'xc6'.
            # The capture could be spotted, but not the move.
            # Allow all movetext like 'Qe3e6' or 'Qe3xe6' when _strict_pgn is
            # not enforced, and perhaps even 'Qe3-c6'.
            # Rooks never need full disambiguation, at most two pawns can
            # capture and land on a square, and there is only one king.
            # Full disambiguation is not needed when less than three pieces of
            # the type can move to the square.
            if piece_placement_data[destination].color != self._active_color:
                self.append_token_and_set_error(match)
                return
            if not self._strict_pgn:
                self._long_algebraic_notation_piece_move(match)
                return
            if FEN_TO_PGN[piece_placement_data[destination].name] == PGN_ROOK:
                self.append_token_and_set_error(match)
                return
            self._disambiguate_piece_move(match)
            return

        candidates = []
        for piece in self._pieces_on_board[piece_name]:
            if piece.square.name in source_squares:
                candidates.append(piece)
        if len(candidates) == 1:
            piece = candidates[0]
            if not self.line_empty(piece.square.name, destination):
                self.append_token_and_set_error(match)
                return
            remove = piece.square.name, piece
            self.remove_piece_on_square(remove)
            place = destination, piece
            self.place_piece_on_square(place)
            if self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
            ):
                self.remove_piece_on_square(place)
                self.place_piece_on_square(remove)
                self.append_token_and_set_error(match)
                return

            # Allow acceptance of superfluous precision in movetext, even
            # though it may be too lenient as there is only one piece that
            # could make the move.
            # For example Nge2 when Ne2 is unambiguous.
            # But Ng1e2 is not accepted at this point.
            if group(IFG_PIECE_MOVE_FROM_FILE_OR_RANK):
                if self._strict_pgn:
                    self.append_token_and_set_error(match)
                    return
                self._text.append(group()[:1] + group()[2:])
            else:
                self._text.append(group())

            self.modify_board_state(
                (
                    (
                        (remove,),
                        self._active_color,
                        self._castling_availability,
                        self._en_passant_target_square,
                        self._halfmove_clock,
                        self._fullmove_number,
                    ),
                    (
                        (place,),
                        OTHER_SIDE[self._active_color],
                        self.get_castling_options_after_move_applied(
                            (remove,)
                        ),
                        FEN_NULL,
                        self._halfmove_clock + 1,
                        fullmove_number_for_next_halfmove,
                    ),
                )
            )
            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._position_deltas[-1][1][1:]
            self.append_check_indicator()
            return
        from_file_or_rank = group(IFG_PIECE_MOVE_FROM_FILE_OR_RANK)
        if from_file_or_rank:
            can_move = []
        fit_count = 0
        chosen_move = None
        for piece in candidates:
            if not self.line_empty(piece.square.name, destination):
                continue
            remove = piece.square.name, piece
            self.remove_piece_on_square(remove)
            place = destination, piece
            self.place_piece_on_square(place)
            if not self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
            ):
                if from_file_or_rank:
                    if from_file_or_rank in remove[0]:
                        chosen_move = remove, place
                        fit_count += 1
                    can_move.append(piece)
                else:
                    chosen_move = remove, place
                    fit_count += 1
            self.remove_piece_on_square(place)
            self.place_piece_on_square(remove)
        if chosen_move is None or fit_count != 1:
            self.append_token_and_set_error(match)
            return

        # Acceptance of superfluous precision in movetext is allowed.
        # For example Nge2 when Ne2 is unambiguous.
        # But Ng1e2 is not accepted at this point.
        if from_file_or_rank:
            if len(can_move) == 1:
                if self._strict_pgn:
                    self.append_token_and_set_error(match)
                    return
                self._text.append(group()[:1] + group()[2:])
            elif from_file_or_rank in RANK_NAMES:
                pfile = chosen_move[0][0][0][0]
                if len([p for p in can_move if p.square.file == pfile]) < 2:
                    self.append_token_and_set_error(match)
                    return
                self._text.append(group())
            else:
                self._text.append(group())
        else:
            self._text.append(group())

        remove, place = chosen_move
        self.remove_piece_on_square(remove)
        self.place_piece_on_square(place)
        self.modify_board_state(
            (
                (
                    (remove,),
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ),
                (
                    (place,),
                    OTHER_SIDE[self._active_color],
                    self.get_castling_options_after_move_applied((remove,)),
                    FEN_NULL,
                    self._halfmove_clock + 1,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = self._position_deltas[-1][1][1:]
        self.append_check_indicator()

    def append_pawn_move(self, match):
        """Append pawn move token to game score and update board state.

        Pawn promotion moves are handled by append_pawn_promote_move.

        Put game in error state if the token represents an illegal move.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        group = match.group
        piece_placement_data = self._piece_placement_data

        # Pawn move and capture.

        if group(IFG_PAWN_CAPTURE_TO_FILE):
            destination = group(IFG_PAWN_CAPTURE_TO_FILE) + group(
                IFG_PAWN_TO_RANK
            )
            pawn_capture_from_file = group(IFG_PAWN_FROM_FILE)
            if self._active_color == FEN_WHITE_ACTIVE:
                fullmove_number_for_next_halfmove = self._fullmove_number
                source_squares_index = FEN_WHITE_PAWN + PGN_CAPTURE_MOVE
            else:
                fullmove_number_for_next_halfmove = self._fullmove_number + 1
                source_squares_index = FEN_BLACK_PAWN + PGN_CAPTURE_MOVE
            try:
                source_squares = SOURCE_SQUARES[source_squares_index][
                    destination
                ]
            except KeyError:
                self.append_token_and_set_error(match)
                return
            for source in source_squares:
                if source.startswith(pawn_capture_from_file):
                    try:
                        if (
                            FEN_PAWNS.get(piece_placement_data[source].name)
                            == self._active_color
                        ):
                            piece = piece_placement_data[source]
                            break
                    except KeyError:
                        self.append_token_and_set_error(match)
                        return
            else:
                self.append_token_and_set_error(match)
                return
            if destination not in piece_placement_data:
                if self._en_passant_target_square == FEN_NULL:
                    self.append_token_and_set_error(match)
                    return
                capture_square = EN_PASSANT_TARGET_SQUARES.get(group()[:4])
                if not capture_square:
                    self.append_token_and_set_error(match)
                    return
                if capture_square not in piece_placement_data:
                    self.append_token_and_set_error(match)
                    return
                if (
                    FEN_PAWNS.get(piece_placement_data[capture_square].name)
                    == self._active_color
                ):
                    self.append_token_and_set_error(match)
                    return
            elif (
                piece_placement_data[source].color
                == piece_placement_data[destination].color
            ):
                self.append_token_and_set_error(match)
                return
            else:
                capture_square = destination
            remove = (
                (capture_square, piece_placement_data[capture_square]),
                (piece.square.name, piece),
            )
            self.remove_piece_from_board(remove[0])
            self.remove_piece_from_board(remove[1])
            place = destination, piece
            self.place_piece_on_board(place)
            if self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
            ):
                self.remove_piece_from_board(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_board(remove[1])
                self.append_token_and_set_error(match)
                return
            self._text.append(group())
            self.modify_board_state(
                (
                    (
                        remove,
                        self._active_color,
                        self._castling_availability,
                        self._en_passant_target_square,
                        self._halfmove_clock,
                        self._fullmove_number,
                    ),
                    (
                        (place,),
                        OTHER_SIDE[self._active_color],
                        self.get_castling_options_after_move_applied(remove),
                        FEN_NULL,
                        0,
                        fullmove_number_for_next_halfmove,
                    ),
                )
            )
            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._position_deltas[-1][1][1:]
            self.append_check_indicator()
            return

        # Pawn move without capture.

        destination = group(IFG_PAWN_FROM_FILE) + group(IFG_PAWN_TO_RANK)
        if destination in piece_placement_data:

            # The pawn-like move has been processed as part of a fully
            # disambiguated piece move.
            if self._full_disambiguation_detected:
                del self._full_disambiguation_detected
                return

            # Allow all movetext like 'e3e4' or 'e3xd4' when _strict_pgn
            # is not enforced, and perhaps even 'e3-e4'.  'exd4' is handled
            # in the 'Pawn move and capture' section, being within the PGN
            # specification.  Pawn promotions such as 'e7e8=Q' or 'e7xf8=Q'
            # are handled here, not by the append_pawn_promote_move method
            # which handles 'e8=Q' and 'exf8=Q'.
            if self._strict_pgn:
                self.append_token_and_set_error(match)
            else:
                self._long_algebraic_notation_pawn_move(match)
            return

        if self._active_color == FEN_WHITE_ACTIVE:
            fullmove_number_for_next_halfmove = self._fullmove_number
            source_squares_index = FEN_WHITE_PAWN
        else:
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
            source_squares_index = FEN_BLACK_PAWN
        try:
            source_squares = SOURCE_SQUARES[source_squares_index][destination]
        except KeyError:
            self.append_token_and_set_error(match)
            return
        for source in source_squares:
            if source in piece_placement_data:
                piece = piece_placement_data[source]
                if FEN_PAWNS.get(piece.name) == self._active_color:
                    if self.line_empty(destination, source):
                        break
        else:
            self.append_token_and_set_error(match)
            return
        remove = piece.square.name, piece
        self.remove_piece_on_square(remove)
        new_en_passant_target_square = EN_PASSANT_TARGET_SQUARES[
            OTHER_SIDE[self._active_color]
        ].get((destination, piece.square.name), FEN_NULL)
        place = destination, piece
        self.place_piece_on_square(place)
        if self.is_square_attacked_by_other_side(
            self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
        ):
            self.remove_piece_on_square(place)
            self.place_piece_on_square(remove)
            self.append_token_and_set_error(match)
            return
        self._text.append(group())
        self.modify_board_state(
            (
                (
                    (remove,),
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ),
                (
                    (place,),
                    OTHER_SIDE[self._active_color],
                    self.get_castling_options_after_move_applied((remove,)),
                    new_en_passant_target_square,
                    0,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = self._position_deltas[-1][1][1:]
        self.append_check_indicator()

    def append_pawn_promote_move(self, match):
        """Append pawn promotion move token from game score.

        Put game in error state if the token represents an illegal move.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        group = match.group
        if group(IFG_PAWN_PROMOTE_TO_RANK) is None:
            self.append_token_and_set_error(match)
            return
        piece_placement_data = self._piece_placement_data

        # Promotion move and capture.

        if group(IFG_PAWN_CAPTURE_TO_FILE):
            destination = group(IFG_PAWN_CAPTURE_TO_FILE) + group(
                IFG_PAWN_PROMOTE_TO_RANK
            )
            pawn_capture_from_file = group(IFG_PAWN_FROM_FILE)
            if self._active_color == FEN_WHITE_ACTIVE:
                fullmove_number_for_next_halfmove = self._fullmove_number
                source_squares_index = FEN_WHITE_PAWN + PGN_CAPTURE_MOVE
            else:
                fullmove_number_for_next_halfmove = self._fullmove_number + 1
                source_squares_index = FEN_BLACK_PAWN + PGN_CAPTURE_MOVE
            try:
                source_squares = SOURCE_SQUARES[source_squares_index][
                    destination
                ]
            except KeyError:
                self.append_token_and_set_error(match)
                return
            for source in source_squares:
                if source.startswith(pawn_capture_from_file):
                    try:
                        if (
                            FEN_PAWNS.get(piece_placement_data[source].name)
                            == self._active_color
                        ):
                            piece = piece_placement_data[source]
                            break
                    except KeyError:
                        self.append_token_and_set_error(match)
                        return
            else:
                self.append_token_and_set_error(match)
                return
            if destination not in piece_placement_data:
                if self._en_passant_target_square == FEN_NULL:
                    self.append_token_and_set_error(match)
                    return
                capture_square = EN_PASSANT_TARGET_SQUARES.get(group()[:4])
                if not capture_square:
                    self.append_token_and_set_error(match)
                    return
                if capture_square not in piece_placement_data:
                    self.append_token_and_set_error(match)
                    return
                if (
                    FEN_PAWNS.get(piece_placement_data[capture_square].name)
                    == self._active_color
                ):
                    self.append_token_and_set_error(match)
                    return
            elif (
                piece_placement_data[source].color
                == piece_placement_data[destination].color
            ):
                self.append_token_and_set_error(match)
                return
            else:
                capture_square = destination
            remove = (
                (capture_square, piece_placement_data[capture_square]),
                (piece.square.name, piece),
            )
            self.remove_piece_from_board(remove[0])
            self.remove_piece_from_board(remove[1])
            promoted_pawn = piece.promoted_pawn(
                PROMOTED_PIECE_NAME[self._active_color][
                    group(IFG_PAWN_PROMOTE_PIECE)
                ],
                destination,
            )
            place = destination, promoted_pawn
            self.place_piece_on_board(place)
            if self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[promoted_pawn.name]][
                    0
                ].square.name
            ):
                self.remove_piece_from_board(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_board(remove[1])
                self.append_token_and_set_error(match)
                return
            self._text.append(group())
            self.modify_board_state(
                (
                    (
                        remove,
                        self._active_color,
                        self._castling_availability,
                        self._en_passant_target_square,
                        self._halfmove_clock,
                        self._fullmove_number,
                    ),
                    (
                        (place,),
                        OTHER_SIDE[self._active_color],
                        self.get_castling_options_after_move_applied(remove),
                        FEN_NULL,
                        0,
                        fullmove_number_for_next_halfmove,
                    ),
                )
            )
            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._position_deltas[-1][1][1:]
            self.append_check_indicator()
            return

        # Promotion move without capture.

        destination = group(IFG_PAWN_FROM_FILE) + group(
            IFG_PAWN_PROMOTE_TO_RANK
        )
        if destination in piece_placement_data:
            self.append_token_and_set_error(match)
            return
        if self._active_color == FEN_WHITE_ACTIVE:
            fullmove_number_for_next_halfmove = self._fullmove_number
            source_squares_index = FEN_WHITE_PAWN
        else:
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
            source_squares_index = FEN_BLACK_PAWN
        try:
            source_squares = SOURCE_SQUARES[source_squares_index][destination]
        except KeyError:
            self.append_token_and_set_error(match)
            return
        for source in source_squares:
            if source in piece_placement_data:
                piece = piece_placement_data[source]
                if FEN_PAWNS.get(piece.name) == self._active_color:
                    if self.line_empty(destination, source):
                        break
        else:
            self.append_token_and_set_error(match)
            return
        remove = piece.square.name, piece
        self.remove_piece_from_board(remove)
        new_en_passant_target_square = FEN_NULL
        promoted_pawn = piece.promoted_pawn(
            PROMOTED_PIECE_NAME[self._active_color][
                group(IFG_PAWN_PROMOTE_PIECE)
            ],
            destination,
        )
        place = destination, promoted_pawn
        self.place_piece_on_board(place)
        if self.is_square_attacked_by_other_side(
            self._pieces_on_board[PIECE_TO_KING[promoted_pawn.name]][
                0
            ].square.name
        ):
            self.remove_piece_from_board(place)
            self.place_piece_on_board(remove)
            self.append_token_and_set_error(match)
            return
        self._text.append(group())
        self.modify_board_state(
            (
                (
                    (remove,),
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ),
                (
                    (place,),
                    OTHER_SIDE[self._active_color],
                    self.get_castling_options_after_move_applied((remove,)),
                    new_en_passant_target_square,
                    0,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = self._position_deltas[-1][1][1:]
        self.append_check_indicator()

    def _continue_current_choice(self):
        # 'Nf3((Nc3)a3(e3))' is a valid way of expressing alternatives to Nf3.
        # Continue with e3 as an alternative to Nf3 if the two RAVs starting
        # before Nc3 refer to same position and there is only one move in the
        # RAV interrupted by '(e3)'.
        ravstack = self._ravstack
        if len(ravstack) < 2:
            return False
        if ravstack[-1][2] is not None:
            return False
        rsac = ravstack[-1][1][1]
        rsfmc = ravstack[-1][1][5]
        if rsfmc != ravstack[-2][3][5]:
            return False
        if rsac != ravstack[-2][3][1]:
            return False
        if (
            self._active_color == FEN_WHITE_ACTIVE
            and rsac == FEN_BLACK_ACTIVE
            and int(rsfmc) + 1 == int(self._fullmove_number)
        ):
            return True
        if (
            self._active_color == FEN_BLACK_ACTIVE
            and rsac == FEN_WHITE_ACTIVE
            and int(rsfmc) == int(self._fullmove_number)
        ):
            return True
        return False

    def append_start_rav(self, match):
        """Append start recursive annotation variation token to game score.

        Put game in error state if a variation cannot be put at current place
        in game score.

        """
        # The formal syntax for PGN, section 18 in specification, allows text
        # such as, for example:
        # '12 ( 12. e4 )'
        # '. ( 12 e4 )'
        # '...... ( 12 e4 )'
        # '...12... 13 ( 12 e4 )'
        # This program ignores numbers and dots for state and storage of games.
        # The formal syntax also allows recursive annotation variations before
        # the first SAN-move.  Section 8.2.5 in specification implies recursive
        # annotation variations must be preceded by a SAN-move.  Section 8.2.5
        # is implemented here because a variation varies from something.
        if self._movetext_offset is None:
            self.append_token_and_set_error(match)
            return

        if len(self._ravstack[-1]) == 1:
            if self._position_deltas[-1] is None:
                self.append_token_and_set_error(match)
                return
            if len(self._position_deltas[-1]) == 1:
                self.set_position_to_play_right_nested_rav_at_move()
            else:
                self.set_position_to_play_first_rav_at_move()

        # The 'Nf3((Nc3)a3(e3))' cases caught here fail the tests below on
        # self._ravstack[-1][2] because it is None, but are processed in
        # the same way.
        elif self._continue_current_choice():

            # Clear out stuff left over from previous RAV at this level.
            del self._ravstack[-1][1:]

            self.set_position_to_play_first_rav_at_move()
        elif (
            self._ravstack[-1][2][1] != self._active_color
            or self._ravstack[-1][2][5] != self._fullmove_number
        ):

            # Clear out stuff left over from previous RAV at this level.
            del self._ravstack[-1][1:]

            self.set_position_to_play_first_rav_at_move()
        else:
            self.reset_board_state(
                ((self._ravstack[-1][1],) + self._ravstack[-1][-1][1:],)
            )

            # This is most of set_position_to_play_right_nested_rav_at_move.
            rav_piece_placement_data = self._position_deltas[-1][0][0]
            pieces_on_board = self._pieces_on_board
            for val in pieces_on_board.values():
                val.clear()
            piece_placement_data = self._piece_placement_data
            piece_placement_data.clear()
            for piece, square in rav_piece_placement_data:
                piece_placement_data[square] = piece
                piece.set_square(square)
                if piece.name == FEN_WHITE_PAWN:
                    pieces_on_board[piece.square.file + FEN_WHITE_PAWN].append(
                        piece
                    )
                elif piece.name == FEN_BLACK_PAWN:
                    pieces_on_board[piece.square.file + FEN_BLACK_PAWN].append(
                        piece
                    )
                else:
                    pieces_on_board[piece.name].append(piece)

            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._ravstack[-1][-1][1:]
        self._ravstack[-1][0] += 1
        self._ravstack.append([0])
        self._text.append(match.group())
        self._state_stack.append(self._state)

    def append_end_rav(self, match):
        """Append end recursive annotation variation token to game score.

        Put game in error state if a variation cannot be finished at current
        place in game score.

        """
        # Return True if ')' is valid: for benefit of subclass caller to decide
        # on it's action.
        # The formal syntax for PGN, section 18 in specification, allows text
        # such as, for example:
        # '( e4 12 )'
        # '( e4 . )'
        # '( e4 ...... )'
        # '( e4 ...12... 13 )'
        # This program ignores numbers and dots for state and storage of games.
        if self._state is not None or self._movetext_offset is None:
            self.append_token_and_set_error(match)
            return None

        if self._movetext_offset is None:
            self.append_token_and_set_error(match)
            return None
        if len(self._ravstack) == 1:
            self.append_token_and_set_error(match)
            return None
        del self._ravstack[-1]
        del self._state_stack[-1]
        self._state = self._state_stack[-1]

        # The formal syntax for PGN, section 18 in specification, allows '()'
        # as a recursive annotation variation.
        # The commented code bans this sequence.
        # if (self._active_color == self._ravstack[-1][3][1] and
        #    self._fullmove_number == self._ravstack[-1][3][5]):
        #    self.append_token_and_set_error(match)
        #    return None

        if self._ravstack[-1][2] is None:
            self.set_position_to_play_prior_right_nested_rav_at_move()
        else:
            self.set_position_to_play_main_line_at_move()
        self._text.append(match.group())
        return True

    def append_game_termination(self, match):
        """Append game termination token to game score and update game state.

        Put game in error state if no moves exists in game score and the
        initial position is not valid.  Validation includes piece counts and
        some piece placement: pawns on ranks 2 to 7 only and king of active
        color not in check for example.  Verification that the initial position
        declared in a PGN FEN tag is reachable from the standard starting
        position is not attempted.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self.append_token_and_set_error(match)
                return
            self._movetext_offset = len(self._text)
        self._text.append(match.group())
        self.add_board_state_none(None)

    def append_glyph_for_traditional_annotation(self, match):
        """Append NAG for traditional annotation to game score.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(SUFFIX_ANNOTATION_TO_NAG[match.group()])
        try:
            self.repeat_board_state(self._position_deltas[-1])
        except IndexError:
            self.add_board_state_none(None)

    def ignore_escape(self, match):
        r"""Ignore escape token and rest of line containing the token.

        The '\n' termination for the escaped line is not captured because it
        may start an escaped line.

        The '\n' must be appended to the token in subclasses which capture
        the escaped line.

        """

    def ignore_end_of_file_marker_prefix_to_tag(self, match):
        r"""Ignore end of file marker if it is prefix to a PGN tag.

        Concatenated PGN files may have an end of file marker, '\032' also
        called Ctrl-Z, followed immediately by the PGN Tag which was at start
        of next file.  This breaks the PGN specification because the PGN tag is
        not at the start of a line.

        Strictly Ctrl-Z is one of the ASCII control characters not permitted
        in PGN files, 4.1 in PGN specification, but according to Wikipedia,
        en.wikipedia.org/wiki/End-of-file, the end of file marker exists for
        two reasons.  One suggestion on the 'talk' page is Ctrl-Z was never
        necessary but in practice useful for a while in the 1980s.

        """

    def ignore_move_number(self, match):
        """Ignore move number indication token."""

    def ignore_dots(self, match):
        """Ignore dot sequence token.

        The PGN specification mentions dots as part of move number indication,
        '12.' and '12...' for example.  This class ignores any sequence of
        dots containing at least one dot in sequences of valid tokens.

        """

    def ignore_check_indicator(self, match):
        """Ignore check indicator indication token.

        Check indicators are required in PGN export format.  This PGN parser
        verifies a move does not leave the moving side's king in check, but
        takes no interest in whether a move gives check or checkmate except
        for output in PGN export format.  Game.append_check_indicator can
        be overridden to do this.

        """

    def _disambiguate_piece_move(self, match):
        group = match.group
        if self._active_color == FEN_WHITE_ACTIVE:
            piece_name = group(IFG_PIECE_MOVE)
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            piece_name = group(IFG_PIECE_MOVE).lower()
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        peek_start = match.span(match.lastindex)[-1]
        dtfm = disambiguate_text_format.match(
            match.string[peek_start : peek_start + 10]
        )
        if not dtfm:
            self.append_token_and_set_error(match)
            return
        piece_placement_data = self._piece_placement_data
        piece = piece_placement_data[group(IFG_PIECE_DESTINATION)]
        destination = dtfm.group(DG_DESTINATION)
        source_squares = SOURCE_SQUARES[group(IFG_PIECE_MOVE)][destination]

        # Piece move and capture.

        if dtfm.group(DG_CAPTURE):
            if destination not in piece_placement_data:
                self.append_token_and_set_error(match)
                return
            candidates = []
            for cpiece in self._pieces_on_board[piece_name]:
                if cpiece.square.name in source_squares:
                    candidates.append(cpiece)
            file_count = 0
            rank_count = 0
            sfile, srank = piece.square.name
            for cpiece in candidates:
                if not self.line_empty(cpiece.square.name, destination):
                    continue
                cpfile, cprank = cpiece.square.name
                remove = (
                    (destination, piece_placement_data[destination]),
                    (cpiece.square.name, cpiece),
                )
                self.remove_piece_from_board(remove[0])
                self.remove_piece_on_square(remove[1])
                place = destination, cpiece
                self.place_piece_on_square(place)
                if not self.is_square_attacked_by_other_side(
                    self._pieces_on_board[PIECE_TO_KING[cpiece.name]][
                        0
                    ].square.name
                ):
                    if cpfile == sfile:
                        file_count += 1
                    if cprank == srank:
                        rank_count += 1
                self.remove_piece_on_square(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_square(remove[1])
            if file_count < 2 or rank_count < 2:
                self.append_token_and_set_error(match)
                return
            remove = (
                (destination, piece_placement_data[destination]),
                (piece.square.name, piece),
            )
            self.remove_piece_from_board(remove[0])
            self.remove_piece_on_square(remove[1])
            place = destination, piece, piece.name
            self.place_piece_on_square(place)
            if self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
            ):
                self.remove_piece_on_square(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_square(remove[1])
                self.append_token_and_set_error(match)
                return
            self._text.append(group() + dtfm.group())
            self.modify_board_state(
                (
                    (
                        remove,
                        self._active_color,
                        self._castling_availability,
                        self._en_passant_target_square,
                        self._halfmove_clock,
                        self._fullmove_number,
                    ),
                    (
                        (place,),
                        OTHER_SIDE[self._active_color],
                        self.get_castling_options_after_move_applied(remove),
                        FEN_NULL,
                        0,
                        fullmove_number_for_next_halfmove,
                    ),
                )
            )
            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._position_deltas[-1][1][1:]
            self._full_disambiguation_detected = True
            self.append_check_indicator()
            return

        # Piece move without capture.
        candidates = []
        for cpiece in self._pieces_on_board[piece_name]:
            if cpiece.square.name in source_squares:
                candidates.append(cpiece)
        file_count = 0
        rank_count = 0
        sfile, srank = piece.square.name
        for cpiece in candidates:
            if not self.line_empty(cpiece.square.name, destination):
                continue
            cpfile, cprank = cpiece.square.name
            remove = cpiece.square.name, cpiece
            self.remove_piece_on_square(remove)
            place = destination, cpiece
            self.place_piece_on_square(place)
            if not self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[cpiece.name]][
                    0
                ].square.name
            ):
                if cpfile == sfile:
                    file_count += 1
                if cprank == srank:
                    rank_count += 1
            self.remove_piece_on_square(place)
            self.place_piece_on_square(remove)
        if file_count < 2 or rank_count < 2:
            self.append_token_and_set_error(match)
            return
        remove = piece.square.name, piece
        self.remove_piece_on_square(remove)
        place = destination, piece
        self.place_piece_on_square(place)
        if self.is_square_attacked_by_other_side(
            self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
        ):
            self.remove_piece_on_square(place)
            self.place_piece_on_square(remove)
            self.append_token_and_set_error(match)
            return
        self._text.append(group() + dtfm.group())
        self.modify_board_state(
            (
                (
                    (remove,),
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ),
                (
                    (place,),
                    OTHER_SIDE[self._active_color],
                    self.get_castling_options_after_move_applied((remove,)),
                    FEN_NULL,
                    self._halfmove_clock + 1,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = self._position_deltas[-1][1][1:]
        self.append_check_indicator()
        self._full_disambiguation_detected = True

    def _long_algebraic_notation_destination(self, match):
        peek_start = match.span(match.lastindex)[-1]
        pms = match.string[peek_start : peek_start + 10]
        lfm = lan_format.match(pms.lower())
        if lfm:
            if isinstance(self, (GameIgnoreCasePGN, GameTextPGN)):
                return lfm
            if pms.startswith(lfm.group()):
                return lfm
        return None

    def _long_algebraic_notation_piece_move(self, match):
        group = match.group
        if self._active_color == FEN_WHITE_ACTIVE:
            piece_name = group(IFG_PIECE_MOVE)
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            piece_name = group(IFG_PIECE_MOVE).lower()
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        landm = self._long_algebraic_notation_destination(match)

        # This token must be a match as second part of move, and must be
        # correct as a pawn or piece move in combination with first part.
        if not landm:
            self.append_token_and_set_error(match)
            return

        piece_placement_data = self._piece_placement_data
        capture, destination, promotion_piece = landm.groups()
        if capture != PGN_CAPTURE_MOVE:
            if destination in piece_placement_data:
                self.append_token_and_set_error(match)
                return
        elif destination not in piece_placement_data:
            self.append_token_and_set_error(match)
            return

        # Piece move.
        if piece_name:
            if promotion_piece:
                self.append_token_and_set_error(match)
                return
            piece = piece_placement_data[group(IFG_PIECE_DESTINATION)]
            source_squares = SOURCE_SQUARES[group(IFG_PIECE_MOVE)][destination]

            # Piece move and capture.
            if capture == PGN_CAPTURE_MOVE:
                candidates = []
                for cpiece in self._pieces_on_board[piece_name]:
                    if cpiece.square.name in source_squares:
                        candidates.append(cpiece)
                if not candidates:
                    self.append_token_and_set_error(match)
                    return
                file_count = {}
                rank_count = {}
                if len(candidates) > 1:
                    sfile, srank = piece.square.name
                    for cpiece in candidates:
                        if not self.line_empty(
                            cpiece.square.name, destination
                        ):
                            continue
                        cpfile, cprank = cpiece.square.name
                        remove = (
                            (destination, piece_placement_data[destination]),
                            (cpiece.square.name, cpiece),
                        )
                        self.remove_piece_from_board(remove[0])
                        self.remove_piece_on_square(remove[1])
                        place = destination, cpiece
                        self.place_piece_on_square(place)
                        if not self.is_square_attacked_by_other_side(
                            self._pieces_on_board[PIECE_TO_KING[cpiece.name]][
                                0
                            ].square.name
                        ):
                            if cpfile not in file_count:
                                file_count[cpfile] = 1
                            else:
                                file_count[cpfile] += 1
                            if cprank not in rank_count:
                                rank_count[cprank] = 1
                            else:
                                rank_count[cprank] += 1
                        self.remove_piece_on_square(place)
                        self.place_piece_on_board(remove[0])
                        self.place_piece_on_square(remove[1])
                if not self.line_empty(piece.square.name, destination):
                    self.append_token_and_set_error(match)
                    return
                remove = (
                    (destination, piece_placement_data[destination]),
                    (piece.square.name, piece),
                )
                self.remove_piece_from_board(remove[0])
                self.remove_piece_on_square(remove[1])
                place = destination, piece
                self.place_piece_on_square(place)
                if self.is_square_attacked_by_other_side(
                    self._pieces_on_board[PIECE_TO_KING[piece.name]][
                        0
                    ].square.name
                ):
                    self.remove_piece_on_square(place)
                    self.place_piece_on_board(remove[0])
                    self.place_piece_on_square(remove[1])
                    self.append_token_and_set_error(match)
                    return
                if len(file_count) < 2 and len(rank_count) < 2:
                    self._text.append(
                        PGN_CAPTURE_MOVE.join(
                            (group(IFG_PIECE_MOVE), destination)
                        )
                    )
                elif file_count[sfile] == 1:
                    self._text.append(
                        "".join(
                            (
                                group(IFG_PIECE_MOVE),
                                sfile,
                                PGN_CAPTURE_MOVE,
                                destination,
                            )
                        )
                    )
                elif rank_count[srank] == 1:
                    self._text.append(
                        "".join(
                            (
                                group(IFG_PIECE_MOVE),
                                srank,
                                PGN_CAPTURE_MOVE,
                                destination,
                            )
                        )
                    )
                else:
                    self._text.append(
                        "".join(
                            (
                                group(IFG_PIECE_MOVE),
                                sfile,
                                srank,
                                PGN_CAPTURE_MOVE,
                                destination,
                            )
                        )
                    )
                self.modify_board_state(
                    (
                        (
                            remove,
                            self._active_color,
                            self._castling_availability,
                            self._en_passant_target_square,
                            self._halfmove_clock,
                            self._fullmove_number,
                        ),
                        (
                            (place,),
                            OTHER_SIDE[self._active_color],
                            self.get_castling_options_after_move_applied(
                                remove
                            ),
                            FEN_NULL,
                            0,
                            fullmove_number_for_next_halfmove,
                        ),
                    )
                )
                (
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ) = self._position_deltas[-1][1][1:]
                self.append_check_indicator()
                self._full_disambiguation_detected = True
                return

            # Piece move without capture.
            candidates = []
            for cpiece in self._pieces_on_board[piece_name]:
                if cpiece.square.name in source_squares:
                    candidates.append(cpiece)
            if not candidates:
                self.append_token_and_set_error(match)
                return
            file_count = {}
            rank_count = {}
            if len(candidates) > 1:
                sfile, srank = piece.square.name
                for cpiece in candidates:
                    if not self.line_empty(cpiece.square.name, destination):
                        continue
                    cpfile, cprank = cpiece.square.name
                    remove = cpiece.square.name, cpiece
                    self.remove_piece_on_square(remove)
                    place = destination, cpiece
                    self.place_piece_on_square(place)
                    if not self.is_square_attacked_by_other_side(
                        self._pieces_on_board[PIECE_TO_KING[cpiece.name]][
                            0
                        ].square.name
                    ):
                        if cpfile not in file_count:
                            file_count[cpfile] = 1
                        else:
                            file_count[cpfile] += 1
                        if cprank not in rank_count:
                            rank_count[cprank] = 1
                        else:
                            rank_count[cprank] += 1
                    self.remove_piece_on_square(place)
                    self.place_piece_on_square(remove)
            if not self.line_empty(piece.square.name, destination):
                self.append_token_and_set_error(match)
                return
            remove = piece.square.name, piece
            self.remove_piece_on_square(remove)
            place = destination, piece
            self.place_piece_on_square(place)
            if self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
            ):
                self.remove_piece_on_square(place)
                self.place_piece_on_square(remove)
                self.append_token_and_set_error(match)
                return
            if len(file_count) < 2 and len(rank_count) < 2:
                self._text.append(group(IFG_PIECE_MOVE) + destination)
            elif file_count[sfile] == 1:
                self._text.append(
                    "".join((group(IFG_PIECE_MOVE), sfile, destination))
                )
            elif rank_count[srank] == 1:
                self._text.append(
                    "".join((group(IFG_PIECE_MOVE), srank, destination))
                )
            else:
                self._text.append(
                    "".join((group(IFG_PIECE_MOVE), sfile, srank, destination))
                )
            self.modify_board_state(
                (
                    (
                        (remove,),
                        self._active_color,
                        self._castling_availability,
                        self._en_passant_target_square,
                        self._halfmove_clock,
                        self._fullmove_number,
                    ),
                    (
                        (place,),
                        OTHER_SIDE[self._active_color],
                        self.get_castling_options_after_move_applied(
                            (remove,)
                        ),
                        FEN_NULL,
                        self._halfmove_clock + 1,
                        fullmove_number_for_next_halfmove,
                    ),
                )
            )
            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._position_deltas[-1][1][1:]
            self.append_check_indicator()
            self._full_disambiguation_detected = True
            return

    def _long_algebraic_notation_pawn_move(self, match):
        group = match.group
        if self._active_color == FEN_WHITE_ACTIVE:
            source_squares_index = FEN_WHITE_PAWN
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            source_squares_index = FEN_BLACK_PAWN
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        square_name = group(IFG_PAWN_FROM_FILE) + group(IFG_PAWN_TO_RANK)
        landm = self._long_algebraic_notation_destination(match)

        # This token must be a match as second part of move, and must be
        # correct as a pawn or piece move in combination with first part.
        if not landm:
            self.append_token_and_set_error(match)
            return

        piece_placement_data = self._piece_placement_data
        capture, destination, promotion_piece = landm.groups()
        if capture != PGN_CAPTURE_MOVE:
            if destination in piece_placement_data:
                self.append_token_and_set_error(match)
                return
        elif self._en_passant_target_square == FEN_NULL:
            if destination not in piece_placement_data:
                self.append_token_and_set_error(match)
                return
        elif self._en_passant_target_square != destination:
            if destination not in piece_placement_data:
                self.append_token_and_set_error(match)
                return
        elif destination in piece_placement_data:
            try:
                raise GameError(
                    "".join(
                        (
                            "En-passant target square '",
                            self._en_passant_target_square,
                            "' is not consistent with position on board '",
                            generate_fen_for_position(
                                piece_placement_data.values(),
                                self._active_color,
                                self._castling_availability,
                                self._en_passant_target_square,
                                self._halfmove_clock,
                                self._fullmove_number,
                            ),
                        )
                    )
                )
            except:
                raise GameError(
                    "En-passant target square does not fit position"
                )

        if destination[1] in "18":
            if not promotion_piece:
                self.append_token_and_set_error(match)
                return
            promotion_piece = promotion_piece.upper()

            # Promotion move and capture.
            if capture == PGN_CAPTURE_MOVE:
                if (
                    square_name
                    not in SOURCE_SQUARES[
                        source_squares_index + PGN_CAPTURE_MOVE
                    ][destination]
                ):
                    self.append_token_and_set_error(match)
                    return
                if destination not in piece_placement_data:
                    self.append_token_and_set_error(match)
                    return
                if (
                    piece_placement_data[square_name].color
                    == piece_placement_data[destination].color
                ):
                    self.append_token_and_set_error(match)
                    return
                remove = (
                    (destination, piece_placement_data[destination]),
                    (piece.square.name, piece),
                )
                self.remove_piece_from_board(remove[0])
                self.remove_piece_from_board(remove[1])
                promoted_pawn = piece.promoted_pawn(
                    PROMOTED_PIECE_NAME[self._active_color][promotion_piece],
                    destination,
                )
                place = destination, promoted_pawn
                self.place_piece_on_board(place)
                if self.is_square_attacked_by_other_side(
                    self._pieces_on_board[PIECE_TO_KING[promoted_pawn.name]][
                        0
                    ].square.name
                ):
                    self.remove_piece_from_board(place)
                    self.place_piece_on_board(remove[0])
                    self.place_piece_on_board(remove[1])
                    self.append_token_and_set_error(match)
                    return
                self._text.append(group())
                self.modify_board_state(
                    (
                        (
                            remove,
                            self._active_color,
                            self._castling_availability,
                            self._en_passant_target_square,
                            self._halfmove_clock,
                            self._fullmove_number,
                        ),
                        (
                            (place,),
                            OTHER_SIDE[self._active_color],
                            self.get_castling_options_after_move_applied(
                                remove
                            ),
                            FEN_NULL,
                            0,
                            fullmove_number_for_next_halfmove,
                        ),
                    )
                )
                (
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ) = self._position_deltas[-1][1][1:]
                self.append_check_indicator()
                return

            # Promotion move without capture.
            if (
                square_name
                not in SOURCE_SQUARES[source_squares_index][destination]
            ):
                self.append_token_and_set_error(match)
                return
            piece = piece_placement_data[square_name]
            remove = piece.square.name, piece
            self.remove_piece_from_board(remove)
            promoted_pawn = piece.promoted_pawn(
                PROMOTED_PIECE_NAME[self._active_color][promotion_piece],
                destination,
            )
            place = destination, promoted_pawn
            self.place_piece_on_board(place)
            if self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[promoted_pawn.name]][
                    0
                ].square.name
            ):
                self.remove_piece_from_board(place)
                self.place_piece_on_board(remove)
                self.append_token_and_set_error(match)
                return
            self._text.append(group())
            self.modify_board_state(
                (
                    (
                        (remove,),
                        self._active_color,
                        self._castling_availability,
                        self._en_passant_target_square,
                        self._halfmove_clock,
                        self._fullmove_number,
                    ),
                    (
                        (place,),
                        OTHER_SIDE[self._active_color],
                        self.get_castling_options_after_move_applied(
                            (remove,)
                        ),
                        FEN_NULL,
                        0,
                        fullmove_number_for_next_halfmove,
                    ),
                )
            )
            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._position_deltas[-1][1][1:]
            self.append_check_indicator()

            self.append_token_and_set_error(match)
            return

        # Pawn move and capture.
        if promotion_piece:
            self.append_token_and_set_error(match)
            return
        if capture == PGN_CAPTURE_MOVE:
            if (
                square_name
                not in SOURCE_SQUARES[source_squares_index + PGN_CAPTURE_MOVE][
                    destination
                ]
            ):
                self.append_token_and_set_error(match)
                return
            piece = piece_placement_data[square_name]
            if FEN_PAWNS.get(piece.name) != self._active_color:
                self.append_token_and_set_error(match)
                return
            if not self.line_empty(destination, square_name):
                self.append_token_and_set_error(match)
                return
            if destination not in piece_placement_data:
                capture_square = EN_PASSANT_TARGET_SQUARES.get(
                    PGN_CAPTURE_MOVE.join(
                        (group(IFG_PAWN_FROM_FILE), destination)
                    )
                )
                if not capture_square:
                    self.append_token_and_set_error(match)
                    return
                if capture_square not in piece_placement_data:
                    self.append_token_and_set_error(match)
                    return
                if (
                    FEN_PAWNS.get(piece_placement_data[capture_square].name)
                    == self._active_color
                ):
                    self.append_token_and_set_error(match)
                    return
            elif (
                piece_placement_data[square_name].color
                == piece_placement_data[destination].color
            ):
                self.append_token_and_set_error(match)
                return
            else:
                capture_square = destination
            remove = (
                (capture_square, piece_placement_data[capture_square]),
                (piece.square.name, piece),
            )
            self.remove_piece_from_board(remove[0])
            self.remove_piece_from_board(remove[1])
            place = destination, piece
            self.place_piece_on_board(place)
            if self.is_square_attacked_by_other_side(
                self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
            ):
                self.remove_piece_from_board(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_board(remove[1])
                self.append_token_and_set_error(match)
                return
            self._text.append(
                PGN_CAPTURE_MOVE.join(
                    (group(IFG_PAWN_FROM_FILE), capture_square)
                )
            )
            self.modify_board_state(
                (
                    (
                        remove,
                        self._active_color,
                        self._castling_availability,
                        self._en_passant_target_square,
                        self._halfmove_clock,
                        self._fullmove_number,
                    ),
                    (
                        (place,),
                        OTHER_SIDE[self._active_color],
                        self.get_castling_options_after_move_applied(remove),
                        FEN_NULL,
                        0,
                        fullmove_number_for_next_halfmove,
                    ),
                )
            )
            (
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            ) = self._position_deltas[-1][1][1:]
            self.append_check_indicator()
            return

        # Pawn move without capturing or promoting.
        if (
            square_name
            not in SOURCE_SQUARES[source_squares_index][destination]
        ):
            self.append_token_and_set_error(match)
            return
        piece = piece_placement_data[square_name]
        if FEN_PAWNS.get(piece.name) != self._active_color:
            self.append_token_and_set_error(match)
            return
        if not self.line_empty(destination, square_name):
            self.append_token_and_set_error(match)
            return
        remove = piece.square.name, piece
        self.remove_piece_on_square(remove)
        new_en_passant_target_square = EN_PASSANT_TARGET_SQUARES[
            OTHER_SIDE[self._active_color]
        ].get((destination, piece.square.name), FEN_NULL)
        place = destination, piece
        self.place_piece_on_square(place)
        if self.is_square_attacked_by_other_side(
            self._pieces_on_board[PIECE_TO_KING[piece.name]][0].square.name
        ):
            self.remove_piece_on_square(place)
            self.place_piece_on_square(remove)
            self.append_token_and_set_error(match)
            return
        self._text.append(destination)
        self.modify_board_state(
            (
                (
                    (remove,),
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ),
                (
                    (place,),
                    OTHER_SIDE[self._active_color],
                    self.get_castling_options_after_move_applied((remove,)),
                    new_en_passant_target_square,
                    0,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = self._position_deltas[-1][1][1:]
        self.append_check_indicator()
        self._full_disambiguation_detected = True

    def set_initial_position(self):
        """Initialise board state, using PGN FEN tag if there is one.

        Default is the standard starting position.

        """
        # If both FEN and SetUp tags are present the SetUP value must be '1'.
        # If only the SetUp tag is present it's value must be '0'.
        tag_fen = self._tags.get(TAG_FEN)
        tag_setup = self._tags.get(TAG_SETUP, SETUP_VALUE_FEN_ABSENT)
        if (tag_fen is not None and tag_setup != SETUP_VALUE_FEN_PRESENT) or (
            tag_fen is None and tag_setup != SETUP_VALUE_FEN_ABSENT
        ):
            if self._state is None:
                for token_number, mvt in enumerate(self._text):
                    if (
                        mvt[IFG_TAG_NAME] == TAG_FEN
                        or mvt[IFG_TAG_NAME] == TAG_SETUP
                    ):
                        self._state = token_number
                        self._state_stack[-1] = self._state
                        break
                else:
                    self._state = len(self._text)
                    self._state_stack[-1] = self._state
                return False

        pieces_on_board = self._pieces_on_board
        board = []
        piece_placement_data = self._piece_placement_data
        for piece in (
            FEN_WHITE_KING,
            FEN_WHITE_QUEEN,
            FEN_WHITE_ROOK,
            FEN_WHITE_BISHOP,
            FEN_WHITE_KNIGHT,
            FEN_BLACK_KING,
            FEN_BLACK_QUEEN,
            FEN_BLACK_ROOK,
            FEN_BLACK_BISHOP,
            FEN_BLACK_KNIGHT,
        ):
            pieces_on_board[piece] = []
        for file in FILE_NAMES:
            for piece in FEN_WHITE_PAWN, FEN_BLACK_PAWN:
                pieces_on_board[file + piece] = []
        if tag_fen is not None:
            tff = tag_fen.split(FEN_FIELD_DELIM)
            if len(tff) != FEN_FIELD_COUNT:
                self._state = len(self._text)
                self._state_stack[-1] = self._state
                return False
            active_color = tff[FEN_ACTIVE_COLOR_FIELD_INDEX]
            if active_color not in FEN_WHITE_ACTIVE + FEN_BLACK_ACTIVE:
                self._state = len(self._text)
                self._state_stack[-1] = self._state
                return False
            i = 0
            for fen_char in tff[FEN_PIECE_PLACEMENT_FIELD_INDEX]:
                if fen_char == FEN_RANK_DELIM:
                    if divmod(i, 8)[1]:
                        self._state = len(self._text)
                        self._state_stack[-1] = self._state
                        return False
                    continue
                if fen_char in RANK_NAMES:
                    i += int(fen_char)
                    continue
                if fen_char not in FEN_PIECE_NAMES:
                    self._state = len(self._text)
                    self._state_stack[-1] = self._state
                    return False
                rank, file = divmod(i, 8)
                piece = Piece(fen_char, FILE_NAMES[file] + RANK_NAMES[rank])
                piece_placement_data[piece.square.name] = piece
                board.append(piece)
                if fen_char == FEN_WHITE_PAWN:
                    pieces_on_board[piece.square.file + FEN_WHITE_PAWN].append(
                        piece
                    )
                    if piece.square.rank in "18":
                        return False
                elif fen_char == FEN_BLACK_PAWN:
                    pieces_on_board[piece.square.file + FEN_BLACK_PAWN].append(
                        piece
                    )
                    if piece.square.rank in "18":
                        return False
                else:
                    pieces_on_board[fen_char].append(piece)
                i += 1
            if i != len(RANK_NAMES) * len(FILE_NAMES):
                return False
            castling_availability = tff[FEN_CASTLING_AVAILABILITY_FIELD_INDEX]
            if castling_availability != FEN_NULL:
                if set(FEN_INITIAL_CASTLING).union(tff[2]) != set(
                    FEN_INITIAL_CASTLING
                ):
                    self._state = len(self._text)
                    self._state_stack[-1] = self._state
                    return False
                for square, castling_option in CASTLING_RIGHTS.items():
                    if square not in piece_placement_data:
                        if castling_option in castling_availability:
                            self._state = len(self._text)
                            self._state_stack[-1] = self._state
                            return False
                        continue
                    for option in castling_option:
                        if option not in castling_availability:
                            continue
                        if (
                            piece_placement_data[square].name
                            != CASTLING_PIECE_FOR_SQUARE[square]
                        ):
                            self._state = len(self._text)
                            self._state_stack[-1] = self._state
                            return False
            en_passant_target_square = tff[
                FEN_EN_PASSANT_TARGET_SQUARE_FIELD_INDEX
            ]
            if en_passant_target_square != FEN_NULL:
                if en_passant_target_square not in Squares.squares:
                    return False
                if active_color == FEN_WHITE_ACTIVE:
                    target_pawn = FEN_BLACK_PAWN
                else:
                    target_pawn = FEN_WHITE_PAWN
                if en_passant_target_square in piece_placement_data:
                    return False
                for k, target_square in EN_PASSANT_TARGET_SQUARES[
                    active_color
                ].items():
                    if target_square == en_passant_target_square:
                        occupied_square, source_square = k
                        if source_square in piece_placement_data:
                            return False
                        if occupied_square not in piece_placement_data:
                            return False
                        if (
                            piece_placement_data[occupied_square].name
                            != target_pawn
                        ):
                            return False
                        break
                else:
                    return False
            white_king_count = 0
            white_queen_count = 0
            white_rook_count = 0
            white_bishop_count = 0
            white_knight_count = 0
            white_pawn_count = 0
            black_king_count = 0
            black_queen_count = 0
            black_rook_count = 0
            black_bishop_count = 0
            black_knight_count = 0
            black_pawn_count = 0
            for pce in board:
                if pce.name == FEN_WHITE_KING:
                    white_king_count += 1
                elif pce.name == FEN_WHITE_QUEEN:
                    white_queen_count += 1
                elif pce.name == FEN_WHITE_ROOK:
                    white_rook_count += 1
                elif pce.name == FEN_WHITE_BISHOP:
                    white_bishop_count += 1
                elif pce.name == FEN_WHITE_KNIGHT:
                    white_knight_count += 1
                elif pce.name == FEN_WHITE_PAWN:
                    white_pawn_count += 1
                elif pce.name == FEN_BLACK_KING:
                    black_king_count += 1
                elif pce.name == FEN_BLACK_QUEEN:
                    black_queen_count += 1
                elif pce.name == FEN_BLACK_ROOK:
                    black_rook_count += 1
                elif pce.name == FEN_BLACK_BISHOP:
                    black_bishop_count += 1
                elif pce.name == FEN_BLACK_KNIGHT:
                    black_knight_count += 1
                elif pce.name == FEN_BLACK_PAWN:
                    black_pawn_count += 1
            if white_king_count != 1 or black_king_count != 1:
                return False
            if white_pawn_count > 8 or black_pawn_count > 8:
                return False
            if (
                white_queen_count
                + white_rook_count
                + white_bishop_count
                + white_knight_count
            ) > 7 + 8 - white_pawn_count:
                return False
            if (
                black_queen_count
                + black_rook_count
                + black_bishop_count
                + black_knight_count
            ) > 7 + 8 - black_pawn_count:
                return False
            if white_queen_count + white_pawn_count > 9:
                return False
            if black_queen_count + black_pawn_count > 9:
                return False
            for count in (
                white_rook_count,
                white_bishop_count,
                white_knight_count,
            ):
                if count + white_pawn_count > 10:
                    return False
            for count in (
                black_rook_count,
                black_bishop_count,
                black_knight_count,
            ):
                if count + black_pawn_count > 10:
                    return False
            halfmove_clock = tff[FEN_HALFMOVE_CLOCK_FIELD_INDEX]
            if not halfmove_clock.isdigit():
                self._state = len(self._text)
                self._state_stack[-1] = self._state
                return False
            fullmove_number = tff[FEN_FULLMOVE_NUMBER_FIELD_INDEX]
            if not fullmove_number.isdigit():
                self._state = len(self._text)
                self._state_stack[-1] = self._state
                return False
            if active_color == FEN_WHITE_ACTIVE:
                king = FEN_BLACK_KING
            else:
                king = FEN_WHITE_KING
            for piece in board:
                if piece.name == king:
                    self._active_color = OTHER_SIDE[active_color]
                    if self.is_square_attacked_by_other_side(
                        piece.square.name
                    ):
                        self._active_color = active_color
                        return False
                    break
            else:
                return False
            self._active_color = active_color
            self._en_passant_target_square = en_passant_target_square
            self._castling_availability = castling_availability
            self._halfmove_clock = int(halfmove_clock)
            self._fullmove_number = int(fullmove_number)
        else:
            board.extend(
                [
                    Piece(FEN_BLACK_ROOK, FILE_NAMES[0] + RANK_NAMES[0]),
                    Piece(FEN_BLACK_KNIGHT, FILE_NAMES[1] + RANK_NAMES[0]),
                    Piece(FEN_BLACK_BISHOP, FILE_NAMES[2] + RANK_NAMES[0]),
                    Piece(FEN_BLACK_QUEEN, FILE_NAMES[3] + RANK_NAMES[0]),
                    Piece(FEN_BLACK_KING, FILE_NAMES[4] + RANK_NAMES[0]),
                    Piece(FEN_BLACK_BISHOP, FILE_NAMES[5] + RANK_NAMES[0]),
                    Piece(FEN_BLACK_KNIGHT, FILE_NAMES[6] + RANK_NAMES[0]),
                    Piece(FEN_BLACK_ROOK, FILE_NAMES[7] + RANK_NAMES[0]),
                    Piece(FEN_BLACK_PAWN, FILE_NAMES[0] + RANK_NAMES[1]),
                    Piece(FEN_BLACK_PAWN, FILE_NAMES[1] + RANK_NAMES[1]),
                    Piece(FEN_BLACK_PAWN, FILE_NAMES[2] + RANK_NAMES[1]),
                    Piece(FEN_BLACK_PAWN, FILE_NAMES[3] + RANK_NAMES[1]),
                    Piece(FEN_BLACK_PAWN, FILE_NAMES[4] + RANK_NAMES[1]),
                    Piece(FEN_BLACK_PAWN, FILE_NAMES[5] + RANK_NAMES[1]),
                    Piece(FEN_BLACK_PAWN, FILE_NAMES[6] + RANK_NAMES[1]),
                    Piece(FEN_BLACK_PAWN, FILE_NAMES[7] + RANK_NAMES[1]),
                    Piece(FEN_WHITE_PAWN, FILE_NAMES[0] + RANK_NAMES[6]),
                    Piece(FEN_WHITE_PAWN, FILE_NAMES[1] + RANK_NAMES[6]),
                    Piece(FEN_WHITE_PAWN, FILE_NAMES[2] + RANK_NAMES[6]),
                    Piece(FEN_WHITE_PAWN, FILE_NAMES[3] + RANK_NAMES[6]),
                    Piece(FEN_WHITE_PAWN, FILE_NAMES[4] + RANK_NAMES[6]),
                    Piece(FEN_WHITE_PAWN, FILE_NAMES[5] + RANK_NAMES[6]),
                    Piece(FEN_WHITE_PAWN, FILE_NAMES[6] + RANK_NAMES[6]),
                    Piece(FEN_WHITE_PAWN, FILE_NAMES[7] + RANK_NAMES[6]),
                    Piece(FEN_WHITE_ROOK, FILE_NAMES[0] + RANK_NAMES[7]),
                    Piece(FEN_WHITE_KNIGHT, FILE_NAMES[1] + RANK_NAMES[7]),
                    Piece(FEN_WHITE_BISHOP, FILE_NAMES[2] + RANK_NAMES[7]),
                    Piece(FEN_WHITE_QUEEN, FILE_NAMES[3] + RANK_NAMES[7]),
                    Piece(FEN_WHITE_KING, FILE_NAMES[4] + RANK_NAMES[7]),
                    Piece(FEN_WHITE_BISHOP, FILE_NAMES[5] + RANK_NAMES[7]),
                    Piece(FEN_WHITE_KNIGHT, FILE_NAMES[6] + RANK_NAMES[7]),
                    Piece(FEN_WHITE_ROOK, FILE_NAMES[7] + RANK_NAMES[7]),
                ]
            )
            for piece in board:
                piece_placement_data[piece.square.name] = piece
                if piece.name == FEN_WHITE_PAWN:
                    pieces_on_board[piece.square.file + FEN_WHITE_PAWN].append(
                        piece
                    )
                elif piece.name == FEN_BLACK_PAWN:
                    pieces_on_board[piece.square.file + FEN_BLACK_PAWN].append(
                        piece
                    )
                else:
                    pieces_on_board[piece.name].append(piece)
            self._active_color = FEN_WHITE_ACTIVE
            self._en_passant_target_square = FEN_NULL
            self._castling_availability = FEN_INITIAL_CASTLING
            self._halfmove_clock = 0
            self._fullmove_number = 1
        self.set_initial_board_state(
            (
                tuple(
                    (p, p.square.name)
                    for p in self._piece_placement_data.values()
                ),
                self._active_color,
                self._castling_availability,
                self._en_passant_target_square,
                self._halfmove_clock,
                self._fullmove_number,
            )
        )
        return True

    def remove_piece_on_square(self, sn_p_n):
        """Remove piece from square as part of making a move.

        There will be a later call of place_piece_on_square to complete the
        move.

        active_color is changed after a move is completed.

        """
        del self._piece_placement_data[sn_p_n[0]]

    def remove_piece_from_board(self, sn_p_n):
        """Remove piece from board as part of making a move.

        A piece is captured using this method, and a pawn capturing something,
        or being promoted, is removed from the board using this method.

        There will be a later call of place_piece_on_board to complete a
        pawn move which captures something, or which promotes the pawn.

        active_color is changed after a move is completed.

        """
        square = sn_p_n[0]
        piece_placement_data = self._piece_placement_data
        piece = piece_placement_data[square]
        if piece.name == FEN_WHITE_PAWN:
            pobkey = piece.square.file + FEN_WHITE_PAWN
        elif piece.name == FEN_BLACK_PAWN:
            pobkey = piece.square.file + FEN_BLACK_PAWN
        else:
            pobkey = piece.name
        for piece_occurrence, pob in enumerate(self._pieces_on_board[pobkey]):
            if pob.square.name == square:
                self._pieces_on_board[pobkey].pop(piece_occurrence)
                break
        else:
            raise GameError(
                "".join(
                    (str(piece), " not in _pieces_on_board at square ", square)
                )
            )
        del piece_placement_data[square]

    def place_piece_on_square(self, sn_p_n):
        """Place piece on square as part of making a move.

        There will have been a prior call of remove_piece_on_square for this
        piece to start the move.

        (The piece is virtually on the board without a square).

        active_color is changed after a move is completed.

        """
        self._piece_placement_data[sn_p_n[0]] = sn_p_n[1]
        sn_p_n[1].set_square(sn_p_n[0])

    def place_piece_on_board(self, sn_p_n):
        """Place piece on board as part of making a move.

        There will have been a prior call of remove_piece_from_board, for a
        pawn, to start the move.

        A piece is always repositioned using this method when undoing capture
        of it; and pawns are always repositioned using this method when doing
        a capture (it counts as removing the pawn from one file and placing
        it on another).

        active_color is changed after a move is completed.

        """
        piece = sn_p_n[1]
        self._piece_placement_data[sn_p_n[0]] = piece
        piece.set_square(sn_p_n[0])
        pieces_on_board = self._pieces_on_board
        name = piece.name
        if name == FEN_WHITE_PAWN:
            pieces_on_board[piece.square.file + FEN_WHITE_PAWN].append(piece)
        elif name == FEN_BLACK_PAWN:
            pieces_on_board[piece.square.file + FEN_BLACK_PAWN].append(piece)
        else:
            pieces_on_board[name].append(piece)

    def set_position_to_play_first_rav_at_move(self):
        """Set position to play first move of first RAV for move.

        Set position associated with first start_of_rav token at move.
        The first '(' in 'a3Ke7(Kf8...)(O-O...)b4' needs full position setup
        but second and subsequent '('s are copies of the first, which has
        been retained in ravstack.

        """
        place, remove = self._position_deltas[-1]
        if len(place[0]) == len(remove[0]):

            # If these two piece names are different the source move was a pawn
            # promotion: remove and place the pieces on the board rather than
            # just change the square.
            if remove[0][-1][1].name != place[0][-1][1].name:
                for pce in remove[0]:
                    self.remove_piece_from_board(pce)
                for pce in place[0]:
                    self.place_piece_on_board(pce)
            else:
                for pce in remove[0]:
                    self.remove_piece_on_square(pce)
                for pce in place[0]:
                    self.place_piece_on_square(pce)

        else:

            # Pawns must be removed from board and placed on board because they
            # change name when capturing: the file is prefix to pawn name.
            # This name is the key into self._pieces_on_board.
            if place[0][-1][1].name in "Pp":
                self.remove_piece_from_board(remove[0][0])
                self.place_piece_on_board(place[0][0])
                self.place_piece_on_board(place[0][1])
            else:
                self.remove_piece_on_square(remove[0][0])
                self.place_piece_on_board(place[0][0])
                self.place_piece_on_square(place[0][1])

        self._ravstack[-1].extend(
            (
                tuple(
                    (p, p.square.name)
                    for p in self._piece_placement_data.values()
                ),
                remove,
                place,
            )
        )
        self.reset_board_state(((self._ravstack[-1][1],) + place[1:],))
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = place[1:]

    def set_position_to_play_right_nested_rav_at_move(self):
        """Set position to play first move of right-nested RAV.

        Style is '((' rather than '(Ke2(' with intervening comments and
        similar allowed such as '({comment}('.  In '(Ke2Ke7(f4' the move
        'f4' is an alternative to 'Ke2' not 'Ke7'.  In '(Ke2(f4' the move
        'f4' is still an alternative to 'Ke2', but here both moves are
        adjacent to the same '('.

        """
        rav_piece_placement_data = self._position_deltas[-1][0][0]
        pieces_on_board = self._pieces_on_board
        for val in pieces_on_board.values():
            val.clear()
        piece_placement_data = self._piece_placement_data
        piece_placement_data.clear()
        for piece, square in rav_piece_placement_data:
            piece_placement_data[square] = piece
            piece.set_square(square)
            if piece.name == FEN_WHITE_PAWN:
                pieces_on_board[piece.square.file + FEN_WHITE_PAWN].append(
                    piece
                )
            elif piece.name == FEN_BLACK_PAWN:
                pieces_on_board[piece.square.file + FEN_BLACK_PAWN].append(
                    piece
                )
            else:
                pieces_on_board[piece.name].append(piece)
        self.repeat_board_state(self._position_deltas[-1])
        self._ravstack[-1].extend((self._position_deltas[-1][0], None, None))

    def set_position_to_play_main_line_at_move(self):
        """Set position associated with end_of_rav token."""
        count, rav_piece_placement_data, place, remove = self._ravstack[-1]
        pieces_on_board = self._pieces_on_board
        for val in pieces_on_board.values():
            val.clear()
        piece_placement_data = self._piece_placement_data
        piece_placement_data.clear()
        for piece, square in rav_piece_placement_data:
            piece_placement_data[square] = piece
            piece.set_square(square)
            if piece.name == FEN_WHITE_PAWN:
                pieces_on_board[piece.square.file + FEN_WHITE_PAWN].append(
                    piece
                )
            elif piece.name == FEN_BLACK_PAWN:
                pieces_on_board[piece.square.file + FEN_BLACK_PAWN].append(
                    piece
                )
            else:
                pieces_on_board[piece.name].append(piece)
        if len(place[0]) == len(remove[0]):

            # If these two piece names are different the source move was a pawn
            # promotion: remove and place the pieces on the board rather than
            # just change the square.
            if remove[0][-1][1].name != place[0][-1][1].name:
                for pce in remove[0]:
                    self.remove_piece_from_board(pce)
                for pce in place[0]:
                    self.place_piece_on_board(pce)
            else:
                for pce in remove[0]:
                    self.remove_piece_on_square(pce)
                for pce in place[0]:
                    self.place_piece_on_square(pce)

        else:
            self.remove_piece_from_board(remove[0][0])

            # Pawns must be removed from board and placed on board because they
            # change name when capturing: the file is prefix to pawn name.
            # This name is the key into self._pieces_on_board.
            if remove[0][-1][1].name in "Pp":
                self.remove_piece_from_board(remove[0][1])
                self.place_piece_on_board(place[0][0])
            else:
                self.remove_piece_on_square(remove[0][1])
                self.place_piece_on_square(place[0][0])

        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = place[1:]
        self.set_board_state(
            (
                (
                    tuple(
                        (p, p.square.name)
                        for p in self._piece_placement_data.values()
                    ),
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ),
            )
        )

    def set_position_to_play_prior_right_nested_rav_at_move(self):
        """Set position for end_of_rav token of right-nested RAV."""
        rav_piece_placement_data = self._ravstack[-1][1]
        pieces_on_board = self._pieces_on_board
        for val in pieces_on_board.values():
            val.clear()
        piece_placement_data = self._piece_placement_data
        piece_placement_data.clear()
        for piece, square in rav_piece_placement_data[0]:
            piece_placement_data[square] = piece
            piece.set_square(square)
            if piece.name == FEN_WHITE_PAWN:
                pieces_on_board[piece.square.file + FEN_WHITE_PAWN].append(
                    piece
                )
            elif piece.name == FEN_BLACK_PAWN:
                pieces_on_board[piece.square.file + FEN_BLACK_PAWN].append(
                    piece
                )
            else:
                pieces_on_board[piece.name].append(piece)
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = rav_piece_placement_data[1:]
        self.set_board_state(
            (
                (
                    tuple(
                        (p, p.square.name)
                        for p in self._piece_placement_data.values()
                    ),
                    self._active_color,
                    self._castling_availability,
                    self._en_passant_target_square,
                    self._halfmove_clock,
                    self._fullmove_number,
                ),
            )
        )

    def line_empty(self, square1, square2):
        """Return True if the squares between square1 and square2 are empty."""
        piece_placement_data = self._piece_placement_data
        ptp = POINT_TO_POINT.get((square1, square2))
        if ptp is None:
            return True
        for sqr in ptp[2][ptp[0] : ptp[1]]:
            if sqr in piece_placement_data:
                return False
        return True

    def get_castling_options_after_move_applied(self, remove):
        """Return castling options available after proposed move is made.

        Called while applying a move to the board.  In particular the pieces
        being moved or captured have been removed from the board, but have
        not been put on their new squares.  Two pieces are moved castling and
        a different piece is put on the board by pawn promotion.

        """
        if self._castling_availability == FEN_NULL:
            return FEN_NULL
        castling_rights_lost = "".join(
            Squares.squares[r[0]].castling_rights_lost for r in remove
        )
        if not castling_rights_lost:
            return self._castling_availability
        adjusted_castling_availability = "".join(
            sorted(
                set(self._castling_availability) - set(castling_rights_lost)
            )
        )
        if not adjusted_castling_availability:
            return FEN_NULL
        return adjusted_castling_availability

    # There is a case for piece_placement_data and active_color to be arguments
    # of is_square_attacked_by_other_side to avoid temporary adjustment of the
    # attributes validating FEN Tags and determining check indicators.
    def is_square_attacked_by_other_side(self, square):
        """Return True if square is attacked by side without the move."""
        piece_placement_data = self._piece_placement_data
        active_color = self._active_color

        point, line = FILE_ATTACKS[square]
        for square_list in reversed(line[:point]), line[point + 1 :]:
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = FEN_SOURCE_SQUARES.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                return True

        point, line = RANK_ATTACKS[square]
        for square_list in reversed(line[:point]), line[point + 1 :]:
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = FEN_SOURCE_SQUARES.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                return True

        point, line = LRD_DIAGONAL_ATTACKS[square]
        for square_list in reversed(line[:point]), line[point + 1 :]:
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = FEN_SOURCE_SQUARES.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                return True

        point, line = RLD_DIAGONAL_ATTACKS[square]
        for square_list in reversed(line[:point]), line[point + 1 :]:
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = FEN_SOURCE_SQUARES.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                return True

        if active_color == FEN_WHITE_ACTIVE:
            knight_search = FEN_BLACK_KNIGHT
        else:
            knight_search = FEN_WHITE_KNIGHT
        square_list = FEN_SOURCE_SQUARES[knight_search]
        for sqr in square_list:
            if sqr not in piece_placement_data:
                continue
            piece = piece_placement_data[sqr]
            if piece.color == active_color:
                break
            if piece.name == knight_search:
                if square in square_list[sqr]:
                    return True

        return False

    def seven_tag_roster_collation_value(self):
        """Return Seven Tag Roster tuple converted to sort in collation order.

        Order is: Date, Event, Site, Round, White, Black, Result.

        A Query ('?') represents an unknown value in Event, Site, White, and
        Black, tags.

        A Query ('?') represents an unknown round and a hyphen ('-') means
        round not relevant.  Query is before hyphen in the collation order.

        A Query ('?') represents an unknown character in a date value.  It is
        treated as '0' for collation.

        """
        tags = self._tags
        event = tags.get(TAG_EVENT, DEFAULT_SORT_TAG_VALUE)
        site = tags.get(TAG_SITE, DEFAULT_SORT_TAG_VALUE)
        white = tags.get(TAG_WHITE, DEFAULT_SORT_TAG_VALUE)
        black = tags.get(TAG_BLACK, DEFAULT_SORT_TAG_VALUE)
        return (
            tags.get(TAG_DATE, DEFAULT_TAG_DATE_VALUE).replace("?", "0"),
            event if event != DEFAULT_TAG_VALUE else DEFAULT_SORT_TAG_VALUE,
            site if site != DEFAULT_TAG_VALUE else DEFAULT_SORT_TAG_VALUE,
            tags.get(TAG_ROUND, DEFAULT_TAG_VALUE).replace("?", " "),
            white if white != DEFAULT_TAG_VALUE else DEFAULT_SORT_TAG_VALUE,
            black if black != DEFAULT_TAG_VALUE else DEFAULT_SORT_TAG_VALUE,
            tags.get(TAG_RESULT, DEFAULT_SORT_TAG_RESULT_VALUE),
        )

    def movetext_collation_value(self):
        """Return movetext converted to sort in collation order.

        1. e4 is before 1... e4 in collation order but self._text normally will
        not have the move number indications.  If sorting gets into movetext it
        is possible the ordering implemented in this method will differ from
        the ordering implied by the PGN specification when move sufficies are
        present.

        """
        if TAG_FEN in self._tags:
            fen = self._tags[TAG_FEN].split()
            move_number = int(fen[FEN_FULLMOVE_NUMBER_FIELD_INDEX])
            inactive_color = OTHER_SIDE[fen[FEN_ACTIVE_COLOR_FIELD_INDEX]]
        else:
            move_number = 1
            inactive_color = FEN_BLACK_ACTIVE
        if self._movetext_offset:
            movetext = self._text[self._movetext_offset :]
        else:
            movetext = self._text[:]
        return move_number, inactive_color, movetext

    def __eq__(self, other):
        """Return  True if self == other in PGN collating order."""
        strs = self.seven_tag_roster_collation_value()
        stro = other.seven_tag_roster_collation_value()
        if strs != stro:
            return False
        smcv = self.movetext_collation_value()
        omcv = other.movetext_collation_value()
        if smcv != omcv:
            return False
        return True

    def __ge__(self, other):
        """Return  True if self >= other in PGN collating order."""
        strs = self.seven_tag_roster_collation_value()
        stro = other.seven_tag_roster_collation_value()
        if strs > stro:
            return True
        if strs < stro:
            return False
        smcv = self.movetext_collation_value()
        omcv = other.movetext_collation_value()
        if smcv > omcv:
            return True
        if smcv < omcv:
            return False
        return True

    def __gt__(self, other):
        """Return  True if self > other in PGN collating order."""
        strs = self.seven_tag_roster_collation_value()
        stro = other.seven_tag_roster_collation_value()
        if strs > stro:
            return True
        if strs < stro:
            return False
        smcv = self.movetext_collation_value()
        omcv = other.movetext_collation_value()
        if smcv > omcv:
            return True
        if smcv < omcv:
            return False
        return False

    def __le__(self, other):
        """Return  True if self <= other in PGN collating order."""
        strs = self.seven_tag_roster_collation_value()
        stro = other.seven_tag_roster_collation_value()
        if strs < stro:
            return True
        if strs > stro:
            return False
        smcv = self.movetext_collation_value()
        omcv = other.movetext_collation_value()
        if smcv < omcv:
            return True
        if smcv > omcv:
            return False
        return True

    def __lt__(self, other):
        """Return  True if self < other in PGN collating order."""
        strs = self.seven_tag_roster_collation_value()
        stro = other.seven_tag_roster_collation_value()
        if strs < stro:
            return True
        if strs > stro:
            return False
        smcv = self.movetext_collation_value()
        omcv = other.movetext_collation_value()
        if smcv < omcv:
            return True
        if smcv > omcv:
            return False
        return False

    def get_tags(self, name_value_separator=" "):
        """Return list of PGN tags in an undefined order.

        The default name_value_separator gives PGN tags in export format.

        """
        return [
            "".join(("[", k, name_value_separator, '"', v, '"]'))
            for k, v in self._tags.items()
        ]

    def get_tags_in_text_order(self):
        """Return list of tags in their order in game text in export format."""
        if self._movetext_offset is None:
            return []
        return self._text[: self._movetext_offset]

    def get_non_seven_tag_roster_tags(self):
        """Return string of sorted tags not in Seven Tag Roster."""
        return "\n".join(
            [
                "".join(("[", k, ' "', v, '"]'))
                for k, v in sorted(self._tags.items())
                if k not in SEVEN_TAG_ROSTER
            ]
        )

    def get_seven_tag_roster_tags(self):
        """Return Seven Tag Roster string in order given in PGN specification.

        The PGN specification says name format is <family name>,< ><first name>
        or when an initial is given it is immediately followed by a period.
        Thus 'Smyslov, Vassily V.' but nothing is said about multiple initials
        or cases where 'Smyslov, V. Vassily' is the correct form.  It seems
        consistent to do multiple initials like 'Smyslov, V. V.' with a single
        space following the dot too.

        Many PGN files do something very close to, but not exactly, this in
        the White and Black tags.

        """
        tags = self._tags
        str_tags = []
        for tag in SEVEN_TAG_ROSTER:
            if tag not in tags:
                value = SEVEN_TAG_ROSTER_DEFAULTS.get(tag, DEFAULT_TAG_VALUE)
            elif tag in (TAG_WHITE, TAG_BLACK):
                val = white_black_tag_value_format.findall(tags[tag])
                if len(val) == 1:
                    value = val[0]
                else:
                    value = [val.pop(0) + ","]
                    value.extend(
                        [(n + "." if len(n) == 1 else n) for n in val]
                    )
                    value = " ".join(value)
            else:
                value = tags[tag]
            str_tags.append("".join(("[", tag, ' "', value, '"]')))
        return "\n".join(str_tags)

    def _set_movetext_indicators(self):
        if TAG_FEN in self._tags:
            fen = self._tags[TAG_FEN].split()
            fullmove_number = int(fen[FEN_FULLMOVE_NUMBER_FIELD_INDEX])
            active_color = fen[FEN_ACTIVE_COLOR_FIELD_INDEX]
        else:
            fullmove_number = 1
            active_color = FEN_WHITE_ACTIVE
        return fullmove_number, active_color

    @staticmethod
    def _add_token_to_movetext(token, movetext, length):
        # Not modified to do what everyone else seems to do with '(...)':
        # '16. e4 Qd8 (16... dxe4) 17. fxe4' rather than
        # '16. e4 Qd8 ( 16... dxe4 ) 17. fxe4'.
        # I think both are allowed by the PGN specification along with,
        # strictly speaking, '16. e4 Qd8(16... dxe4)17. fxe4' since '(' and ')'
        # are self-terminating and nothing is said about separation from
        # adjacent tokens.
        if not length:
            movetext.append(token)
            return len(token)
        if len(token) + length >= PGN_MAXIMUM_LINE_LENGTH:
            movetext.append(PGN_LINE_SEPARATOR)
            movetext.append(token)
            return len(token)
        # if token == ')':
        #    movetext.append(token)
        #    return len(token) + length
        # if movetext[-1] == '(':
        #    movetext.append(token)
        #    return len(token) + length
        # else:
        movetext.append(PGN_TOKEN_SEPARATOR)
        movetext.append(token)
        return len(token) + length + 1

    def get_movetext(self):
        """Return list of movetext.

        Moves have check and checkmate indicators, but not the black move
        indicators found in export format if a black move follows a comment
        or is first move in a RAV, nor move numbers.

        """
        if self._movetext_offset is None:
            return []
        return self._text[self._movetext_offset :]

    def get_all_movetext_in_pgn_export_format(self):
        """Return all movetext in pgn export format.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return movetext
        length = 0
        insert_fullmove_number = True
        fnas = [[fullmove_number, active_color]]
        _attm = self._add_token_to_movetext
        termination = self._tags.get(TAG_RESULT, DEFAULT_TAG_RESULT_VALUE)
        for mvt in self._text[self._movetext_offset :]:
            if mvt.startswith("{"):
                for word in mvt.split():
                    length = _attm(word, movetext, length)
                insert_fullmove_number = True
            elif mvt.startswith("$"):
                length = _attm(mvt, movetext, length)
            elif mvt.startswith(";"):
                if len(mvt) + length >= PGN_MAXIMUM_LINE_LENGTH:
                    movetext.append(PGN_LINE_SEPARATOR)
                else:
                    movetext.append(PGN_TOKEN_SEPARATOR)
                movetext.append(mvt)
                length = 0
                insert_fullmove_number = True
            elif mvt == "(":
                length = _attm(mvt, movetext, length)
                fnas[-1] = [fullmove_number, active_color]
                active_color = OTHER_SIDE[active_color]
                if active_color == FEN_BLACK_ACTIVE:
                    fullmove_number -= 1
                fnas.append([fullmove_number, active_color])
                insert_fullmove_number = True
            elif mvt == ")":
                length = _attm(mvt, movetext, length)
                del fnas[-1]
                fullmove_number, active_color = fnas[-1]
                insert_fullmove_number = True
            elif mvt == termination:
                length = _attm(mvt, movetext, length)
            elif active_color == FEN_WHITE_ACTIVE:
                length = _attm(
                    str(fullmove_number) + PGN_DOT, movetext, length
                )
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                insert_fullmove_number = False
            else:
                if insert_fullmove_number:
                    length = _attm(
                        str(fullmove_number) + PGN_DOT * 3, movetext, length
                    )
                    insert_fullmove_number = False
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                fullmove_number += 1
        return "".join(movetext)

    def get_archive_movetext(self):
        """Return Reduced Export format PGN movetext.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return movetext
        length = 0
        insert_fullmove_number = True
        rav_depth = 0
        _attm = self._add_token_to_movetext
        termination = self._tags.get(TAG_RESULT, DEFAULT_TAG_RESULT_VALUE)
        for mvt in self._text[self._movetext_offset :]:
            if (
                mvt.startswith("{")
                or mvt.startswith("$")
                or mvt.startswith(";")
            ):
                pass
            elif mvt == "(":
                rav_depth += 1
            elif mvt == ")":
                rav_depth -= 1
            elif rav_depth:
                pass
            elif mvt == termination:
                length = _attm(mvt, movetext, length)
            elif active_color == FEN_WHITE_ACTIVE:
                length = _attm(
                    str(fullmove_number) + PGN_DOT, movetext, length
                )
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                insert_fullmove_number = False
            else:
                if insert_fullmove_number:
                    length = _attm(
                        str(fullmove_number) + PGN_DOT * 3, movetext, length
                    )
                    insert_fullmove_number = False
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                fullmove_number += 1
        return "".join(movetext)

    def get_movetext_without_comments_in_pgn_export_format(self):
        """Return movetext without comments in pgn export format.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return movetext
        length = 0
        insert_fullmove_number = True
        fnas = [[fullmove_number, active_color]]
        _attm = self._add_token_to_movetext
        termination = self._tags.get(TAG_RESULT, DEFAULT_TAG_RESULT_VALUE)
        for mvt in self._text[self._movetext_offset :]:
            if (
                mvt.startswith("{")
                or mvt.startswith("$")
                or mvt.startswith(";")
            ):
                pass
            elif mvt == "(":
                length = _attm(mvt, movetext, length)
                fnas[-1] = [fullmove_number, active_color]
                active_color = OTHER_SIDE[active_color]
                if active_color == FEN_BLACK_ACTIVE:
                    fullmove_number -= 1
                fnas.append([fullmove_number, active_color])
                insert_fullmove_number = True
            elif mvt == ")":
                length = _attm(mvt, movetext, length)
                del fnas[-1]
                fullmove_number, active_color = fnas[-1]
                insert_fullmove_number = True
            elif mvt == termination:
                length = _attm(mvt, movetext, length)
            elif active_color == FEN_WHITE_ACTIVE:
                length = _attm(
                    str(fullmove_number) + PGN_DOT, movetext, length
                )
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                insert_fullmove_number = False
            else:
                if insert_fullmove_number:
                    length = _attm(
                        str(fullmove_number) + PGN_DOT * 3, movetext, length
                    )
                    insert_fullmove_number = False
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                fullmove_number += 1
        return "".join(movetext)

    def get_export_pgn_elements(self):
        """Return Export format PGN version of game.

        This method will be removed without notice in future.  It seems more
        convenient and clearer to use the called methods directly.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        return (
            self.get_seven_tag_roster_tags(),
            self.get_all_movetext_in_pgn_export_format(),
            self.get_non_seven_tag_roster_tags(),
        )

    def get_archive_pgn_elements(self):
        """Return Archive format PGN version of game. (Reduced Export Format).

        This method will be removed without notice in future.  It seems more
        convenient and clearer to use the called methods directly.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        return self.get_seven_tag_roster_tags(), self.get_archive_movetext()

    def get_export_pgn_rav_elements(self):
        """Return Export format PGN version of game with RAVs but no comments.

        This method will be removed without notice in future.  It seems more
        convenient and clearer to use the called methods directly.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        return (
            self.get_seven_tag_roster_tags(),
            self.get_movetext_without_comments_in_pgn_export_format(),
            self.get_non_seven_tag_roster_tags(),
        )

    def get_text_of_game(self):
        """Return current text version of game."""
        return "".join(self._text)

    def append_check_indicator(self):
        """Do nothing.

        Check and checkmate indicators are not added to movetext where the
        move gives check or checkmate.

        Use the GameIndicateCheck class to append these indicators to movetext.

        This method is used after the move in self._text[-1] has been applied
        to the board, but before processing the next token starts.
        """


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
            self.append_token_and_set_error()
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
            self.append_token_and_set_error(match)

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
                        super(GameTextPGN, self).append_pawn_promote_move(
                            pgn_match
                        )
                        return
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
                super(GameTextPGN, self).append_piece_move(piece_match)
                self._bishop_or_bpawn = None
                return
            if match[0].isupper():
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
                super(GameTextPGN, self).append_pawn_move(pawn_match)
                self._bishop_or_bpawn = None
            elif (
                pawn_promotion_match
                and pawn_promotion_match.lastindex == IFG_PAWN_PROMOTE_PIECE
            ):
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
            source_squares = WHITE_PAWN_CAPTURES.get(square)
            pawn = FEN_WHITE_PAWN
        else:
            source_squares = BLACK_PAWN_CAPTURES.get(square)
            pawn = FEN_BLACK_PAWN

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
                    pgn_np.lower()
                    if self._active_color == FEN_BLACK_ACTIVE
                    else pgn_np
                ]:
                    if POINT_TO_POINT.get(pobsq.square.name, square):
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
                super(GameTextPGN, self).append_piece_move(bishop)
                self._bishop_or_bpawn = None
                return
            self.append_token_and_set_error()
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
            pawn_match.lastindex == IFG_PAWN_TO_RANK
            or pawn_match.lastindex == IFG_PAWN_PROMOTE_PIECE
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


class GameIndicateCheck(Game):
    """Add check and checkmate indicators to games extracted from database.

    Append check and checkmate indicators, '+' and '#', to movetext where the
    move gives check or checkmate by overriding append_check_indicator()
    method.

    Note the methods in this class are not needed to determine legality of a
    move.  Their purpose is to decide if a move needs a check indicator to
    comply with the Export Format defined in the PGN standard.

    """

    def append_check_indicator(self):
        """Append correct check indicator, '+' and '#', suffix to movetext.

        This method is used after the move in self._text[-1] has been applied
        to the board, but before processing the next token starts.

        '#' indicators are replaced by '+' because checkmate is not validated
        explicitly unless the move is not followed by a valid move in the game
        or variation.  This is done later, and the positions to test must be
        set here but is not implemented yet.

        """
        if self.is_square_attacked_by_other_side(
            self._pieces_on_board[SIDE_TO_MOVE_KING[self._active_color]][
                0
            ].square.name
        ):
            self._text[-1] += "#" if self.is_position_checkmate() else "+"

    def is_position_checkmate(self):
        """Return True if the side to move is checkmated."""
        piece_placement_data = self._piece_placement_data.copy()
        pieces_on_board = self._pieces_on_board
        side_to_move_king = SIDE_TO_MOVE_KING[self._active_color]
        king_square = pieces_on_board[side_to_move_king][0].square.name
        escape_squares = KING_MOVES[king_square]

        # Be sure to put king back!
        del self._piece_placement_data[king_square]

        # Can king avoid check by moving?
        # Test all possible destination squares without putting king on them.
        for sqr in escape_squares:
            if sqr not in piece_placement_data:
                if not self.is_square_attacked_by_other_side(sqr):
                    self._piece_placement_data[
                        king_square
                    ] = piece_placement_data[king_square]
                    return False
            elif (
                PIECE_TO_KING[piece_placement_data[sqr].name]
                != side_to_move_king
            ):
                if not self.is_square_attacked_by_other_side(sqr):
                    self._piece_placement_data[
                        king_square
                    ] = piece_placement_data[king_square]
                    return False

        # Put king back.
        self._piece_placement_data[king_square] = piece_placement_data[
            king_square
        ]

        # Can side to move block the check?
        attack_lines = self.get_attacks_on_square_by_other_side(king_square)
        if len(attack_lines) > 1:
            return True
        if len(attack_lines) == 0:
            return False
        if self.legal_move_to_square_exists(
            attack_lines[0], PGN_CAPTURE_MOVE, king_square
        ):
            return False
        ptp = POINT_TO_POINT.get((attack_lines[0], king_square))
        if ptp is not None:
            for sqr in ptp[2][ptp[0] : ptp[1]]:
                if self.legal_move_to_square_exists(sqr, "", king_square):
                    return False
            return True
        ptp = KNIGHT_MOVES.get(attack_lines[0])
        if ptp is not None:
            for sqr in ptp:
                if self.legal_move_to_square_exists(sqr, "", king_square):
                    return False
            return True
        return False

    def get_attacks_on_square_by_other_side(self, square):
        """Return list of attacking squares.

        This method is intended for deciding if a check is checkmate, so the
        list is returned early if it's length reaches two because a single
        move cannot block checks from two squares.

        It is assumed the king cannot escape check by moving itself.

        """
        piece_placement_data = self._piece_placement_data
        active_color = self._active_color
        attacking_squares = []

        point, line = FILE_ATTACKS[square]
        for square_list in reversed(line[:point]), line[point + 1 :]:
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = FEN_SOURCE_SQUARES.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                attacking_squares.append(sqr)
                if len(attacking_squares) > 1:
                    return attacking_squares
                break

        point, line = RANK_ATTACKS[square]
        for square_list in reversed(line[:point]), line[point + 1 :]:
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = FEN_SOURCE_SQUARES.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                attacking_squares.append(sqr)
                if len(attacking_squares) > 1:
                    return attacking_squares
                break

        point, line = LRD_DIAGONAL_ATTACKS[square]
        for square_list in reversed(line[:point]), line[point + 1 :]:
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = FEN_SOURCE_SQUARES.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                attacking_squares.append(sqr)
                if len(attacking_squares) > 1:
                    return attacking_squares
                break

        point, line = RLD_DIAGONAL_ATTACKS[square]
        for square_list in reversed(line[:point]), line[point + 1 :]:
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == active_color:
                    break
                sources = FEN_SOURCE_SQUARES.get(piece.name)
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
        square_list = FEN_SOURCE_SQUARES[knight_search]
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

    def legal_move_to_square_exists(self, square, capture, king_square):
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
        for from_square, piece in ppd.copy().items():
            if piece.color != self._active_color:
                continue
            name = piece.name
            if name == checked_king:
                continue
            if name in FEN_PAWNS:
                name += capture
                if square in SOURCE_SQUARES[name]:
                    if from_square not in SOURCE_SQUARES[name][square]:
                        continue
                    ppd_to = ppd.pop(square, None)
                    ppd_from = ppd.pop(from_square)
                    ppd[square] = ppd_from
                    check = self.is_square_attacked_by_other_side(king_square)
                    del ppd[square]
                    if ppd_to is not None:
                        ppd[square] = ppd_to
                    ppd[from_square] = ppd_from
                    if not check:
                        return True
                continue
            if from_square in FEN_SOURCE_SQUARES[name][square]:
                if name in (FEN_WHITE_KNIGHT, FEN_BLACK_KNIGHT):
                    ppd_to = ppd.pop(square, None)
                    ppd_from = ppd.pop(from_square)
                    ppd[square] = ppd_from
                    check = self.is_square_attacked_by_other_side(king_square)
                    del ppd[square]
                    if ppd_to is not None:
                        ppd[square] = ppd_to
                    ppd[from_square] = ppd_from
                    if not check:
                        return True
                    continue
                ptp = POINT_TO_POINT[from_square, square]
                for line_sq in ptp[2][ptp[0] : ptp[1]]:
                    if line_sq in ppd:
                        break
                else:
                    ppd_to = ppd.pop(square, None)
                    ppd_from = ppd.pop(from_square)
                    ppd[square] = ppd_from
                    check = self.is_square_attacked_by_other_side(king_square)
                    del ppd[square]
                    if ppd_to is not None:
                        ppd[square] = ppd_to
                    ppd[from_square] = ppd_from
                    if not check:
                        return True
        if capture and self._en_passant_target_square != FEN_NULL:
            for k, value in EN_PASSANT_TARGET_SQUARES[
                self._active_color
            ].items():
                if value != self._en_passant_target_square:
                    continue
                if k[0] != square:
                    continue
                if self._active_color == FEN_WHITE_ACTIVE:
                    pawn = FEN_WHITE_PAWN
                else:
                    pawn = FEN_BLACK_PAWN
                for from_square in FEN_SOURCE_SQUARES[pawn][
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
                    check = self.is_square_attacked_by_other_side(king_square)
                    del ppd[self._en_passant_target_square]
                    if ppd_to is not None:
                        ppd[square] = ppd_to
                    ppd[from_square] = ppd_from
                    if not check:
                        return True
        return False


def generate_fen_for_position(
    pieces,
    active_color,
    castling_availability,
    en_passant_target_square,
    halfmove_clock,
    fullmove_number,
):
    """Return Forsyth English Notation (FEN) string for Game position."""
    rank = 0
    file = -1
    chars = []
    for piece in sorted(pieces):
        piece_rank = RANK_NAMES.index(piece.square.rank)
        piece_file = FILE_NAMES.index(piece.square.file)
        if piece_rank != rank:
            if file != 7:
                chars.append(str(7 - file))
            chars.append("/")
            while True:
                rank += 1
                if piece_rank == rank:
                    file = -1
                    break
                chars.append("8/")
            else:
                continue
        if piece_file != file:
            if piece_file - file > 1:
                chars.append(str(piece_file - file - 1))
            chars.append(piece.name)
            file = piece_file
        else:
            chars.append(piece.name)
    if file != 7:
        chars.append(str(7 - file))
    while True:
        if rank == 7:
            break
        chars.append("/8")
        rank += 1
    fen = " ".join(
        (
            "".join(chars),
            active_color,
            castling_availability,
            en_passant_target_square,
            str(halfmove_clock),
            str(fullmove_number),
        )
    )
    return fen
