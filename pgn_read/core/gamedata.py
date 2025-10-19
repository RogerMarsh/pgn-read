# gamedata.py
# Copyright 2025 Roger Marsh
# Licence: See LICENCE (BSD licence)
# Code transferred from 2025 version of game.py.

"""Portable Game Notation (PGN) position and game data structures."""
import re

from .constants import (
    IFG_TAG_NAME,
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
    FEN_FIELD_COUNT,
    FEN_PIECE_PLACEMENT_FIELD_INDEX,
    FEN_ACTIVE_COLOR_FIELD_INDEX,
    FEN_CASTLING_AVAILABILITY_FIELD_INDEX,
    FEN_EN_PASSANT_TARGET_SQUARE_FIELD_INDEX,
    FEN_HALFMOVE_CLOCK_FIELD_INDEX,
    FEN_FULLMOVE_NUMBER_FIELD_INDEX,
    CASTLING_RIGHTS,
    CASTLING_PIECE_FOR_SQUARE,
    OTHER_SIDE,
    SIDE_TO_MOVE_KING,
    PIECE_TO_KING,
    # The TAG_* list is long enough to cause a pylint duplicate-code report
    # citing pgn_read.core.constants module.
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
    DEFAULT_SORT_TAG_VALUE,
    DEFAULT_SORT_TAG_RESULT_VALUE,
    SEVEN_TAG_ROSTER_DEFAULTS,
    PGN_TOKEN_SEPARATOR,
)
from .piece import Piece
from .squares import (
    fen_squares,
    fen_square_names,
    fen_source_squares,
    en_passant_target_squares,
)

white_black_tag_value_format = re.compile(r"\s*([^,.\s]+)")
KNIGHTS = FEN_WHITE_KNIGHT + FEN_BLACK_KNIGHT


class GameError(Exception):
    """Exceptions raised manipulating Game state."""


