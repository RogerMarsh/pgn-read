# parser.py
# Copyright 2003, 2010, 2016 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Portable Game Notation (PGN) parser.

This parser checks that a sequence of PGN represents a playable game and
deduces the moves played from the PGN.

The PGN specification is very lenient compared with the export format and is
hardly less strict than the import format.

A sequence of moves in export format is '12. Qe2 Rfe8 13. Rc1 Rac8' but the
sequence '12. Qe2 12. 12..{Poorly placed commentary}. Rfe8 13. Rc1 Rac8' is
not banned by the specification for import format, despite the additional
move numbers and oddly placed comment.

This parser accepts '12.Qe212.12..{Poorly placed commentary}.Rfe8Rc1Rac8' and
so on.  No whitespace required outside comments.  It has to know the board
position to do this: does Qd1f3 mean a queen move (to d1) followed by a pawn
move (to f3) or a queen move (from d1 to f3) if more than two queens are able
to move to f3.

"""

import re

from .constants import (
    FULLSTOP,
    LEFT_ANGLE_BRACE,
    RIGHT_ANGLE_BRACE,
    PERCENT,
    IMPORT_FORMAT,
    DISAMBIGUATE_FORMAT,
    UNAMBIGUOUS_FORMAT,
    POSSIBLE_MOVE,
    IFG_START_TAG,
    IFG_TAG_SYMBOL,
    IFG_TAG_STRING_VALUE,
    IFG_PAWN_PROMOTE_FROM_FILE,
    IFG_PAWN_TAKES_PROMOTE,
    IFG_PAWN_PROMOTE_SQUARE,
    IFG_PAWN_PROMOTE_PIECE,
    IFG_PAWN_CAPTURE_FROM_FILE,
    IFG_PAWN_TAKES,
    IFG_PAWN_CAPTURE_SQUARE,
    IFG_KING_CAPTURE,
    IFG_PIECE_CAPTURE,
    IFG_PIECE_CAPTURE_FROM,
    IFG_PIECE_TAKES,
    IFG_PIECE_CAPTURE_SQUARE,
    IFG_PIECE_CHOICE,
    IFG_PIECE_CHOICE_FILE_OR_RANK,
    IFG_PIECE_CHOICE_SQUARE,
    IFG_PIECE_MOVE,
    IFG_PIECE_SQUARE,
    IFG_PAWN_SQUARE,
    IFG_CASTLES,
    IFG_CHECK,
    IFG_ANNOTATION,
    IFG_COMMENT,
    IFG_NAG,
    IFG_COMMENT_TO_EOL,
    IFG_TERMINATION,
    IFG_START_RAV,
    IFG_END_RAV,
    IFG_ANYTHING_ELSE,
    PGN_SEARCHING,
    PGN_SEARCHING_AFTER_ERROR_IN_RAV,
    PGN_SEARCHING_AFTER_ERROR_IN_GAME,
    PGN_COLLECTING_TAG_PAIRS,
    PGN_COLLECTING_MOVETEXT,
    PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING,
    PGN_DISAMBIGUATE_MOVE,
    LINEFEED,
    CARRIAGE_RETURN,
    START_TAG,
    END_TAG,
    SPACE,
    HORIZONTAL_TAB,
    FORMFEED,
    VERTICAL_TAB,
    NEWLINE,
    TAG_FEN,
    RESULT_SET,
    PLAIN_MOVE,
    NOPIECE,
    O_O_O,
    O_O,
    SEVEN_TAG_ROSTER,
    PGN_FROM_SQUARE_DISAMBIGUATION,
    MOVE_NUMBER_KEYS,
    NON_MOVE,
    MOVE_ERROR,
    MOVE_AFTER_ERROR,
    MOVE_TEXT,
    TAG_RESULT,
    TAG_OPENING,
    SEVEN_TAG_ROSTER_EXPORT_ORDER,
    REPERTOIRE_TAG_ORDER,
    REPERTOIRE_GAME_TAGS,
    PGN_MAX_LINE_LEN,
    SEVEN_TAG_ROSTER_ARCHIVE_SORT1,
    SEVEN_TAG_ROSTER_ARCHIVE_SORT2,
    TAG_DATE,
    TAG_ROUND,
    SPECIAL_TAG_DATE,
    SPECIAL_TAG_ROUND,
    NORMAL_TAG_ROUND,
    WKING,
    WQUEEN,
    WROOK,
    WBISHOP,
    WKNIGHT,
    WPAWN,
    BKING,
    BQUEEN,
    BROOK,
    BBISHOP,
    BKNIGHT,
    BPAWN,
    WHITE_SIDE,
    INITIAL_BOARD,
    INITIAL_BOARD_BITMAP,
    INITIAL_OCCUPIED_SQUARES,
    INITIAL_PIECE_LOCATIONS,
    FEN_FIELD_DELIM,
    FEN_FIELD_COUNT,
    FEN_SIDES,
    FEN_NULL,
    FEN_INITIAL_CASTLING,
    FEN_WHITE,
    FEN_INITIAL_HALFMOVE_COUNT,
    FEN_WHITE_MOVE_TO_EN_PASSANT,
    FEN_INITIAL_FULLMOVE_NUMBER,
    FEN_RANK_DELIM,
    BOARDSIDE,
    FEN_PIECE_COUNT_PER_SIDE_MAX,
    FEN_KING_COUNT,
    FEN_PAWN_COUNT_MAX,
    FEN_QUEEN_COUNT_INITIAL,
    FEN_ROOK_COUNT_INITIAL,
    FEN_BISHOP_COUNT_INITIAL,
    FEN_KNIGHT_COUNT_INITIAL,
    CASTLING_W,
    CASTLING_WK,
    CASTLING_WQ,
    CASTLING_B,
    CASTLING_BK,
    CASTLING_BQ,
    WPIECES,
    PIECES,
    SQUARE_BITS,
    GAPS,
    FEN_CASTLING_OPTION_REPEAT_MAX,
    FEN_BLACK,
    FEN_BLACK_MOVE_TO_EN_PASSANT,
    BPIECES,
    PIECE_CAPTURE_MAP,
    OTHER_SIDE,
    SIDE_KING,
    FEN_TOMOVE,
    FEN_MAXIMUM_PIECES_GIVING_CHECK,
    MAPFILE,
    MAP_PGN_SQUARE_NAME_TO_FEN_ORDER,
    MAP_FEN_ORDER_TO_PGN_SQUARE_NAME,
    MAPPIECE,
    CAPTURE_MOVE,
    PIECE_MOVE_MAP,
    FILES,
    PGN_PAWN,
    RANKS,
    EN_PASSANT_FROM_SQUARES,
    EN_PASSANT_TO_SQUARES,
    FEN_EN_PASSANT_TARGET_RANK,
    MAPROW,
    BLACK_SIDE,
    PGN_KING,
    CASTLING_AVAILABITY_SQUARES,
    CASTLING_SQUARES,
    FEN_WHITE_CAPTURE_EN_PASSANT,
    FEN_BLACK_CAPTURE_EN_PASSANT,
    PGN_QUEEN,
    PGN_ROOK,
    PGN_BISHOP,
    PGN_KNIGHT,
    PAWN_MOVE_DESITINATION,
    ERROR_START_COMMENT,
    ESCAPE_END_COMMENT,
    END_COMMENT,
    )

re_tokens = re.compile(IMPORT_FORMAT)

# Avoid re.fullmatch() method while compatibility with Python 3.3 is important.
re_disambiguate_error = re.compile(DISAMBIGUATE_FORMAT.join(('^', '$')))
re_disambiguate_non_move = re.compile(UNAMBIGUOUS_FORMAT.join(('^', '$')))
re_possible_move = re.compile(POSSIBLE_MOVE.join(('(^', '$)')))


class PGNError(Exception):
    pass


class PGN(object):
    """Extract moves, comments, PGN tags from score and check moves are legal.

    None of the data structures specific to displaying a game or updating a
    database are generated.  use the appropriate subclass to do these things.
    
    """

    def __init__(self):
        super().__init__()
        
        # data generated from PGN text for game while checking moves are legal
        self.tokens = []
        self.error_tokens = []
        self.tags_in_order = []
        
        # data generated from PGN text for game after checking moves are legal
        self.collected_game = None
        self.board_bitmap = None
        self.occupied_squares = []
        self.board = []
        self.piece_locations = {}
        self.fullmove_number = None
        self.halfmove_count = None
        self.en_passant = None
        self.castling = None
        self.active_side = None

        # ravstack keeps track of the position at start of game or variation
        # and the position after application of a valid move.  Thus the value
        # in ravstack[-1] is (None, <position start>) at start of game or line
        # and (<position start>, <position after move>) after application of a
        # valid move from gametokens.
        self.ravstack = []
        
        # data used while parsing PGN text to split into tag and move tokens
        self._initial_fen = None
        self._state = None
        self._move_error_state = None
        self._rewind_state = None
        
        self._despatch_table = [
            self._searching,
            self._searching_after_error_in_rav,
            self._searching_after_error_in_game,
            self._collecting_tag_pairs,
            self._collecting_movetext,
            self._collecting_non_whitespace_while_searching,
            self._disambiguate_move,
            ]

    @staticmethod
    def _read_pgn(string, length):
        pgntext = string.read(length)
        while len(pgntext):
            yield pgntext
            pgntext = string.read(length)
        yield pgntext
    
    def read_games(self, source, size=10000000, housekeepinghook=lambda:None):
        """Extract games from file-like source.

        Yield each token where the match is on a game termination token.  The
        collected_game attribute is bound to the game just terminated.

        source - file-like object from which to read pgn text
        size - number of characters to read in each read() call
        housekeepinghook - periodic callback when importing many games

        housekeepinghook introduced to commit database updates in DPT while
        code remains unchanged for other database engines

        """
        self._state = PGN_SEARCHING
        self._move_error_state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
        for pgntext in self._read_pgn(source, size):
            if len(self.error_tokens):
                self._state = self._rewind_state
                pgntext = ''.join(self.error_tokens) + pgntext
                self.error_tokens.clear()
            for t in re_tokens.finditer(pgntext):
                self._despatch_table[self._state](t)
                if t.group(IFG_TERMINATION):
                    yield t
            housekeepinghook()

    def read_pgn_tokens(
        self, source, size=10000000, housekeepinghook=lambda:None):
        """Extract games from file-like source yielding for each token.

        The termination group value for each match is yielded, so bool(<yield>)
        is True for the '1-0', '0-1', '1/2-1/2', and '*', tokens but False for
        the rest.

        source - file-like object from which to read pgn text
        size - number of characters to read in each read() call
        housekeepinghook - ignored, present for compatibility with read_games.

        """
        self._state = PGN_SEARCHING
        self._move_error_state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
        for pgntext in self._read_pgn(source, size):
            if len(self.error_tokens):
                self._state = self._rewind_state
                pgntext = ''.join(self.error_tokens) + pgntext
                self.error_tokens.clear()
            for t in re_tokens.finditer(pgntext):
                self._despatch_table[self._state](t)
                yield t.group(IFG_TERMINATION)

    def get_games(self, source):
        """Extract games from string.

        Yield each token where the match is on a game termination token.  The
        collected_game attribute is bound to the game just terminated.

        source - file-like object from which to read pgn text

        """
        self._state = PGN_SEARCHING
        self._move_error_state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
        for t in re_tokens.finditer(source):
            self._despatch_table[self._state](t)
            if t.group(IFG_TERMINATION):
                yield t

    def get_first_pgn_token(self, source):
        """Return termination group value for first token matched in string.

        Thus bool(<return>) is True for the '1-0', '0-1', '1/2-1/2', and '*',
        tokens but False for the rest.

        source - file-like object from which to read pgn text

        """
        self._state = PGN_SEARCHING
        self._move_error_state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
        try:
            t = next(re_tokens.finditer(source))
            self._despatch_table[self._state](t)
            return False if t.group(IFG_TERMINATION) else True
        except StopIteration:
            return

    def read_first_game(
        self, source, size=10000000, housekeepinghook=lambda:None):
        """Extract first games from file-like source.

        source - file-like object from which to read pgn text
        size - number of characters to read in each read() call
        housekeepinghook - periodic callback when importing many games

        housekeepinghook introduced to commit database updates in DPT while
        code remains unchanged for other database engines

        """
        return next(self.read_games(source,
                                    size=size,
                                    housekeepinghook=housekeepinghook))

    def get_first_game(self, source):
        """Extract first game from string.

        source - file-like object from which to read pgn text

        """
        return next(self.get_games(source))
    
    def is_movetext_valid(self):
        """Return True if there are no error_tokens in the collected game.

        A collected movetext with no PGN errors in the main line but errors in
        one or more RAVs will cause this method to return True.

        """
        return not self.collected_game[3]
    
    def is_pgn_valid(self):
        """Return True if the tags and movetext in the collected game are valid.

        A collected movetext with no PGN errors in the main line but errors in
        one or more RAVs will cause this method to return True.

        """
        return self.is_movetext_valid() and self.is_tag_roster_valid()
    
    def is_tag_roster_valid(self):
        """Return True if the tag roster in the collected game is valid."""
        tags_in_order = self.collected_game[0]
        tags = self.collected_game[1]
        if len(tags) != len(tags_in_order):
            # Tag must appear no more than once
            return False
        for v in tags.values():
            if len(v) == 0:
                # Tag value must not be null
                return False
        for t in SEVEN_TAG_ROSTER:
            if t not in tags:
                # A mandatory tag is missing
                return False
        return True

    def set_position_fen(self, fen=None):
        """Initialize PGN score parser with Forsyth Edwards Notation position.

        fen defaults to the starting position for a game of chess.

        All the validition that is either simple or important is implemented,
        but this function will accept positions that cannot be reached by any
        legal sequence of moves from the standard starting position as valid.
        Thus an argument placing pawns on rank 0 or rank 7 is rejected, but
        an argument placing 8 black pawns on rank 2 and 8 white pawns on rank
        5 with all other pieces on their starting squares is accepted.
        
        """
        # fen is standard start position by default
        if fen is None:
            self.board_bitmap = INITIAL_BOARD_BITMAP
            self.board = list(INITIAL_BOARD)
            self.occupied_squares[:] = [
                set(s) for s in INITIAL_OCCUPIED_SQUARES]
            self.piece_locations = {k:set(v)
                                    for k, v in INITIAL_PIECE_LOCATIONS.items()}
            self.ravstack[:] = [(None, (INITIAL_BOARD,
                                        WHITE_SIDE,
                                        FEN_INITIAL_CASTLING,
                                        FEN_NULL))]
            self.active_side = WHITE_SIDE
            self.castling = FEN_INITIAL_CASTLING
            self.en_passant = FEN_NULL
            self.halfmove_count = FEN_INITIAL_HALFMOVE_COUNT
            self.fullmove_number = FEN_INITIAL_FULLMOVE_NUMBER
            self._initial_fen = True
            return

        # fen specifies an arbitrary position.

        # fen has six space delimited fields.
        fs = fen.split(FEN_FIELD_DELIM)
        if len(fs) != FEN_FIELD_COUNT:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        (piece_placement,
         active_side,
         castling,
         en_passant,
         halfmove_count,
         fullmove_number,
         ) = fs
        del fs

        # fen side to move field.
        if active_side not in FEN_SIDES:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # fen castling field.
        if castling != FEN_NULL:
            for c in FEN_INITIAL_CASTLING:
                if castling.count(c) > FEN_CASTLING_OPTION_REPEAT_MAX:
                    self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                    return
            for c in castling:
                if c not in FEN_INITIAL_CASTLING:
                    self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                    return

        # fen square to which a pawn can move when capturing en passant.
        if active_side == FEN_WHITE:
            if en_passant not in FEN_WHITE_MOVE_TO_EN_PASSANT:
                if en_passant != FEN_NULL:
                    self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                    return
        elif active_side == FEN_BLACK:
            if en_passant not in FEN_BLACK_MOVE_TO_EN_PASSANT:
                if en_passant != FEN_NULL:
                    self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                    return

        # Earlier 'fen side to move field' test makes this unreachable.
        else:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # fen halfmove count since pawn move or capture.
        if not halfmove_count.isdigit():
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # fen fullmove number.
        if not fullmove_number.isdigit():
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # fen piece placement field has eight ranks delimited by '/'.
        ranks = piece_placement.split(FEN_RANK_DELIM)
        if len(ranks) != BOARDSIDE:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # fen piece placement field has pieces and empty squares only.
        for r in ranks:
            for c in r:
                if c not in PIECES:
                    if not c.isdigit():
                        self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                        return

        # Exactly 64 squares: equivalent to exactly 8 squares per rank.
        for r in ranks:
            if sum([1 if not s.isdigit() else int(s)
                    for s in r]) != BOARDSIDE:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return

        # No pawns on first or eighth ranks.
        if (ranks[0].count(WPAWN) +
            ranks[0].count(BPAWN) +
            ranks[BOARDSIDE-1].count(WPAWN) +
            ranks[BOARDSIDE-1].count(BPAWN)):
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # No more than 16 pieces per side.
        for s in WPIECES, BPIECES:
            for p in s:
                if sum([piece_placement.count(p)
                        for p in s]) > FEN_PIECE_COUNT_PER_SIDE_MAX:
                    self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                    return

        # Exactly one king per side.
        for p in WKING, BKING:
            if piece_placement.count(p) != FEN_KING_COUNT:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return

        # No more than eight pawns per side.
        for p in WPAWN, BPAWN:
            if piece_placement.count(p) > FEN_PAWN_COUNT_MAX:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return

        # Piece counts within initial position and pawn promotion bounds.
        if (piece_placement.count(WPAWN) -
            FEN_PAWN_COUNT_MAX +
            max(piece_placement.count(WQUEEN) -
                FEN_QUEEN_COUNT_INITIAL, 0) +
            max(piece_placement.count(WROOK) -
                FEN_ROOK_COUNT_INITIAL, 0) +
            max(piece_placement.count(WBISHOP) -
                FEN_BISHOP_COUNT_INITIAL, 0) +
            max(piece_placement.count(WKNIGHT) -
                FEN_KNIGHT_COUNT_INITIAL, 0)
            ) > 0:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        if (piece_placement.count(BPAWN) -
            FEN_PAWN_COUNT_MAX +
            max(piece_placement.count(BQUEEN) -
                FEN_QUEEN_COUNT_INITIAL, 0) +
            max(piece_placement.count(BROOK) -
                FEN_ROOK_COUNT_INITIAL, 0) +
            max(piece_placement.count(BBISHOP) -
                FEN_BISHOP_COUNT_INITIAL, 0) +
            max(piece_placement.count(BKNIGHT) -
                FEN_KNIGHT_COUNT_INITIAL, 0)
            ) > 0:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # Position is legal apart from checks, actual and deduced, and deduced
        # move that sets up en passant capture possibility.
        board = []
        for r in ranks:
            for c in r:
                if c in PIECES:
                    board.append(c)
                else:
                    board.extend([NOPIECE] * int(c))

        # Castling availability must fit the board position.
        if board[CASTLING_W] != WKING:
            if WKING in castling:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return
            if WQUEEN in castling:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return
        if board[CASTLING_B] != BKING:
            if BKING in castling:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return
            if BQUEEN in castling:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return
        if board[CASTLING_WK] != WROOK:
            if WKING in castling:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return
        if board[CASTLING_WQ] != WROOK:
            if WQUEEN in castling:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return
        if board[CASTLING_BK] != BROOK:
            if BKING in castling:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return
        if board[CASTLING_BQ] != BROOK:
            if BQUEEN in castling:
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return

        # the two squares behind the pawn that can be captured en passant
        # must be empty. FEN quotes en passant capture square if latest move
        # is a two square pawn move,there does not need to be a pawn able to
        # make the capture. The side with the move must not be in check
        # diagonally through the square containing a pawn that can be captured
        # en passant, treating that square as empty.
        if en_passant != FEN_NULL:
            if en_passant in FEN_WHITE_MOVE_TO_EN_PASSANT:
                s = FEN_WHITE_MOVE_TO_EN_PASSANT[en_passant]
                if (board[s] != NOPIECE or
                    board[s-8] != NOPIECE or
                    board[s+8] != BPAWN):
                    self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                    return
            elif en_passant in FEN_BLACK_MOVE_TO_EN_PASSANT:
                s = FEN_BLACK_MOVE_TO_EN_PASSANT[en_passant]
                if (board[s] != NOPIECE or
                    board[s+8] != NOPIECE or
                    board[s-8] != WPAWN):
                    self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                    return
            else:

                # Should not happen, caught earlier.
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return

        # FEN is legal, except for restrictions on kings in check, so set
        # instance attributes to fit description of position.
        piece_locations = {k:set() for k in INITIAL_PIECE_LOCATIONS}
        active_side_squares = set()
        inactive_side_squares = set()
        board_bitmap = []
        if active_side == FEN_WHITE:
            active_side_pieces = WPIECES
        else:
            active_side_pieces = BPIECES
        for s, p in enumerate(board):
            if p in PIECES:
                piece_locations[p].add(s)
                board_bitmap.append(SQUARE_BITS[s])
                if p in active_side_pieces:
                    active_side_squares.add(s)
                else:
                    inactive_side_squares.add(s)
        for active_side_king_square in piece_locations[
            SIDE_KING[FEN_SIDES[active_side]]]:
            pass # set active_side_king_square without pop() and add().
        for inactive_side_king_square in piece_locations[
            SIDE_KING[OTHER_SIDE[FEN_SIDES[active_side]]]]:
            pass # set active_side_king_square without pop() and add().

        # Side without the move must not be in check.
        # Cannot use is_active_king_attacked method because attributes are
        # not set until the position is ok.
        gap = GAPS[inactive_side_king_square]
        board_bitmap = sum(board_bitmap)
        for s in active_side_squares:
            if (not board_bitmap & gap[s] and
                SQUARE_BITS[s] &
                PIECE_CAPTURE_MAP[board[s]][inactive_side_king_square]):
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                return

        # Side with the move must not be in check from more than two squares.
        # Cannot use count_attacks_on_square_by_side method because attributes
        # are not set until the position is ok.
        gap = GAPS[active_side_king_square]
        if len([s for s in inactive_side_squares
                if (not board_bitmap & gap[s] and
                    SQUARE_BITS[s] &
                    PIECE_CAPTURE_MAP[board[s]][active_side_king_square]
                    )]) > FEN_MAXIMUM_PIECES_GIVING_CHECK:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        self.board_bitmap = board_bitmap
        self.board = board
        if active_side == FEN_WHITE:
            self.occupied_squares[
                :] = active_side_squares, inactive_side_squares
        else:
            self.occupied_squares[
                :] = inactive_side_squares, active_side_squares
        self.piece_locations = piece_locations
        self.ravstack[:] = [(None, (tuple(board),
                                    FEN_SIDES[active_side],
                                    castling,
                                    en_passant))]
        self.active_side = FEN_SIDES[active_side]
        self.castling = castling
        self.en_passant = en_passant
        self.halfmove_count = int(halfmove_count)
        self.fullmove_number = int(fullmove_number)
        self._initial_fen = fen

    def _play_move(self,
                   pgn_piece,
                   pgn_from,
                   pgn_capture,
                   pgn_tosquare,
                   pgn_promote):
        """Play move or adjust state to indicate move was not played.

        State constants.PGN_FROM_SQUARE_DISAMBIGUATION indicates it is possible
        the stated move is the first part of a move specification where more
        than two pieces of the same kind can move to a square: Qd1 where Qd1f3
        is needed to state the move, for example.

        State False indicates the stated move cannot be played in the position.

        """
        tosquare = MAP_PGN_SQUARE_NAME_TO_FEN_ORDER[pgn_tosquare]
        piece = MAPPIECE[self.active_side][pgn_piece]
        g = GAPS[tosquare]
        b = self.board
        bb = self.board_bitmap
        if pgn_capture == CAPTURE_MOVE:
            pts = PIECE_CAPTURE_MAP[piece][tosquare]
        else:
            pts = PIECE_MOVE_MAP[piece][tosquare]
        from_squares = [s for s in self.piece_locations[piece]
                        if (SQUARE_BITS[s] & pts and not bb & g[s])]
        if len(from_squares) > 1:
            if pgn_from:
                fm = MAPFILE.get(pgn_from[0])
                if fm is not None:
                    fm = FILES[fm]
                    from_squares = [s for s in from_squares
                                    if SQUARE_BITS[s] & fm]
                if len(from_squares) > 1:
                    fm = MAPROW.get(pgn_from[-1])
                    if fm is not None:
                        fm = RANKS[fm]
                        from_squares = [s for s in from_squares
                                        if SQUARE_BITS[s] & fm]
            if len(from_squares) > 1:
                inactive_side_squares = self.occupied_squares[
                    OTHER_SIDE[self.active_side]]
                for active_side_king_square in self.piece_locations[
                    SIDE_KING[self.active_side]]:
                    pass # set active_side_king_square without pop() and add().
                gk = GAPS[active_side_king_square]
                pinned_to_king = set()
                for si in inactive_side_squares:
                    if PIECE_CAPTURE_MAP[b[si]][active_side_king_square
                                                ] & SQUARE_BITS[si]:
                        for s in from_squares:
                            if gk[si] & SQUARE_BITS[s]:
                                if not ((bb ^ SQUARE_BITS[s] |
                                         SQUARE_BITS[tosquare]) &
                                        gk[si]):
                                    if si != tosquare:
                                        pinned_to_king.add(s)
                from_squares = [s for s in from_squares
                                if s not in pinned_to_king]
        if pgn_capture == PLAIN_MOVE and b[tosquare] == piece:

            # If moving piece is on tosquare and the next token is a square
            # identity try tosquare as fromsquare and next token as tosquare
            # for the piece move.
            # Only applies to Q B N non-capture moves where the moving side
            # has more than 2 of the moving piece so it is possible there
            # are two pieces of the moving kind on the same rank and the
            # same file at the same time which can reach the tosquare.
            # Check that there are at least three pieces of one kind which
            # can move to the same square and note the possibilities for
            # evaluation in two subsequent states where the next tokens are
            # readily available for comparison.  The next two tokens must be
            # '' and a square identity and the square identity must be one
            # of the possibilities.
            if b.count(piece) > 2:
                if pgn_piece in PGN_FROM_SQUARE_DISAMBIGUATION:
                    self._state = PGN_DISAMBIGUATE_MOVE
                    self._rewind_state = self._state
                    return

            self._illegal_play_move()
            return

        # After the disambiguation test, plain move to square containing piece
        # which is moving, because queen moves like both rook and bishop.
        if len(from_squares) != 1:
            self._illegal_play_move()
            return

        piece_locations = self.piece_locations
        fromsquare = from_squares.pop()
        if pgn_capture == CAPTURE_MOVE:
            inactive_side_squares = self.occupied_squares[
                OTHER_SIDE[self.active_side]]
            if tosquare not in inactive_side_squares:
                if pgn_piece != PGN_PAWN:
                    self._illegal_play_move()
                    return
                elif pgn_tosquare != self.en_passant:
                    self._illegal_play_move()
                    return

                # Remove pawn captured en passant.
                elif self.en_passant in FEN_WHITE_CAPTURE_EN_PASSANT:
                    eps = FEN_WHITE_CAPTURE_EN_PASSANT[self.en_passant]
                    b[eps] = NOPIECE
                    inactive_side_squares.remove(eps)
                    piece_locations[BPAWN].remove(eps)
                    self.board_bitmap &= (
                        self.board_bitmap ^ SQUARE_BITS[eps])
                elif self.en_passant in FEN_BLACK_CAPTURE_EN_PASSANT:
                    eps = FEN_BLACK_CAPTURE_EN_PASSANT[self.en_passant]
                    b[eps] = NOPIECE
                    inactive_side_squares.remove(eps)
                    piece_locations[WPAWN].remove(eps)
                    self.board_bitmap &= (
                        self.board_bitmap ^ SQUARE_BITS[eps])

                else:
                    self._illegal_play_move()
                    return

            else:
                inactive_side_squares.remove(tosquare)
                piece_locations[b[tosquare]].remove(tosquare)
            self.en_passant = FEN_NULL
            self.halfmove_count = 0
        elif SQUARE_BITS[tosquare] & bb:
            self._illegal_play_move()
            return
        elif pgn_piece == PGN_PAWN:

            # Moves like 'b1' for black, and 'b8' for white, are passed earlier
            # to cope with disambiguating queen moves like 'Qd1f1'.
            if not (SQUARE_BITS[tosquare] &
                    PAWN_MOVE_DESITINATION[self.active_side]):
                if not pgn_promote:
                    self._illegal_play_move()
                    return
            
            self.halfmove_count = 0
            if (SQUARE_BITS[fromsquare] & EN_PASSANT_FROM_SQUARES and
                SQUARE_BITS[tosquare] & EN_PASSANT_TO_SQUARES):
                self.en_passant = (
                    pgn_tosquare[0] +
                    FEN_EN_PASSANT_TARGET_RANK[pgn_tosquare[1]])
            else:
                self.en_passant = FEN_NULL
        else:
            self.en_passant = FEN_NULL
            self.halfmove_count = self.halfmove_count + 1
        active_side_squares = self.occupied_squares[self.active_side]

        # Remove moving piece from current square.
        b[fromsquare] = NOPIECE
        active_side_squares.remove(fromsquare)
        piece_locations[piece].remove(fromsquare)
        self.board_bitmap &= self.board_bitmap ^ SQUARE_BITS[fromsquare]

        # Put moving piece on new square.
        b[tosquare] = piece
        active_side_squares.add(tosquare)
        piece_locations[piece].add(tosquare)
        self.board_bitmap |= SQUARE_BITS[tosquare]

        # Replace moving pawn on promotion and update inactive king square.
        if pgn_promote:
            piece_locations[b[tosquare]].remove(tosquare)
            b[tosquare] = MAPPIECE[self.active_side][pgn_promote]
            piece_locations[b[tosquare]].add(tosquare)
        
        # Undo move if it leaves king in check.
        if self.is_active_king_attacked():
            self.reset_position(self.ravstack[-1][-1])
            self._illegal_play_move()
            return

        # Castling availabity.
        # tosquare tests deal with capture of rooks which have not moved.
        # For real games the top condition is false for more than half the game
        # and the next condition is usually false.
        if self.castling != FEN_NULL:
            if ((SQUARE_BITS[fromsquare] | SQUARE_BITS[tosquare]) &
                CASTLING_AVAILABITY_SQUARES):
                if fromsquare == CASTLING_W:
                    self.castling = self.castling.replace(WKING, NOPIECE)
                    self.castling = self.castling.replace(WQUEEN, NOPIECE)
                elif fromsquare == CASTLING_WK:
                    self.castling = self.castling.replace(WKING, NOPIECE)
                elif fromsquare == CASTLING_WQ:
                    self.castling = self.castling.replace(WQUEEN, NOPIECE)
                elif fromsquare == CASTLING_B:
                    self.castling = self.castling.replace(BKING, NOPIECE)
                    self.castling = self.castling.replace(BQUEEN, NOPIECE)
                elif fromsquare == CASTLING_BK:
                    self.castling = self.castling.replace(BKING, NOPIECE)
                elif fromsquare == CASTLING_BQ:
                    self.castling = self.castling.replace(BQUEEN, NOPIECE)
                elif tosquare == CASTLING_WK:
                    self.castling = self.castling.replace(WKING, NOPIECE)
                elif tosquare == CASTLING_WQ:
                    self.castling = self.castling.replace(WQUEEN, NOPIECE)
                elif tosquare == CASTLING_BK:
                    self.castling = self.castling.replace(BKING, NOPIECE)
                elif tosquare == CASTLING_BQ:
                    self.castling = self.castling.replace(BQUEEN, NOPIECE)
                if self.castling == NOPIECE:
                    self.castling = FEN_NULL

        self.add_move_to_game()

    def _play_castles(self, token):
        """Play move or adjust state to indicate move was not played.

        State False indicates the stated move cannot be played in the position.

        """

        # Verify castling availability and pick castling rules.
        if token.startswith(O_O_O):
            if self.active_side == WHITE_SIDE:
                if WQUEEN not in self.castling:
                    self._illegal_play_castles()
                    return
                castling_squares = CASTLING_SQUARES[WQUEEN]
            else:
                if BQUEEN not in self.castling:
                    self._illegal_play_castles()
                    return
                castling_squares = CASTLING_SQUARES[BQUEEN]
        elif token.startswith(O_O):
            if self.active_side == WHITE_SIDE:
                if WKING not in self.castling:
                    self._illegal_play_castles()
                    return
                castling_squares = CASTLING_SQUARES[WKING]
            else:
                if BKING not in self.castling:
                    self._illegal_play_castles()
                    return
                castling_squares = CASTLING_SQUARES[BKING]
        else:
            self._illegal_play_castles()
            return

        bb = self.board_bitmap
        board = self.board
        piece_locations = self.piece_locations
        active_side_squares = self.occupied_squares[self.active_side]
        active_side_king_locations = piece_locations[
            SIDE_KING[self.active_side]]
        if self.active_side == WHITE_SIDE:
            active_side_rook_locations = piece_locations[WROOK]
        else:
            active_side_rook_locations = piece_locations[BROOK]
        for active_side_king_square in active_side_king_locations:
            pass # set active_side_king_square without pop() and add().

        # Confirm board position is consistent with castling availability.
        if (active_side_king_square != castling_squares[0] or
            board[castling_squares[0]] != castling_squares[5] or
            board[castling_squares[1]] != castling_squares[4]):
            self._illegal_play_castles()
            return

        # Squares between king and castling rook must be empty.
        for squares in castling_squares[2:4]:
            for s in squares:
                if SQUARE_BITS[s] & bb:
                    self._illegal_play_castles()
                    return

        # Castling king must not be in check.
        if self.is_square_attacked_by_side(castling_squares[0],
                                           OTHER_SIDE[self.active_side]):
            self._illegal_play_castles()
            return

        # Castling king's destination square, and the one between, must not be
        # attacked by the other side.
        for square in castling_squares[2]:
            if self.is_square_attacked_by_side(
                square, OTHER_SIDE[self.active_side]):
                self._illegal_play_castles()
                return

        king_square = castling_squares[0]
        new_king_square = castling_squares[2][1]
        rook_square = castling_squares[1]
        new_rook_square = castling_squares[2][0]

        # Put moving pieces on new squares.
        board[new_king_square] = board[king_square]
        board[new_rook_square] = board[rook_square]
        active_side_squares.add(new_king_square)
        active_side_king_locations.add(new_king_square)
        active_side_squares.add(new_rook_square)
        active_side_rook_locations.add(new_rook_square)
        self.board_bitmap |= (SQUARE_BITS[new_king_square] |
                              SQUARE_BITS[new_rook_square])

        # Remove moving pieces from current squares.
        board[king_square] = NOPIECE
        board[rook_square] = NOPIECE
        active_side_squares.remove(king_square)
        active_side_king_locations.remove(king_square)
        active_side_squares.remove(rook_square)
        active_side_rook_locations.remove(rook_square)
        self.board_bitmap &= (
            self.board_bitmap ^ (SQUARE_BITS[king_square] |
                                 SQUARE_BITS[rook_square]))

        # Castling availabity.
        if self.active_side == WHITE_SIDE:
            self.castling = self.castling.replace(
                WKING, NOPIECE)
            self.castling = self.castling.replace(
                WQUEEN, NOPIECE)
        else:
            self.castling = self.castling.replace(
                BKING, NOPIECE)
            self.castling = self.castling.replace(
                BQUEEN, NOPIECE)
        if self.castling == NOPIECE:
            self.castling = FEN_NULL

        # Cannot be en-passant
        self.en_passant = FEN_NULL

        self.halfmove_count = self.halfmove_count + 1
        self.add_move_to_game()

    def is_active_king_attacked(self):
        """Return True if king of side with move is attacked.

        Strictly this is not 'in check' because the position is illegal.

        The method is used to check the legality of a proposed move.

        """
        b = self.board
        bb = self.board_bitmap

        # Only one element in this container.
        for ks in self.piece_locations[SIDE_KING[self.active_side]]:
            g = GAPS[ks]
            for s in self.occupied_squares[OTHER_SIDE[self.active_side]]:
                if (not bb & g[s] and
                    SQUARE_BITS[s] & PIECE_CAPTURE_MAP[b[s]][ks]):
                    return True
        return False

    def is_square_attacked_by_side(self, square, side):
        """Return True if square is attacked by at least one piece of side.

        Only pieces which can move to a square if it were their side's turn are
        counted.

        """
        g = GAPS[square]
        b = self.board
        bb = self.board_bitmap
        for s in self.occupied_squares[side]:
            if (not bb & g[s] and
                SQUARE_BITS[s] & PIECE_CAPTURE_MAP[b[s]][square]):
                return True
        return False

    def count_attacks_on_square_by_side(self, square, side):
        """Return count of side's pieces which attack a square.

        Only pieces which can move to a square if it were their side's turn are
        counted.

        """
        g = GAPS[square]
        b = self.board
        bb = self.board_bitmap
        return len([s for s in self.occupied_squares[side]
                    if (not bb & g[s] and
                        SQUARE_BITS[s] & PIECE_CAPTURE_MAP[b[s]][square]
                        )])

    def add_move_to_game(self):
        """Add legal move to data structures describing game.

        """
        self.active_side = OTHER_SIDE[self.active_side]
        self.ravstack[-1] = (
            self.ravstack[-1][-1],
            (tuple(self.board),
             self.active_side,
             self.castling,
             self.en_passant))

    def collect_token(self, match):
        """"""
        self.tokens.append(match)

    def collect_game_tokens(self):
        """Create snapshot of tokens extracted from PGN.

        This method is expected to be called on detection of termination token.

        """
        self.collected_game = (
            self.tags_in_order,
            {m.group(IFG_TAG_SYMBOL):m.group(IFG_TAG_STRING_VALUE)
             for m in self.tags_in_order},
            self.tokens,
            self.error_tokens)

    def _play_disambiguated_move(self, pgn_piece, pgn_fromsquare, pgn_tosquare):
        """Play move or adjust state to indicate move was not played.

        State False indicates the stated move cannot be played in the position.

        the second token in <piece><fromsquare><tosquare> sequence is used to
        determine the move.

        If more than two pieces of a kind can move to a square the move is
        represented as Qd1f3 for example.  The parser treats this sequence as
        a queen move followed by a pawn move normally.  If that assumption
        fails and there is a queen of the side to move on d1 and more than two
        queens of this side on the board the piece move interpretation of
        Qd1f3 is tested by this method.  Rooks, bishops, and knights, too. 

        """
        fromsquare = MAP_PGN_SQUARE_NAME_TO_FEN_ORDER[pgn_fromsquare]
        tosquare = MAP_PGN_SQUARE_NAME_TO_FEN_ORDER[pgn_tosquare]
        piece = MAPPIECE[self.active_side][pgn_piece]
        if fromsquare not in self.piece_locations[piece]:
            self._illegal_play_disambiguated_move()
            return
        if not (SQUARE_BITS[fromsquare] &
                PIECE_MOVE_MAP[piece][tosquare] and not
                self.board_bitmap & GAPS[tosquare][fromsquare]):
            self._illegal_play_disambiguated_move()
            return
        if SQUARE_BITS[tosquare] & self.board_bitmap:
            self._illegal_play_disambiguated_move()
            return
        else:
            self.halfmove_count = self.halfmove_count + 1
        b = self.board
        piece_locations = self.piece_locations
        active_side_squares = self.occupied_squares[self.active_side]

        # Remove moving piece from current square.
        b[fromsquare] = NOPIECE
        active_side_squares.remove(fromsquare)
        piece_locations[piece].remove(fromsquare)
        self.board_bitmap &= self.board_bitmap ^ SQUARE_BITS[fromsquare]

        # Put moving piece on new square.
        b[tosquare] = piece
        active_side_squares.add(tosquare)
        piece_locations[piece].add(tosquare)
        self.board_bitmap |= SQUARE_BITS[tosquare]
        
        # Undo move if it leaves king in check.
        if self.is_active_king_attacked():
            self.reset_position(self.ravstack[-1][-1])
            self._illegal_play_disambiguated_move()
            return

        # Castling availabity is not affected because rooks cannot be involved
        # in moves which need disambiguation.

        # Cannot be en-passant
        self.en_passant = FEN_NULL

        self.add_move_to_game()

    # Maybe should not be a method now, but retain shape of pre-FEN class code
    # for ease of comparison until sure everything works.
    # Just say self._fen = ... where method is called.
    def reset_position(self, position):
        """Reset squares and locations etc to position."""
        board, self.active_side, self.castling, self.en_passant = position
        self.board[:] = list(board)
        occupied_squares = self.occupied_squares
        for side in occupied_squares:
            side.clear()
        piece_locations = self.piece_locations
        for piece in piece_locations.values():
            piece.clear()
        board_bitmap = 0
        for square, piece in enumerate(board):
            if piece in WPIECES:
                occupied_squares[0].add(square)
                piece_locations[piece].add(square)
                board_bitmap |= SQUARE_BITS[square]
            elif piece in BPIECES:
                occupied_squares[1].add(square)
                piece_locations[piece].add(square)
                board_bitmap |= SQUARE_BITS[square]
        self.board_bitmap = board_bitmap

    def _start_variation(self):
        self.ravstack.append((None, self.ravstack[-1][0]))
        self.reset_position(self.ravstack[-1][-1])

    def _end_variation(self):
        try:
            del self.ravstack[-1]
            try:
                self.reset_position(self.ravstack[-1][-1])
            except:
                pass
        except:
            pass

    def _searching(self, match):
        mg = match.group
        if mg(IFG_START_TAG):
            self.tags_in_order.append(match)
            if mg(IFG_TAG_SYMBOL) == TAG_FEN:
                self.set_position_fen(mg(IFG_TAG_STRING_VALUE))
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        if mg(IFG_PIECE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_MOVE),
                            '',
                            '',
                            mg(IFG_PIECE_SQUARE),
                            '')
            return
        if mg(IFG_PAWN_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move('',
                            '',
                            '',
                            mg(IFG_PAWN_SQUARE),
                            '')
            return
        if mg(IFG_PIECE_CAPTURE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_CAPTURE) or mg(IFG_KING_CAPTURE),
                            mg(IFG_PIECE_CAPTURE_FROM),
                            mg(IFG_PIECE_TAKES),
                            mg(IFG_PIECE_CAPTURE_SQUARE),
                            '')
            return
        if mg(IFG_PAWN_CAPTURE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move('',
                            mg(IFG_PAWN_CAPTURE_FROM_FILE),
                            mg(IFG_PAWN_TAKES),
                            mg(IFG_PAWN_CAPTURE_SQUARE),
                            '')
            return
        if mg(IFG_PIECE_CHOICE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_CHOICE),
                            mg(IFG_PIECE_CHOICE_FILE_OR_RANK),
                            '',
                            mg(IFG_PIECE_CHOICE_SQUARE),
                            '')
            return
        if mg(IFG_CASTLES):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_castles(mg(IFG_CASTLES))
            return
        if mg(IFG_PAWN_PROMOTE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move('',
                            mg(IFG_PAWN_PROMOTE_FROM_FILE),
                            mg(IFG_PAWN_TAKES_PROMOTE),
                            mg(IFG_PAWN_PROMOTE_SQUARE),
                            mg(IFG_PAWN_PROMOTE_PIECE)[1])
            return
        if mg(IFG_COMMENT):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.collect_token(match)
            return
        if mg(IFG_NAG):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.collect_token(match)
            return
        if mg(IFG_COMMENT_TO_EOL):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.collect_token(match)
            return

        # The captured tokens not accepted when searching for start of game.
        if mg(IFG_START_RAV):
            self.error_tokens.append(mg())
            self._state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
            return
        if mg(IFG_END_RAV):
            self.error_tokens.append(mg())
            self._state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
            return
        if mg(IFG_TERMINATION):
            self._termination_while_searching(match)
            return

        # Action for non-captured groups is decided by looking at whole token.
        string = mg()

        if not string.strip():
            return
        if string.isdigit():
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if string == FULLSTOP:
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return

        # Only other groups with length > 1:
        # '<reserved>'
        # '%escaped\n'
        # are not captured and are ignored.
        if len(string) > 1:
            return
        
        self.error_tokens.append(string)
        self._state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
        return

    def _searching_after_error_in_rav(self, match):
        if match.group(IFG_START_RAV):
            self.error_tokens.append(match.group())
            self._ravstack_length += 1
            return
        if match.group(IFG_END_RAV):
            if self._ravstack_length == len(self.ravstack):
                self._convert_error_tokens_to_token()
                self.collect_token(match)
                self._end_variation()
                self.error_tokens = []
                self._state = PGN_COLLECTING_MOVETEXT
                self._rewind_state = self._state
                if self._ravstack_length > 2:
                    self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_RAV
                else:
                    self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                del self._ravstack_length
            else:
                self.error_tokens.append(match.group())
                self._ravstack_length -= 1
            return
        if match.group(IFG_TERMINATION):
            self._convert_error_tokens_to_token()
            self.collect_token(match)
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = []
            self._state = PGN_SEARCHING
            self._rewind_state = self._state
            del self._ravstack_length
            return
        if match.group(IFG_START_TAG):
            self._convert_error_tokens_to_token()
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = [match]
            if match.group(IFG_TAG_SYMBOL) == TAG_FEN:
                self.set_position_fen(match.group(IFG_TAG_STRING_VALUE))
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            del self._ravstack_length
            return
        self.error_tokens.append(match.group())

    def _searching_after_error_in_game(self, match):
        if match.group(IFG_TERMINATION):
            self._convert_error_tokens_to_token()
            self.collect_token(match)
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = []
            self._state = PGN_SEARCHING
            self._rewind_state = self._state
            return
        if match.group(IFG_START_TAG):
            self._convert_error_tokens_to_token()
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = [match]
            if match.group(IFG_TAG_SYMBOL) == TAG_FEN:
                self.set_position_fen(match.group(IFG_TAG_STRING_VALUE))
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        self.error_tokens.append(match.group())

    def _collecting_tag_pairs(self, match):
        mg = match.group
        if mg(IFG_START_TAG):
            self.tags_in_order.append(match)
            if mg(IFG_TAG_SYMBOL) == TAG_FEN:
                self.set_position_fen(mg(IFG_TAG_STRING_VALUE))
            return
        if mg(IFG_PIECE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_MOVE),
                            '',
                            '',
                            mg(IFG_PIECE_SQUARE),
                            '')
            return
        if mg(IFG_PAWN_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move('',
                            '',
                            '',
                            mg(IFG_PAWN_SQUARE),
                            '')
            return
        if mg(IFG_PIECE_CAPTURE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_CAPTURE) or mg(IFG_KING_CAPTURE),
                            mg(IFG_PIECE_CAPTURE_FROM),
                            mg(IFG_PIECE_TAKES),
                            mg(IFG_PIECE_CAPTURE_SQUARE),
                            '')
            return
        if mg(IFG_PAWN_CAPTURE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move('',
                            mg(IFG_PAWN_CAPTURE_FROM_FILE),
                            mg(IFG_PAWN_TAKES),
                            mg(IFG_PAWN_CAPTURE_SQUARE),
                            '')
            return
        if mg(IFG_PIECE_CHOICE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_CHOICE),
                            mg(IFG_PIECE_CHOICE_FILE_OR_RANK),
                            '',
                            mg(IFG_PIECE_CHOICE_SQUARE),
                            '')
            return
        if mg(IFG_CASTLES):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_castles(mg(IFG_CASTLES))
            return
        if mg(IFG_PAWN_PROMOTE_SQUARE):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_move('',
                            mg(IFG_PAWN_PROMOTE_FROM_FILE),
                            mg(IFG_PAWN_TAKES_PROMOTE),
                            mg(IFG_PAWN_PROMOTE_SQUARE),
                            mg(IFG_PAWN_PROMOTE_PIECE)[1])
            return
        if mg(IFG_TERMINATION):
            if not self._initial_fen:
                self.set_position_fen()
            self.collect_token(match)
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = []
            self._state = PGN_SEARCHING
            self._rewind_state = self._state
            return
        if mg(IFG_COMMENT):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.collect_token(match)
            return
        if mg(IFG_NAG):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.collect_token(match)
            return
        if mg(IFG_COMMENT_TO_EOL):
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.collect_token(match)
            return

        # The captured tokens not accepted when searching for tag pairs.
        if mg(IFG_START_RAV):
            self.error_tokens.append(mg())
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        if mg(IFG_END_RAV):
            self.error_tokens.append(mg())
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # Action for non-captured groups is decided by looking at whole token.
        string = mg()

        if not string.strip():
            return
        if string.isdigit():
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if string == FULLSTOP:
            if not self._initial_fen:
                self.set_position_fen()
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return

        # Only other groups with length > 1:
        # '<reserved>'
        # '%escaped\n'
        # are not captured and are ignored.
        if len(string) > 1:
            return
        
        self.error_tokens.append(string)
        self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
        return

    def _collecting_movetext(self, match):
        mg = match.group
        if mg(IFG_PIECE_SQUARE):
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_MOVE),
                            '',
                            '',
                            mg(IFG_PIECE_SQUARE),
                            '')
            return
        if mg(IFG_PAWN_SQUARE):
            self.tokens.append(match)
            self._play_move('',
                            '',
                            '',
                            mg(IFG_PAWN_SQUARE),
                            '')
            return
        if mg(IFG_PIECE_CAPTURE_SQUARE):
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_CAPTURE) or mg(IFG_KING_CAPTURE),
                            mg(IFG_PIECE_CAPTURE_FROM),
                            mg(IFG_PIECE_TAKES),
                            mg(IFG_PIECE_CAPTURE_SQUARE),
                            '')
            return
        if mg(IFG_PAWN_CAPTURE_SQUARE):
            self.tokens.append(match)
            self._play_move('',
                            mg(IFG_PAWN_CAPTURE_FROM_FILE),
                            mg(IFG_PAWN_TAKES),
                            mg(IFG_PAWN_CAPTURE_SQUARE),
                            '')
            return
        if mg(IFG_PIECE_CHOICE_SQUARE):
            self.tokens.append(match)
            self._play_move(mg(IFG_PIECE_CHOICE),
                            mg(IFG_PIECE_CHOICE_FILE_OR_RANK),
                            '',
                            mg(IFG_PIECE_CHOICE_SQUARE),
                            '')
            return
        if mg(IFG_CASTLES):
            self.tokens.append(match)
            self._play_castles(mg(IFG_CASTLES))
            return
        if mg(IFG_PAWN_PROMOTE_SQUARE):
            self.tokens.append(match)
            self._play_move('',
                            mg(IFG_PAWN_PROMOTE_FROM_FILE),
                            mg(IFG_PAWN_TAKES_PROMOTE),
                            mg(IFG_PAWN_PROMOTE_SQUARE),
                            mg(IFG_PAWN_PROMOTE_PIECE)[1])
            return
        if mg(IFG_START_RAV):
            self._start_variation()
            self.collect_token(match)
            return
        if mg(IFG_END_RAV):
            if len(self.ravstack) > 1:
                self._end_variation()
                self.collect_token(match)
            else:
                self.error_tokens.append(mg())
                self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        if mg(IFG_TERMINATION):
            self.collect_token(match)
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = []
            self._state = PGN_SEARCHING
            self._rewind_state = self._state
            return
        if mg(IFG_COMMENT):
            self.collect_token(match)
            return
        if mg(IFG_NAG):
            self.collect_token(match)
            return
        if mg(IFG_COMMENT_TO_EOL):
            self.collect_token(match)
            return

        # Other groups are not put on self.tokens because they are not shown in
        # game displays and do not need to the associated with a position on
        # the board.

        # The non-captured groups which are accepted without action.
        string = mg()

        if not string.strip():
            return
        if string.isdigit():
            return
        if string == FULLSTOP:
            return

        # Current movetext finishes in error, no termination, assume start of
        # new game.
        if mg(IFG_START_TAG):
            self._convert_error_tokens_to_token()
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = [match]
            if mg(IFG_TAG_SYMBOL) == TAG_FEN:
                self.set_position_fen(mg(IFG_TAG_STRING_VALUE))
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # Only other groups with length > 1:
        # '<reserved>'
        # '%escaped\n'
        # are not captured and are ignored.
        if len(string) > 1:
            return

        # The non-captured groups which cause an error condition.
        self.error_tokens.append(string)
        self._ravstack_length = len(self.ravstack)
        if self._ravstack_length > 1:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_RAV
        else:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME

    def _collecting_non_whitespace_while_searching(self, match):
        if match.group(IFG_START_TAG):
            self._convert_error_tokens_to_token()
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = [match]
            if match.group(IFG_TAG_SYMBOL) == TAG_FEN:
                self.set_position_fen(match.group(IFG_TAG_STRING_VALUE))
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        if not match.group().split():
            self.error_tokens.append(match.group())
            return
        self.error_tokens.append(match.group())

    def _disambiguate_move(self, match):
        mg = match.group
        if mg(IFG_PAWN_SQUARE):
            start = self.tokens.pop()
            match = re_disambiguate_error.match(start.group() + mg())
            if match is None:
                match = re_disambiguate_non_move.match(start.group() + mg())
                self.tokens.append(match)
                self._illegal_play_disambiguated_move()
                return
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            self.tokens.append(match)
            self._play_disambiguated_move(start.group(IFG_PIECE_MOVE),
                                          start.group(IFG_PIECE_SQUARE),
                                          mg(IFG_PAWN_SQUARE))
            return
        self.error_tokens.append(self.tokens.pop().group() + mg())
        self._ravstack_length = len(self.ravstack)
        if self._ravstack_length > 1:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_RAV
        else:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME

    def _illegal_play_move(self):
        self._state = self._move_error_state
        et = self.tokens.pop()
        self.error_tokens.append(et.group())

    def _illegal_play_castles(self):
        self._illegal_play_move()

    def _illegal_play_disambiguated_move(self):
        self._illegal_play_move()

    def _convert_error_tokens_to_token(self):
        """Generate error token '{Error: <original tokens> }'.

        Any '}' in <original tokens> replaced by '::{{::'.  Assume '::{{::' and
        '{Error: ' do not occur naturally in '{}' comments.
        """
        self.collect_token(re_tokens.match(
            ''.join((ERROR_START_COMMENT,
                     ''.join(self.error_tokens).replace(
                         END_COMMENT, ESCAPE_END_COMMENT),
                     END_COMMENT))))
        # Should this method clear self.error_tokens too?

    def _termination_while_searching(self, match):
        self.error_tokens.append(match.group())
        self._state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING

    def __eq__(self, other):
        """Return (self == other).  Relevant attributes compared explicitly."""
        if len(self.collected_game[2]) != len(other.collected_game[2]):
            return False
        if self.collected_game[3] or other.collected_game[3]:
            return False
        for ta, tb in zip(self.collected_game[2], other.collected_game[2]):
            if ta.group() != tb.group():
                return False
        return True

    def __ne__(self, other):
        """Return (not self == other)."""
        return not self == other


class PGNDisplayMoves(PGN):
    """Base class for generating data structures to display a game.
    
    """

    def __init__(self):
        super().__init__()
        
        '''Add structures to support display of PGN moves'''

        # moves describes the contents of tokens (see superclass).
        # Each element in moves is (<type>, <token index>, <data>).
        # A move is (True, <token index>, <position after move>) so the
        # very first move is (True, None, <start position>) following the
        # convention in ravstack.  The initial position of a variation is
        # ('(', <token index for '('>, <variation start position>) and the
        # end is (')', <token index for ')'>, None).
        self.moves = []

    def set_position_fen(self, fen=None):
        """Initialize PGN score parser with Forsyth Edwards Notation position.

        fen defaults to the starting position for a game of chess.

        """
        super().set_position_fen(fen=fen)
        if self._initial_fen:
            self.moves = [(None, self.ravstack[-1][-1])]

    def add_move_to_game(self):
        """Add legal move to data structures describing game.

        """
        #super().add_move_to_game()
        self.active_side = OTHER_SIDE[self.active_side]
        self.ravstack[-1] = (
            self.ravstack[-1][-1],
            (tuple(self.board),
             self.active_side,
             self.castling,
             self.en_passant))

        self.moves.append((self.tokens[-1], self.ravstack[-1][-1]))

    def collect_token(self, match):
        """"""
        #super().collect_token(match)
        self.tokens.append(match)

        self.moves.append((self.tokens[-1], self.ravstack[-1][-1]))

    def collect_game_tokens(self):
        """Create snapshot of tokens extracted from PGN.

        This method is expected to be called on detection of termination token.

        """
        self.collected_game = (
            self.tags_in_order,
            {m.group(IFG_TAG_SYMBOL):m.group(IFG_TAG_STRING_VALUE)
             for m in self.tags_in_order},
            self.tokens,
            self.error_tokens,
            self.moves)


class PGNDisplay(PGNDisplayMoves):
    """Generate data structures to display a game without ability to edit.
    
    """

    def _add_token_to_text(self, token, movetext, length):
        """"""
        if not length:
            movetext.append(token)
            return len(token)
        elif len(token) + length >= PGN_MAX_LINE_LEN:
            movetext.append(LINEFEED)
            movetext.append(token)
            return len(token)
        else:
            movetext.append(SPACE)
            movetext.append(token)
            return len(token) + length + 1

    def get_export_pgn_movetext(self):
        """Return Export format PGN movetext"""
        ordered_tags, tags, tokens, error_tokens, moves = self.collected_game
        active_side = moves[0][1][1]
        fullmove_number = self.fullmove_number
        movetext = ['\n']
        length = 0
        blackmove_number = True
        mns = [[fullmove_number, active_side]]
        for e, t in enumerate(tokens):
            if t.group(IFG_COMMENT):
                for cw in t.group().split():
                    length = self._add_token_to_text(cw, movetext, length)
                blackmove_number = True
            elif t.group(IFG_NAG):
                length = self._add_token_to_text(t.group(), movetext, length)
                blackmove_number = True
            elif t.group(IFG_COMMENT_TO_EOL):
                if len(t.group()) + length >= PGN_MAX_LINE_LEN:
                    movetext.append(LINEFEED)
                else:
                    movetext.append(SPACE)
                movetext.append(t.group())
                length = 0
                blackmove_number = True
            elif t.group(IFG_START_RAV):
                length = self._add_token_to_text(t.group(), movetext, length)
                mns[-1] = [fullmove_number, active_side]
                active_side = OTHER_SIDE[active_side]
                mns.append([fullmove_number, active_side])
                blackmove_number = True
            elif t.group(IFG_END_RAV):
                length = self._add_token_to_text(t.group(), movetext, length)
                del mns[-1]
                fullmove_number, active_side = mns[-1]
                blackmove_number = True
            elif t.group(IFG_TERMINATION):
                length = self._add_token_to_text(t.group(), movetext, length)
            elif active_side == WHITE_SIDE:
                length = self._add_token_to_text(
                    str(fullmove_number) + FULLSTOP,
                    movetext,
                    length)
                length = self._add_token_to_text(t.group(), movetext, length)
                active_side = OTHER_SIDE[active_side]
                blackmove_number = False
            else:
                if blackmove_number:
                    length = self._add_token_to_text(
                        str(fullmove_number) + FULLSTOP * 3,
                        movetext,
                        length)
                    blackmove_number = False
                length = self._add_token_to_text(t.group(), movetext, length)
                active_side = OTHER_SIDE[active_side]
                fullmove_number += 1
        movetext.append('\n\n')
        return ''.join(movetext)

    def get_archive_movetext(self):
        """Return Reduced Export format PGN movetext"""
        ordered_tags, tags, tokens, error_tokens, moves = self.collected_game
        active_side = moves[0][1][1]
        fullmove_number = self.fullmove_number
        movetext = ['\n']
        length = 0
        blackmove_number = True
        rav_depth = 0
        mns = [[fullmove_number, active_side]]
        for e, t in enumerate(tokens):
            if (t.group(IFG_COMMENT) or
                t.group(IFG_NAG) or
                t.group(IFG_COMMENT_TO_EOL)):
                pass
            elif t.group(IFG_START_RAV):
                rav_depth += 1
            elif t.group(IFG_END_RAV):
                rav_depth -= 1
            elif t.group(IFG_TERMINATION):
                length = self._add_token_to_text(t.group(), movetext, length)
            elif rav_depth:
                pass
            elif active_side == WHITE_SIDE:
                length = self._add_token_to_text(
                    str(fullmove_number) + FULLSTOP,
                    movetext,
                    length)
                length = self._add_token_to_text(t.group(), movetext, length)
                active_side = OTHER_SIDE[active_side]
                blackmove_number = False
            else:
                if blackmove_number:
                    length = self._add_token_to_text(
                        str(fullmove_number) + FULLSTOP * 3,
                        movetext,
                        length)
                    blackmove_number = False
                length = self._add_token_to_text(t.group(), movetext, length)
                active_side = OTHER_SIDE[active_side]
                fullmove_number += 1
        movetext.append('\n\n')
        return ''.join(movetext)

    def get_export_pgn_rav_movetext(self):
        """Return Export format PGN moves and RAVs"""
        ordered_tags, tags, tokens, error_tokens, moves = self.collected_game
        active_side = moves[0][1][1]
        fullmove_number = self.fullmove_number
        movetext = ['\n']
        length = 0
        blackmove_number = True
        mns = [[fullmove_number, active_side]]
        for e, t in enumerate(tokens):
            if (t.group(IFG_COMMENT) or
                t.group(IFG_NAG) or
                t.group(IFG_COMMENT_TO_EOL)):
                pass
            elif t.group(IFG_START_RAV):
                length = self._add_token_to_text(t.group(), movetext, length)
                mns[-1] = [fullmove_number, active_side]
                active_side = OTHER_SIDE[active_side]
                mns.append([fullmove_number, active_side])
                blackmove_number = True
            elif t.group(IFG_END_RAV):
                length = self._add_token_to_text(t.group(), movetext, length)
                del mns[-1]
                fullmove_number, active_side = mns[-1]
                blackmove_number = True
            elif t.group(IFG_TERMINATION):
                length = self._add_token_to_text(t.group(), movetext, length)
            elif active_side == WHITE_SIDE:
                length = self._add_token_to_text(
                    str(fullmove_number) + FULLSTOP,
                    movetext,
                    length)
                length = self._add_token_to_text(t.group(), movetext, length)
                active_side = OTHER_SIDE[active_side]
                blackmove_number = False
            else:
                if blackmove_number:
                    length = self._add_token_to_text(
                        str(fullmove_number) + FULLSTOP * 3,
                        movetext,
                        length)
                    blackmove_number = False
                length = self._add_token_to_text(t.group(), movetext, length)
                active_side = OTHER_SIDE[active_side]
                fullmove_number += 1
        movetext.append('\n\n')
        return ''.join(movetext)

    def get_non_seven_tag_roster_tags(self):
        """Return string of sorted tags not in Seven Tag Roster"""
        return '\n'.join(sorted(
            [t.group()
             for t in self.collected_game[0]
             if t.group(IFG_TAG_SYMBOL) not in SEVEN_TAG_ROSTER]))

    def get_seven_tag_roster_tags(self):
        """Return tuple of Seven Tag Roster tags decorated for sorting games.

        The tuple is:
        (Date tag with '?'s replaced by '0',
         Event, Site, and Date, tags,
         Round tag with '?', '-', and any other, replaced by 1, 2, and 3,
         Round, White, Black, and Result, tags,
        )

        """
        tags = self.collected_game[1]
        return [
            tags.get(TAG_DATE, SEVEN_TAG_ROSTER[TAG_DATE]
                     ).replace(*SPECIAL_TAG_DATE).join(('"', '"')),
            ''.join([''.join(['[',
                              t,
                              ' "',
                              tags.get(t, SEVEN_TAG_ROSTER[t]),
                              '"]\n'])
                     for t in SEVEN_TAG_ROSTER_ARCHIVE_SORT1]),
            SPECIAL_TAG_ROUND.get(tags.get(TAG_ROUND,
                                           SEVEN_TAG_ROSTER[TAG_ROUND]),
                                  NORMAL_TAG_ROUND),
            ''.join([''.join(['[',
                              t,
                              ' "',
                              tags.get(t, SEVEN_TAG_ROSTER[t]),
                              '"]\n'])
                     for t in SEVEN_TAG_ROSTER_ARCHIVE_SORT2]),
            ]

    def get_export_pgn_elements(self):
        """Return Export format PGN text"""
        return (
            self.get_seven_tag_roster_tags(),
            self.get_export_pgn_movetext(),
            self.get_non_seven_tag_roster_tags())

    def get_archive_pgn_elements(self):
        """Return Reduced Export format PGN text"""
        return (self.get_seven_tag_roster_tags(), self.get_archive_movetext())

    def get_export_pgn_rav_elements(self):
        """Return Export format PGN text"""
        return (
            self.get_seven_tag_roster_tags(),
            self.get_export_pgn_rav_movetext(),
            self.get_non_seven_tag_roster_tags())


class PGNEdit(PGNDisplay):
    """Generate data structures to display a game for editing.
    
    """

    def _convert_error_tokens_to_token(self):
        """Override to spot possible moves in error tokens.

        Usually all the PGN text is present before parsing.  But when editing
        the text incomplete moves will be present and the 'R1' part of 'R1a4',
        for example, gets treated as two tokens, 'R' and '1' by the re_tokens
        regular expression when the rest of the move has not yet been typed.

        """
        possible_move = ''.join(self.error_tokens)
        fullmatch = re_possible_move.match(possible_move)
        if fullmatch:
            self.collect_token(fullmatch)
            self.error_tokens.clear()
        else:
            self.collect_token(re_tokens.match(
                ''.join(('{Error: ', possible_move, '}'))))
        # Should this method clear self.error_tokens too?


class PGNMove(PGN):
    """Generate data structures to check legality of a move being edited.
    
    """
    # Should _convert_error_tokens_to_token() be overridden here?

    def __init__(self):
        """Extend to support restoration of initial position state"""
        super().__init__()
        self._initial_position = None

    def is_movetext_valid(self):
        """Override to return True if exactly one valid move in movetext."""
        if self.collected_game is None:
            return bool(len(self.tokens) == 1)
        return bool(len(self.collected_game[2]) == 1)

    def set_position_fen(self, fen=None):
        """Extend to remember full state for initial position in fen"""
        super().set_position_fen(fen=fen)
        if self._initial_fen:
            self._initial_position = self.ravstack[0][-1]


class PGNRepertoireDisplay(PGNDisplay):
    """Generate data to display repertoire game without ability to edit.

    The Opening tag is mandatory and is intended for naming the repertoire.
    
    """
    
    def is_tag_roster_valid(self):
        """Return True if the tag roster in the collected game is valid."""
        tags_in_order = self.collected_game[0]
        tags = self.collected_game[1]
        if len(tags) != len(tags_in_order):
            # Tag must appear no more than once
            return False
        for v in tags.values():
            if len(v) == 0:
                # Tag value must not be null
                return False
        if TAG_OPENING not in tags:
            # A mandatory tag is missing
            return False
        return True

    def get_export_repertoire_text(self):
        """Return Export format PGN text for repertoire"""
        tags = self.collected_game[1]
        pb = []
        for t in REPERTOIRE_TAG_ORDER:
            pb.extend(
                ['[', t, ' "',
                 tags.get(t, REPERTOIRE_GAME_TAGS[t]),
                 '"]\n'])
        for t, v in sorted([tv for tv in tags.items()
                            if tv[0] not in REPERTOIRE_GAME_TAGS]):
            pb.extend(['[', t, ' "', v, '"]\n'])
        pb.append(self.get_export_pgn_movetext())
        return ''.join(pb)

    def get_export_repertoire_rav_text(self):
        """Return Export format PGN text for repertoire RAV"""
        tags = self.collected_game[1]
        pb = []
        for t in REPERTOIRE_TAG_ORDER:
            pb.extend(
                ['[', t, ' "',
                 tags.get(t, REPERTOIRE_GAME_TAGS[t]),
                 '"]\n'])
        for t, v in sorted([tv for tv in tags.items()
                            if tv[0] not in REPERTOIRE_GAME_TAGS]):
            pb.extend(['[', t, ' "', v, '"]\n'])
        pb.append(self.get_export_pgn_rav_movetext())
        return ''.join(pb)


class PGNRepertoireUpdate(PGN):
    """Generate data structures to update a repertoire game on a database.

    The Opening tag is mandatory and is intended for naming the repertoire.

    """
    
    def is_tag_roster_valid(self):
        tags_in_order = self.collected_game[0]
        tags = self.collected_game[1]
        if len(tags) != len(tags_in_order):
            # Tag must appear no more than once
            return False
        for v in tags.values():
            if len(v) == 0:
                # Tag value must not be null
                return False
        if TAG_OPENING not in tags:
            # A mandatory tag is missing
            return False
        return True


class PGNTags(PGN):
    """Generate data structures to display the PGN Tags of a game.

    Comments on two methods are worth making:

    _disambiguate_move is defined but the only way it should be reached has
    been disabled by overriding _collecting_movetext.  The definition ensures
    PGN._disambiguate_move is never called.

    PGN._collecting_non_whitespace_while_searching is correct in this class too.
    
    """

    def _searching(self, match):
        if match.group(IFG_START_TAG):
            self.tags_in_order.append(match)
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        mg = match.group
        if mg(IFG_PIECE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PAWN_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PIECE_CAPTURE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PAWN_CAPTURE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PIECE_CHOICE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_CASTLES):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PAWN_PROMOTE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_COMMENT):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_NAG):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_COMMENT_TO_EOL):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return

        # The captured tokens not accepted when searching for start of game.
        if mg(IFG_START_RAV):
            self.error_tokens.append(mg())
            self._state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
            return
        if mg(IFG_END_RAV):
            self.error_tokens.append(mg())
            self._state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
            return
        if mg(IFG_TERMINATION):
            self._termination_while_searching(match)
            return

        # Action for non-captured groups is decided by looking at whole token.
        string = mg()

        if not string.strip():
            return
        if string.isdigit():
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if string == FULLSTOP:
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return

        # Only other groups with length > 1:
        # '<reserved>'
        # '%escaped\n'
        # are not captured and are ignored.
        if len(string) > 1:
            return
        
        self.error_tokens.append(string)
        self._state = PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
        return

    def _searching_after_error_in_rav(self, match):
        if match.group(IFG_START_RAV):
            self._ravstack_length += 1
            return
        if match.group(IFG_END_RAV):
            if self._ravstack_length == len(self.ravstack):
                self.error_tokens = []
                self._state = PGN_COLLECTING_MOVETEXT
                self._rewind_state = self._state
                if self._ravstack_length > 2:
                    self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_RAV
                else:
                    self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
                del self._ravstack_length
            else:
                self._ravstack_length -= 1
            return
        if match.group(IFG_TERMINATION):
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = []
            self._state = PGN_SEARCHING
            self._rewind_state = self._state
            del self._ravstack_length
            return
        if match.group(IFG_START_TAG):
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = [match]
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            del self._ravstack_length
            return

    def _searching_after_error_in_game(self, match):
        if match.group(IFG_TERMINATION):
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = []
            self._state = PGN_SEARCHING
            self._rewind_state = self._state
            return
        if match.group(IFG_START_TAG):
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = [match]
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

    def _collecting_tag_pairs(self, match):
        if match.group(IFG_START_TAG):
            self.tags_in_order.append(match)
            return
        mg = match.group
        if mg(IFG_PIECE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PAWN_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PIECE_CAPTURE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PAWN_CAPTURE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PIECE_CHOICE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_CASTLES):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_PAWN_PROMOTE_SQUARE):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_TERMINATION):
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = []
            self._state = PGN_SEARCHING
            self._rewind_state = self._state
            return
        if mg(IFG_COMMENT):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_NAG):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if mg(IFG_COMMENT_TO_EOL):
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return

        # The captured tokens not accepted when searching for tag pairs.
        if mg(IFG_START_RAV):
            self.error_tokens.append(mg())
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return
        if mg(IFG_END_RAV):
            self.error_tokens.append(mg())
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # Action for non-captured groups is decided by looking at whole token.
        string = mg()

        if not string.strip():
            return
        if string.isdigit():
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        if string == FULLSTOP:
            self.ravstack[:] = [None]
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return

        # Only other groups with length > 1:
        # '<reserved>'
        # '%escaped\n'
        # are not captured and are ignored.
        if len(string) > 1:
            return
        
        self.error_tokens.append(string)
        self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
        return

    def _collecting_movetext(self, match):
        mg = match.group
        if mg(IFG_PIECE_SQUARE):
            return
        if mg(IFG_PAWN_SQUARE):
            return
        if mg(IFG_PIECE_CAPTURE_SQUARE):
            return
        if mg(IFG_PAWN_CAPTURE_SQUARE):
            return
        if mg(IFG_PIECE_CHOICE_SQUARE):
            return
        if mg(IFG_CASTLES):
            return
        if mg(IFG_PAWN_PROMOTE_SQUARE):
            return
        if mg(IFG_START_RAV):
            self._start_variation()
            return
        if mg(IFG_END_RAV):
            self._end_variation()
            return
        if mg(IFG_TERMINATION):
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = []
            self._state = PGN_SEARCHING
            self._rewind_state = self._state
            return
        if mg(IFG_COMMENT):
            return
        if mg(IFG_NAG):
            return
        if mg(IFG_COMMENT_TO_EOL):
            return

        # Other groups are not put on self.tokens because they are not shown in
        # game displays and do not need to be associated with a position on
        # the board.

        # The non-captured groups which are accepted without action.
        string = mg()

        if not string.strip():
            return
        if string.isdigit():
            return
        if string == FULLSTOP:
            return

        # Current movetext finishes in error, no termination, assume start of
        # new game.
        if mg(IFG_START_TAG):
            self.collect_game_tokens()
            self._initial_fen = False
            self.tokens = []
            self.error_tokens = []
            self.tags_in_order = [match]
            self._state = PGN_COLLECTING_TAG_PAIRS
            self._rewind_state = self._state
            self._move_error_state = PGN_SEARCHING_AFTER_ERROR_IN_GAME
            return

        # Only other groups with length > 1:
        # '<reserved>'
        # '%escaped\n'
        # are not captured and are ignored.
        if len(string) > 1:
            return

        # The non-captured groups which cause an error condition.
        self._ravstack_length = len(self.ravstack)
        if self._ravstack_length > 1:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_RAV
        else:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME

    def _disambiguate_move(self, match):
        if match.group(IFG_PAWN_SQUARE):
            self._state = PGN_COLLECTING_MOVETEXT
            self._rewind_state = self._state
            return
        self._ravstack_length = len(self.ravstack)
        if self._ravstack_length > 1:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_RAV
        else:
            self._state = PGN_SEARCHING_AFTER_ERROR_IN_GAME

    def _start_variation(self):
        self.ravstack.append(None)

    def _end_variation(self):
        try:
            del self.ravstack[-1]
        except:
            pass


class PGNRepertoireTags(PGNTags):
    """Generate data structures to display the PGN Tags of a repertoire.

    The notion of mandatory PGN tags, like the 'seven tag roster', is removed
    from the PGNTags class.

    """
    
    def is_tag_roster_valid(self):
        """Return True if the tag roster in the collected game is valid."""
        tags_in_order = self.collected_game[0]
        tags = self.collected_game[1]
        if len(tags) != len(tags_in_order):
            # Tag must appear no more than once
            return False
        for v in tags.values():
            if len(v) == 0:
                # Tag value must not be null
                return False
        if TAG_OPENING not in tags:
            # A mandatory tag is missing
            return False
        return True


class PGNAnalysis(PGNDisplay):
    """Generate data to display Chess Engine analysis without ability to edit.

    The notion of mandatory PGN tags, like the 'seven tag roster', is removed
    from the PGNDisplay class.

    Subclasses may use the PGN tag structure to manage analysis, but exactly
    what tags are defined is up to them.

    A single main move is required; to which chess engine analysis is attached
    as a sequence of RAVs, each RAV corresponding to one PV in a PV or multiPV
    response from a chess engine.
    
    """
    
    def is_tag_roster_valid(self):
        """Return True if the tag roster in the collected game is valid."""
        tags_in_order = self.collected_game[0]
        tags = self.collected_game[1]
        if len(tags) != len(tags_in_order):
            # Tag must appear no more than once
            return False
        for v in tags.values():
            if len(v) == 0:
                # Tag value must not be null
                return False
        return True

    def _termination_while_searching(self, match):
        if not self._initial_fen:
            self.set_position_fen()
        self.collect_token(match)
        self.collect_game_tokens()
        self._initial_fen = False
        self.tokens = []
        self.error_tokens = []
        self.tags_in_order = []
        self._state = PGN_SEARCHING
        self._rewind_state = self._state


def get_fen_string(description, halfmoves=0, fullmoves=1):
    """Return Forsythe Edwards Notation string for position description.

    The FEN string can be given as a PGN Tag in a PGN game score.  It can also
    be used to set a PGN instance to a given position.
    
    """
    board, side_to_move, castle_options, ep_square = description
    fenboard = []
    fenrank = []
    gap_length = 0
    for e, r in enumerate(board):
        if not e % BOARDSIDE:
            if gap_length:
                fenrank.append(str(gap_length))
                gap_length = 0
            if len(fenrank):
                fenboard.append(''.join(fenrank))
                fenrank = []
        if r == NOPIECE:
            gap_length += 1
            continue
        if gap_length:
            fenrank.append(str(gap_length))
            gap_length = 0
        fenrank.append(r)
    if gap_length:
        fenrank.append(str(gap_length))
    fenboard.append(''.join(fenrank))
    return ' '.join(('/'.join(fenboard),
                     FEN_TOMOVE[side_to_move],
                     castle_options,
                     ep_square,
                     str(halfmoves),
                     str(fullmoves)))
