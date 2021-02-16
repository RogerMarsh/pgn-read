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
TERMINATION = '*' # Unknown result
RESULT_SET = {WHITE_WIN, BLACK_WIN, DRAW, TERMINATION}

PGN_PAWN = ''
PGN_KING = 'K'
PGN_QUEEN = 'Q'
PGN_ROOK = 'R'
PGN_BISHOP = 'B'
PGN_KNIGHT = 'N'
PGN_FROM_SQUARE_DISAMBIGUATION = frozenset((PGN_QUEEN, PGN_BISHOP, PGN_KNIGHT))

# PGN regular expression pattern matching strings
PRINT_CHARS = ''.join((
    '[',
    ' -~',
    '-'.join((chr(192), chr(255))),
    ']',
    ))
ESCAPE_TO_EOL = '%' # loosely '\n%.*' ignore line
COMMENT_TO_EOL = ';' # loosely ';.*'
CHECK = '[+#]?'
ANNOTATION = '(?:[!?][!?]?)?'
# MOVETEXT matches the shortest string that could be a legal move.
# Thus it would find two moves, Qg7 and d4, from Qg7d4 not interpreting this
# as either the over elaborate recording of moving a queen from g7 to d4 or
# the possible, but unlikely, disambiguation needed when two queens on the
# g-file and two queens on the 7-rank can move to d4.  The parser considers
# the disambiguation possibility if there is a Q on g7 when Qg7 is given.
# It also rules out impossible moves such as axb4=Q.
# MOVETEXT is used in splitting a PGN text into moves.
MOVETEXT = ''.join((
    '(?:',
    '|'.join((
        '(?:[a-h](?:x[a-h])?[2-7])',
        '(?:[a-h](?:x[a-h])?[18]=[BNQR])',
        '(?:[BNQR][a-h]?[1-8]?x[a-h][1-8])',
        '(?:[BNQR][a-h1-8]?[a-h][1-8])',
        '(?:Kx?[a-h][1-8])',
        '(?:O-O-O)',
        '(?:O-O)',
        )),
    ')',
    '(?:', CHECK, ')?',
    '(?:', ANNOTATION, ')?',
    ))
# MOVE_DETAIL matches the longest string that could be a legal move.
# It is used to extract information from moves found by splitting a PGN text
# and assumes that the splitting was done using MOVETEXT.
# Thus axb4=Q and so on are assumed not to occur when using MOVE_DETAIL to
# determine if a move is legal in a game position.
MOVE_DETAIL = ''.join((
    '(?:',
    '|'.join((
        '(?:([KBNQR]?)([a-h]?)([1-8]?)(x?)([a-h])([1-8])(?:=([BNQR]))?)',
        '(?:O-O-O)',
        '(?:O-O)',
        )),
    ')',
    '(?:', CHECK, ')?',
    '(', ANNOTATION, ')?',
    ))
# MOVETEXT_EDIT matches the shortest string that could be a legal move or the
# start of a legal move.
# It modifies MOVETEXT to cope with editing Movetext when the text is parsed
# after each addition or removal of a character.
# Primary task is to stop 'R1' becoming two tokens 'R' '1' before 'R1a4' is
# typed for example.
MOVETEXT_EDIT = ''.join((
    '(?:',
    '|'.join((
        '(?:[a-h](?:x[a-h])?[2-7])',
        '(?:[a-h](?:x[a-h])?[18]=[BNQR])',
        '(?:[BNQR][a-h]?[1-8]?x[a-h][1-8])',
        '(?:[BNQR][a-h1-8]?[a-h][1-8])',
        '(?:Kx?[a-h][1-8])',
        '(?:O-O-O)',
        '(?:O-O)',
        '(?:[BNQR][1-8]x?[a-h]?)',
        '(?:[a-h][18]=?)',
        '(?:[a-h]x[a-h][18]=?)',
        )),
    ')',
    '(?:', CHECK, ')?',
    '(?:', ANNOTATION, ')?',
    ))
PIECE_GROUP = 0
FROMFILE_GROUP = 1
FROMRANK_GROUP = 2
MOVE_OR_CAPTURE_GROUP = 3
TOFILE_GROUP = 4
TORANK_GROUP = 5
PROMOTE_GROUP = 6
ANNOTATION_GROUP = 7
# DISAMBIGUATE matches the string that should be the destination square in a
# move where more than two of the specified piece can move to the square
DISAMBIGUATE = ''.join((
    '(?:([a-h])([1-8]))',
    '(?:', CHECK, ')?',
    '(', ANNOTATION, ')?',
    ))
DISAMBIGUATE_TOFILE_GROUP = 0
DISAMBIGUATE_TORANK_GROUP = 1
DISAMBIGUATE_ANNOTATION_GROUP = 2
O_O_O = 'O-O-O'
O_O = 'O-O'
PLAIN_MOVE = ''
CAPTURE_MOVE = 'x'
# Tokens
STRING = ''.join((
    '"',
    PRINT_CHARS,
    '*?"',
    ))