class GameData:
    """Data structure of game positions derived from a PGN game score.

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

    # Locate position in PGN text file of latest game.
    game_offset = 0

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

        set_game_error() does nothing if the current state is not None.

        Otherwise the state is set to the current length of the list of
        tokens found, and this value is appended to the state stack.

        set_game_error() should not be used within the Game class or any
        subclass.

        """
        if self._state is None:
            self._state = len(self._text)
            self._state_stack[-1] = self._state

    def len_ravstack(self):
        """Return self._ravstack depth."""
        return len(self._ravstack)

    @property
    def pgn_tags(self):
        """Return _tags dict of PGN tag names and values."""
        return self._tags

    @property
    def pgn_text(self):
        """Return _text str of PGN text (the whole game score)."""
        return self._text

    @property
    def piece_placement_data(self):
        """Return _piece_placement_data dict of ."""
        return self._piece_placement_data

    @property
    def active_color(self):
        """Return _active_color str indicating side to move."""
        return self._active_color

    @property
    def castling_availability(self):
        """Return _castling_availability str of castling options."""
        return self._castling_availability

    @property
    def en_passant_target_square(self):
        """Return _en_passant_target_square str for capture square."""
        return self._en_passant_target_square

    @property
    def halfmove_clock(self):
        """Return _halfmove_clock int of moves since capture or pawn move."""
        return self._halfmove_clock

    @property
    def fullmove_number(self):
        """Return _fullmove_number int of move number in game or variation."""
        return self._fullmove_number

    @property
    def initial_position(self):
        """Return _initial_position str of game or None."""
        return self._initial_position

    @property
    def position_deltas(self):
        """Return _position_deltas tuple of changes between positions."""
        return self._position_deltas

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

    def add_board_state_none(self):
        """Append placeholder, None, for token being processed.

        Subclasses may extend this method as needed: it is used when a PGN Tag,
        or a game termination token, is found.

        """
        self._position_deltas.append(None)

    def repeat_board_state(self):
        """Copy preceding board state for token being processed.

        Subclasses may extend this method as needed: it is used when various
        non-move tokens such as comments, but not start and end RAV markers,
        are found.

        """
        self._position_deltas.append(self._position_deltas[-1])

    def set_board_state(self, position_delta):
        """Set board state for token being processed.

        Subclasses may extend this method as needed: it is used when setting
        the board state after the end of a RAV.

        """
        self._position_deltas.append(position_delta)

    def set_initial_board_state(self, position_delta):
        """Set initial position state as position_delta.

        Subclasses may extend this method as needed: it is used when a PGN FEN
        Tag is found or the first move token is found.

        """
        self._initial_position = position_delta

    def modify_board_state(self, position_delta):
        """Append board state for token being processed.

        Subclasses may extend this method as needed: it is used when setting
        the board state for a move played in the game or a RAV.

        """
        self._position_deltas.append(position_delta)
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = self._position_deltas[-1][1][1:]

    def undo_board_state(self):
        """Delete board state for token being processed.

        Subclasses may extend this method as needed: it is used when most
        recent move would leave the king of moving side in check.

        """
        (
            self._active_color,
            self._castling_availability,
            self._en_passant_target_square,
            self._halfmove_clock,
            self._fullmove_number,
        ) = self._position_deltas[-1][0][1:]
        del self._position_deltas[-1]

    def is_check_given_by_move(self):
        """Return True if move gives check."""
        piece_placement_data = self._piece_placement_data
        delta = self._position_deltas[-1]
        side = self._active_color
        king_square = self._pieces_on_board[SIDE_TO_MOVE_KING[side]][0].square
        king_square_name = king_square.name
        source_square_piece = delta[1][0]
        for delta_square_piece in source_square_piece + delta[0][0]:
            attack_line = king_square.attack_line(
                fen_squares[delta_square_piece[0]]
            )
            if attack_line is None:
                continue
            for square_list in attack_line:
                for square in square_list:
                    if square not in piece_placement_data:
                        continue
                    square_piece = piece_placement_data[square]
                    if square_piece.color == side:
                        break
                    sources = fen_source_squares.get(square_piece.name)
                    if sources is None or square not in sources.get(
                        king_square_name, ""
                    ):
                        break
                    return True
        if source_square_piece[0][1].name in KNIGHTS:
            return (
                source_square_piece[0][1].square.name
                in fen_source_squares[FEN_WHITE_KNIGHT][king_square_name]
            )
        return False

    def is_square_attacked_by_other_side(self, square, side):
        """Return True if square is attacked by a piece not of side."""
        piece_placement_data = self._piece_placement_data

        for square_list in fen_squares[square].attack_lines():
            for sqr in square_list:
                if sqr not in piece_placement_data:
                    continue
                piece = piece_placement_data[sqr]
                if piece.color == side:
                    break
                sources = fen_source_squares.get(piece.name)
                if sources is None or sqr not in sources.get(square, ""):
                    break
                return True

        if side == FEN_WHITE_ACTIVE:
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
            if piece.color == side:
                break
            if piece.name == knight_search:
                if square in square_list[sqr]:
                    return True

        return False

    # There are situations where it is reasonable to assume False is the
    # correct answer.  In those cases is_side_off_move_in_check should be
    # overridden to return False.
    def is_side_off_move_in_check(self):
        """Return True if king of side off-move is in check.

        This method is intended to test a move does not leave the king of
        the side making the move in check.

        """
        side = OTHER_SIDE[self._active_color]
        return self.is_square_attacked_by_other_side(
            self._pieces_on_board[SIDE_TO_MOVE_KING[side]][0].square.name,
            side,
        )

    def is_piece_pinned_to_king(self, piece, square_before_move):
        """Return True if piece is pinned to king."""
        king_square = self._pieces_on_board[PIECE_TO_KING[piece.name]][
            0
        ].square
        attack_line = king_square.attack_line(square_before_move)
        if attack_line is None:
            return False
        side = self._active_color
        king_square_name = king_square.name
        piece_placement_data = self._piece_placement_data
        for square_list in attack_line:
            for square in square_list:
                if square not in piece_placement_data:
                    continue
                square_piece = piece_placement_data[square]
                if square_piece.color == side:
                    break
                sources = fen_source_squares.get(square_piece.name)
                if sources is None or square not in sources.get(
                    king_square_name, ""
                ):
                    break
                return True
        return False

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
        # The item list in piece is long enough to cause pylint duplicate-code
        # reports citing pgn_read.core.constants module.
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
                piece = Piece(fen_char, fen_square_names[i])
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
                if en_passant_target_square not in fen_squares:
                    return False
                if active_color == FEN_WHITE_ACTIVE:
                    target_pawn = FEN_BLACK_PAWN
                else:
                    target_pawn = FEN_WHITE_PAWN
                if en_passant_target_square in piece_placement_data:
                    return False
                for k, target_square in en_passant_target_squares[
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
                    if self.is_square_attacked_by_other_side(
                        piece.square.name, OTHER_SIDE[active_color]
                    ):
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
        self.set_board_state(((self._ravstack[-1][1],) + place[1:],))
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
        self.repeat_board_state()
        self._ravstack[-1].extend((self._position_deltas[-1][0], None, None))

    def set_position_to_play_main_line_at_move(self):
        """Set position associated with end_of_rav token."""
        rav_piece_placement_data, place, remove = self._ravstack[-1][1:]
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
            fen_squares[r[0]].castling_rights_lost for r in remove
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

    def get_movetext(self):
        """Return list of movetext.

        Moves have check and checkmate indicators, but not the black move
        indicators found in export format if a black move follows a comment
        or is first move in a RAV, nor move numbers.

        """
        if self._movetext_offset is None:
            return []
        return self._text[self._movetext_offset :]

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

    def _append_token_and_set_error(self, match, index=0):
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
        self._text.append(PGN_TOKEN_SEPARATOR + match.group(index))

        # len(self._position_deltas) will be 0 if end of buffer reached while
        # collecting PGN Tags.
        try:
            self.repeat_board_state()
        except IndexError:
            if self._position_deltas:
                raise

    def _reset_after_end_rav(self, match):
        """Return True if game state is reset after end RAV, ')'.

        Put game in error state if a variation cannot be finished at current
        place in game score and return False.

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
            self._append_token_and_set_error(match)
            return False

        if self._movetext_offset is None:
            self._append_token_and_set_error(match)
            return False
        if len(self._ravstack) == 1:
            self._append_token_and_set_error(match)
            return False
        del self._ravstack[-1]
        del self._state_stack[-1]
        self._state = self._state_stack[-1]

        # The formal syntax for PGN, section 18 in specification, allows '()'
        # as a recursive annotation variation.
        # The commented code bans this sequence.
        # if (self._active_color == self._ravstack[-1][3][1] and
        #    self._fullmove_number == self._ravstack[-1][3][5]):
        #    self._append_token_and_set_error(match)
        #    return False
        return True

    def _reset_position_after_end_rav(self, match):
        """Reset position after end rav, ')'.

        This method should be called only if _reset_after_end_rav has
        returned True.  It is not part of _reset_after_end_rav because some
        versions of append_end_rav() do not want this done at all after the
        _reset_after_end_rav() call.

        """
        del match
        if self._ravstack[-1][2] is None:
            self.set_position_to_play_prior_right_nested_rav_at_move()
        else:
            self.set_position_to_play_main_line_at_move()

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

    def _reset_after_start_rav(self, match):
        """Return True if game state is reset after start RAV, '('.

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
            self._append_token_and_set_error(match)
            return False

        if len(self._ravstack[-1]) == 1:
            if self._position_deltas[-1] is None:
                self._append_token_and_set_error(match)
                return False
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
            self.set_board_state(
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
        self._state_stack.append(self._state)
        return True

    def _modify_game_state_castles(
        self, remove, place, fullmove_number_for_next_halfmove
    ):
        """Modify game state for castles move."""
        self.remove_piece_on_square(remove[0])
        self.remove_piece_on_square(remove[1])
        self.place_piece_on_square(place[0])
        self.place_piece_on_square(place[1])
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

    def _modify_game_state_piece_move(
        self, remove, place, fullmove_number_for_next_halfmove
    ):
        """Modify game state for piece move without capture.

        Note .game.Game.append_piece_move() method cannot use this because
        it modifies game state while confirming king is not left in check
        and does not reset before calling modify_board_state itself.

        """
        self.remove_piece_on_square(remove[0])
        self.place_piece_on_square(place[0])
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

    def _modify_game_state_piece_capture(
        self, remove, place, fullmove_number_for_next_halfmove
    ):
        """Modify game state for piece move with capture.

        Note .game.Game.append_piece_move() method cannot use this because
        it modifies game state while confirming king is not left in check
        and does not reset before calling modify_board_state itself.

        """
        self.remove_piece_from_board(remove[0])
        self.remove_piece_on_square(remove[1])
        self.place_piece_on_square(place[0])
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
                    0,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )

    def _modify_game_state_pawn_move(
        self,
        remove,
        place,
        fullmove_number_for_next_halfmove,
        new_en_passant_target_square,
    ):
        """Modify game state for pawn move without promotion.

        Note .game.Game.append_pawn_move() method cannot use this because
        it modifies game state while confirming king is not left in check
        and does not reset before calling modify_board_state itself.

        """
        self.remove_piece_on_square(remove[0])
        self.place_piece_on_square(place[0])
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
                    new_en_passant_target_square,
                    0,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )

    def _modify_game_state_pawn_capture(
        self, remove, place, fullmove_number_for_next_halfmove
    ):
        """Modify game state for pawn move with capture without promotion.

        Note .game.Game.append_pawn_move() method cannot use this because
        it modifies game state while confirming king is not left in check
        and does not reset before calling modify_board_state itself.

        """
        self.remove_piece_from_board(remove[0])
        self.remove_piece_from_board(remove[1])
        self.place_piece_on_board(place[0])
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
                    0,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )

    def _modify_game_state_pawn_promote(
        self, remove, place, fullmove_number_for_next_halfmove
    ):
        """Modify game state for pawn promotion without capture.

        Note .game.Game.append_pawn_promote_move() method cannot use this
        because it modifies game state while confirming king is not left in
        check and does not reset before calling modify_board_state itself.

        """
        self.remove_piece_from_board(remove[0])
        self.place_piece_on_board(place[0])
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
                    0,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )

    def _modify_game_state_pawn_promote_capture(
        self, remove, place, fullmove_number_for_next_halfmove
    ):
        """Modify game state for pawn promotion with capture.

        Note .game.Game.append_pawn_promote_move() method cannot use this
        because it modifies game state while confirming king is not left in
        check and does not reset before calling modify_board_state itself.

        """
        self.remove_piece_from_board(remove[0])
        self.remove_piece_from_board(remove[1])
        self.place_piece_on_board(place[0])
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
                    0,
                    fullmove_number_for_next_halfmove,
                ),
            )
        )

    def _append_decorated_text(self, movetext):
        """Append movetext to self._text.

        Subclasses may extand or override this method to decorate the text
        with some combination of check indicators, source square name, and
        side of moving piece.

        """
        self._text.append(movetext)

    def _append_decorated_castles_text(self, movetext):
        """Append movetext to self._text.

        Subclasses may extand or override this method to decorate the text
        with some combination of check indicators, source square name, and
        side of moving piece.

        """
        self._text.append(movetext)


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
