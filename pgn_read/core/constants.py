# constants.py
# Copyright 2010, 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Constants for Portable Game Notation (PGN) parser.

The defined constants are used when parsing PGN and FEN text, and when checking
the PGN game score represents a legal sequence of moves and variations.

"""

# r'(?:([a-h])x)?(([a-h])(?:[2-7]|([18])))(?:=([QRBN]))?' is the alternative
# considered for the pawn element of PGN_FORMAT.
# It's good point is the destination square is in a single captured group.
# It's bad point is the extra choices at the start of the element.
# The chosen version is probably slightly quicker, but 233,768 games were
# processed in just under 22 minutes to see a possible difference of 10 seconds
# in elapsed time.
# Changed to r'(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])(?:=([QRBN]))))' because
# it is easy to convert to the FIDE style for pawn promotion, 'e8Q' not 'e8=Q',
# additionally allowed in TEXT_FORMAT.  (It's another 10 seconds quicker too.)
PGN_FORMAT = r'|'.join((
    r''.join((r'(?#Start Tag)\[\s*',
              r'(?#Tag Name)([A-Za-z0-9_]+)\s*',
              r'(?#Tag Value)"((?:[^\\"]|\\.)*)"\s*',
              r'(?#End Tag)(\])')),
    r'(?:(?#Moves)(?#Piece)([KQRBN])([a-h1-8]?)(x?)([a-h][1-8])',
    r'(?#Pawn)(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])(?:=([QRBN]))))',
    r'(?#Castle)(O-O-O|O-O)(?#sevoM))(?#Suffix)[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
    r'(?#Game termination)(1-0|1/2-1/2|0-1|\*)',
    r'(?#Move number)([1-9][0-9]*)',
    r'(?#Dots)(\.+)',
    r'(?#EOL comment)(;(?:[^\n]*))',
    r'(?#Comment)(\{[^}]*\})',
    r'(?#Start RAV)(\()',
    r'(?#End RAV)(\))',
    r'(?#Numeric Annotation Glyph)(\$(?:[1-9][0-9]{0,2}))',
    r'(?#Reserved)(<[^>]*>)',
    r'(?#Escaped)(\A%[^\n]*|\n%[^\n]*)',
    r'(?#Pass)(--)',
    ))
PGN_DISAMBIGUATION = r''.join(
    (r'(?#Disambiguation PGN)',
     r'(x?[a-h][1-8][+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
     ))
TEXT_DISAMBIGUATION = r''.join(
    (r'(?#Disambiguation Text)',
     r'((?:-|x[QRBN]?)[a-h][1-8][+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
     ))
ANYTHING_ELSE = r'(?#Anything else)\S+[ \t\r\f\v]*)'
IMPORT_FORMAT = r'|'.join((
    PGN_FORMAT,
    PGN_DISAMBIGUATION,
    ANYTHING_ELSE))
TEXT_FORMAT = r'|'.join((
    PGN_FORMAT,
    TEXT_DISAMBIGUATION,
    ANYTHING_ELSE)).replace(r'O-O-O|O-O', r'O-O-O|O-O|0-0-0|0-0'
                            ).replace(r'(?:=([QRBN])', r'(?:=?([QRBN])')
IGNORE_CASE_FORMAT = r'(?#Ignore case)(?i)' + TEXT_FORMAT.replace(r'A-Z', r'')

# Indicies of captured groups in PGN input format for match.group.
IFG_TAG_NAME = 1
IFG_TAG_VALUE = 2
IFG_END_TAG = 3
IFG_PIECE_MOVE = 4
IFG_PIECE_MOVE_FROM_FILE_OR_RANK = 5
IFG_PIECE_CAPTURE = 6
IFG_PIECE_DESTINATION = 7
IFG_PAWN_FROM_FILE = 8
IFG_PAWN_CAPTURE_TO_FILE = 9
IFG_PAWN_TO_RANK = 10
IFG_PAWN_PROMOTE_TO_RANK = 11
IFG_PAWN_PROMOTE_PIECE = 12
IFG_CASTLES = 13
IFG_GAME_TERMINATION = 14
IFG_MOVE_NUMBER = 15
IFG_DOTS = 16
IFG_COMMENT_TO_EOL = 17
IFG_COMMENT = 18
IFG_START_RAV = 19
IFG_END_RAV = 20
IFG_NUMERIC_ANNOTATION_GLYPH = 21
IFG_RESERVED = 22
IFG_ESCAPE = 23
IFG_PASS = 24
IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE = 25

# For spotting the pawn-move-like string which is the destination of a fully
# disambiguated piece move, say 'Qb4d4+??' including optional sufficies, where
# Qb4 has been rejected as a move because there is a Q on b4.
DISAMBIGUATE_TEXT = r'\A(x?)([a-h][1-8])[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?'
DISAMBIGUATE_PGN = r'\Ax?[a-h][1-8][+#]?(?:!!|!\?|!|\?\?|\?!|\?)?'

# Indicies of captured groups for fully disambiguated piece move.
DG_CAPTURE = 1
DG_DESTINATION = 2

# For spotting the second part, of two, of a movetext token in long algebraic
# format (LAN).  The first part, such as 'Qe2', will have been found by the
# IMPORT_FORMAT rules.  LAN_FORMAT is similar to DISAMBIGUATE_TEXT.
LAN_FORMAT = r''.join((r'\A([-x]?)([a-h][1-8])(?:=(QRBN))?',
                       r'\s*([+#]?)\s*((?:!!|!\?|!|\?\?|\?!|\?)?)'))

# Indicies of captured groups for long algebraic notation move.
LAN_CAPTURE_OR_MOVE = 1
LAN_DESTINATION = 2
LAN_PROMOTE_PIECE = 3
LAN_CHECK_INDICATOR = 4
LAN_SUFFIX_ANNOTATION = 5

# For normalising a text promotion move to PGN.
TEXT_PROMOTION = r''.join((r'(?#Lower case)([a-h](?:[x-][a-h])?[18]=?)([qrbn])',
                           r'\s*([+#]?)\s*((?:!!|!\?|!|\?\?|\?!|\?)?)'))

# Indicies of captured groups for normalising promotion move to PGN.
TP_MOVE = 1
TP_PROMOTE_TO_PIECE = 2
TP_CHECK_INDICATOR = 3
TP_SUFFIX_ANNOTATION = 4

# The parser.PGN.read_games method uses UNTERMINATED when deciding if a PGN Tag
# found in an error sequence should start a new game.
UNTERMINATED = '<{'

# Seven Tag Roster.
TAG_EVENT = 'Event'
TAG_SITE = 'Site'
TAG_DATE = 'Date'
TAG_ROUND = 'Round'
TAG_WHITE = 'White'
TAG_BLACK = 'Black'
TAG_RESULT = 'Result'
SEVEN_TAG_ROSTER = (
    TAG_EVENT,
    TAG_SITE,
    TAG_DATE,
    TAG_ROUND,
    TAG_WHITE,
    TAG_BLACK,
    TAG_RESULT,
    )

# Default Seven Tag Roster values.
DEFAULT_TAG_VALUE = '?'
DEFAULT_TAG_DATE_VALUE = '????.??.??'
DEFAULT_TAG_RESULT_VALUE = '*'
DEFAULT_SORT_TAG_VALUE = DEFAULT_TAG_VALUE.replace('?', ' ')
DEFAULT_SORT_TAG_RESULT_VALUE = DEFAULT_TAG_RESULT_VALUE.replace('*', ' ')
SEVEN_TAG_ROSTER_DEFAULTS = {
    TAG_DATE: DEFAULT_TAG_DATE_VALUE,
    TAG_RESULT: DEFAULT_TAG_RESULT_VALUE,
    }

# FEN Tags.
TAG_FEN = 'FEN'
TAG_SETUP = 'SetUp'
SETUP_VALUE_FEN_ABSENT = '0'
SETUP_VALUE_FEN_PRESENT = '1'

# PGN constants
PGN_CAPTURE_MOVE = 'x'
PGN_PAWN = ''
PGN_KING = 'K'
PGN_QUEEN = 'Q'
PGN_ROOK = 'R'
PGN_BISHOP = 'B'
PGN_KNIGHT = 'N'
PGN_O_O = 'O-O'
PGN_O_O_O = 'O-O-O'
PGN_PROMOTION = '='
PGN_NAMED_PIECES = PGN_KING + PGN_QUEEN + PGN_ROOK + PGN_BISHOP + PGN_KNIGHT

# Maximum line length in PGN file for movetext excluding EOL ('\n') is 79.
# Some PGN Tags are allowed to exceed this.
# The rule may not be enforcable for comments, especially any re-exported,
# without disturbing any formatting attempts with EOL and spaces.
PGN_MAXIMUM_LINE_LENGTH = 79
PGN_LINE_SEPARATOR = '\n'
PGN_TOKEN_SEPARATOR = ' '
PGN_DOT = '.'

# FEN constants
FEN_FIELD_COUNT = 6
FEN_PIECE_PLACEMENT_FIELD_INDEX = 0
FEN_ACTIVE_COLOR_FIELD_INDEX = 1
FEN_CASTLING_AVAILABILITY_FIELD_INDEX = 2
FEN_EN_PASSANT_TARGET_SQUARE_FIELD_INDEX = 3
FEN_HALFMOVE_CLOCK_FIELD_INDEX = 4
FEN_FULLMOVE_NUMBER_FIELD_INDEX = 5
FEN_WHITE_ACTIVE = 'w'
FEN_BLACK_ACTIVE = 'b'
FEN_FIELD_DELIM = ' '
FEN_RANK_DELIM = '/'
FEN_NULL = '-'
FEN_WHITE_KING = 'K'
FEN_WHITE_QUEEN = 'Q'
FEN_WHITE_ROOK = 'R'
FEN_WHITE_BISHOP = 'B'
FEN_WHITE_KNIGHT = 'N'
FEN_WHITE_PAWN = 'P'
FEN_BLACK_KING = 'k'
FEN_BLACK_QUEEN = 'q'
FEN_BLACK_ROOK = 'r'
FEN_BLACK_BISHOP = 'b'
FEN_BLACK_KNIGHT = 'n'
FEN_BLACK_PAWN = 'p'

FEN_TO_PGN = {FEN_WHITE_KING: PGN_KING,
              FEN_WHITE_QUEEN: PGN_QUEEN,
              FEN_WHITE_ROOK: PGN_ROOK,
              FEN_WHITE_BISHOP: PGN_BISHOP,
              FEN_WHITE_KNIGHT: PGN_KNIGHT,
              FEN_WHITE_PAWN: PGN_PAWN,
              FEN_BLACK_KING: PGN_KING,
              FEN_BLACK_QUEEN: PGN_QUEEN,
              FEN_BLACK_ROOK: PGN_ROOK,
              FEN_BLACK_BISHOP: PGN_BISHOP,
              FEN_BLACK_KNIGHT: PGN_KNIGHT,
              FEN_BLACK_PAWN: PGN_PAWN,
              }
FEN_PAWNS = {FEN_WHITE_PAWN: FEN_WHITE_ACTIVE, FEN_BLACK_PAWN: FEN_BLACK_ACTIVE}
FEN_INITIAL_CASTLING = (
    FEN_WHITE_KING + FEN_WHITE_QUEEN + FEN_BLACK_KING + FEN_BLACK_QUEEN)

# Mapping for FEN string to piece-square names: 'Pp' missing because pawns are
# not named in moves, and 'a4' as a piece-square name means a black pawn.
FEN_WHITE_PIECES = ''.join(
    (FEN_WHITE_KING,
     FEN_WHITE_QUEEN,
     FEN_WHITE_ROOK,
     FEN_WHITE_BISHOP,
     FEN_WHITE_KNIGHT,
     FEN_WHITE_PAWN,
     ))
FEN_BLACK_PIECES = ''.join(
    (FEN_BLACK_KING,
     FEN_BLACK_QUEEN,
     FEN_BLACK_ROOK,
     FEN_BLACK_BISHOP,
     FEN_BLACK_KNIGHT,
     FEN_BLACK_PAWN,
     ))
FEN_PIECE_NAMES = FEN_WHITE_PIECES + FEN_BLACK_PIECES
FILE_NAMES = 'abcdefgh'
RANK_NAMES = '87654321'
CASTLING_RIGHTS = {
    FILE_NAMES[0] + RANK_NAMES[-1]: FEN_WHITE_QUEEN,
    FILE_NAMES[-1] + RANK_NAMES[-1]: FEN_WHITE_KING,
    FILE_NAMES[0] + RANK_NAMES[0]: FEN_BLACK_QUEEN,
    FILE_NAMES[-1] + RANK_NAMES[0]: FEN_BLACK_KING,
    FILE_NAMES[4] + RANK_NAMES[-1]: FEN_WHITE_KING + FEN_WHITE_QUEEN,
    FILE_NAMES[4] + RANK_NAMES[0]: FEN_BLACK_KING + FEN_BLACK_QUEEN,
    }
CASTLING_PIECE_FOR_SQUARE = {
    FILE_NAMES[0] + RANK_NAMES[-1]: FEN_WHITE_ROOK,
    FILE_NAMES[-1] + RANK_NAMES[-1]: FEN_WHITE_ROOK,
    FILE_NAMES[0] + RANK_NAMES[0]: FEN_BLACK_ROOK,
    FILE_NAMES[-1] + RANK_NAMES[0]: FEN_BLACK_ROOK,
    FILE_NAMES[4] + RANK_NAMES[-1]: FEN_WHITE_KING,
    FILE_NAMES[4] + RANK_NAMES[0]: FEN_BLACK_KING,
    }
CASTLING_MOVE_RIGHTS = {
    (FEN_WHITE_ACTIVE, PGN_O_O): FEN_WHITE_KING,
    (FEN_WHITE_ACTIVE, PGN_O_O_O): FEN_WHITE_QUEEN,
    (FEN_BLACK_ACTIVE, PGN_O_O): FEN_BLACK_KING,
    (FEN_BLACK_ACTIVE, PGN_O_O_O): FEN_BLACK_QUEEN,
    }

OTHER_SIDE = {FEN_WHITE_ACTIVE: FEN_BLACK_ACTIVE,
              FEN_BLACK_ACTIVE: FEN_WHITE_ACTIVE}
PIECE_TO_KING = {
    FEN_WHITE_KING: FEN_WHITE_KING,
    FEN_WHITE_QUEEN: FEN_WHITE_KING,
    FEN_WHITE_ROOK: FEN_WHITE_KING,
    FEN_WHITE_BISHOP: FEN_WHITE_KING,
    FEN_WHITE_KNIGHT: FEN_WHITE_KING,
    FEN_WHITE_PAWN: FEN_WHITE_KING,
    FEN_BLACK_KING: FEN_BLACK_KING,
    FEN_BLACK_QUEEN: FEN_BLACK_KING,
    FEN_BLACK_ROOK: FEN_BLACK_KING,
    FEN_BLACK_BISHOP: FEN_BLACK_KING,
    FEN_BLACK_KNIGHT: FEN_BLACK_KING,
    FEN_BLACK_PAWN: FEN_BLACK_KING,
    }
PROMOTED_PIECE_NAME = {
    FEN_WHITE_ACTIVE: {
        PGN_QUEEN: FEN_WHITE_QUEEN,
        PGN_ROOK: FEN_WHITE_ROOK,
        PGN_BISHOP: FEN_WHITE_BISHOP,
        PGN_KNIGHT: FEN_WHITE_KNIGHT,
        },
    FEN_BLACK_ACTIVE: {
        PGN_QUEEN: FEN_BLACK_QUEEN,
        PGN_ROOK: FEN_BLACK_ROOK,
        PGN_BISHOP: FEN_BLACK_BISHOP,
        PGN_KNIGHT: FEN_BLACK_KNIGHT,
        },
    }

files = {}
for f in FILE_NAMES:
    files[f] = {f + r for r in RANK_NAMES}
ranks = {}
for r in RANK_NAMES:
    ranks[r] = {f + r for f in FILE_NAMES}
ROOK_MOVES = {}
for f in files:
    for r in ranks:
        ROOK_MOVES[f+r] = files[f].union(ranks[r])
        ROOK_MOVES[f+r].remove(f+r)
left_to_right = []
right_to_left = []
for e in range(len(FILE_NAMES)):
    left_to_right.append(set())
    for x, y in zip(FILE_NAMES[e:], RANK_NAMES):
        left_to_right[-1].add(x + y)
    right_to_left.append(set())
    for x, y in zip(reversed(FILE_NAMES[:e+1]), RANK_NAMES[:e+2]):
        right_to_left[-1].add(x + y)
for e in range(len(RANK_NAMES) - 1):
    left_to_right.append(set())
    for x, y in zip(FILE_NAMES[:-e-1], RANK_NAMES[e+1:]):
        left_to_right[-1].add(x + y)
    right_to_left.append(set())
    for x, y in zip(reversed(FILE_NAMES[-e-1:]), RANK_NAMES[-e-1:]):
        right_to_left[-1].add(x + y)
BISHOP_MOVES = {}
for f in FILE_NAMES:
    for r in RANK_NAMES:
        sq = f + r
        for eltr, ltr in enumerate(left_to_right):
            if sq in ltr:
                for ertl, rtl in enumerate(right_to_left):
                    if sq in rtl:
                        BISHOP_MOVES[sq] = ltr.union(rtl)
                        BISHOP_MOVES[sq].remove(sq)
                        break
                break
KNIGHT_MOVES = {}
for ef, f in enumerate(FILE_NAMES):
    for er, r in enumerate(RANK_NAMES):
        sq = f + r
        KNIGHT_MOVES[sq] = set()
        for h, v in ((2, 1), (2, -1), (1, -2), (1, 2),
                     (-2, -1), (-2, 1), (-1, 2), (-1, -2)):
            h += ef
            v += er
            if h < 0 or h > 7 or v < 0 or v > 7:
                continue
            KNIGHT_MOVES[sq].add(FILE_NAMES[h] + RANK_NAMES[v])
KING_MOVES = {}
for ef, f in enumerate(FILE_NAMES):
    for er, r in enumerate(RANK_NAMES):
        sq = f + r
        KING_MOVES[sq] = set()
        for h, v in ((1, 1), (1, 0), (1, -1), (0, 1),
                     (-1, 1), (-1, 0), (-1, -1), (0, -1)):
            h += ef
            v += er
            if h < 0 or h > 7 or v < 0 or v > 7:
                continue
            KING_MOVES[sq].add(FILE_NAMES[h] + RANK_NAMES[v])
for f in files:
    files[f] = sorted(files[f])
EN_PASSANT_TARGET_SQUARES = {FEN_WHITE_ACTIVE: {}, FEN_BLACK_ACTIVE: {}}
WHITE_PAWN_MOVES = {}
for sqs in files.values():
    for e, sq in enumerate(sqs[2:]):
        WHITE_PAWN_MOVES[sq] = {sqs[e+1]}
    WHITE_PAWN_MOVES[sqs[3]].add(sqs[1])
    EN_PASSANT_TARGET_SQUARES[FEN_BLACK_ACTIVE][sqs[3], sqs[1]] = sqs[2]
BLACK_PAWN_MOVES = {}
for sqs in files.values():
    sqs = [i for i in reversed(sqs)]
    for e, sq in enumerate(sqs[2:]):
        BLACK_PAWN_MOVES[sq] = {sqs[e+1]}
    BLACK_PAWN_MOVES[sqs[3]].add(sqs[1])
    EN_PASSANT_TARGET_SQUARES[FEN_WHITE_ACTIVE][sqs[3], sqs[1]] = sqs[2]
WHITE_PAWN_CAPTURES = {}
for ef, f in enumerate(FILE_NAMES):
    for er, r in enumerate(files[f][2:]):
        WHITE_PAWN_CAPTURES[r] = set()
        if ef < 7:
            WHITE_PAWN_CAPTURES[r].add(files[FILE_NAMES[ef+1]][er+1])
        if ef > 0:
            WHITE_PAWN_CAPTURES[r].add(files[FILE_NAMES[ef-1]][er+1])
    if ef < 7:
        EN_PASSANT_TARGET_SQUARES[
            PGN_CAPTURE_MOVE.join((f, files[FILE_NAMES[ef+1]][5]))
            ] = files[FILE_NAMES[ef+1]][4]
    if ef > 0:
        EN_PASSANT_TARGET_SQUARES[
            PGN_CAPTURE_MOVE.join((f, files[FILE_NAMES[ef-1]][5]))
            ] = files[FILE_NAMES[ef-1]][4]
BLACK_PAWN_CAPTURES = {}
for ef, f in enumerate(FILE_NAMES):
    for er, r in enumerate(files[f][:-2]):
        BLACK_PAWN_CAPTURES[r] = set()
        if ef < 7:
            BLACK_PAWN_CAPTURES[r].add(files[FILE_NAMES[ef+1]][er+1])
        if ef > 0:
            BLACK_PAWN_CAPTURES[r].add(files[FILE_NAMES[ef-1]][er+1])
    if ef < 7:
        EN_PASSANT_TARGET_SQUARES[
            PGN_CAPTURE_MOVE.join((f, files[FILE_NAMES[ef+1]][-6]))
            ] = files[FILE_NAMES[ef+1]][-5]
    if ef > 0:
        EN_PASSANT_TARGET_SQUARES[
            PGN_CAPTURE_MOVE.join((f, files[FILE_NAMES[ef-1]][-6]))
            ] = files[FILE_NAMES[ef-1]][-5]
QUEEN_MOVES = {k: set() for k in ROOK_MOVES.keys()}
for k, v in QUEEN_MOVES.items():
    v.update(ROOK_MOVES[k])
    v.update(BISHOP_MOVES[k])
POINT_TO_POINT = {}
RANK_ATTACKS = {}
FILE_ATTACKS = {}

# LRD_* is diagonals parallel to 'a8-h1' (left to right down)
# RLD_* is diagonals parallel to 'a1-h8'
LRD_DIAGONAL_ATTACKS = {}
RLD_DIAGONAL_ATTACKS = {}

for k, v in files.items():
    line = tuple(v)
    for e, sq1 in enumerate(line):
        FILE_ATTACKS[sq1] = e, line
        for es, sq2 in enumerate(line[e+1:]):
            POINT_TO_POINT[sq1, sq2] = e + 1, e + 1 + es, line
            POINT_TO_POINT[sq2, sq1] = POINT_TO_POINT[sq1, sq2]
for k, v in ranks.items():
    line = tuple(sorted(v))
    for e, sq1 in enumerate(line):
        RANK_ATTACKS[sq1] = e, line
        for es, sq2 in enumerate(line[e+1:]):
            POINT_TO_POINT[sq1, sq2] = e + 1, e + 1 + es, line
            POINT_TO_POINT[sq2, sq1] = POINT_TO_POINT[sq1, sq2]
for v in left_to_right:
    line = tuple(sorted(v))
    for e, sq1 in enumerate(line):
        LRD_DIAGONAL_ATTACKS[sq1] = e, line
        for es, sq2 in enumerate(line[e+1:]):
            POINT_TO_POINT[sq1, sq2] = e + 1, e + 1 + es, line
            POINT_TO_POINT[sq2, sq1] = POINT_TO_POINT[sq1, sq2]
for v in right_to_left:
    line = tuple(sorted(v))
    for e, sq1 in enumerate(line):
        RLD_DIAGONAL_ATTACKS[sq1] = e, line
        for es, sq2 in enumerate(line[e+1:]):
            POINT_TO_POINT[sq1, sq2] = e + 1, e + 1 + es, line
            POINT_TO_POINT[sq2, sq1] = POINT_TO_POINT[sq1, sq2]

# For testing moves in PGN.
SOURCE_SQUARES = {
    PGN_KING: KING_MOVES,
    PGN_QUEEN: QUEEN_MOVES,
    PGN_ROOK: ROOK_MOVES,
    PGN_BISHOP: BISHOP_MOVES,
    PGN_KNIGHT: KNIGHT_MOVES,
    FEN_WHITE_PAWN: WHITE_PAWN_MOVES,
    FEN_BLACK_PAWN: BLACK_PAWN_MOVES,
    FEN_WHITE_PAWN + PGN_CAPTURE_MOVE: WHITE_PAWN_CAPTURES,
    FEN_BLACK_PAWN + PGN_CAPTURE_MOVE: BLACK_PAWN_CAPTURES,
    }

# For testing if a square is attacked by a piece.
FEN_SOURCE_SQUARES = {
    FEN_WHITE_KING: KING_MOVES,
    FEN_WHITE_QUEEN: QUEEN_MOVES,
    FEN_WHITE_ROOK: ROOK_MOVES,
    FEN_WHITE_BISHOP: BISHOP_MOVES,
    FEN_WHITE_KNIGHT: KNIGHT_MOVES,
    FEN_WHITE_PAWN: WHITE_PAWN_CAPTURES,
    FEN_BLACK_KING: KING_MOVES,
    FEN_BLACK_QUEEN: QUEEN_MOVES,
    FEN_BLACK_ROOK: ROOK_MOVES,
    FEN_BLACK_BISHOP: BISHOP_MOVES,
    FEN_BLACK_KNIGHT: KNIGHT_MOVES,
    FEN_BLACK_PAWN: BLACK_PAWN_CAPTURES,
    }

del e, ef, eltr, er, ertl, es, f, files, h, k, left_to_right, ltr, r, ranks
del right_to_left, rtl, sq, sq1, sq2, sqs, v, x, y, line