INTEGER = '(?:[1-9][0-9]*)'
PERIOD = '.'
START_COMMENT = '{'
END_COMMENT = '}' # Commentary. Loosely '{' + PRINT_CHARS + '*' + '}'
START_TAG = '['
END_TAG = ']' # See TAG_PAIR
START_RAV = '('
END_RAV = ')' # See recursive annotation variation
START_RESERVED = '<'
END_RESERVED = '>' # Undefined. Assumed loosely '{' + PRINT_CHARS + '*' + '}'
GLYPH = '$'
NAG = ''.join(('\$', INTEGER))
SYMBOL = '[A-Za-z0-9][A-Za-z0-9_+#=:-]*'
TAG_NAME = '[A-Z][A-Za-z0-9_+#=:-]*' # Symbol used as database field name
RESULT = '|'.join((
    WHITE_WIN.join(('(?:', ')')),
    BLACK_WIN.join(('(?:', ')')),
    DRAW.join(('(?:', ')')),
    ))
# If TERMINATION is included with the other results and RESULTS is placed
# early in TOKENS, for the split order, anything after RESULT is not split
# corrrectly.  Not quite sure what I am saying wrong to cause this.  Putting
# TERMINATION at end of TOKENS does what I want and is reasonable because it
# is one of the rarest tokens.
#
# RESULT_EDIT matches the shortest string that could be a legal result or the
# start of a legal result.
# It modifies RESULT to cope with editing Movetext when the text is parsed
# after each addition or removal of a character.
# Primary task is to stop '1-' becoming two tokens '1' '-' before '1-0' is
# typed for example.
RESULT_EDIT = '|'.join((
    WHITE_WIN.join(('(?:', ')')),
    BLACK_WIN.join(('(?:', ')')),
    DRAW.join(('(?:', ')')),
    '(?:1-)',
    '(?:0-)',
    '(?:1/2-1/)',
    '(?:1/2-1)',
    '(?:1/2-)',
    '(?:1/2)',
    '(?:1/)',
    ))
LINEFEED = '\n'
CARRIAGE_RETURN = '\r'
NEWLINE = ''.join((LINEFEED, CARRIAGE_RETURN))
SPACE = ' '
HORIZONTAL_TAB = '\t'
FORMFEED = '\f'
VERTICAL_TAB = '\v'
WHITESPACE = ''.join((SPACE, HORIZONTAL_TAB, FORMFEED, VERTICAL_TAB))
# Structures
TAG_PAIR = ''.join((
    START_TAG.join(('[', ']')),
    '\s*',
    SYMBOL,
    '\s*',
    STRING,
    '\s*',
    END_TAG.join(('[', ']')),
    ))
SPLIT_INTO_GAMES = ''.join((
    '((?:',
    TAG_PAIR,
    '\s*',
    ')*)',
    )) # Cannot have commentary or escaped data mixed in tag pairs
SPLIT_INTO_TAGS = ''.join((
    '(',
    TAG_PAIR,
    ')',
    )) # Non-whitespace outside a tag is assumed to be movetext
TOKEN = '|'.join((
    MOVETEXT,
    NAG,
    RESULT,
    INTEGER, # must be after MOVETEXT NAG and RESULT for correct splitting
    WHITESPACE.join(('[', ']')),
    PERIOD.join(('[', ']')),
    NEWLINE.join(('[', ']')),
    START_RAV.join(('[', ']')),
    END_RAV.join(('[', ']')),
    START_COMMENT,
    END_COMMENT,
    START_RESERVED,
    END_RESERVED,
    COMMENT_TO_EOL,
    ESCAPE_TO_EOL,
    TERMINATION.join(('[', ']')),
    ))
SPLIT_INTO_TOKENS = ''.join((
    '(',
    TOKEN,
    ')',
    )) # Cannot have commentary or escaped data mixed in tag pairs
TOKEN_EDIT = '|'.join((
    MOVETEXT_EDIT,
    NAG,
    RESULT_EDIT,
    INTEGER, # must be after MOVETEXT_EDIT NAG and RESULT for correct splitting
    WHITESPACE.join(('[', ']')),
    PERIOD.join(('[', ']')),
    NEWLINE.join(('[', ']')),
    START_RAV.join(('[', ']')),
    END_RAV.join(('[', ']')),
    START_COMMENT,
    END_COMMENT,
    START_RESERVED,
    END_RESERVED,
    COMMENT_TO_EOL,
    ESCAPE_TO_EOL,
    TERMINATION.join(('[', ']')),
    ))
SPLIT_INTO_TOKENS_EDIT = ''.join((
    '(',
    TOKEN_EDIT,
    ')',
    )) # Cannot have commentary or escaped data mixed in tag pairs

#
# numeric annotation glyphs (just validation for now)
#
NAG_TRANSLATION = {}
for o in range(1, 499): # only 1 though 139 have a formal definition
    NAG_TRANSLATION['$' + str(o)] = None
del o

#
# error states for PGN parser
#
PGN_MOVE_NOT_RECOGNISED = '1'  # token does not generate legal move in position
PGN_TOKENS_AFTER_RESULT = '2'  # token present after result (so game is valid)
PGN_ERROR = '3' # any error not classified under another error state 

#
# Square constants and flags
#
NO_EP_SQUARE = None

# Castling flags
WK_CASTLES = 1
WQ_CASTLES = 2
BK_CASTLES = 3
BQ_CASTLES = 4
CASTLEALL = 15
CASTLESET = {WK_CASTLES:8, WQ_CASTLES:4, BK_CASTLES:2, BQ_CASTLES:1}
CASTLEVOID_K = 7
CASTLEVOID_Q = 11
CASTLEVOID_k = 13
CASTLEVOID_q = 14
CASTLEVOID_w = 3
CASTLEVOID_b = 12

