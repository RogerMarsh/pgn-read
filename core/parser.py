# parser.py
# Copyright 2003, 2010 Roger Marsh
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

List of classes

PGN
PGNDisplayMoves
PGNDisplay
PGNEdit
PGNMove
PGNUpdate
PGNTags

List of functions

get_board_from_position
get_fen_from_position
get_position_string

"""

# Original pgn.py works but I dare not try changing it in any significant way,
# such as improving the score editor to detect and note valid PGN syntax even
# if moves do not make sense after an error is detected.
#
# For example an error in a variation does not mean the PGN after end of line
# is wrong.  In fact an error implies the PGN leading to the error represents
# a playable sequence of moves.  pgn.py handles variations nested indefinitely
# but does not track errors at the line level.
#

import re

from .constants import (
    NO_EP_SQUARE,
    CASTLEALL,
    WHITE_TO_MOVE,
    BLACK_TO_MOVE,
    INITIAL_WP_SQUARES,
    INITIAL_BP_SQUARES,
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
    WPIECES,
    FEN_FIELD_DELIM,
    FEN_WHITE,
    FEN_BLACK,
    FEN_NO_DATA,
    FEN_RANK_DELIM,
    FEN_WPAWN,
    FEN_BPAWN,
    FEN_WKING,
    FEN_BKING,
    FEN_ADJACENT_EMPTY_SQUARES,
    MAPFILE,
    MAPRANK,
    FEN_PIECEMAP,
    FEN_EP_SQUARES,
    CASTLEKEY,
    CASTLEMOVES,
    CASTLESET,
    OTHERSIDE_PAWN,
    OTHER_SIDE,
    SIDE_KING,
    SCH,
    SPLIT_INTO_TOKENS,
    SPLIT_INTO_TOKENS_EDIT,
    SPLIT_INTO_TAGS,
    MOVETEXT,
    MOVE_DETAIL,
    END_COMMENT,
    LINEFEED,
    CARRIAGE_RETURN,
    START_COMMENT,
    END_RESERVED,
    START_RESERVED,
    ESCAPE_TO_EOL,
    RESULT,
    PGN_ERROR,
    COMMENT_TO_EOL,
    PERIOD,
    START_TAG,
    END_TAG,
    START_RAV,
    END_RAV,
    SPACE,
    HORIZONTAL_TAB,
    FORMFEED,
    VERTICAL_TAB,
    NEWLINE,
    TAG_FEN,
    INITIAL_BOARD,
    RESULT_SET,
    MOVE_OR_CAPTURE_GROUP,
    PLAIN_MOVE,
    PROMOTE_GROUP,
    MAPPIECE,
    PIECE_MOVE_MAP,
    PATH,
    NOPIECE,
    CASTLEMASKS,
    PGN_PAWN,
    ALLOW_EP_MOVES,
    PIECES_ATTACK,
    GAPS,
    CAPTURE_MOVE,
    PIECE_CAPTURE_MAP,
    O_O_O,
    O_O,
    WK_CASTLES,
    BPIECES,
    FILES,
    SEVEN_TAG_ROSTER,
    RANKS,
    HIDDEN,
    BK_CASTLES,
    WQ_CASTLES,
    MAPROW,
    BQ_CASTLES,
    EP_MOVES,
    PIECE_GROUP,
    CAPTURE_MOVE,
    PGN_FROM_SQUARE_DISAMBIGUATION,
    DISAMBIGUATE,
    MOVE_NUMBER_KEYS,
    NON_MOVE,
    MOVE_ERROR,
    MOVE_AFTER_ERROR,
    TERMINATION,
    MOVE_TEXT,
    GLYPH,
    SPLIT_INTO_GAMES,
    POSITION_KEY_TO_PIECES,
    POSITION_KEY_TO_FLAGS,
    TOMOVE_TO_POSITION_KEY,
    INITIAL_SQUARES,
    PCH,
    FULLBOARD,
    DECODE,
    SPECIAL_VALUES_OFFSET,
    SPECIAL_VALUES_TOMOVE,
    SPECIAL_VALUES_CASTLE,
    SPECIAL_VALUES_ENPASSANT,
    TAG_RESULT,
    INTEGER,
    PIECE_FENMAP,
    SIDE_TO_MOVE_FENMAP,
    CASTLING_OPTION_FENMAP,
    EN_PASSANT_FENMAP,
    )

re_tokens = re.compile(SPLIT_INTO_TOKENS)
re_tokens_edit = re.compile(SPLIT_INTO_TOKENS_EDIT)
re_tags = re.compile(SPLIT_INTO_TAGS)
re_detail = re.compile(MOVE_DETAIL)
re_disambiguate = re.compile(DISAMBIGUATE)
re_games = re.compile(SPLIT_INTO_GAMES)


class PGN(object):
    """Extract moves, comments, PGN tags from score and check moves are legal.

    None of the data structures specific to displaying a game or updating a
    database are generated.  use the appropriate subclass to do these things.

    Methods added:

    extract_first_game
    get_attacks_on_square
    get_tag_result
    is_movetext_valid
    is_pgn_valid
    is_tag_roster_valid
    process_game
    reset_position
    set_position_fen
    _add_move_to_game
    _comment_to_eol
    _comment_to_eol_after_nl_between_moves
    _disambiguate_move
    _end_comment
    _end_reserved
    _end_variation
    _end_variation_containing_error
    _escape_to_eol
    _escape_to_eol_after_nl_between_moves
    _is_attacked
    _is_king_in_check_after_move
    _make_castles_move
    _make_capture
    _make_move
    _make_pawn_capture
    _make_pawn_capture_promotion
    _make_pawn_move
    _make_pawn_promotion
    _move_error
    _movetext_error
    _newline
    _newline_between_moves
    _newline_in_comment_to_eol
    _newline_in_escape_to_eol
    _newline_repeat
    _newline_repeat_between_moves
    _process_movetext
    _process_token
    _prune_pieces_pinned_to_king
    _revert_state_and_reprocess_token
    _set_game_data
    _start_comment
    _start_reserved
    _start_variation
    _start_variation_in_error_sequence
    _token_comment
    _token_comment_after_newline
    _token_digit
    _token_end_comment
    _token_end_reserved
    _token_end_variation
    _token_glyph
    _token_move
    _token_move_detail_error
    _token_move_disambiguate
    _token_move_error
    _token_move_error_disambiguate
    _token_move_in_error_sequence
    _token_movetext_error
    _token_newline
    _token_newline_keep
    _token_period
    _token_previous_move_error
    _token_result
    _token_start_comment
    _token_start_reserved
    _token_start_variation
    _token_whitespace

    Methods overridden:

    None
    
    Methods extended:

    __init__
    
    """

    def __init__(self):
        super(PGN, self).__init__()
        
        # data generated from PGN text for game before checking moves are legal
        self.tokens = []
        self.tags = {}
        self.tags_in_order = []
        self._tag_string = ''
        self._move_string = ''
        
        # data generated from PGN text for game after checking moves are legal
        self.gametokens = []
        self.occupied_square_pieces = []
        self.board_pieces = []
        self.piece_locations = []
        # ravstack keeps track of the position at start of game or variation
        # and the position after application of a valid move.  Thus the value
        # in ravstack[-1] is (None, <position start>) at start of game or line
        # and (<position start>, <position after move>) after application of a
        # valid move from gametokens.
        self.ravstack = []
        self.move_number = None # set but not used in original pgn.py
        self.since_capture = None
        self.ep_move_to_sq = None
        self.castle_options = None
        self.side_to_move = None
        
        # data used while parsing PGN text to split into tag and move tokens
        self._movetext_valid = None
        self._token = ''
        self._tags_valid = None
        self._state = None
        self._state_stack = []
        
        self._despatch_table = {
            START_COMMENT: { # comment tokens until END_COMMENT
                END_COMMENT: self._end_comment,
                LINEFEED: self._newline,
                None: self._token_comment,
                },
            START_RESERVED: { # treat as comment tokens until END_RESERVED
                END_RESERVED: self._end_reserved,
                LINEFEED: self._newline,
                None: self._token_comment,
                },
            ESCAPE_TO_EOL: { # treat as comment tokens until newline
                LINEFEED: self._newline_in_escape_to_eol,
                None: self._token_comment,
                },
            RESULT: { # non-whitespace token after result treated as comment
                LINEFEED: self._token_whitespace,
                CARRIAGE_RETURN: self._token_whitespace,
                SPACE: self._token_whitespace,
                HORIZONTAL_TAB: self._token_whitespace,
                FORMFEED: self._token_whitespace,
                VERTICAL_TAB: self._token_whitespace,
                None: self._token_comment,
                },
            PGN_ERROR: { # An error deemed unrecoverable detected
                None: self._token_movetext_error,
                },
            COMMENT_TO_EOL: { # tokens until newline are comments
                LINEFEED: self._newline_in_comment_to_eol,
                None: self._token_comment,
                },
            MOVETEXT: { # main line or variation contains move(s)
                PERIOD: self._token_period,
                START_COMMENT: self._start_comment,
                END_COMMENT: self._movetext_error,
                START_TAG: self._movetext_error, # should be unrecoverable?
                END_TAG: self._movetext_error, # should be unrecoverable?
                START_RAV: self._start_variation,
                END_RAV: self._end_variation,
                START_RESERVED: self._start_reserved,
                END_RESERVED: self._movetext_error,
                LINEFEED: self._newline_between_moves,
                CARRIAGE_RETURN: self._token_whitespace,
                SPACE: self._token_whitespace,
                HORIZONTAL_TAB: self._token_whitespace,
                FORMFEED: self._token_whitespace,
                VERTICAL_TAB: self._token_whitespace,
                COMMENT_TO_EOL: self._comment_to_eol,
                None: self._process_token,
                },
            False: { # move tokens treated as comment till matching END_RAV
                PERIOD: self._token_comment,
                START_COMMENT: self._start_comment, # ..._in_error_sequence
                END_COMMENT: self._token_comment, # should be an error?
                START_TAG: self._token_comment, # should be unrecoverable?
                END_TAG: self._token_comment, # should be unrecoverable?
                START_RAV: self._start_variation_in_error_sequence,
                END_RAV: self._end_variation_containing_error,
                START_RESERVED: self._start_reserved, # ..._in_error_sequence
                END_RESERVED: self._token_comment, # should be an error?
                LINEFEED: self._newline_between_moves, # ..._in_error_sequence
                CARRIAGE_RETURN: self._token_comment,
                SPACE: self._token_comment,
                HORIZONTAL_TAB: self._token_comment,
                FORMFEED: self._token_comment,
                VERTICAL_TAB: self._token_comment,
                COMMENT_TO_EOL: self._comment_to_eol, # ..._in_error_sequence
                None: self._token_move_in_error_sequence,
                },
            None: { # at start of main line or variation
                PERIOD: self._token_period,
                START_COMMENT: self._start_comment,
                END_COMMENT: self._movetext_error,
                START_TAG: self._movetext_error, # should be unrecoverable?
                END_TAG: self._movetext_error, # should be unrecoverable?
                START_RAV: self._movetext_error,
                END_RAV: self._movetext_error,
                START_RESERVED: self._start_reserved,
                END_RESERVED: self._movetext_error,
                LINEFEED: self._newline_between_moves,
                CARRIAGE_RETURN: self._token_whitespace,
                SPACE: self._token_whitespace,
                HORIZONTAL_TAB: self._token_whitespace,
                FORMFEED: self._token_whitespace,
                VERTICAL_TAB: self._token_whitespace,
                COMMENT_TO_EOL: self._comment_to_eol,
                None: self._process_token,
                },
            LINEFEED: { # newlines between moves allow escape or comment to eol
                ESCAPE_TO_EOL: self._escape_to_eol_after_nl_between_moves,
                LINEFEED: self._newline_repeat_between_moves,
                COMMENT_TO_EOL: self._comment_to_eol_after_nl_between_moves,
                None: self._revert_state_and_reprocess_token,
                },
            NEWLINE: { # newlines in {comment} allow escape to eol
                ESCAPE_TO_EOL: self._escape_to_eol,
                LINEFEED: self._newline_repeat,
                None: self._revert_state_and_reprocess_token,
                },
            PGN_FROM_SQUARE_DISAMBIGUATION: { # token must be piece tosquare
                None: self._disambiguate_move,
                },
            }
        
        self._unmatched_text_valid_table = {
            START_COMMENT: self._token_comment,
            START_RESERVED: self._token_comment,
            ESCAPE_TO_EOL: self._token_comment,
            RESULT: self._token_comment,
            COMMENT_TO_EOL: self._token_comment,
            MOVETEXT: self._move_error,
            None: self._move_error,
            False: self._token_comment,
            LINEFEED: self._move_error,
            NEWLINE: self._token_comment,
            PGN_ERROR: self._token_comment,
            PGN_FROM_SQUARE_DISAMBIGUATION: self._token_previous_move_error,
            }

    def extract_first_game(self, pgntext):
        '''Return tuple(PGN tags, PGN movetext) for first game in pgntext.'''
        games = re_games.split(pgntext)
        if len(games[0]):
            self._tag_string = ''
            self._move_string = games[0]
            return
        self._tag_string = games[1]
        self._move_string = games[2]
        return
    
    def get_tag_result(self):
        return self.tags.get(TAG_RESULT)
    
    def is_movetext_valid(self):
        if not self._movetext_valid:
            # Movetext deemed invalid even if calculation says ok
            return False
        return self._state == RESULT
    
    def is_pgn_valid(self):
        return self.is_movetext_valid() and self.is_tag_roster_valid()
    
    def is_tag_roster_valid(self):
        if not self._tags_valid:
            # Tags deemed invalid even if calculation says ok
            return False
        if len(self.tags) != len(self.tags_in_order):
            # Tag must appear no more than once
            return False
        for v in self.tags.itervalues():
            if len(v) == 0:
                # Tag value must not be null
                return False
        for t in SEVEN_TAG_ROSTER:
            if t not in self.tags:
                # A mandatory tag is missing
                return False
        return True

    def process_game(self):
        self._movetext_valid = True
        self._collect_tags()
        if TAG_FEN in self.tags:
            self._state = self.set_position_fen(
                fen=self.tags[TAG_FEN])
        else:
            self._state = self.set_position_fen()
        self.tokens[:] = re_tokens.split(self._move_string)
        self._process_movetext()

    def set_position_fen(self, fen=None):
        """Initialize PGN score parser with Forsyth Edwards Notation position.

        fen defaults to the starting position for a game of chess.

        All the validition that is either simple or important is implemented,
        but this function will accept positions that cannot be reached by any
        legal sequence of moves from the standard starting position as valid.
        Thus an argument placing pawns on rank 0 or rank 7 is rejected, but
        an argument placing 8 black pawns on rank 2 and 8 white pawns on rank
        5 with all other pieces on their starting squares is accepted.

        return == None
        fen represents a legal position and the parser will accept import
        format PGN as the game score.

        return == PGN_ERROR
        fen does not represent a legal position and the parser will treat any
        input as a single comment.
        
        """
        # fen is standard start position by default
        if fen == None:
            self.gametokens[:] = []
            self.occupied_square_pieces[:] = [
                set(INITIAL_WP_SQUARES),
                set(INITIAL_BP_SQUARES)]
            self.board_pieces[:] = list(INITIAL_BOARD)
            self.ravstack[:] = [
                (None,
                 (tuple(self.board_pieces),
                  WHITE_TO_MOVE,
                  CASTLEALL,
                  NO_EP_SQUARE))]
            self.piece_locations[:] = [set(s) for s in INITIAL_SQUARES] 
            self.move_number = 1
            self.since_capture = 0
            self.ep_move_to_sq = NO_EP_SQUARE
            self.castle_options = CASTLEALL
            self.side_to_move = WHITE_TO_MOVE
            return None

        # fen specifies an arbitrary position
        
        # set all piece counts to zero
        sp_piececount = {
            WKING:0, WQUEEN:0, WROOK:0, WBISHOP:0, WKNIGHT:0, WPAWN:0,
            BKING:0, BQUEEN:0, BROOK:0, BBISHOP:0, BKNIGHT:0, BPAWN:0
            }

        # fen has six space delimited fields
        sp_p = fen.split(FEN_FIELD_DELIM)
        if len(sp_p) != 6:
            return PGN_ERROR

        # fen side to move field
        if sp_p[1] == FEN_WHITE:
            sp_side_to_move = WHITE_TO_MOVE
        elif sp_p[1] == FEN_BLACK:
            sp_side_to_move = BLACK_TO_MOVE
        else:
            return PGN_ERROR

        # fen square to which a pawn can move when capturing en passant
        if sp_p[3] == FEN_NO_DATA:
            sp_ep_remove_pawn_sq = sp_ep_move_to_sq = NO_EP_SQUARE
        else:
            if len(sp_p[3]) != 2:
                return PGN_ERROR
            elif sp_p[3][0] not in MAPFILE:
                return PGN_ERROR
            elif sp_p[3][1] not in MAPRANK:
                return PGN_ERROR
            sp_i = MAPFILE[sp_p[3][0]] + MAPRANK[sp_p[3][1]]
            if not sp_i in FEN_EP_SQUARES:
                return PGN_ERROR
            elif FEN_EP_SQUARES[sp_i][2] != sp_side_to_move:
                return PGN_ERROR
            else:
                sp_ep_move_to_sq = sp_i
                sp_ep_remove_pawn_sq = FEN_EP_SQUARES[sp_i][0]

        # fen moves since pawn move or capture
        if sp_p[4].isdigit() == 0:
            return PGN_ERROR
        else:
            sp_since_capture = int(sp_p[4])

        # fen next move number
        if sp_p[5].isdigit() == 0:
            return PGN_ERROR
        elif int(sp_p[5]) == 0:
            return PGN_ERROR
        else:
            sp_move_number = int(sp_p[5])

        # fen position field has eight / delimited ranks
        sp_rank = sp_p[0].split(FEN_RANK_DELIM)
        if len(sp_rank) != 8:
            return PGN_ERROR

        # no pawns on first or eighth ranks
        if sp_rank[0].count(FEN_WPAWN) + sp_rank[0].count(FEN_BPAWN) + sp_rank[7].count(FEN_WPAWN) + sp_rank[7].count(FEN_BPAWN):
            return PGN_ERROR

        # no more than 32 pieces and exactly 64 squares
        sp_i = 0
        for sp_j in FEN_PIECEMAP:
            sp_k = sp_piececount[FEN_PIECEMAP[sp_j]] = sp_p[0].count(sp_j)
            sp_i += sp_k
        if sp_i > 32:
            return PGN_ERROR
        for sp_j in FEN_ADJACENT_EMPTY_SQUARES:
            sp_i += int(sp_j) * sp_p[0].count(sp_j)
        if sp_i != 64:
            return PGN_ERROR

        # piece counts within pawn promotion bounds
        sp_i = sp_piececount[WPAWN] - 8
        sp_i += max(sp_piececount[WQUEEN] - 1, 0)
        sp_i += max(sp_piececount[WROOK] - 2, 0)
        sp_i += max(sp_piececount[WBISHOP] - 2, 0)
        sp_i += max(sp_piececount[WKNIGHT] - 2, 0)
        if sp_i > 0:
            return PGN_ERROR
        sp_i = sp_piececount[BPAWN] - 8
        sp_i += max(sp_piececount[BQUEEN] - 1, 0)
        sp_i += max(sp_piececount[BROOK] - 2, 0)
        sp_i += max(sp_piececount[BBISHOP] - 2, 0)
        sp_i += max(sp_piececount[BKNIGHT] - 2, 0)
        if sp_i > 0:
            return PGN_ERROR

        # no more than eight pawns per side
        if sp_piececount[WPAWN] > 8:
            return PGN_ERROR
        if sp_piececount[BPAWN] > 8:
            return PGN_ERROR

        # exactly one king per side
        if sp_piececount[WKING] != 1:
            return PGN_ERROR
        if sp_piececount[BKING] != 1:
            return PGN_ERROR

        # check 8 squares per rank and build internal position map
        # note white and black king squares
        sp_i = -1
        sp_white = set()
        sp_black = set()
        sp_occupied_square_pieces = [sp_white, sp_black]
        sp_board_pieces = [NOPIECE] * 64
        sp_piece_locations = [
            set(), set(), set(), set(), set(), set(),
            set(), set(), set(), set(), set(), set(),
            set(range(64)),
            ]
        for sp_r in sp_rank:
            sp_i += 1
            sp_fm = sorted(
                RANKS[len(RANKS) - sp_i - 1])
            sp_k = 0
            for sp_j in sp_r:
                if sp_j in FEN_PIECEMAP:
                    sp_l = sp_fm[sp_k]
                    if FEN_PIECEMAP[sp_j] in WPIECES:
                        sp_white.add(sp_l)
                    else:
                        sp_black.add(sp_l)
                    sp_piece_locations[FEN_PIECEMAP[sp_j]].add(sp_l)
                    sp_piece_locations[NOPIECE].discard(sp_l)
                    sp_board_pieces[sp_l] = FEN_PIECEMAP[sp_j]
                    if sp_j == FEN_WKING:
                        sp_wking_sq = sp_l
                    elif sp_j == FEN_BKING:
                        sp_bking_sq = sp_l
                    sp_k += 1
                elif sp_j in FEN_ADJACENT_EMPTY_SQUARES:
                    sp_k += int(sp_j)
                else:
                    return PGN_ERROR
            if sp_k != 8:
                return PGN_ERROR

        # fen castling field
        sp_OO_options = 0
        if sp_p[2] != FEN_NO_DATA:
            for sp_j in sp_p[2]:
                if sp_p[2].count(sp_j) > 1:
                    return PGN_ERROR
                if sp_j not in CASTLEKEY:
                    return PGN_ERROR
                sp_k = CASTLEMOVES[CASTLEKEY[sp_j]]
                for sp_l in sp_k:
                    if sp_l[1] not in sp_piece_locations[sp_l[0]]:
                        return PGN_ERROR
                sp_OO_options += CASTLESET[CASTLEKEY[sp_j]]

        # position is legal apart from checks, actual and deduced, and deduced
        # move that sets up en passant capture possibility.

        # the two squares behind the pawn that can be captured en passant
        # must be empty. FEN quotes en passant capture square if latest move
        # is a two square pawn move,there does not need to be a pawn able to
        # make the capture. The side with the move must not be in check
        # diagonally through the square containing a pawn that can be captured
        # en passant square, treating that square as empty.
        if sp_ep_move_to_sq != NO_EP_SQUARE:
            if sp_ep_remove_pawn_sq not in sp_piece_locations[
                OTHERSIDE_PAWN[sp_side_to_move]]:
                return PGN_ERROR
            for sp_k in sp_occupied_square_pieces:
                if sp_ep_move_to_sq in sp_k:
                    return PGN_ERROR
                if FEN_EP_SQUARES[sp_ep_move_to_sq][1] in sp_k:
                    return PGN_ERROR
            ep_squares = sp_occupied_square_pieces[OTHER_SIDE[sp_side_to_move]]
            if sp_side_to_move == WHITE_TO_MOVE:
                sp_i = sp_ep_remove_pawn_sq + 16
                sp_j = BPAWN
            else:
                sp_i = sp_ep_remove_pawn_sq - 16
                sp_j = WPAWN
            ep_squares.add(sp_i)
            ep_squares.discard(sp_ep_remove_pawn_sq)
            if PGN._is_attacked(
                ep_squares,
                sp_piece_locations[SIDE_KING[sp_side_to_move]],
                sp_board_pieces,
                sp_occupied_square_pieces[sp_side_to_move]):
                return PGN_ERROR
            ep_squares.discard(sp_i)
            ep_squares.add(sp_ep_remove_pawn_sq)

        # the side without the move must not be in check
        sp_i = OTHER_SIDE[sp_side_to_move]
        if PGN._is_attacked(
            sp_occupied_square_pieces[OTHER_SIDE[sp_i]],
            sp_piece_locations[SIDE_KING[sp_i]],
            sp_board_pieces,
            sp_occupied_square_pieces[sp_i]):
            return PGN_ERROR

        # side with the move must not be in check from more than two squares
        sp_i = sp_side_to_move
        sp_j = PGN.get_attacks_on_square(
            sp_occupied_square_pieces[OTHER_SIDE[sp_i]],
            sp_piece_locations[SIDE_KING[sp_i]],
            sp_board_pieces,
            sp_occupied_square_pieces[sp_i])
        if len(sp_j) > 2:
            return PGN_ERROR

        # position is legal so set up self.position and self.piece_locations
        self.gametokens[:] = []
        self.ravstack[:] = [
            (None,
             (tuple(sp_board_pieces),
              sp_side_to_move,
              sp_OO_options,
              sp_ep_move_to_sq))]
        self.occupied_square_pieces[:] = sp_occupied_square_pieces
        self.piece_locations[:] = sp_piece_locations
        self.board_pieces[:] = sp_board_pieces
        self.move_number = sp_move_number * 2 - (
            sp_side_to_move == WHITE_TO_MOVE)
        self.since_capture = sp_since_capture
        self.ep_move_to_sq = sp_ep_move_to_sq
        self.castle_options = sp_OO_options
        self.side_to_move = sp_side_to_move

        return None

    @staticmethod
    def get_attacks_on_square(tomove, targets, board_pieces, offmove):
        """Returns a list of attacks on square by side without the move.
        
        Mainly to validate fen.
        Return a list of squares containg pieces of the side without the move
        that attack the square. A list of squares between the two squares is
        held in GAPS.
        Attacks on e4 by Rb4 Rh4 Nc3 Ng3 and Bd5 would be represented by
        [18, 22, 25, 31, 35] each element being a square occupied by a piece
        that can move to e4.
        
        """
        attacks = []
        for square in targets:
            att = PIECES_ATTACK[square]
            gap = GAPS[square]
            for sq in tomove:
                if board_pieces[sq] in att[sq]:
                    for s in gap[sq]:
                        if s in tomove:
                            break
                        if s in offmove:
                            break
                    else:
                        attacks.append(sq)
        return attacks

    def _add_move_to_game(self):
        """Add legal move to data structures describing game.

        Caller has modified the board description as specified by the move
        ignoring whether the king of the moving side is left in check.  If
        the king is left in check undo the move and return False.  If not
        update the variation structure of the game and return True.

        """
        self.side_to_move = OTHER_SIDE[self.side_to_move]
        self.ravstack[-1] = (
            self.ravstack[-1][-1],
            (tuple(self.board_pieces),
             self.side_to_move,
             self.castle_options,
             self.ep_move_to_sq))
        self._state = MOVETEXT
        self._token_move()

    def _collect_tags(self): # update and display may have different versions
        self.tags.clear()
        tags_in_order = self.tags_in_order
        tags_in_order[:] = []
        self._tags_valid = True
        for t in re_tags.split(self._tag_string):
            st = t.strip()
            if st:
                try:
                    f, v = st.split('"', 1)
                    f = f[1:].strip()
                    tags_in_order.append((f, v.rsplit('"', 1)[0]))
                except ValueError:
                    pass
                except:
                    self._tags_valid = False
                    raise
        self.tags.update(tags_in_order)

    def _disambiguate_move(self):
        """Process second token in <piece><fromsquare><tosquare> sequence.

        If more than two pieces of a kind can move to a square the move is
        represented as Qd1f3 for example.  The parser treats this sequence as
        a queen move followed by a pawn move normally.  If that assumption
        fails and there is a queen of the side to move on d1 and more than two
        queens of this side on the board the piece move interpretation of
        Qd1f3 is tested by this method.

        """
        t = re_disambiguate.match(self._token)
        if not t:
            self._token_move_error_disambiguate()
            self._state = False
            return False
        (pgn_piece,
         tofile,
         torank,
         capture,
         fromfile,
         fromrank,
         pgn_promote,
         annotation,
         ) = self._token_groups
        (tofile, torank, annotation,) = t.groups()
        tosquare = MAPFILE[tofile] + MAPRANK[torank]
        fromsquare = MAPFILE[fromfile] + MAPRANK[fromrank]
        piece = MAPPIECE[pgn_piece][self.side_to_move]
        from_squares = self.piece_locations[piece].intersection(
            PIECE_MOVE_MAP[piece][tosquare]).intersection(
            RANKS[MAPROW[fromrank]].union(FILES[MAPFILE[fromfile]]))
        for fs in from_squares.copy():
            if not GAPS[tosquare][fromsquare].issubset(
                self.piece_locations[NOPIECE]):
                from_squares.discard(fs)
        self._prune_pieces_pinned_to_king(from_squares, tosquare)
        # PGN specification implies that the Qd1f3 kind of move specification is
        # to be used only if both rank alone and file alone are insufficient.
        # At this point there must be three or more items in from_squares to
        # meet this condition.  This rule is not enforced (as for corresponding
        # rules for rank and file in Qdf3 and Q1f3 move specifications).
        if fromsquare not in from_squares:
            self._token_move_error_disambiguate()
            self._state = False
            return False
        if tosquare not in self.piece_locations[NOPIECE]:
            self._token_move_error_disambiguate()
            self._state = False
            return False
        self.castle_options &= CASTLEMASKS[fromsquare]
        # remove moving piece from old square
        self.piece_locations[piece].discard(fromsquare)
        self.piece_locations[NOPIECE].add(fromsquare)
        self.occupied_square_pieces[self.side_to_move].discard(fromsquare)
        self.board_pieces[fromsquare] = NOPIECE
        # add moving piece to new square
        self.piece_locations[piece].add(tosquare)
        self.piece_locations[NOPIECE].discard(tosquare)
        self.occupied_square_pieces[self.side_to_move].add(tosquare)
        self.board_pieces[tosquare] = piece
        self.ep_move_to_sq = NO_EP_SQUARE
        # undo move if it leaves king in check
        if self._is_king_in_check_after_move():
            self.reset_position(self.ravstack[-1][-1])
            self._token_move_error_disambiguate()
            self._state = False
            return False
        # add move to data structures describing game
        self._token = ''.join((self.gametokens.pop(), self._token))
        return self._add_move_to_game()

    def _process_movetext(self):
        dt = self._despatch_table
        utvt = self._unmatched_text_valid_table
        tokens = self.tokens
        for e, self._token in enumerate(tokens):
            if e % 2:
                dt[self._state].get(self._token, dt[self._state][None])()
            elif len(self._token):
                utvt[self._state]()
        self._set_game_data()

    def _revert_state_and_reprocess_token(self):
        self._state = self._state_stack.pop()
        return self._despatch_table[self._state].get(
            self._token,
            self._despatch_table[self._state][None])()

    def _process_token(self):
        """Process move token in main line or variation"""
        t = re_detail.match(self._token)
        if not t:
            if self._token.isdigit():
                self._token_digit()
                return
            if self._token.startswith(GLYPH):
                self._token_glyph()
                return
            if self._token in RESULT_SET:
                try:
                    del self.ravstack[-1]
                    if len(self.ravstack):
                        self._state = PGN_ERROR
                        self._token_movetext_error()
                    else:
                        self._state = RESULT
                        self._token_result()
                except:
                    self._state = PGN_ERROR
                    self._token_movetext_error()
                return
            self._state = False
            self._token_move_detail_error()
            return
        self._token_groups = t.groups()
        # Pick and call the appropriate method for the move
        if self._token_groups[PIECE_GROUP] == PGN_PAWN:
            if self._token_groups[MOVE_OR_CAPTURE_GROUP] == PLAIN_MOVE:
                if self._token_groups[PROMOTE_GROUP]:
                    self._make_pawn_promotion()
                else:
                    self._make_pawn_move()
            else:
                if self._token_groups[PROMOTE_GROUP]:
                    self._make_pawn_capture_promotion()
                else:
                    self._make_pawn_capture()
        elif self._token_groups[MOVE_OR_CAPTURE_GROUP] == PLAIN_MOVE:
            self._make_move()
        elif self._token_groups[MOVE_OR_CAPTURE_GROUP] == CAPTURE_MOVE:
            self._make_capture()
        else:
            self._make_castles_move()

    def _make_castles_move(self):
        if self._token.startswith(O_O_O):
            if self.side_to_move == WHITE_TO_MOVE:
                castles = CASTLEMOVES[WQ_CASTLES]
            elif self.side_to_move == BLACK_TO_MOVE:
                castles = CASTLEMOVES[BQ_CASTLES]
            else:
                self._state = False
                self._token_move_error()
                return
        elif self._token.startswith(O_O):
            if self.side_to_move == WHITE_TO_MOVE:
                castles = CASTLEMOVES[WK_CASTLES]
            elif self.side_to_move == BLACK_TO_MOVE:
                castles = CASTLEMOVES[BK_CASTLES]
            else:
                self._state = False
                self._token_move_error()
                return
        else:
            self._state = False
            self._token_move_error()
            return
        if not (CASTLESET[CASTLEKEY[castles[0][3]]] &
                self.castle_options):
            self._state = False
            self._token_move_error()
            return
        for piece in castles:
            if self.board_pieces[piece[1]] != piece[0]:
                self._state = False
                self._token_move_error()
                return
        for square in castles[1][2]:
            if self.board_pieces[square] != NOPIECE:
                self._state = False
                self._token_move_error()
                return
        self.ep_move_to_sq = NO_EP_SQUARE
        # Cannot castle out of, or through, check.
        # As implemented this test does not stop the king being placed on an
        # attacked square; but the add_move_to_game() call can, and is the
        # most convenient place to, do this test for all types of move.
        if PGN._is_attacked(
            self.occupied_square_pieces[
                OTHER_SIDE[self.side_to_move]],
            castles[0][4],
            self.board_pieces,
            self.occupied_square_pieces[self.side_to_move]):
            self._state = False
            self._token_move_error()
            return
        for piece, fromsquare in (
            (castles[0][0], castles[0][1],), # king
            (castles[1][0], castles[1][1],), # rook
            ):
            self.castle_options &= CASTLEMASKS[fromsquare]
            self.piece_locations[piece].discard(fromsquare)
            self.piece_locations[NOPIECE].add(fromsquare)
            self.occupied_square_pieces[self.side_to_move].discard(fromsquare)
            self.board_pieces[fromsquare] = NOPIECE
        for piece, tosquare in (
            (castles[0][0], castles[0][2][-1],), # king
            (castles[1][0], castles[1][2][-1],), # rook
            ):
            self.piece_locations[piece].add(tosquare)
            self.piece_locations[NOPIECE].discard(tosquare)
            self.occupied_square_pieces[self.side_to_move].add(tosquare)
            self.board_pieces[tosquare] = piece
        # undo move if it leaves king in check
        if self._is_king_in_check_after_move():
            self.reset_position(self.ravstack[-1][-1])
            self._state = False
            self._token_move_error()
            return
        # add move to data structures describing game
        self._add_move_to_game()

    def _make_capture(self):
        (pgn_piece,
         fromfile,
         fromrank,
         capture,
         tofile,
         torank,
         pgn_promote,
         annotation,
         ) = self._token_groups
        tosquare = MAPFILE[tofile] + MAPRANK[torank]
        piece = MAPPIECE[pgn_piece][self.side_to_move]
        from_squares = self.piece_locations[piece].intersection(
            PIECE_CAPTURE_MAP[piece][tosquare])
        if len(from_squares) > 1:
            if fromfile:
                from_squares.intersection_update(
                    FILES[MAPFILE[fromfile]])
            if fromrank:
                from_squares.intersection_update(
                    RANKS[MAPROW[fromrank]])
            if len(from_squares) > 1:
                occupied = self.occupied_square_pieces[
                    OTHER_SIDE[self.side_to_move]].union(
                        self.occupied_square_pieces[self.side_to_move])
                for fs in from_squares.copy():
                    for gs in occupied.intersection(
                        GAPS[tosquare][fs]):
                        from_squares.difference_update(
                            from_squares.intersection(
                                HIDDEN[tosquare][gs]))
            if len(from_squares) > 1:
                self._prune_pieces_pinned_to_king(from_squares, tosquare)
        if len(from_squares) != 1:
            self._state = False
            self._token_move_error()
            return
        fromsquare = from_squares.pop()
        if not GAPS[tosquare][fromsquare].issubset(
            self.piece_locations[NOPIECE]):
                self._state = False
                self._token_move_error()
                return
        # remove captured piece from old square
        if tosquare in self.piece_locations[NOPIECE]:
            self._state = False
            self._token_move_error()
            return
        self.piece_locations[
            self.board_pieces[tosquare]].discard(tosquare)
        self.occupied_square_pieces[
            OTHER_SIDE[self.side_to_move]].discard(tosquare)
        self.castle_options &= (CASTLEMASKS[fromsquare] &
                                CASTLEMASKS[tosquare])
        # add moving piece to new square
        self.piece_locations[piece].add(tosquare)
        self.occupied_square_pieces[self.side_to_move].add(tosquare)
        self.board_pieces[tosquare] = piece
        # remove moving piece from old square
        self.piece_locations[piece].discard(fromsquare)
        self.piece_locations[NOPIECE].add(fromsquare)
        self.occupied_square_pieces[self.side_to_move].discard(fromsquare)
        self.board_pieces[fromsquare] = NOPIECE
        self.ep_move_to_sq = NO_EP_SQUARE
        # undo move if it leaves king in check
        if self._is_king_in_check_after_move():
            self.reset_position(self.ravstack[-1][-1])
            self._state = False
            self._token_move_error()
            return
        # add move to data structures describing game
        self._add_move_to_game()

    def _make_move(self):
        (pgn_piece,
         fromfile,
         fromrank,
         capture,
         tofile,
         torank,
         pgn_promote,
         annotation,
         ) = self._token_groups
        tosquare = MAPFILE[tofile] + MAPRANK[torank]
        piece = MAPPIECE[pgn_piece][self.side_to_move]
        from_squares = self.piece_locations[piece].intersection(
            PIECE_MOVE_MAP[piece][tosquare])
        if len(from_squares) > 1:
            # if ... elif ... as get here only if exactly one of these given
            if fromfile:
                from_squares.intersection_update(
                    FILES[MAPFILE[fromfile]])
            elif fromrank:
                from_squares.intersection_update(
                    RANKS[MAPROW[fromrank]])
            if len(from_squares) > 1:
                occupied = self.occupied_square_pieces[
                    OTHER_SIDE[self.side_to_move]].union(
                        self.occupied_square_pieces[self.side_to_move])
                for fs in from_squares.copy():
                    for gs in occupied.intersection(
                        GAPS[tosquare][fs]):
                        from_squares.difference_update(
                            from_squares.intersection(
                                HIDDEN[tosquare][gs]))
            if len(from_squares) > 1:
                self._prune_pieces_pinned_to_king(from_squares, tosquare)
        if len(from_squares) != 1:
            # If moving piece is on tosquare and the next token is a square
            # identity try tosquare as fromsquare and next token as tosquare
            # for the piece move.
            # Only applies to Q B N non-capture moves where the moving side
            # has more than 2 of the moving piece so it is possible there are
            # two pieces of the moving kind on the same rank and the same
            # file at the same time which can reach the tosquare.
            # Check that there are at least three pieces of one kind which
            # can move to the same square and note the possibilities for
            # evaluation in two subsequent states where the next tokens are
            # readily available for comparison.  The next two tokens must be
            # '' and a square identity and the square identity must be one of
            # the possibilities.
            if self.board_pieces[tosquare] == piece:
                if len(self.piece_locations[piece]) > 2:
                    if pgn_piece in PGN_FROM_SQUARE_DISAMBIGUATION:
                        self._state = PGN_FROM_SQUARE_DISAMBIGUATION
                        self._token_move_disambiguate()
                        return True
            self._state = False
            self._token_move_error()
            return
        fromsquare = from_squares.pop()
        if not PATH[tosquare][fromsquare].issubset(
            self.piece_locations[NOPIECE]):
                self._state = False
                self._token_move_error()
                return
        # check for tosquare empty implied by PATH test
        self.castle_options &= CASTLEMASKS[fromsquare]
        # remove moving piece from old square
        self.piece_locations[piece].discard(fromsquare)
        self.piece_locations[NOPIECE].add(fromsquare)
        self.occupied_square_pieces[self.side_to_move].discard(fromsquare)
        self.board_pieces[fromsquare] = NOPIECE
        # add moving piece to new square
        self.piece_locations[piece].add(tosquare)
        self.piece_locations[NOPIECE].discard(tosquare)
        self.occupied_square_pieces[self.side_to_move].add(tosquare)
        self.board_pieces[tosquare] = piece
        self.ep_move_to_sq = NO_EP_SQUARE
        # undo move if it leaves king in check
        if self._is_king_in_check_after_move():
            self.reset_position(self.ravstack[-1][-1])
            self._state = False
            self._token_move_error()
            return
        # add move to data structures describing game
        self._add_move_to_game()

    def _make_pawn_capture(self):
        (pgn_piece,
         fromfile,
         fromrank,
         capture,
         tofile,
         torank,
         pgn_promote,
         annotation,
         ) = self._token_groups
        tosquare = MAPFILE[tofile] + MAPRANK[torank]
        piece = MAPPIECE[pgn_piece][self.side_to_move]
        from_squares = self.piece_locations[piece].intersection(
            PIECE_CAPTURE_MAP[piece][tosquare])
        if len(from_squares) > 1:
            from_squares.intersection_update(
                FILES[MAPFILE[fromfile]])
        if len(from_squares) != 1:
            self._state = False
            self._token_move_error()
            return
        fromsquare = from_squares.pop()
        if not GAPS[tosquare][fromsquare].issubset(
            self.piece_locations[NOPIECE]):
                self._state = False
                self._token_move_error()
                return
        # remove captured piece from old square or ep square
        if tosquare in self.piece_locations[NOPIECE]:
            # check for en passant before saying illegal move
            if tosquare != self.ep_move_to_sq:
                self._state = False
                self._token_move_error()
                return
            ep_capture_sq = EP_MOVES[self.ep_move_to_sq]
            self.piece_locations[
                self.board_pieces[ep_capture_sq]].discard(ep_capture_sq)
            self.piece_locations[NOPIECE].add(ep_capture_sq)
            self.piece_locations[NOPIECE].discard(self.ep_move_to_sq)
            self.occupied_square_pieces[
                OTHER_SIDE[self.side_to_move]].discard(ep_capture_sq)
            self.board_pieces[ep_capture_sq] = NOPIECE
        else:
            self.piece_locations[
                self.board_pieces[tosquare]].discard(tosquare)
            self.occupied_square_pieces[
                OTHER_SIDE[self.side_to_move]].discard(tosquare)
        self.castle_options &= (CASTLEMASKS[fromsquare] &
                                CASTLEMASKS[tosquare])
        # add moving piece to new square
        self.piece_locations[piece].add(tosquare)
        self.occupied_square_pieces[self.side_to_move].add(tosquare)
        self.board_pieces[tosquare] = piece
        # remove moving piece from old square
        self.piece_locations[piece].discard(fromsquare)
        self.piece_locations[NOPIECE].add(fromsquare)
        self.occupied_square_pieces[self.side_to_move].discard(fromsquare)
        self.board_pieces[fromsquare] = NOPIECE
        self.ep_move_to_sq = NO_EP_SQUARE
        # undo move if it leaves king in check
        if self._is_king_in_check_after_move():
            self.reset_position(self.ravstack[-1][-1])
            self._state = False
            self._token_move_error()
            return
        # add move to data structures describing game
        self._add_move_to_game()

    def _make_pawn_capture_promotion(self):
        (pgn_piece,
         fromfile,
         fromrank,
         capture,
         tofile,
         torank,
         pgn_promote,
         annotation,
         ) = self._token_groups
        tosquare = MAPFILE[tofile] + MAPRANK[torank]
        piece = MAPPIECE[pgn_piece][self.side_to_move]
        from_squares = self.piece_locations[piece].intersection(
            PIECE_CAPTURE_MAP[piece][tosquare])
        if len(from_squares) > 1:
            from_squares.intersection_update(
                FILES[MAPFILE[fromfile]])
        if len(from_squares) != 1:
            self._state = False
            self._token_move_error()
            return
        fromsquare = from_squares.pop()
        if not GAPS[tosquare][fromsquare].issubset(
            self.piece_locations[NOPIECE]):
                self._state = False
                self._token_move_error()
                return
        if tosquare not in self.occupied_square_pieces[
            OTHER_SIDE[self.side_to_move]]:
            self._state = False
            self._token_move_error()
            return
        promote = MAPPIECE[pgn_promote][self.side_to_move]
        self.castle_options &= (CASTLEMASKS[fromsquare] &
                                CASTLEMASKS[tosquare])
        # the captured piece
        self.piece_locations[
            self.board_pieces[tosquare]].discard(tosquare)
        self.occupied_square_pieces[
            OTHER_SIDE[self.side_to_move]].discard(tosquare)
        # the promoted pawn
        self.piece_locations[piece].discard(fromsquare)
        self.piece_locations[NOPIECE].add(fromsquare)
        self.occupied_square_pieces[self.side_to_move].discard(fromsquare)
        self.board_pieces[fromsquare] = NOPIECE
        # the promoted piece
        self.piece_locations[promote].add(tosquare)
        self.occupied_square_pieces[self.side_to_move].add(tosquare)
        self.board_pieces[tosquare] = promote
        self.ep_move_to_sq = NO_EP_SQUARE
        # undo move if it leaves king in check
        if self._is_king_in_check_after_move():
            self.reset_position(self.ravstack[-1][-1])
            self._state = False
            self._token_move_error()
            return
        # add move to data structures describing game
        self._add_move_to_game()

    def _make_pawn_move(self):
        (pgn_piece,
         fromfile,
         fromrank,
         capture,
         tofile,
         torank,
         pgn_promote,
         annotation,
         ) = self._token_groups
        tosquare = MAPFILE[tofile] + MAPRANK[torank]
        piece = MAPPIECE[pgn_piece][self.side_to_move]
        from_squares = self.piece_locations[piece].intersection(
            PIECE_MOVE_MAP[piece][tosquare])
        if len(from_squares) > 1:
            occupied = self.occupied_square_pieces[
                OTHER_SIDE[self.side_to_move]].union(
                    self.occupied_square_pieces[self.side_to_move])
            for fs in from_squares.copy():
                for gs in occupied.intersection(
                    GAPS[tosquare][fs]):
                    from_squares.difference_update(
                        from_squares.intersection(
                            HIDDEN[tosquare][gs]))
        if len(from_squares) != 1:
            self._state = False
            self._token_move_error()
            return
        fromsquare = from_squares.pop()
        if not PATH[tosquare][fromsquare].issubset(
            self.piece_locations[NOPIECE]):
                self._state = False
                self._token_move_error()
                return
        # check for tosquare empty implied by PATH test
        self.castle_options &= CASTLEMASKS[fromsquare]
        # remove moving piece from old square
        self.piece_locations[piece].discard(fromsquare)
        self.piece_locations[NOPIECE].add(fromsquare)
        self.occupied_square_pieces[self.side_to_move].discard(fromsquare)
        self.board_pieces[fromsquare] = NOPIECE
        # add moving piece to new square
        self.piece_locations[piece].add(tosquare)
        self.piece_locations[NOPIECE].discard(tosquare)
        self.occupied_square_pieces[self.side_to_move].add(tosquare)
        self.board_pieces[tosquare] = piece
        self.ep_move_to_sq = ALLOW_EP_MOVES.get(
            (fromsquare, tosquare), NO_EP_SQUARE)
        # undo move if it leaves king in check
        if self._is_king_in_check_after_move():
            self.reset_position(self.ravstack[-1][-1])
            self._state = False
            self._token_move_error()
            return
        # add move to data structures describing game
        self._add_move_to_game()

    def _make_pawn_promotion(self):
        (pgn_piece,
         fromfile,
         fromrank,
         capture,
         tofile,
         torank,
         pgn_promote,
         annotation,
         ) = self._token_groups
        tosquare = MAPFILE[tofile] + MAPRANK[torank]
        piece = MAPPIECE[pgn_piece][self.side_to_move]
        from_squares = self.piece_locations[piece].intersection(
            PIECE_MOVE_MAP[piece][tosquare])
        if len(from_squares) != 1:
            self._state = False
            self._token_move_error()
            return
        fromsquare = from_squares.pop()
        if not PATH[tosquare][fromsquare].issubset(
            self.piece_locations[NOPIECE]):
                self._state = False
                self._token_move_error()
                return
        # check for tosquare empty implied by PATH test
        promote = MAPPIECE[pgn_promote][self.side_to_move]
        self.castle_options &= CASTLEMASKS[fromsquare]
        # the promoted pawn
        self.piece_locations[piece].discard(fromsquare)
        self.piece_locations[NOPIECE].add(fromsquare)
        self.occupied_square_pieces[self.side_to_move].discard(fromsquare)
        self.board_pieces[fromsquare] = NOPIECE
        # the promoted piece
        self.piece_locations[promote].add(tosquare)
        self.piece_locations[NOPIECE].discard(tosquare)
        self.occupied_square_pieces[self.side_to_move].add(tosquare)
        self.board_pieces[tosquare] = promote
        self.ep_move_to_sq = NO_EP_SQUARE
        # undo move if it leaves king in check
        if self._is_king_in_check_after_move():
            self.reset_position(self.ravstack[-1][-1])
            self._state = False
            self._token_move_error()
            return
        # add move to data structures describing game
        self._add_move_to_game()

    @staticmethod
    def _is_attacked(tomove, targets, board_pieces, offmove):
        """Return a clear line from a square in targets to a square in tomove.

        Clear line is an iterable of squares from GAP, which lists
        the squares between but not including two squares.
        tomove and offmove are iterables of squares containing pieces of the
        side with the move and the side without the move respectively.
        targets is an iterable of squares to be tested for the possibilty of
        moving a piece from a square in tomove to a square in targets.
        If multiple clear lines exist for the given squares one of these lines
        is returned. Which one is undefined.
        
        """
        for square in targets:
            att = PIECES_ATTACK[square]
            gap = GAPS[square]
            for sq in tomove:
                if board_pieces[sq] in att[sq]:
                    for s in gap[sq]:
                        if s in tomove:
                            break
                        if s in offmove:
                            break
                    else:
                        return gap[sq]
        return False

    def _is_king_in_check_after_move(self):
        """Return True if king would be in check if move is played.

        Same algorithm as _is_attacked but volume of use justifies it being
        separate method.
        
        """
        tomove = self.occupied_square_pieces[OTHER_SIDE[self.side_to_move]]
        empty = self.piece_locations[NOPIECE]
        board_pieces = self.board_pieces
        for square in self.piece_locations[SIDE_KING[self.side_to_move]]:
            att = PIECES_ATTACK[square]
            gap = GAPS[square]
            for sq in tomove:
                if board_pieces[sq] in att[sq]:
                    for s in gap[sq]:
                        if s not in empty:
                            break
                    else:
                        return True
        return False

    def _prune_pieces_pinned_to_king(self, from_squares, tosquare):
        """Remove pieces pinned against king from list of potential moves.

        Rg3, for example, is not ambiguous if one of two rooks that could
        move to g3 is pinned against the king and g3 is not in the line on
        which the rook is pinned.  Rxg3, however, must be ambigous if more
        than one rook can do the capture and the pinning piece is on g3.

        This method is designed to disambiguate moves and leaves the legality
        of a move based on the king being in check after playing a move till
        after the move is played.  But if both rooks are pinned, by different
        pieces, both moves are removed from the list of potential moves.
        
        """
        kingsquares = self.piece_locations[SIDE_KING[self.side_to_move]]
        for fm_sq in tuple(from_squares):
            # remove potentially moving piece from board
            fm_piece = self.board_pieces[fm_sq]
            self.occupied_square_pieces[
                self.side_to_move].discard(fm_sq)
            self.piece_locations[fm_piece].discard(fm_sq)
            self.board_pieces[fm_sq] = NOPIECE
            for square in kingsquares:
                line = PGN._is_attacked(
                    self.occupied_square_pieces[
                        OTHER_SIDE[self.side_to_move]].intersection(
                            HIDDEN[square][fm_sq]),
                    kingsquares,
                    self.board_pieces,
                    self.occupied_square_pieces[self.side_to_move])
                if line:
                    if tosquare not in line:
                        if fm_sq != tosquare:
                            from_squares.discard(fm_sq)
            # put potentially moving piece back on board
            self.piece_locations[fm_piece].add(fm_sq)
            self.occupied_square_pieces[self.side_to_move].add(fm_sq)
            self.board_pieces[fm_sq] = fm_piece

    def reset_position(self, position):
        """Reset squares piece_locations etc to position."""
        self.board_pieces[:] = list(position[0])
        (self.side_to_move,
         self.castle_options,
         self.ep_move_to_sq) = position[1:]
        occupied_square_pieces = self.occupied_square_pieces
        for side in occupied_square_pieces:
            side.clear()
        piece_locations = self.piece_locations
        for i in piece_locations:
            i.clear()
        for sq, piece in enumerate(self.board_pieces):
            if piece in WPIECES:
                occupied_square_pieces[0].add(sq)
            elif piece in BPIECES:
                occupied_square_pieces[1].add(sq)
            piece_locations[piece].add(sq)

    def _comment_to_eol(self):
        self._state_stack.append(self._state)
        self._state = COMMENT_TO_EOL
        self._token_comment()

    def _comment_to_eol_after_nl_between_moves(self):
        self._state_stack.append(self._state)
        self._state = COMMENT_TO_EOL
        self._token_comment_after_newline()

    def _newline(self):
        self._state_stack.append(self._state)
        self._state = NEWLINE
        self._token_newline()

    def _newline_between_moves(self):
        self._state_stack.append(self._state)
        self._state = LINEFEED
        self._token_newline()

    def _newline_in_comment_to_eol(self):
        self._state = LINEFEED
        self._token_newline_keep()

    def _newline_in_escape_to_eol(self):
        self._state = LINEFEED
        self._token_newline_keep()

    def _newline_repeat(self):
        self._token_newline_keep()

    def _newline_repeat_between_moves(self):
        self._token_newline()

    def _escape_to_eol(self):
        self._state = ESCAPE_TO_EOL
        self._token_comment()

    def _escape_to_eol_after_nl_between_moves(self):
        self._state = ESCAPE_TO_EOL
        self._token_comment_after_newline()

    def _end_comment(self):
        self._state = self._state_stack.pop()
        self._token_end_comment()

    def _start_comment(self):
        self._state_stack.append(self._state)
        self._state = START_COMMENT
        self._token_start_comment()

    def _end_reserved(self):
        self._state = self._state_stack.pop()
        self._token_end_reserved()

    def _start_reserved(self):
        self._state_stack.append(self._state)
        self._state = START_RESERVED
        self._token_start_reserved()

    def _start_variation(self):
        self.ravstack.append((None, self.ravstack[-1][0]))
        self.reset_position(self.ravstack[-1][-1])
        self._state_stack.append(self._state)
        self._state = None
        self._token_start_variation()

    def _start_variation_in_error_sequence(self):
        self.ravstack.append(None)
        self._state_stack.append(self._state)
        self._state = False
        self._token_comment()

    def _end_variation(self):
        self._state = self._state_stack.pop()
        try:
            del self.ravstack[-1]
            try:
                self.reset_position(self.ravstack[-1][-1])
                self._token_end_variation()
            except:
                self._state = PGN_ERROR
                self._token_movetext_error()
        except:
            self._state = PGN_ERROR
            self._token_movetext_error()

    def _end_variation_containing_error(self):
        # different from _end_variation to emphasise state change
        self._state = self._state_stack.pop()
        del self.ravstack[-1]
        if self.ravstack[-1] is not None:
            self.reset_position(self.ravstack[-1][-1])
            self._token_end_variation()
        else:
            self._token_comment()

    def _move_error(self):
        self._state = False#PGN_ERROR
        self._movetext_valid = False # in case error is in a RAV
        self._token_move_error()

    def _movetext_error(self):
        self._state = PGN_ERROR
        self._token_movetext_error()

    # start of refactored game token collection for base class

    def _set_game_data(self):
        pass

    def _token_comment(self):
        pass

    def _token_comment_after_newline(self):
        pass

    def _token_digit(self):
        pass

    def _token_end_variation(self):
        pass

    def _token_glyph(self):
        pass

    def _token_move(self):
        pass

    def _token_move_detail_error(self):
        pass

    def _token_move_disambiguate(self):
        pass

    def _token_move_error(self):
        pass

    def _token_move_error_disambiguate(self):
        pass

    def _token_move_in_error_sequence(self):
        pass

    def _token_movetext_error(self):
        pass

    def _token_newline(self):
        pass

    def _token_newline_keep(self):
        pass

    def _token_period(self):
        pass

    def _token_previous_move_error(self):
        pass

    def _token_result(self):
        pass

    def _token_end_comment(self):
        pass

    def _token_start_comment(self):
        pass

    def _token_end_reserved(self):
        pass

    def _token_start_reserved(self):
        pass

    def _token_start_variation(self):
        pass

    def _token_whitespace(self):
        pass


class PGNDisplayMoves(PGN):
    """Base class for generating data structures to display a game.

    Methods added:

    None

    Methods overridden:

    _set_game_data
    _token_end_variation
    _token_move
    _token_move_detail_error
    _token_move_disambiguate
    _token_move_error_disambiguate
    _token_move_error
    _token_move_in_error_sequence
    _token_previous_move_error
    _token_result
    _token_start_variation
    
    Methods extended:

    __init__
    set_position_fen
    _add_move_to_game
    
    """

    def __init__(self):
        super(PGNDisplayMoves, self).__init__()
        
        '''Add structures to support display of PGN moves'''
        # moves describes the contents of gametokens (see superclass).
        # Each element in moves is (<type>, <gametoken index>, <data>).
        # A move is (True, <gametoken index>, <position after move>) so the
        # very first move is (True, None, <start position>) following the
        # convention in ravstack.  The initial position of a variation is
        # ('(', <gametoken index for '('>, <variation start position>) and the
        # end is (')', <gametoken index for ')'>, None).
        self.moves = []

    def set_position_fen(self, fen=None):
        """Initialize PGN score parser with Forsyth Edwards Notation position.

        fen defaults to the starting position for a game of chess.

        """
        if super(PGNDisplayMoves, self).set_position_fen(fen=fen) is None:
            self.moves[:] = [(TAG_FEN, None, self.ravstack[-1][-1])]
            return None
        return PGN_ERROR

    def _add_move_to_game(self):
        """Add legal move to data structures describing game.

        Caller has modified the board description as specified by the move
        ignoring whether the king of the moving side is left in check.  If
        the king is left in check undo the move and return False.  If not
        update the variation structure of the game and return True.

        """
        super(PGNDisplayMoves, self)._add_move_to_game()
        # extra code in this subclass

    def _set_game_data(self):
        if self._state == PGN_FROM_SQUARE_DISAMBIGUATION:
            self.moves.append((MOVE_ERROR, len(self.gametokens) - 1, False))

    def _token_end_variation(self):
        self.moves.append(
            (END_RAV, len(self.gametokens), self.ravstack[-1][-1]))
        self.gametokens.append(self._token)

    def _token_move(self):
        self.moves.append(
            (MOVE_TEXT, len(self.gametokens), self.ravstack[-1][-1]))
        self.gametokens.append(self._token)

    def _token_move_detail_error(self):
        self.moves.append((MOVE_ERROR, len(self.gametokens), False))
        self.gametokens.append(self._token)

    def _token_move_disambiguate(self):
        self.gametokens.append(self._token)

    def _token_move_error_disambiguate(self):
        self.moves.append((MOVE_ERROR, len(self.gametokens) - 1, False))
        self.moves.append((MOVE_AFTER_ERROR, len(self.gametokens), False))
        self.gametokens.append(self._token)

    def _token_move_error(self):
        self.moves.append((MOVE_ERROR, len(self.gametokens), False))
        self.gametokens.append(self._token)

    def _token_move_in_error_sequence(self):
        self.moves.append((MOVE_AFTER_ERROR, len(self.gametokens), False))
        self.gametokens.append(self._token)

    def _token_previous_move_error(self):
        self.moves.append((MOVE_ERROR, len(self.gametokens) - 1, False))
        self.moves.append((NON_MOVE, len(self.gametokens), False))
        self.gametokens.append(self._token)

    def _token_result(self):
        self.moves.append(
            (TERMINATION, len(self.gametokens), None))
        self.gametokens.append(self._token)

    def _token_start_variation(self):
        self.moves.append(
            (START_RAV, len(self.gametokens), self.ravstack[-1][-1]))
        self.gametokens.append(self._token)


class PGNDisplay(PGNDisplayMoves):
    """Generate data structures to display a game without ability to edit.

    Methods added:

    _concatenate_comments

    Methods overridden:

    _comment_to_eol_after_nl_between_moves
    _token_comment
    _token_comment_after_newline
    _token_digit
    _token_end_comment
    _token_end_reserved
    _token_glyph
    _token_movetext_error
    _token_newline
    _token_newline_keep
    _token_period
    _token_start_comment
    _token_start_reserved
    _token_whitespace
    
    Methods extended:

    __init__
    set_position_fen
    _comment_to_eol
    _escape_to_eol_after_nl_between_moves
    _set_game_data
    _token_end_variation
    _token_move
    _token_move_detail_error
    _token_move_error
    _token_move_in_error_sequence
    _token_result
    _token_start_variation
    
    """

    def __init__(self):
        super(PGNDisplay, self).__init__()
        
        '''Add structures to support display and edit of full PGN score'''
        # _comments is a buffer for collecting an uninterrupted sequence of
        # tokens to be treated as a single comment element when displayed.
        self._comments = []
        # _comment_type is the kind of token being collected.  Tags [...],
        # reserved <...>, comment {...}, nag $..., escape \n%...\n, and
        # comment to eol ;...\n or \n;...\n, are the options.
        self._comment_type = NON_MOVE

    def set_position_fen(self, fen=None):
        """Initialize PGN score parser with Forsyth Edwards Notation position.

        fen defaults to the starting position for a game of chess.

        """
        if super(PGNDisplay, self).set_position_fen(fen=fen) is None:
            self._comments[:] = []
            return None
        return PGN_ERROR

    def _concatenate_comments(self):
        """Concatenate adjacent comment tokens into one token for display."""
        comments = self._comments
        if len(comments) == 1:
            if comments[0] == ' ':
                # join(self.gametokens) will insert a space between tokens
                self._comments[:] = []
                return
        elif len(comments):
            if comments[0] == ' ':
                # join(self.gametokens) will insert a space before comment
                del comments[0]
            if comments[-1] == ' ':
                # join(self.gametokens) will insert a space after comment
                del comments[-1]
        if len(comments):
            self.moves.append((self._comment_type, len(self.gametokens), False))
            self.gametokens.append(''.join(comments))
            self._comments[:] = []
        self._comment_type = NON_MOVE

    def _comment_to_eol(self):
        self._concatenate_comments()
        super(PGNDisplay, self)._comment_to_eol()
        self._comment_type = COMMENT_TO_EOL

    def _comment_to_eol_after_nl_between_moves(self):
        self._comment_to_eol()

    def _escape_to_eol_after_nl_between_moves(self):
        nl = self._comments.pop()
        self._concatenate_comments()
        self._comments.append(nl)
        super(PGNDisplay, self)._escape_to_eol_after_nl_between_moves()
        self._comment_type = ESCAPE_TO_EOL

    # start of refactored game token collection for display and edit

    def _set_game_data(self):
        super(PGNDisplay, self)._set_game_data()
        self._concatenate_comments()

    def _token_comment(self):
        self._comments.append(self._token)

    def _token_comment_after_newline(self):
        self._comments.append(self._token)

    def _token_digit(self):
        self._concatenate_comments()
        self.moves.append((INTEGER, len(self.gametokens), False))
        self.gametokens.append(self._token)

    def _token_end_variation(self):
        self._concatenate_comments()
        super(PGNDisplay, self)._token_end_variation()

    def _token_glyph(self):
        self._concatenate_comments()
        self.moves.append((GLYPH, len(self.gametokens), False))
        self.gametokens.append(self._token)

    def _token_move(self):
        self._concatenate_comments()
        super(PGNDisplay, self)._token_move()

    def _token_move_detail_error(self):
        self._concatenate_comments()
        super(PGNDisplay, self)._token_move_detail_error()

    def _token_move_error(self):
        self._concatenate_comments()
        super(PGNDisplay, self)._token_move_error()

    def _token_move_in_error_sequence(self):
        self._concatenate_comments()
        super(PGNDisplay, self)._token_move_in_error_sequence()

    def _token_movetext_error(self):
        self._comments.append(self._token)

    def _token_newline(self):
        self._comments.append(self._token)

    def _token_newline_keep(self):
        self._comments.append(self._token)

    def _token_period(self):
        if self._comment_type is not PERIOD:
            self._concatenate_comments()
            self._comment_type = PERIOD
        self._comments.append(self._token)

    def _token_result(self):
        self._concatenate_comments()
        super(PGNDisplay, self)._token_result()

    def _token_end_comment(self):
        self._comments.append(self._token)
        self._concatenate_comments()

    def _token_start_comment(self):
        self._concatenate_comments()
        self._comment_type = START_COMMENT
        self._comments.append(self._token)

    def _token_end_reserved(self):
        self._comments.append(self._token)
        self._concatenate_comments()

    def _token_start_reserved(self):
        self._concatenate_comments()
        self._comment_type = START_RESERVED
        self._comments.append(self._token)

    def _token_start_variation(self):
        self._concatenate_comments()
        super(PGNDisplay, self)._token_start_variation()

    def _token_whitespace(self):
        self._comments.append(self._token)


class PGNEdit(PGNDisplay):
    """Generate data structures to display a game for editing.

    Methods added:

    None

    Methods overridden:

    process_game
    
    Methods extended:

    None
    
    """

    def process_game(self):
        """Override to use regular expression appropriate for editing PGN.

        Usually all the PGN text is present before parsing.  But when editing
        the text incomplete moves will be present and the 'R1' part of 'R1a4',
        for example, gets treated as two tokens, 'R' and '1' by the re_tokens
        regular expression when the 'a' has not yet been typed.

        """
        self._movetext_valid = True
        self._collect_tags()
        if TAG_FEN in self.tags:
            self._state = self.set_position_fen(
                fen=self.tags[TAG_FEN])
        else:
            self._state = self.set_position_fen()
        self.tokens[:] = re_tokens_edit.split(self._move_string)
        self._process_movetext()


class PGNMove(PGN):
    """Generate data structures to check legality of a move being edited.

    Methods added:

    None

    Methods overridden:

    is_movetext_valid
    process_game
    
    Methods extended:

    __init__
    set_position_fen
    
    """

    def __init__(self):
        """Extend to support restoration of initial position state"""
        super(PGNMove, self).__init__()
        self._initial_position = None
        self._move_number = self.move_number
        self._since_capture = self.since_capture

    def is_movetext_valid(self):
        """Override to return True if exactly one valid move in movetext."""
        if not self._movetext_valid:
            # Movetext deemed invalid even if calculation says ok
            return False
        return self._state is MOVETEXT
    
    def process_game(self):
        """Override to use existing start position and accept one move only.

        Use case is editing an existing game score and caller modifies that
        game score and discards the instance of this class once it has found
        a valid move to insert.

        """
        self._movetext_valid = True
        self._collect_tags()
        if self.ravstack[0][0] is None:
            self.gametokens[:] = []
            self.ravstack[:] = [(None, self._initial_position)]
            self.reset_position(self._initial_position)
            self.move_number = self._move_number
            self.since_capture = self._since_capture
        self._state = None
        self.tokens[:] = re_tokens.split(self._move_string)
        self._process_movetext()
        if len(self.tokens) > 3:
            self._movetext_valid = False
        elif len(self.tokens) < 3:
            self._movetext_valid = True
        elif len(self.tokens[2]):
            self._movetext_valid = False

    def set_position_fen(self, fen=None):
        """Extend to remember full state for initial position in fen"""
        state = super(PGNMove, self).set_position_fen(fen=fen)
        self._initial_position = self.ravstack[0][-1]
        self._move_number = self.move_number
        self._since_capture = self.since_capture
        return state


class PGNUpdate(PGN):
    """Generate data structures to update a game on a database.

    Methods added:

    None

    Methods overridden:

    _add_move_to_game
    _token_comment
    _token_comment_after_newline
    _token_digit
    _token_end_comment
    _token_end_reserved
    _token_end_variation
    _token_glyph
    _token_move
    _token_move_detail_error
    _token_move_disambiguate
    _token_move_error
    _token_move_error_disambiguate
    _token_move_in_error_sequence
    _token_movetext_error
    _token_newline
    _token_newline_keep
    _token_period
    _token_previous_move_error
    _token_result
    _token_start_comment
    _token_start_reserved
    _token_start_variation
    _token_whitespace
    
    Methods extended:

    __init__
    set_position_fen
    
    """

    def __init__(self):
        super(PGNUpdate, self).__init__()
        
        '''Add structures to support update of PGN records on database'''
        self.positions = []
        self.piecesquaremoves = []

    def set_position_fen(self, fen=None):
        """Initialize PGN score parser with Forsyth Edwards Notation position.

        fen defaults to the starting position for a game of chess.

        """
        if super(PGNUpdate, self).set_position_fen(fen=fen) is None:
            self.positions[:] = []
            self.piecesquaremoves[:] = []
            return None
        return PGN_ERROR

    def _add_move_to_game(self):
        """Add legal move to data structures describing game.

        Caller has modified the board description as specified by the move
        ignoring whether the king of the moving side is left in check.  If
        the king is left in check undo the move and return False.  If not
        update the variation structure of the game and generate database keys
        for position on board and return True.

        """
        # superclass code repeated rather than called
        self.side_to_move = OTHER_SIDE[self.side_to_move]
        self.ravstack[-1] = (
            self.ravstack[-1][-1],
            (tuple(self.board_pieces),
             self.side_to_move,
             self.castle_options,
             self.ep_move_to_sq))
        self._state = MOVETEXT
        self._token_move()
        # extra code in this subclass
        board_pieces = self.board_pieces
        try:
            movenumber = MOVE_NUMBER_KEYS[len(self.positions)]
        except IndexError:
            n = len(self.positions)
            b = []
            while n:
                n, r = divmod(n, 256)
                b.append(SCH[r])
            try:
                movenumber = ''.join((SCH[len(b)], ''.join(b)))
            except IndexError:
                movenumber = ''.join((SCH[len(b) % 256], ''.join(b)))
        # This algorithm leads to run-times about 5% faster than obtained
        # with the one used in PGNDisplay.get_position_string() method when
        # updating the database.  Significant for large PGN files.
        # There are reasonable-looking algorithms that take 25% longer.
        piecesquares = sorted([PCH[board_pieces[square] * 64 + square]
                               for side in self.occupied_square_pieces
                               for square in side])
        self.positions.append(''.join(
            piecesquares +
            [TOMOVE_TO_POSITION_KEY[self.side_to_move]]))
        self.piecesquaremoves.extend(
            [''.join((s, movenumber)) for s in piecesquares])
        
    # start of refactored game token collection for update

    def _token_comment(self):
        self.gametokens.append(self._token)

    def _token_comment_after_newline(self):
        self.gametokens.append(LINEFEED)
        self.gametokens.append(self._token)

    def _token_digit(self):
        pass

    def _token_end_variation(self):
        self.gametokens.append(self._token)

    def _token_glyph(self):
        self.gametokens.append(self._token)

    def _token_move(self):
        self.gametokens.append(self._token)

    def _token_move_detail_error(self):
        self.gametokens.append(self._token)

    def _token_move_disambiguate(self):
        self.gametokens.append(self._token)

    def _token_move_error(self):
        self.gametokens.append(self._token)

    def _token_move_error_disambiguate(self):
        self.gametokens.append(self._token)

    def _token_move_in_error_sequence(self):
        self.gametokens.append(self._token)

    def _token_movetext_error(self):
        self.gametokens.append(self._token)

    def _token_newline(self):
        pass

    def _token_newline_keep(self):
        self.gametokens.append(self._token)

    def _token_period(self):
        pass

    def _token_previous_move_error(self):
        self.gametokens.append(self._token)

    def _token_result(self):
        self.gametokens.append(self._token)

    def _token_end_comment(self):
        self.gametokens.append(self._token)

    def _token_start_comment(self):
        self.gametokens.append(self._token)

    def _token_end_reserved(self):
        self.gametokens.append(self._token)

    def _token_start_reserved(self):
        self.gametokens.append(self._token)

    def _token_start_variation(self):
        self.gametokens.append(self._token)

    def _token_whitespace(self):
        pass


class PGNTags(PGN):
    """Generate data structures to display the PGN Tags of a game.

    Methods added:

    get_game_score

    Methods overridden:

    _process_movetext
    
    Methods extended:

    __init__
    
    """

    def __init__(self):
        super(PGNTags, self).__init__()
        self._gamescore = None

    def get_game_score(self):
        """Process PGN movetext if required and return game score"""
        if self._gamescore is None:
            super(PGNTags, self)._process_movetext()
            self._gamescore = ''.join(self.tokens)
        return self._gamescore

    def _process_movetext(self):
        """Override so PGN movetext is not processed"""


def get_board_from_position(position):
    """Return board description where position is after move played.

    Return value is
    tuple(tuple(<pieces on squares>), <whose move>, <castling>, <en passant>)

    """
    board = [NOPIECE] * 64
    castle_options = False
    ep_square = False
    side_to_move = False
    offset = 0
    for pk in position:
        decode = DECODE[pk] + offset
        if decode in POSITION_KEY_TO_FLAGS:
            if decode in SPECIAL_VALUES_OFFSET:
                offset = POSITION_KEY_TO_FLAGS[decode]
                continue
            elif decode in SPECIAL_VALUES_TOMOVE:
                side_to_move = POSITION_KEY_TO_FLAGS[decode]
            elif decode in SPECIAL_VALUES_CASTLE:
                castle_options = POSITION_KEY_TO_FLAGS[decode]
            elif decode in SPECIAL_VALUES_ENPASSANT:
                if side_to_move == WHITE_TO_MOVE:
                    ep_square = (MAPFILE[POSITION_KEY_TO_FLAGS[decode]] +
                                 MAPRANK['6'])
                elif side_to_move == BLACK_TO_MOVE:
                    ep_square = (MAPFILE[POSITION_KEY_TO_FLAGS[decode]] +
                                 MAPRANK['3'])
        else:
            square, piece = POSITION_KEY_TO_PIECES[decode]
            board[square] = piece
        offset = 0
    return tuple(board), side_to_move, castle_options, ep_square


def get_fen_from_position(position, halfmoves=0, fullmoves=1):
    """Return FEN description of position.

    The FEN description can be given as a PGN Tag in a PGN game score.  It
    can also be used to set a PGN instance to a given position.
    
    """
    board, side_to_move, castle_options, ep_square = position
    board = list(board)
    fen_board = []
    while len(board):
        rank = []
        while len(rank) < len(FILES):
            rank.insert(0, board.pop())
        gap_length = 0
        fen_rank = []
        for p in rank:
            if p == NOPIECE:
                gap_length += 1
                continue
            if gap_length:
                fen_rank.append(FEN_ADJACENT_EMPTY_SQUARES[gap_length - 1])
                gap_length = 0
            fen_rank.append(PIECE_FENMAP[p])
        if gap_length:
            fen_rank.append(FEN_ADJACENT_EMPTY_SQUARES[gap_length - 1])
        fen_board.append(''.join(fen_rank))
    return ' '.join((
        '/'.join(fen_board),
        SIDE_TO_MOVE_FENMAP[side_to_move],
        CASTLING_OPTION_FENMAP[castle_options],
        EN_PASSANT_FENMAP[ep_square],
        str(halfmoves),
        str(fullmoves)))


def get_position_string(position):
    """Return position for use as key in game retrieval.

    Encoded as a sorted sequence of one or two byte values representing
    the piece and it's host square.  There are 832 values including those
    representing an empty square.  The piece encoding is chosen such that
    the unused pawn-square codes (for a1..h1 and a8..h8) include those
    which represent 512 and 768 when used in integer context.  Castling
    options and en passant move, if any, are not included; being left to
    evaluation of the PGN game score in retrieved records.
    
    """
    '''May remove en passant from position specification because self.moves
    is tuple(previous position, current position) and can determine if en
    passant is possible by comparing the two positions.  Castling options
    persist so those flags must remain.'''
    # note that this algorithm to calculate the position key is not used in
    # PGNUpdate._add_move_to_game() method because it adds about 5% to the
    # run-time when updating database.  Significant when importing a large
    # PGN file.  However the data structure used there is not available to
    # this method. (That's 5% without the sort which is included here for
    # compatibility as the sort is needed in the other algorithm).
    board, side_to_move = position[:2]
    return ''.join(
        sorted([PCH[board[square] * 64 + square]
                for square in FULLBOARD if board[square] != NOPIECE]) +
        [TOMOVE_TO_POSITION_KEY[side_to_move]])

