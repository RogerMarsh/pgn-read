# constants.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Constants for Portable Game Notation (PGN) parser.

PGN

"""

# pgn specification values
TAG_EVENT = 'Event'
TAG_SITE = 'Site'
TAG_DATE = 'Date'
TAG_ROUND = 'Round'
TAG_WHITE = 'White'
TAG_BLACK = 'Black'
TAG_RESULT = 'Result'
TAG_FEN = 'FEN'
SEVEN_TAG_ROSTER = {
    TAG_EVENT: '?',
    TAG_SITE: '?',
    TAG_DATE: '????.??.??',
    TAG_ROUND: '?',
    TAG_WHITE: '?',
    TAG_BLACK: '?',
    TAG_RESULT: '*',
    }
SEVEN_TAG_ROSTER_DISPLAY_ORDER = (
    TAG_SITE,
    TAG_ROUND,
    TAG_EVENT,
    TAG_DATE,
    TAG_WHITE,
    TAG_BLACK,
    TAG_RESULT,
    )
SEVEN_TAG_ROSTER_EXPORT_ORDER = (
    TAG_EVENT,
    TAG_SITE,
    TAG_DATE,
    TAG_ROUND,
    TAG_WHITE,
    TAG_BLACK,
    TAG_RESULT,
    )
# Allow for decorators to do special cases for Date and Round sorting
SPECIAL_TAG_DATE = ('?', '0')
SPECIAL_TAG_ROUND = {'?': 1, '-':2}
NORMAL_TAG_ROUND = 3
SEVEN_TAG_ROSTER_ARCHIVE_SORT1 = (
    TAG_EVENT,
    TAG_SITE,
    TAG_DATE,
    )
SEVEN_TAG_ROSTER_ARCHIVE_SORT2 = (
    TAG_ROUND,
    TAG_WHITE,
    TAG_BLACK,
    TAG_RESULT,
    )

# Repertoire Tags (non-standard)
TAG_OPENING = 'Opening'
REPERTOIRE_TAG_ORDER = (TAG_OPENING, TAG_RESULT)
REPERTOIRE_GAME_TAGS = {
    TAG_OPENING: '?',
    TAG_RESULT: '*',
    }

WHITE_WIN = '1-0'
BLACK_WIN = '0-1'
DRAW = '1/2-1/2'
UNKNOWN_RESULT = '*' # Was TERMINATION
RESULT_SET = {WHITE_WIN, BLACK_WIN, DRAW, UNKNOWN_RESULT}

PGN_PAWN = ''
PGN_KING = 'K'
PGN_QUEEN = 'Q'
PGN_ROOK = 'R'
PGN_BISHOP = 'B'
PGN_KNIGHT = 'N'
PGN_FROM_SQUARE_DISAMBIGUATION = frozenset((PGN_QUEEN, PGN_BISHOP, PGN_KNIGHT))

# Refugees from old PGN regular expression pattern matching strings.
O_O_O = 'O-O-O'
O_O = 'O-O'
PLAIN_MOVE = ''
CAPTURE_MOVE = 'x'
LINEFEED = '\n'
CARRIAGE_RETURN = '\r'
NEWLINE = ''.join((LINEFEED, CARRIAGE_RETURN))
SPACE = ' '
HORIZONTAL_TAB = '\t'
FORMFEED = '\f'
VERTICAL_TAB = '\v'

# PGN regular expression pattern matching strings

# Building blocks
ANYTHING_ELSE = '.'
WHITESPACE = '\s+'
FULLSTOP = '.'
PERIOD ='\\' + FULLSTOP
INTEGER = '[1-9][0-9]*'
TERMINATION = '1-0|0-1|1/2-1/2|\*'
START_TAG = '['
END_TAG = ']'
SYMBOL = '([A-Za-z0-9][A-Za-z0-9_+#=:-]*)'
STRING = '((?<![\\\\])"(.*?)(?<![\\\\])")'
TAG_PAIR = ''.join(('(\\', START_TAG, ')\s*',
                    SYMBOL, '\s*',
                    STRING, '\s*',
                    '(\\', END_TAG, ')'))
START_COMMENT = '{'
END_COMMENT = '}'
COMMENT = ''.join(('\\', START_COMMENT, '[^', END_COMMENT, ']*\\', END_COMMENT))
LEFT_ANGLE_BRACE = '<'
RIGHT_ANGLE_BRACE = '>'
RESERVED = ''.join((
    LEFT_ANGLE_BRACE, '[^', RIGHT_ANGLE_BRACE, ']*', RIGHT_ANGLE_BRACE))
COMMENT_TO_EOL = ';(?:(?!$).)*\n'
PERCENT = '%'
ESCAPE_LINE = PERCENT.join(('(?<=\n)', '(?:(?!$).)*\n'))
NAG = '\$[0-9]+(?!/|-)'
START_RAV = '('
END_RAV = ')'
PAWN_PROMOTE = '(?:([a-h])(x))?([a-h][18])(=[BNQR])'
PAWN_CAPTURE = '([a-h])(x)([a-h][2-7])'
PIECE_CAPTURE = '(?:(K)|(?:([BNQR])([a-h]?[1-8]?)))(x)([a-h][1-8])'
PIECE_CHOICE_MOVE = '([BNQR])([a-h1-8])([a-h][1-8])'
PIECE_MOVE = '([KBNQR])([a-h][1-8])'
PAWN_MOVE = '([a-h][1-8])'
CASTLES = '(O-O(?:-O)?)'
CHECK = '([+#]?)'
ANNOTATION = '([!?][!?]?)?'

# Regular expression to detect full games in import format; export format is a
# subset of import format.  The text stored on database is captured.
IMPORT_FORMAT = ''.join(('(?:', TAG_PAIR, ')', '|',
                         '(?:',
                         '(?:',
                         '(?:', PAWN_PROMOTE, ')', '|',
                         '(?:', PAWN_CAPTURE, ')', '|',
                         '(?:', PIECE_CAPTURE, ')', '|',
                         '(?:', PIECE_CHOICE_MOVE, ')', '|',
                         '(?:', PIECE_MOVE, ')', '|',
                         '(?:', PAWN_MOVE, ')', '|',
                         '(?:', CASTLES, ')',
                         ')',
                         '(?:', CHECK, ')',
                         '(?:', ANNOTATION, ')',
                         ')', '|',
                         '(', COMMENT, ')', '|',
                         '(', NAG, ')', '|',
                         '(', COMMENT_TO_EOL, ')', '|',
                         '(', TERMINATION, ')', '|',
                         INTEGER, '|',
                         PERIOD, '|',
                         WHITESPACE, '|',
                         '(\\', START_RAV, ')', '|',
                         '(\\', END_RAV, ')', '|',
                         RESERVED, '|',
                         ESCAPE_LINE, '|',
                         '(', ANYTHING_ELSE, ')'))

# Regular expressions to disambiguate moves: move text like 'Bc4d5' is the only
# kind which could need to be interpreted as one move rather than two.
DISAMBIGUATE_FORMAT = '[BNQ][a-h][1-8][a-h][1-8]'
UNAMBIGUOUS_FORMAT = '.*'

# Regular expression to detect possible beginning of move in an error sequence,
# "Bxa" for example while typing "Bxa6".
POSSIBLE_MOVE = '[OKBNRQa-h][-Oa-h1-8+#?!=]* *'

#
# Group offsets for IMPORT_FORMAT matches
#
IFG_START_TAG = 1
IFG_TAG_SYMBOL = 2
IFG_TAG_STRING = 3
IFG_TAG_STRING_VALUE = 4
#IFG_TAG_END = 5
IFG_PAWN_PROMOTE_FROM_FILE = 6
IFG_PAWN_TAKES_PROMOTE = 7
IFG_PAWN_PROMOTE_SQUARE = 8
IFG_PAWN_PROMOTE_PIECE = 9
IFG_PAWN_CAPTURE_FROM_FILE = 10
IFG_PAWN_TAKES = 11
IFG_PAWN_CAPTURE_SQUARE = 12
IFG_KING_CAPTURE = 13
IFG_PIECE_CAPTURE = 14
IFG_PIECE_CAPTURE_FROM = 15
IFG_PIECE_TAKES = 16
IFG_PIECE_CAPTURE_SQUARE = 17
IFG_PIECE_CHOICE = 18
IFG_PIECE_CHOICE_FILE_OR_RANK = 19
IFG_PIECE_CHOICE_SQUARE = 20
IFG_PIECE_MOVE = 21
IFG_PIECE_SQUARE = 22
IFG_PAWN_SQUARE = 23
IFG_CASTLES = 24
IFG_CHECK = 25
IFG_ANNOTATION = 26
IFG_COMMENT = 27
IFG_NAG = 28
IFG_COMMENT_TO_EOL = 29
IFG_TERMINATION = 30
IFG_START_RAV = 31
IFG_END_RAV = 32
IFG_ANYTHING_ELSE = 33

#
# Parser states
#
PGN_SEARCHING = 0
PGN_SEARCHING_AFTER_ERROR_IN_RAV = 1
PGN_SEARCHING_AFTER_ERROR_IN_GAME = 2
PGN_COLLECTING_TAG_PAIRS = 3
PGN_COLLECTING_MOVETEXT = 4
PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING = 5
PGN_DISAMBIGUATE_MOVE = 6

#
# numeric annotation glyphs (just validation for now)
#
NAG_TRANSLATION = {'$' + str(o): None for o in range(1, 499)}

#
# Square constants and flags
#
BOARDSIDE = 8
BOARDSQUARES = BOARDSIDE * BOARDSIDE
SQUARE_BITS = [1 << i for i in range(BOARDSQUARES)]
ALL_SQUARES = sum(SQUARE_BITS)
EN_PASSANT_TO_SQUARES = sum([SQUARE_BITS[s] for s in range(24, 40)])
EN_PASSANT_FROM_SQUARES = (sum([SQUARE_BITS[s] for s in range(8, 16)]) |
                           sum([SQUARE_BITS[s] for s in range(48, 56)]))

# Pieces
# Encoding positions is more efficient (key length) if pawns are encoded with
# a value less than 4 with either the white or the black pawn encoded as 0 and
# the squares that cannot host a pawn include 0..3 as their encodings (bytes
# \x01..\x03 which arises naturally as the second byte of the 2-byte encodings
# ), typically the squares b1 c1 and d1.  The other two values less than 4 are
# best used for the kings which are always present.  Absence of a piece is best
# encoded with the highest value, which will be 12 if using lists, wherever
# possible, rather than dictionaries for mappings.
NOPIECE = ''
WKING = 'K'
WQUEEN = 'Q'
WROOK = 'R'
WBISHOP = 'B'
WKNIGHT = 'N'
WPAWN = 'P'
BKING = 'k'
BQUEEN = 'q'
BROOK = 'r'
BBISHOP = 'b'
BKNIGHT = 'n'
BPAWN = 'p'
PIECES = frozenset((
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
    ))

# Define white and black pieces and map to values used in database records
WPIECES = frozenset((WKING, WQUEEN, WROOK, WBISHOP, WKNIGHT, WPAWN))
BPIECES = frozenset((BKING, BQUEEN, BROOK, BBISHOP, BKNIGHT, BPAWN))

# The default initial board, internal representation.
INITIAL_BOARD = (
    BROOK, BKNIGHT, BBISHOP, BQUEEN, BKING, BBISHOP, BKNIGHT, BROOK,
    BPAWN, BPAWN, BPAWN, BPAWN, BPAWN, BPAWN, BPAWN, BPAWN,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    WPAWN, WPAWN, WPAWN, WPAWN, WPAWN, WPAWN, WPAWN, WPAWN,
    WROOK, WKNIGHT, WBISHOP, WQUEEN, WKING, WBISHOP, WKNIGHT, WROOK,
    )
INITIAL_OCCUPIED_SQUARES = (
    frozenset((48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63)),
    frozenset((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)))
INITIAL_BOARD_BITMAP = sum([sum([SQUARE_BITS[o] for o in s])
                            for s in INITIAL_OCCUPIED_SQUARES])
INITIAL_PIECE_LOCATIONS = {k:v for k, v in
                           ((WKING, (60,)),
                            (WQUEEN, (59,)),
                            (WROOK, (56, 63)),
                            (WBISHOP, (58, 61)),
                            (WKNIGHT, (57, 62)),
                            (WPAWN, (48, 49, 50, 51, 52, 53, 54, 55)),
                            (BKING, (4,)),
                            (BQUEEN, (3,)),
                            (BROOK, (0, 7)),
                            (BBISHOP, (2, 5)),
                            (BKNIGHT, (1, 6)),
                            (BPAWN, (8, 9, 10, 11, 12, 13, 14, 15)),
                            )}

# White and black side
WHITE_SIDE = 0
BLACK_SIDE = 1
OTHER_SIDE = BLACK_SIDE, WHITE_SIDE
SIDE_KING = WKING, BKING

# Map PGN piece file and rank names to internal representation
MAPPIECE = ({PGN_PAWN: WPAWN,
             PGN_KING: WKING,
             PGN_QUEEN: WQUEEN,
             PGN_ROOK: WROOK,
             PGN_BISHOP: WBISHOP,
             PGN_KNIGHT: WKNIGHT},
            {PGN_PAWN: BPAWN,
             PGN_KING: BKING,
             PGN_QUEEN: BQUEEN,
             PGN_ROOK: BROOK,
             PGN_BISHOP: BBISHOP,
             PGN_KNIGHT: BKNIGHT},
            ) # not sure if this should be set or tuple or dict

MAPFILE = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
MAPRANK = {'8':0, '7':8, '6':16, '5':24, '4':32, '3':40, '2':48, '1':56}
MAPROW = {'8':0, '7':1, '6':2, '5':3, '4':4, '3':5, '2':6, '1':7}

# {'a8':0, 'b8':1, ..., 'g1':62, 'h1':63}, the order squares are listed in
# Forsyth-Edwards Notation and the square numbers used internally.
MAP_PGN_SQUARE_NAME_TO_FEN_ORDER = {''.join((f,r)): fn + rn
                                    for f, fn in MAPFILE.items()
                                    for r, rn in MAPRANK.items()}

# FEN constants
FEN_STARTPOSITION = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
FEN_FIELD_DELIM = ' '
FEN_RANK_DELIM = '/'
FEN_NULL = '-'
FEN_ADJACENT_EMPTY_SQUARES = '12345678'
FEN_NEW = None
FEN_FIELD_DELIM = ' '
FEN_FIELD_COUNT = 6
FEN_WHITE = 'w'
FEN_BLACK = 'b'
FEN_SIDES = {FEN_WHITE: WHITE_SIDE, FEN_BLACK: BLACK_SIDE}
FEN_TOMOVE = FEN_WHITE, FEN_BLACK
FEN_INITIAL_HALFMOVE_COUNT = 0
FEN_INITIAL_FULLMOVE_NUMBER = 1

# Map internal representation to FEN square names for en passant capture
FEN_WHITE_MOVE_TO_EN_PASSANT = {
    'a6': 16,
    'b6': 17,
    'c6': 18,
    'd6': 19,
    'e6': 20,
    'f6': 21,
    'g6': 22,
    'h6': 23,
     }
FEN_BLACK_MOVE_TO_EN_PASSANT = {
    'a3': 40,
    'b3': 41,
    'c3': 42,
    'd3': 43,
    'e3': 44,
    'f3': 45,
    'g3': 46,
    'h3': 47,
    }
FEN_WHITE_CAPTURE_EN_PASSANT = {
    'a6': 24,
    'b6': 25,
    'c6': 26,
    'd6': 27,
    'e6': 28,
    'f6': 29,
    'g6': 30,
    'h6': 31,
     }
FEN_BLACK_CAPTURE_EN_PASSANT = {
    'a3': 32,
    'b3': 33,
    'c3': 34,
    'd3': 35,
    'e3': 36,
    'f3': 37,
    'g3': 38,
    'h3': 39,
    }
FEN_EN_PASSANT_TARGET_RANK = {'5':'6', '4':'3'}

# Castling
FEN_CASTLING = frozenset((WKING, WQUEEN, BKING, BQUEEN))
FEN_KINGS = frozenset((WKING, BKING))
FEN_INITIAL_CASTLING = WKING + WQUEEN + BKING + BQUEEN

# Specification of conditions to be met to permit castling and changes to make
# to board to display move in internal representation.
# The square to which the king moves is not included in the set of squares
# that must not be under attack because this condition is checked for all moves
# after being played provisionally on the board.  The special additional thing
# about castling is that the king cannot move out of or through check; for all
# types of move the king must not be under attack after playing the move.  But
# as currently implemented there is no harm except waste in including the test.
CASTLING_W = 60
CASTLING_WK = 63
CASTLING_WQ = 56
CASTLING_B = 4
CASTLING_BK = 7
CASTLING_BQ = 0
CASTLING_AVAILABITY_SQUARES = (
    SQUARE_BITS[CASTLING_WQ] |
    SQUARE_BITS[CASTLING_W] |
    SQUARE_BITS[CASTLING_WK] |
    SQUARE_BITS[CASTLING_BQ] |
    SQUARE_BITS[CASTLING_B] |
    SQUARE_BITS[CASTLING_BK])
CASTLING_SQUARES = {
    WKING: (
        CASTLING_W,
        CASTLING_WK,
        (CASTLING_W+1, CASTLING_W+2),
        (),
        WROOK,
        WKING),
    WQUEEN: (
        CASTLING_W,
        CASTLING_WQ,
        (CASTLING_W-1, CASTLING_W-2),
        (CASTLING_W-3,),
        WROOK,
        WKING),
    BKING: (
        CASTLING_B,
        CASTLING_BK,
        (CASTLING_B+1, CASTLING_B+2),
        (),
        BROOK,
        BKING),
    BQUEEN: (
        CASTLING_B,
        CASTLING_BQ,
        (CASTLING_B-1, CASTLING_B-2),
        (CASTLING_B-3,),
        BROOK,
        BKING),
    }

# FEN validation
FEN_CASTLING_OPTION_REPEAT_MAX = 1
FEN_PIECE_COUNT_PER_SIDE_MAX = 16
FEN_KING_COUNT = 1
FEN_PAWN_COUNT_MAX = 8
FEN_QUEEN_COUNT_INITIAL = 1
FEN_ROOK_COUNT_INITIAL = 2
FEN_BISHOP_COUNT_INITIAL = 2
FEN_KNIGHT_COUNT_INITIAL = 2
FEN_MAXIMUM_PIECES_GIVING_CHECK = 2

# variation markers and non-move placeholders
NON_MOVE = None
MOVE_ERROR = False
MOVE_AFTER_ERROR = 0
MOVE_TEXT = True

# Maximum line length in PGN file for movetext excluding EOL ('\n')
# Some PGN Tags are allowed to exceed this
# The rule may not be enforcable for comments, especially any re-exported,
# without disturbing any formatting attempts with EOL and spaces.
PGN_MAX_LINE_LEN = 79

# Piece moves and line definitions

_RANKS = [sum([SQUARE_BITS[s+r*BOARDSIDE] for s in range(BOARDSIDE)])
          for r in range(BOARDSIDE)
          for f in range(BOARDSIDE)
          ]
_FILES = [sum([SQUARE_BITS[s*BOARDSIDE+f] for s in range(BOARDSIDE)])
          for r in range(BOARDSIDE)
          for f in range(BOARDSIDE)
          ]
_TOPLEFT_TO_BOTTOMRIGHT = [
    sum([SQUARE_BITS[((f+c)%BOARDSIDE)+((r+c)%BOARDSIDE)*BOARDSIDE]
         for c in range(BOARDSIDE)
         if (f+c<BOARDSIDE and r+c<BOARDSIDE or
             f+c>=BOARDSIDE and r+c>=BOARDSIDE)])
    for r in range(BOARDSIDE)
    for f in range(BOARDSIDE)]
_BOTTOMLEFT_TO_TOPRIGHT = [
    sum([SQUARE_BITS[((f-c)%BOARDSIDE)+((r+c)%BOARDSIDE)*BOARDSIDE]
         for c in range(BOARDSIDE)
         if f>=c and r+c<BOARDSIDE or c>f and r+c>=BOARDSIDE])
    for r in range(BOARDSIDE)
    for f in range(BOARDSIDE)]

RANKS = [_RANKS[r*BOARDSIDE] for r in range(BOARDSIDE)]

FILES = _FILES[:BOARDSIDE]

ROOK_MOVES = [(_RANKS[k]|_FILES[k])-s for k, s in enumerate(SQUARE_BITS)]

BISHOP_MOVES = [(_TOPLEFT_TO_BOTTOMRIGHT[k]|_BOTTOMLEFT_TO_TOPRIGHT[k])-s
                for k, s in enumerate(SQUARE_BITS)]

QUEEN_MOVES = [(BISHOP_MOVES[s] | ROOK_MOVES[s]) for s in range(BOARDSQUARES)]

KNIGHT_MOVES = [
    ((sum(_FILES[kf+r*BOARDSIDE]
          for kf in range(f-2, f+3) if kf >= 0 and kf < BOARDSIDE) &
      sum(_RANKS[f+kr*8]
          for kr in range(r-2, r+3) if kr >= 0 and kr < BOARDSIDE)) &
     ~(_RANKS[f+r*BOARDSIDE] |
       _FILES[f+r*BOARDSIDE] |
       _TOPLEFT_TO_BOTTOMRIGHT[f+r*BOARDSIDE] |
       _BOTTOMLEFT_TO_TOPRIGHT[f+r*BOARDSIDE]))
    for r in range(BOARDSIDE)
    for f in range(BOARDSIDE)]

KING_MOVES = [
    (QUEEN_MOVES[f+r*BOARDSIDE] &
     (sum(_FILES[kf+r*BOARDSIDE]
          for kf in range(f-1, f+2) if kf >= 0 and kf < BOARDSIDE) &
      sum(_RANKS[f+kr*8]
          for kr in range(r-1, r+2) if kr >= 0 and kr < BOARDSIDE)))
    for r in range(BOARDSIDE)
    for f in range(BOARDSIDE)]

WHITE_PAWN_MOVES_TO_SQUARE = []
for s in range(BOARDSQUARES):
    if s < BOARDSQUARES - BOARDSIDE*2:
        WHITE_PAWN_MOVES_TO_SQUARE.append(SQUARE_BITS[s+BOARDSIDE])
    else:
        WHITE_PAWN_MOVES_TO_SQUARE.append(0)
for s in range(BOARDSQUARES-BOARDSIDE*4, BOARDSQUARES-BOARDSIDE*3):
    WHITE_PAWN_MOVES_TO_SQUARE[s] |= SQUARE_BITS[s+BOARDSIDE*2]

BLACK_PAWN_MOVES_TO_SQUARE = []
for s in range(BOARDSQUARES):
    if s < BOARDSIDE*2:
        BLACK_PAWN_MOVES_TO_SQUARE.append(0)
    else:
        BLACK_PAWN_MOVES_TO_SQUARE.append(SQUARE_BITS[s-BOARDSIDE])
for s in range(BOARDSIDE*3, BOARDSIDE*4):
    BLACK_PAWN_MOVES_TO_SQUARE[s] |= SQUARE_BITS[s-BOARDSIDE*2]

# 'b1' for black, and 'b8' for white, are allowed as pawn move specifications
# to disambiguate queen moves like 'Qd1f1'.
# PAWN_MOVE_DESITINATION filters them out.
PAWN_MOVE_DESITINATION = [0, 0]
for s in range(BOARDSQUARES):
    if s < BOARDSIDE:
        pass
    elif s < BOARDSIDE*2:
        PAWN_MOVE_DESITINATION[0] |= SQUARE_BITS[s]
    elif s < BOARDSQUARES-BOARDSIDE*2:
        PAWN_MOVE_DESITINATION[0] |= SQUARE_BITS[s]
        PAWN_MOVE_DESITINATION[1] |= SQUARE_BITS[s]
    elif s < BOARDSQUARES-BOARDSIDE:
        PAWN_MOVE_DESITINATION[1] |= SQUARE_BITS[s]

WHITE_PAWN_CAPTURES_TO_SQUARE = []
for s in range(BOARDSQUARES):
    if s > BOARDSQUARES - BOARDSIDE*2 - 1:
        WHITE_PAWN_CAPTURES_TO_SQUARE.append(0)
    elif s % BOARDSIDE == 0:
        WHITE_PAWN_CAPTURES_TO_SQUARE.append(SQUARE_BITS[s+BOARDSIDE+1])
    elif s % BOARDSIDE == BOARDSIDE - 1:
        WHITE_PAWN_CAPTURES_TO_SQUARE.append(SQUARE_BITS[s+BOARDSIDE-1])
    else:
        WHITE_PAWN_CAPTURES_TO_SQUARE.append(
            SQUARE_BITS[s+BOARDSIDE-1] | SQUARE_BITS[s+BOARDSIDE+1])

BLACK_PAWN_CAPTURES_TO_SQUARE = []
for s in range(BOARDSQUARES):
    if s < BOARDSIDE*2:
        BLACK_PAWN_CAPTURES_TO_SQUARE.append(0)
    elif s % BOARDSIDE == 0:
        BLACK_PAWN_CAPTURES_TO_SQUARE.append(SQUARE_BITS[s-BOARDSIDE+1])
    elif s % BOARDSIDE == BOARDSIDE - 1:
        BLACK_PAWN_CAPTURES_TO_SQUARE.append(SQUARE_BITS[s-BOARDSIDE-1])
    else:
        BLACK_PAWN_CAPTURES_TO_SQUARE.append(
            SQUARE_BITS[s-BOARDSIDE-1] | SQUARE_BITS[s-BOARDSIDE+1])

GAPS = []
for f in range(BOARDSQUARES):
    GAPS.append(list())
    for t in range(BOARDSQUARES):
        aligned = ((_RANKS[f] & _RANKS[t])|
                   (_FILES[f] & _FILES[t])|
                   (_TOPLEFT_TO_BOTTOMRIGHT[f] & _TOPLEFT_TO_BOTTOMRIGHT[t])|
                   (_BOTTOMLEFT_TO_TOPRIGHT[f] & _BOTTOMLEFT_TO_TOPRIGHT[t]))
        if not aligned:
            if SQUARE_BITS[t] & KNIGHT_MOVES[f]:
                GAPS[f].append(0)
            else:
                GAPS[f].append(ALL_SQUARES)
        else:
            gap = (aligned &
                   sum(SQUARE_BITS[min(f,t):max(f,t)+1]) &
                   ~(SQUARE_BITS[f] | SQUARE_BITS[t]))
            if gap:
                GAPS[f].append(gap)
            elif f == t:
                GAPS[f].append(ALL_SQUARES)
            else:
                GAPS[f].append(0)

del _TOPLEFT_TO_BOTTOMRIGHT
del _BOTTOMLEFT_TO_TOPRIGHT
del _FILES
del _RANKS
del f, t, gap, aligned

PIECE_CAPTURE_MAP = {k:v for k, v in
                     ((WKING, KING_MOVES),
                      (WQUEEN, QUEEN_MOVES),
                      (WROOK, ROOK_MOVES),
                      (WBISHOP, BISHOP_MOVES),
                      (WKNIGHT, KNIGHT_MOVES),
                      (WPAWN, WHITE_PAWN_CAPTURES_TO_SQUARE),
                      (BKING, KING_MOVES),
                      (BQUEEN, QUEEN_MOVES),
                      (BROOK, ROOK_MOVES),
                      (BBISHOP, BISHOP_MOVES),
                      (BKNIGHT, KNIGHT_MOVES),
                      (BPAWN, BLACK_PAWN_CAPTURES_TO_SQUARE),
                      )}

PIECE_MOVE_MAP = {k:v for k, v in
                  ((WKING, KING_MOVES),
                   (WQUEEN, QUEEN_MOVES),
                   (WROOK, ROOK_MOVES),
                   (WBISHOP, BISHOP_MOVES),
                   (WKNIGHT, KNIGHT_MOVES),
                   (WPAWN, WHITE_PAWN_MOVES_TO_SQUARE),
                   (BKING, KING_MOVES),
                   (BQUEEN, QUEEN_MOVES),
                   (BROOK, ROOK_MOVES),
                   (BBISHOP, BISHOP_MOVES),
                   (BKNIGHT, KNIGHT_MOVES),
                   (BPAWN, BLACK_PAWN_MOVES_TO_SQUARE),
                   )}

# Lookup tables for string representation of square and move numbers.
SCH = tuple([chr(i) for i in range(256)])
MOVE_NUMBER_KEYS = tuple([''.join((SCH[1], c)) for c in SCH])