# Castling options kept (if possessed) on moving piece from square.
CASTLEMASKS = [CASTLEALL] * 64
CASTLEMASKS[0] = CASTLEVOID_Q
CASTLEMASKS[4] = CASTLEVOID_w
CASTLEMASKS[7] = CASTLEVOID_K
CASTLEMASKS[56] = CASTLEVOID_q
CASTLEMASKS[60] = CASTLEVOID_b
CASTLEMASKS[63] = CASTLEVOID_k

# Pieces
# Encoding positions is more efficient (key length) if pawns are encoded with
# a value less than 4 with either the white or the black pawn encoded as 0 and
# the squares that cannot host a pawn include 0..3 as their encodings (bytes
# \x01..\x03 which arises naturally as the second byte of the 2-byte encodings
# ), typically the squares b1 c1 and d1.  The other two values less than 4 are
# best used for the kings which are always present.  Absence of a piece is best
# encoded with the highest value, which will be 12 if using lists, wherever
# possible, rather than dictionaries for mappings.
NOPIECE = 12
WKING = 2
WQUEEN = 4
WROOK = 5
WBISHOP = 6
WKNIGHT = 7
WPAWN = 0
BKING = 3
BQUEEN = 8
BROOK = 9
BBISHOP = 10
BKNIGHT = 11
BPAWN = 1
PIECES = frozenset((
    NOPIECE,
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

# Packing order for piece counts in position keys for database
INITIAL_BOARD = (
    WROOK, WKNIGHT, WBISHOP, WQUEEN, WKING, WBISHOP, WKNIGHT, WROOK,
    WPAWN, WPAWN, WPAWN, WPAWN, WPAWN, WPAWN, WPAWN, WPAWN,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    NOPIECE, NOPIECE, NOPIECE, NOPIECE,
    BPAWN, BPAWN, BPAWN, BPAWN, BPAWN, BPAWN, BPAWN, BPAWN,
    BROOK, BKNIGHT, BBISHOP, BQUEEN, BKING, BBISHOP, BKNIGHT, BROOK,
    )
FULLBOARD = tuple(range(64))

# To move
WHITE_TO_MOVE = 0
BLACK_TO_MOVE = 1
OTHER_SIDE = [BLACK_TO_MOVE, WHITE_TO_MOVE]
OTHERSIDE_PAWN = [BPAWN, WPAWN]
SIDE_KING = [WKING, BKING]

# Define squares with white and black pieces for standard initial position
INITIAL_WP_SQUARES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
INITIAL_BP_SQUARES = (
    (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63))
INITIAL_SQUARES = tuple([v for k, v in sorted([
    (NOPIECE, (list(range(16, 48)))),
    (WKING, (4,)),
    (WQUEEN, (3,)),
    (WROOK, (0, 7)),
    (WBISHOP, (2, 5)),
    (WKNIGHT, (1, 6)),
    (WPAWN, (8, 9, 10, 11, 12, 13, 14, 15)),
    (BKING, (60,)),
    (BQUEEN, (59,)),
    (BROOK, (56, 63)),
    (BBISHOP, (58, 61)),
    (BKNIGHT, (57, 62)),
    (BPAWN, (48, 49, 50, 51, 52, 53, 54, 55)),
    ])])

# Map PGN piece file and rank names to internal representation
MAPPIECE = {
    PGN_PAWN: (WPAWN, BPAWN),
    PGN_KING: (WKING, BKING),
    PGN_QUEEN: (WQUEEN, BQUEEN),
    PGN_ROOK: (WROOK, BROOK),
    PGN_BISHOP: (WBISHOP, BBISHOP),
    PGN_KNIGHT: (WKNIGHT, BKNIGHT),
    } # not sure if this should be set or tuple or maybe both should exist
MAPFILE = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
MAPRANK = {'1':0, '2':8, '3':16, '4':24, '5':32, '6':40, '7':48, '8':56}
MAPROW = {'1':0, '2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7}

# FEN constants
FEN_STARTPOSITION = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
FEN_FIELD_DELIM = ' '
FEN_RANK_DELIM = '/'
FEN_NO_DATA = '-'
FEN_ADJACENT_EMPTY_SQUARES = '12345678'
FEN_WHITE = 'w'
FEN_BLACK = 'b'
FEN_WKING = 'K'
FEN_WQUEEN = 'Q'
FEN_WROOK = 'R'
FEN_WBISHOP = 'B'
FEN_WKNIGHT = 'N'
FEN_WPAWN = 'P'
FEN_BKING = 'k'
FEN_BQUEEN = 'q'
FEN_BROOK = 'r'
FEN_BBISHOP = 'b'
FEN_BKNIGHT = 'n'
FEN_BPAWN = 'p'

# Map FEN piece names to internal representation
FEN_PIECEMAP = {
    FEN_WKING: WKING,
    FEN_WQUEEN: WQUEEN,
    FEN_WROOK: WROOK,
    FEN_WBISHOP: WBISHOP,
    FEN_WKNIGHT: WKNIGHT,
    FEN_WPAWN: WPAWN,
    FEN_BKING: BKING,
    FEN_BQUEEN: BQUEEN,
    FEN_BROOK: BROOK,
    FEN_BBISHOP: BBISHOP,
    FEN_BKNIGHT: BKNIGHT,
    FEN_BPAWN: BPAWN,
    }

# Map internal representation to FEN piece names
PIECE_FENMAP = {
    WKING: FEN_WKING,
    WQUEEN: FEN_WQUEEN,
    WROOK: FEN_WROOK,
    WBISHOP: FEN_WBISHOP,
    WKNIGHT: FEN_WKNIGHT,
    WPAWN: FEN_WPAWN,
    BKING: FEN_BKING,
    BQUEEN: FEN_BQUEEN,
    BROOK: FEN_BROOK,
    BBISHOP: FEN_BBISHOP,
    BKNIGHT: FEN_BKNIGHT,
    BPAWN: FEN_BPAWN,
    }

# Map internal representation to FEN square names for en passant capture
EN_PASSANT_FENMAP = {
    None: FEN_NO_DATA,
    16: 'a3',
    17: 'b3',
    18: 'c3',
    19: 'd3',
    20: 'e3',
    21: 'f3',
    22: 'g3',
    23: 'h3',
    40: 'a6',
    41: 'b6',
    42: 'c6',
    43: 'd6',
    44: 'e6',
    45: 'f6',
    46: 'g6',
    47: 'h6',
    }

# Map internal representation to FEN castling option names
CASTLING_OPTION_FENMAP = {
    0: FEN_NO_DATA,
    1: FEN_BQUEEN,
    2: FEN_BKING,
    3: ''.join((FEN_BKING, FEN_BQUEEN)),
    4: FEN_WQUEEN,
    5: ''.join((FEN_WQUEEN, FEN_BQUEEN)),
    6: ''.join((FEN_WQUEEN, FEN_BKING)),
    7: ''.join((FEN_WQUEEN, FEN_BKING, FEN_BQUEEN)),
    8: FEN_WKING,
    9: ''.join((FEN_WKING, FEN_BQUEEN)),
    10: ''.join((FEN_WKING, FEN_BKING)),
    11: ''.join((FEN_WKING, FEN_BKING, FEN_BQUEEN)),
    12: ''.join((FEN_WKING, FEN_WQUEEN)),
    13: ''.join((FEN_WKING, FEN_WQUEEN, FEN_BQUEEN)),
    14: ''.join((FEN_WKING, FEN_WQUEEN, FEN_BKING)),
    15: ''.join((FEN_WKING, FEN_WQUEEN, FEN_BKING, FEN_BQUEEN)),
    }

# Map internal representation to FEN side to move names
SIDE_TO_MOVE_FENMAP = {
    WHITE_TO_MOVE: FEN_WHITE,
    BLACK_TO_MOVE: FEN_BLACK,
    }

# Map FEN castling description to internal representation
CASTLEKEY = {
    FEN_WKING: WK_CASTLES,
    FEN_WQUEEN: WQ_CASTLES,
    FEN_BKING: BK_CASTLES,
    FEN_BQUEEN: BQ_CASTLES,
    }

# Specification of conditions to be met to permit castling and changes to make
# to board to display move in internal representation.
# The square to which the king moves is not included in the set of squares
# that must not be under attack because this condition is checked for all moves
# after being played provisionally on the board.  The special additional thing
# about castling is that the king cannot move out of or through check; for all
# types of move the king must not be under attack after playing the move.  But
# as currently implemented there is no harm except waste in including the test.
CASTLEMOVES = {
    WK_CASTLES: (
        [WKING, 4, [5, 6], FEN_WKING, {4, 5}],
        [WROOK, 7, [6, 5]]),
    WQ_CASTLES: (
        [WKING, 4, [3, 2], FEN_WQUEEN, {4, 3}],
        [WROOK, 0, [1, 2, 3]]),
    BK_CASTLES: (
        [BKING, 60, [61, 62], FEN_BKING, {60, 61}],
        [BROOK, 63, [62, 61]]),
    BQ_CASTLES: (
        [BKING, 60, [59, 58], FEN_BQUEEN, {60, 59}],
        [BROOK, 56, [57, 58, 59]]) }

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

#
# The following lookup tables are calculated by _calculate_lookups() which is
# then deleted
#
# the character representation of positions for use as position keys
# not yet clear if castling and en passant possibilities will be included in
# position key but the encodings are defined
SCH = []
MOVE_NUMBER_KEYS = []
POSITION_KEY_TO_PIECES = dict()
POSITION_KEY_TO_FLAGS = dict()
TOMOVE_TO_POSITION_KEY = dict()
PCH = []
DECODE = {}
SPECIAL_VALUES_OFFSET = set()
SPECIAL_VALUES_TOMOVE = set()
SPECIAL_VALUES_CASTLE = set()
SPECIAL_VALUES_ENPASSANT = set()

def _calculate_lookups(boardside=8):
    """Generate lookups for creating database keys."""
    # 832 values are needed to represent all the (piece, square) combinations.
    # 256 values (0..255) can be encoded in 1 byte.  This is 4 sets of 64 which
    # just covers the white and black P K pieces, P the most common and K the
    # one always present.  The rest are encoded in two bytes using some unused
    # pawn encodings as the prefix.  For this it is convenient to encode one of
    # the pawns as 0 so that \x01 \x02 and \x03 are amongst the unused codes
    # (typically the squares b1 c1 and d1) as these byte value arises from
    # 832 / 256 and are a good choice as prefix values.
    boardsquares = boardside * boardside
    bytes256 = bytes(range(256))
    for e in bytes256:
        SCH.append(bytes256[e:e+1].decode('iso-8859-1'))
        DECODE[SCH[-1]] = e
    MOVE_NUMBER_KEYS[:] = [''.join((SCH[1], c)) for c in SCH]
    PCH[:] = [None] * len(PIECES) * boardsquares
    for piece in PIECES:
        base = piece * boardsquares
        if piece == NOPIECE:
            for square in range(boardsquares):
                PCH[base + square] = ''
        else:
            for square in range(boardsquares):
                prefix, code = divmod(base + square, 256)
                if prefix:
                    PCH[base + square] = ''.join((SCH[prefix], SCH[code]))
                else:
                    PCH[base + square] = SCH[code]
                POSITION_KEY_TO_PIECES[base + square] = (square, piece)
    # The special values (unused pawn-square encodings)
    castlemask = 0
    for f, v in sorted(MAPFILE.items()):
        # The en passant files
        POSITION_KEY_TO_FLAGS[WPAWN * boardsquares + MAPRANK['8'] + v] = f
        SPECIAL_VALUES_ENPASSANT.add(WPAWN * boardsquares + MAPRANK['8'] + v)
        # The castling options
        POSITION_KEY_TO_FLAGS[BPAWN * boardsquares + MAPRANK['1'] + v
                              ] = castlemask
        SPECIAL_VALUES_CASTLE.add(BPAWN * boardsquares + MAPRANK['1'] + v)
        POSITION_KEY_TO_FLAGS[BPAWN * boardsquares + MAPRANK['8'] + v
                              ] = castlemask + 8
        SPECIAL_VALUES_CASTLE.add(BPAWN * boardsquares + MAPRANK['8'] + v)
        castlemask += 1
        # Other move flags
        POSITION_KEY_TO_FLAGS[WPAWN * boardsquares + MAPRANK['1'] + v] = None
    # Set other move flags to specific values
    base = WPAWN * boardsquares + MAPRANK['1']
    POSITION_KEY_TO_FLAGS[base + MAPFILE['a']] = None
    POSITION_KEY_TO_FLAGS[base + MAPFILE['b']] = 256
    POSITION_KEY_TO_FLAGS[base + MAPFILE['c']] = 512
    POSITION_KEY_TO_FLAGS[base + MAPFILE['d']] = 768
    POSITION_KEY_TO_FLAGS[base + MAPFILE['e']] = None
    POSITION_KEY_TO_FLAGS[base + MAPFILE['f']] = None
    POSITION_KEY_TO_FLAGS[base + MAPFILE['g']] = WHITE_TO_MOVE
    POSITION_KEY_TO_FLAGS[base + MAPFILE['h']] = BLACK_TO_MOVE
    SPECIAL_VALUES_OFFSET.add(base + MAPFILE['b'])
    SPECIAL_VALUES_OFFSET.add(base + MAPFILE['c'])
    SPECIAL_VALUES_OFFSET.add(base + MAPFILE['d'])
    SPECIAL_VALUES_TOMOVE.add(base + MAPFILE['g'])
    SPECIAL_VALUES_TOMOVE.add(base + MAPFILE['h'])
    TOMOVE_TO_POSITION_KEY[WHITE_TO_MOVE] = PCH[base + MAPFILE['g']]
    TOMOVE_TO_POSITION_KEY[BLACK_TO_MOVE] = PCH[base + MAPFILE['h']]
                          
_calculate_lookups()
del _calculate_lookups

def _generate_square_maps(boardside=8):
    """Generate square mappings needed to determine legality of a chess move.

    Text from PGN gives the destination square, the piece, and as much as, but
    no more than, necessary of the source square to identify the move given
    the position.

    The board position gives the current location of all pieces.

    The mappings allow the legality of a move from PGN text to be determined.

    """
    # Not yet clear whether a further transformation to dictionary access on
    # square rank and file names ('d4' 'f' and '2' for example) is better.
    # Or even need both!

    def fen_en_passant_move_squares():
        # map enabling move to capturing move
        en_passant = dict()
        for s in range(boardside):
            en_passant[s + boardside * 5] = [
                s + boardside * 4,
                s + boardside * 6,
                WHITE_TO_MOVE,
                ]
            en_passant[s + boardside * 2] = [
                s + boardside * 3,
                s + boardside,
                BLACK_TO_MOVE,
                ]
        return en_passant

    def en_passant_move_squares():
        # map enabling move to capturing move
        en_passant = dict()
        for s in range(boardside):
            en_passant[(s + boardside, s + boardside * 3)] = (
                s + boardside * 2)
            en_passant[
                (boardsquares + s - boardside * 2,
                 boardsquares + s - boardside * 4)] = (
                     boardsquares + s - boardside * 3
                     )
        return en_passant

    def en_passant_capture_squares():
        # map capturing move to square where pawn captured
        en_passant = dict()
        for s in range(boardside):
            en_passant[s + boardside * 2] = s + boardside * 3
            en_passant[boardsquares + s - boardside * 3] = (
                     boardsquares + s - boardside * 4
                     )
        return en_passant

    def ranks_and_files():
        # 'a' is rank 0
        # '1' is file 0
        for s in range(boardside):
            rank.append(set())
            file_.append(set())
            
        for s in range(boardsquares):
            same_rank.append(set())
            same_file.append(set())

        for s in range(boardsquares):
            sr, sf = divmod(s, boardside)
            for t in range(s + 1):
                tr, tf = divmod(t, boardside)
                if tr == sr:
                    rank[sr].add(t)
                if tf == sf:
                    file_[sf].add(s)

        for s in range(boardsquares):
            sr, sf = divmod(s, boardside)
            same_rank[s].update(rank[sr])
            same_rank[s].remove(s)
            same_file[s].update(file_[sf])
            same_file[s].remove(s)

    def diagonals():
        # a1-h8 is 'up' diagonal 0
        # a2-g8 is 'up' diagonal 1
        # b1-h7 is 'up' diagonal 14
        # subtracting rank ('1' is 0) from file ('a' is 0) gives the correct
        # negative index to the updiagonals list.
        # a1 is 'down' diagonal 0
        # h1-a8 is 'down' diagonal 7
        # adding rank to file gives correct positive index into downdiagonals.
        for s in range(boardside * 2 - 1):
            downdiagonal.append(set())
            updiagonal.append(set())
            
        for s in range(boardsquares):
            same_downdiagonal.append(set())
            same_updiagonal.append(set())

        for s in range(boardsquares):
            sr, sf = divmod(s, boardside)
            downdiagonal[sr + sf].add(s)
            updiagonal[sr - sf].add(s) # because x[-1] is last element in list x

        for s in range(boardsquares):
            sr, sf = divmod(s, boardside)
            same_downdiagonal[s].update(downdiagonal[sr + sf])
            same_downdiagonal[s].remove(s)
            if not len(same_downdiagonal[s]):
                same_downdiagonal[s] = empty
            same_updiagonal[s].update(updiagonal[sr - sf])
            same_updiagonal[s].remove(s)
            if not len(same_updiagonal[s]):
                same_updiagonal[s] = empty

    def pieces_move_from_squares():
        # squares[10][30] is the set of pieces than can move to 10 from 30
        # pawn capture rules make this different to pieces_attack_from_squares
        # king_moves() queen_moves() and so on must be called before
        # pieces_attack_from_squares()
        squares = []
        wkbk = {WKING, BKING}
        wqbq = {WQUEEN, BQUEEN}
        wrbr = {WROOK, BROOK}
        wbbb = {WBISHOP, BBISHOP}
        wnbn = {WKNIGHT, BKNIGHT}
        wp = {WPAWN}
        bp = {BPAWN}
        for s in range(boardsquares):
            squares.append(list())
            for t in range(boardsquares):
                squares[s].append(set())
                if t in king[s]:
                    squares[s][t].update(wkbk)
                if t in queen[s]:
                    squares[s][t].update(wqbq)
                if t in rook[s]:
                    squares[s][t].update(wrbr)
                if t in bishop[s]:
                    squares[s][t].update(wbbb)
                if t in knight[s]:
                    squares[s][t].update(wnbn)
                if t in white_pawn_moves[s]:
                    squares[s][t].update(wp)
                if t in black_pawn_moves[s]:
                    squares[s][t].update(bp)
                if not len(squares[s][t]):
                    squares[s][t] = empty
        return squares

    def pieces_attack_from_squares():
        # squares[10][30] is the set of pieces than can capture on 10 from 30 
        # pawn capture rules make this different to pieces_move_from_squares
        # king_moves() queen_moves() and so on must be called before
        # pieces_attack_from_squares()
        squares = []
        wkbk = {WKING, BKING}
        wqbq = {WQUEEN, BQUEEN}
        wrbr = {WROOK, BROOK}
        wbbb = {WBISHOP, BBISHOP}
        wnbn = {WKNIGHT, BKNIGHT}
        wp = {WPAWN}
        bp = {BPAWN}
        for s in range(boardsquares):
            squares.append(list())
            for t in range(boardsquares):
                squares[s].append(set())
                if t in king[s]:
                    squares[s][t].update(wkbk)
                if t in queen[s]:
                    squares[s][t].update(wqbq)
                if t in rook[s]:
                    squares[s][t].update(wrbr)
                if t in bishop[s]:
                    squares[s][t].update(wbbb)
                if t in knight[s]:
                    squares[s][t].update(wnbn)
                if t in white_pawn_captures[s]:
                    squares[s][t].update(wp)
                if t in black_pawn_captures[s]:
                    squares[s][t].update(bp)
                if not len(squares[s][t]):
                    squares[s][t] = empty
        return squares

    def attacking_squares():
        # squares[10] is the set of squares from which a suitable piece can
        # capture on 10 
        # ranks_and_files() and diagonals() must be called before queen_moves()
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            squares[s].update(queen[s])
            squares[s].update(knight[s])
        return squares
            
    def queen_moves():
        # ranks_and_files() and diagonals() must be called before queen_moves()
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            squares[s].update(same_rank[s])
            squares[s].update(same_file[s])
            squares[s].update(same_updiagonal[s])
            squares[s].update(same_downdiagonal[s])
        return squares

    def rook_moves():
        # ranks_and_files() must be called before rook_moves()
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            squares[s].update(same_rank[s])
            squares[s].update(same_file[s])
        return squares

    def bishop_moves():
        # diagonals() must be called before bishop_moves()
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            squares[s].update(same_updiagonal[s])
            squares[s].update(same_downdiagonal[s])
        return squares

    def knight_moves():
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            sr, sf = divmod(s, boardside)
            for t in range(boardsquares):
                tr, tf = divmod(t, boardside)
                dr = abs(sr - tr)
                df = abs(sf - tf)
                if (dr == 1) or (df == 1):
                    if dr + df != 1:
                        if abs(dr - df) == 1:
                            squares[s].add(t)
        return squares

    def king_moves():
        # excluding O-O and O-O-O
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            sr, sf = divmod(s, boardside)
            for t in range(boardsquares):
                if t != s:
                    tr, tf = divmod(t, boardside)
                    dr = abs(sr - tr)
                    df = abs(sf - tf)
                    if (dr < 2) and (df < 2):
                        squares[s].add(t)
        return squares

    def white_pawn_moves_to_square():
        # just white pawn non-capture moves
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            sr, sf = divmod(s, boardside)
            if sr > 1:
                squares[s].update(rank[sr - 1].intersection(file_[sf]))
                if sr == 3:
                    squares[s].update(rank[sr - 2].intersection(file_[sf]))
            if not len(squares[s]):
                squares[s] = empty
        return squares

    def white_pawn_captures_to_square():
        # just white pawn capture moves
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            sr, sf = divmod(s, boardside)
            if sr > 1:
                if sf < boardside - 1:
                    squares[s].update(rank[sr - 1].intersection(file_[sf + 1]))
                if sf > 0:
                    squares[s].update(rank[sr - 1].intersection(file_[sf - 1]))
            if not len(squares[s]):
                squares[s] = empty
        return squares

    def black_pawn_moves_to_square():
        # just black pawn non-capture moves
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            sr, sf = divmod(s, boardside)
            if sr < boardside - 2:
                squares[s].update(rank[sr + 1].intersection(file_[sf]))
                if sr == boardside - 4:
                    squares[s].update(rank[sr + 2].intersection(file_[sf]))
            if not len(squares[s]):
                squares[s] = empty
        return squares

    def black_pawn_captures_to_square():
        # just black pawn capture moves
        squares = []
        for s in range(boardsquares):
            squares.append(set())
            sr, sf = divmod(s, boardside)
            if sr < boardside - 2:
                if sf < boardside - 1:
                    squares[s].update(rank[sr + 1].intersection(file_[sf + 1]))
                if sf > 0:
                    squares[s].update(rank[sr + 1].intersection(file_[sf - 1]))
            if not len(squares[s]):
                squares[s] = empty
        return squares

    def hidden_squares():
        # squares[10][30] bisects the line through (10,30) at 30 returning the
        # list of squares in the section containing neither 10 nor 30.
        # only ranks files and diagonals can give a non-empty list of squares
        squares = []
        for s in range(boardsquares):
            squares.append(list())
            for t in range(boardsquares):
                squares[s].append(set())
            
        for s in range(boardsquares):
            sr, sf = divmod(s, boardside)
            for t in range(s):
                tr, tf = divmod(t, boardside)
                if tr == sr:
                    squares[s][t].update(rank[tr])
                    squares[t][s].update(rank[tr])
                elif tf == sf:
                    squares[s][t].update(file_[tf])
                    squares[t][s].update(file_[tf])
                elif sf - tf == sr - tr:
                    squares[s][t].update(updiagonal[tr - tf])
                    squares[t][s].update(updiagonal[tr - tf])
                elif tf - sf == sr - tr:
                    squares[s][t].update(downdiagonal[tr + tf])
                    squares[t][s].update(downdiagonal[tr + tf])
                for u in range(t, boardsquares):
                    squares[s][t].discard(u)
                for u in range(s + 1):
                    squares[t][s].discard(u)

        for s in range(boardsquares):
            for t in range(boardsquares):
                if not len(squares[s][t]):
                    squares[s][t] = empty
            
        return squares

    def gap_squares():
        # squares[10][30] trisects the line through (10,30) returning list of
        # squares in the section between 10 and 30 excluding both 10 and 30.
        # only ranks files and diagonals can give a non-empty list of squares
        # squares[10][10] = []
        for s in range(boardsquares):
            gaps.append(list())
            for t in range(boardsquares):
                gaps[s].append(set())
            
        for s in range(boardsquares):
            sr, sf = divmod(s, boardside)
            for t in range(s):
                tr, tf = divmod(t, boardside)
                if tr == sr:
                    gaps[s][t].update(rank[tr])
                    gaps[t][s] = gaps[s][t]
                elif tf == sf:
                    gaps[s][t].update(file_[tf])
                    gaps[t][s] = gaps[s][t]
                elif sf - tf == sr - tr:
                    gaps[s][t].update(updiagonal[tr - tf])
                    gaps[t][s] = gaps[s][t]
                elif tf - sf == sr - tr:
                    gaps[s][t].update(downdiagonal[tr + tf])
                    gaps[t][s] = gaps[s][t]
                for u in range(t + 1):
                    gaps[s][t].discard(u)
                for u in range(s, boardsquares):
                    gaps[s][t].discard(u)

        for s in range(boardsquares):
            for t in range(boardsquares):
                if not len(gaps[s][t]):
                    gaps[s][t] = empty

    def path_squares():
        # squares[10][30] trisects the line through (10,30) returning list of
        # squares in the section between 10 and 30 including 10 but not 30.
        # only ranks files and diagonals can give a non-empty list of squares
        # squares[10][10] = [10]
        '''A possible optimisation is to refer to the element in gap_squares()
        which includes 30 as well if it exists, and so on.'''
        squares = []
        for s in range(boardsquares):
            squares.append(list())
            for t in range(boardsquares):
                squares[s].append(set())
            
        for s in range(boardsquares):
            sr, sf = divmod(s, boardside)
            for t in range(s):
                tr, tf = divmod(t, boardside)
                if tr == sr:
                    squares[s][t].update(rank[tr])
                    squares[t][s].update(rank[tr])
                elif tf == sf:
                    squares[s][t].update(file_[tf])
                    squares[t][s].update(file_[tf])
                elif sf - tf == sr - tr:
                    squares[s][t].update(updiagonal[tr - tf])
                    squares[t][s].update(updiagonal[tr - tf])
                elif tf - sf == sr - tr:
                    squares[s][t].update(downdiagonal[tr + tf])
                    squares[t][s].update(downdiagonal[tr + tf])
                for u in range(t + 1):
                    squares[s][t].discard(u)
                for u in range(s + 1, boardsquares):
                    squares[s][t].discard(u)
                for u in range(t):
                    squares[t][s].discard(u)
                for u in range(s, boardsquares):
                    squares[t][s].discard(u)
            squares[s][s].add(s)

        for s in range(boardsquares):
            for t in range(boardsquares):
                if not len(squares[s][t]):
                    squares[s][t] = empty
            
        return squares

    empty = set()
    gaps = []
    rank = []
    file_ = []
    updiagonal = []
    downdiagonal = []
    same_rank = []
    same_file = []
    same_updiagonal = []
    same_downdiagonal = []
    knight = []
    bishop = []
    rook = []
    queen = []
    king = []
    white_pawn_captures = []
    black_pawn_captures = []
    boardsquares = boardside * boardside

    ranks_and_files()
    diagonals()
    gap_squares()
    knight = knight_moves()
    bishop = bishop_moves()
    rook = rook_moves()
    queen = queen_moves()
    king = king_moves()
    white_pawn_moves = white_pawn_moves_to_square()
    white_pawn_captures = white_pawn_captures_to_square()
    black_pawn_moves = black_pawn_moves_to_square()
    black_pawn_captures = black_pawn_captures_to_square()
    attack = attacking_squares()
    pieces_attack = pieces_attack_from_squares()
    pieces_move = pieces_move_from_squares()

    return (
        rank,
        file_,
        same_rank,
        same_file,
        updiagonal,
        downdiagonal,
        same_updiagonal,
        same_downdiagonal,
        gaps,
        hidden_squares(),
        path_squares(),
        knight,
        bishop,
        rook,
        queen,
        king,
        white_pawn_moves,
        white_pawn_captures,
        black_pawn_moves,
        black_pawn_captures,
        attack,
        pieces_attack,
        pieces_move,
        en_passant_move_squares(),
        en_passant_capture_squares(),
        fen_en_passant_move_squares(),
        )

(RANKS,
 FILES,
 SAME_RANKS,
 SAME_FILES,
 UPDIAGONALS,
 DOWNDIAGONALS,
 SAME_UPDIAGONALS,
 SAME_DOWNDIAGONALS,
 GAPS,
 HIDDEN,
 PATH,
 KNIGHT_MOVES,
 BISHOP_MOVES,
 ROOK_MOVES,
 QUEEN_MOVES,
 KING_MOVES,
 WHITE_PAWN_MOVES_TO_SQUARE,
 WHITE_PAWN_CAPTURES_TO_SQUARE,
 BLACK_PAWN_MOVES_TO_SQUARE,
 BLACK_PAWN_CAPTURES_TO_SQUARE,
 ATTACK,
 PIECES_ATTACK,
 PIECES_MOVE,
 ALLOW_EP_MOVES,
 EP_MOVES,
 FEN_EP_SQUARES,
 ) = _generate_square_maps()
del _generate_square_maps

def _generate_capture_and_move_maps():
    """Generate piece move maps needed to determine legality of a chess move.

    Associate the piece encodings with the corresponding capture and move maps.

    """
    # A list so the encodings must be in range(len(<map>))
    # Could be a dictionary removing restriction on code values but lookup may
    # be slower enough to be noticed on large imports.
    capture_map = [None] * len(PIECES)
    move_map = [None] * len(PIECES)
    for p, c, m in (
        (NOPIECE, None, None,),
        (WKING, KING_MOVES, KING_MOVES,),
        (WQUEEN, QUEEN_MOVES, QUEEN_MOVES,),
        (WROOK, ROOK_MOVES, ROOK_MOVES,),
        (WBISHOP, BISHOP_MOVES, BISHOP_MOVES,),
        (WKNIGHT, KNIGHT_MOVES, KNIGHT_MOVES,),
        (WPAWN, WHITE_PAWN_CAPTURES_TO_SQUARE, WHITE_PAWN_MOVES_TO_SQUARE,),
        (BKING, KING_MOVES, KING_MOVES,),
        (BQUEEN, QUEEN_MOVES, QUEEN_MOVES,),
        (BROOK, ROOK_MOVES, ROOK_MOVES,),
        (BBISHOP, BISHOP_MOVES, BISHOP_MOVES,),
        (BKNIGHT, KNIGHT_MOVES, KNIGHT_MOVES,),
        (BPAWN, BLACK_PAWN_CAPTURES_TO_SQUARE, BLACK_PAWN_MOVES_TO_SQUARE,),
        ):
        capture_map[p] = c
        move_map[p] = m
    return capture_map, move_map

PIECE_CAPTURE_MAP, PIECE_MOVE_MAP = _generate_capture_and_move_maps()
del _generate_capture_and_move_maps
