# constants.py
# Copyright 2010, 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Constants for Portable Game Notation (PGN) parser.

The defined constants are used when parsing PGN and FEN text, and when checking
the PGN game score represents a legal sequence of moves and variations.

"""

# PGN Tag Pair without capturing name and value.
PGN_TAG = r'\[[^"]*"(?:[^\\"]*(?:\\.[^\\"]*)*)"[^\]]*\]'
# Initial backstep from end of buffer when searching for PGN Tag Pair.
BACK_STEP = 1000
# The non-movetext elements: for detecting games without testing moves.
TAG_PAIR = r"".join(
    (
        r"(?#Start Tag)\[\s*",
        r"(?#Tag Name)([A-Za-z0-9_]+)\s*",
        r'(?#Tag Value)"((?:[^\\"\t\r\f\v\n]*',
        r'(?:\\[^\t\r\f\v\n][^\\"\t\r\f\v\n]*)*))"\s*',
        r"(?#End Tag)(\])",
    )
)
GAME_TERMINATION = r"(?#Game termination)(1-0|1/2-1/2|0-1|\*)"
MOVE_NUMBER = r"(?#Move number)([1-9][0-9]*)"
DOTS = r"(?#Dots)(\.+)"
START_RAV = r"(?#Start RAV)(\()"
END_RAV = r"(?#End RAV)(\))"
# Allow for "$11/2-1/2" and similar meaning "$1" then "1/2-1/2" with maximum
# three digits like "$123" in NAG.
NAG = r"".join(
    (
        r"(?#Numeric Annotation Glyph)",
        r"(\$",
        r"(?:",
        r"(?:[1-9][0-9](?:(?=[01][-/])|[0-9]))",
        r"|(?:[1-9](?:(?=[01][-/])|[0-9]))|",
        r"(?:[1-9])",
        r")",
        r")",
    )
)
EOL_COMMENT = r"(?#EOL comment)(;(?:[^\n]*))(?=\n)"
COMMENT = r"(?#Comment)(\{[^}]*\})"
RESERVED = r"(?#Reserved)(<[^>]*>)"
ESCAPED = r"(?#Escaped)(\A%[^\n]*|\n%[^\n]*)(?=\n)"
PASS = r"(?#Pass)(--|Z0)"
CHECK = r"(?#Check indicators)(?<=[1-8QRBNO])([+#])"
TRADITIONAL = r"(?#Traditional Annonations)(?<=[1-8QRBNO+#])([!?][!?]?)"
BAD_COMMENT = r"(?#Bad Comment)(\{[^}]*)"
BAD_RESERVED = r"(?#Bad Reserved)(<[^>]*)"
TAG_PAIR_DATA_ERROR = r"".join(
    (r'(?#Bad Tag)(\[[^"]*"(?:.*?|', r'[^\\"]*(?:\\.[^\\"]*)*)"\s*\])')
)
END_OF_FILE_MARKER = r'(?#End of file marker)(\032)(?=\[[^"]*".*?"\s*\])'
TEXT = r"\S+[ \t\r\f\v]*"
TAG_PAIR_FORMAT = r"|".join(
    (
        TAG_PAIR,
        GAME_TERMINATION,
        EOL_COMMENT,
        COMMENT,
        RESERVED,
        ESCAPED,
        BAD_COMMENT,
        BAD_RESERVED,
        TAG_PAIR_DATA_ERROR,
        END_OF_FILE_MARKER,
        r"(?#Text)([^[;{<10*\n]+)",  # '\n' to catch '\n;'.
    )
).join(
    (
        r"(?:\s*)(?:",
        r")",
    )
)
GAME_FORMAT = r"|".join(
    (
        TAG_PAIR,
        r"(?#Move symbols)([KQRBN](?:[a-h1-8]?x?)?[a-h][1-8]",
        r"[a-h](?:x[a-h])?[1-8](?:=[QRBN])?",
        r"O-O-O|O-O|x[a-h][1-8])",
        GAME_TERMINATION,
        MOVE_NUMBER,
        DOTS,
        EOL_COMMENT,
        COMMENT,
        START_RAV,
        END_RAV,
        NAG,
        RESERVED,
        ESCAPED,
        PASS,
        CHECK,
        TRADITIONAL,
        BAD_COMMENT,
        BAD_RESERVED,
        TAG_PAIR_DATA_ERROR,
        END_OF_FILE_MARKER,
        TEXT.join((r"(?#Text)(", r")")),
    )
).join(
    (
        r"(?:\s*)(?:",
        r")",
    )
)

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
PGN_FORMAT = r"|".join(
    (
        TAG_PAIR,
        r"(?:(?#Moves)(?#Piece)([KQRBN])([a-h1-8]?)(x?)([a-h][1-8])",
        r"(?#Pawn)(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])(?:=([QRBN]))))",
        r"(?#Castle)(O-O-O|O-O)(?#sevoM))",
        GAME_TERMINATION,
        MOVE_NUMBER,
        DOTS,
        EOL_COMMENT,
        COMMENT,
        START_RAV,
        END_RAV,
        NAG,
        RESERVED,
        ESCAPED,
        PASS,
        CHECK,
        TRADITIONAL,
        BAD_COMMENT,
        BAD_RESERVED,
        TAG_PAIR_DATA_ERROR,
        END_OF_FILE_MARKER,
    )
)
PGN_DISAMBIGUATION = r"".join(
    (
        r"(?#Disambiguation PGN)",
        r"([x-]?[a-h][1-8]",
    )
)
TEXT_DISAMBIGUATION = r"".join(
    (
        r"(?#Disambiguation Text)",
        r"((?:-|x[QRBN]?)?[a-h][1-8]",
    )
)
IGNORE_CASE_DISAMBIGUATION = r"".join(
    (
        r"(?#Disambiguation Text)",
        r"((?:(?:-|[xX][QRBNqrbn]?)?[a-hA-H][1-8](?:=[QRBNqrbn])?)|",
        r"(?:b[xX][QRBNqrbn]?[a-hA-H][18])|",
        r"(?#Promotion)",
        r"=[QRBNqrbn]",
    )
)
ANYTHING_ELSE = TEXT.join((r"(?#Anything else)", r")"))
IMPORT_FORMAT = r"|".join((PGN_FORMAT, PGN_DISAMBIGUATION, ANYTHING_ELSE))
TEXT_FORMAT = (
    r"|".join((PGN_FORMAT, TEXT_DISAMBIGUATION, ANYTHING_ELSE))
    .replace(r"O-O-O|O-O", r"O-O-O|O-O|0-0-0|0-0")
    .replace(r"(?:=([QRBN])", r"(?:=?([QRBN])")
    .replace(r"8QRBNO", r"8QRBNO0")
    .replace(r"?:x", r"?:(?:[2-7][-x]|x)")
    .replace(r"x?", r"[-x]?")
)

# Assume 'B' means bishop unless followed by '[1-8]', and 'b' means bishop
# unless followed by '[1-8xX]'.  There are positions where both a bishop and
# a pawn on the b-file can capture on a square on the 'a' and 'c' files: upper
# or lower case is the only practical way to decide (the following moves may
# be legal after either bishop or pawn capture).  It is almost certain a SAN
# sequence like 'B8d5' will not be used in games to distinguish between two
# bishops able to move to 'd5'.
# The FIDE notation for pawn promotion is not supported when ignoring case
# because the sequence 'bxc8q' is ambiguous, in upper or lower case, until
# after the position has been examined.
IGNORE_CASE_FORMAT = (
    r"|".join((PGN_FORMAT, IGNORE_CASE_DISAMBIGUATION, ANYTHING_ELSE))
    .replace(r"QRBNO", r"QRBNOqrbno0")
    .replace(r"[KQRBN]", r"[KQRNkqrn]|B(?![1-8])|b(?![1-8xX])")
    .replace(r"O-O-O|O-O", r"[Oo0]-[Oo0]-[Oo0]|[Oo0]-[Oo0]")
    .replace(r"[a-h][1-8]", r"[a-hA-H][1-8]")
    .replace(r"[a-h1-8]", r"[a-hA-H1-8]")
    .replace(r"[a-h]", r"[a-hA-H]")
    .replace(r"(x?)", r"([xX]?)")
    .replace(r"?:x", r"?:(?:[2-7][-xX]|[xX])")
    .replace(r"[QRBN]", r"[QRBNqrbn]")
)

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
IFG_CHECK_INDICATOR = 25
IFG_TRADITIONAL_ANNOTATION = 26
IFG_BAD_COMMENT = 27
IFG_BAD_RESERVED = 28
IFG_BAD_TAG = 29
IFG_END_OF_FILE_MARKER = 30
IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE = 31

# For spotting the pawn-move-like string which is the destination of a fully
# disambiguated piece move, say 'Qb4d4+??' including optional sufficies, where
# Qb4 has been rejected as a move because there is a Q on b4.
DISAMBIGUATE_TEXT = r"\A([x-]?)([a-h][1-8])"
DISAMBIGUATE_PGN = r"\A[x-]?[a-h][1-8]"

# The game.GameIgnoreCasePGN class may need to ignore '=Q', and similar, if,
# for example, it were processed by peek ahead to decide between a pawn and
# bishop move for 'bxc8'.
DISAMBIGUATE_PROMOTION = r"\A=[QRBNqrbn]"

# Indicies of captured groups for fully disambiguated piece move.
DG_CAPTURE = 1
DG_DESTINATION = 2

# For spotting the second part, of two, of a movetext token in long algebraic
# format (LAN).  The first part, such as 'Qe2', will have been found by the
# IMPORT_FORMAT rules.  LAN_FORMAT is similar to DISAMBIGUATE_TEXT.
LAN_FORMAT = r"(?#Lower case)\A([-x]?)([a-h][1-8])(?:=([qrbn]))?"
LAN_MOVE_SEPARATOR = "-"

# Indicies of captured groups for long algebraic notation move.
LAN_CAPTURE_OR_MOVE = 1
LAN_DESTINATION = 2
LAN_PROMOTE_PIECE = 3

# For normalising a text promotion move to PGN.
TEXT_PROMOTION = r"(?#Lower case)([a-h](?:[x-][a-h])?[18]=?)([qrbn])"

# Indicies of captured groups for normalising promotion move to PGN.
TP_MOVE = 1
TP_PROMOTE_TO_PIECE = 2

# Indicies of captured groups in PGN ignoring movetext, for counting games
# and extracting Tag Pairs but not moves.
TPF_TAG_NAME = 1
TPF_TAG_VALUE = 2
TPF_END_TAG = 3
TPF_GAME_TERMINATION = 4
TPF_COMMENT_TO_EOL = 5
TPF_COMMENT = 6
TPF_RESERVED = 7
TPF_ESCAPE = 8
TPF_BAD_COMMENT = 9
TPF_BAD_RESERVED = 10
TPF_BAD_TAG = 11
TPF_END_OF_FILE_MARKER = 12
TPF_OTHER_WITH_NON_NEWLINE_WHITESPACE = 13

# Indicies of captured groups in PGN for estimating number of moves in games.
CGM_TAG_NAME = 1
CGM_TAG_VALUE = 2
CGM_END_TAG = 3
CGM_MOVE_SYMBOLS = 4
CGM_GAME_TERMINATION = 5
CGM_MOVE_NUMBER = 6
CGM_DOTS = 7
CGM_COMMENT_TO_EOL = 8
CGM_COMMENT = 9
CGM_START_RAV = 10
CGM_END_RAV = 11
CGM_NUMERIC_ANNOTATION_GLYPH = 12
CGM_RESERVED = 13
CGM_ESCAPE = 14
CGM_PASS = 15
CGM_CHECK_INDICATOR = 16
CGM_TRADITIONAL_ANNOTATION = 17
CGM_BAD_COMMENT = 18
CGM_BAD_RESERVED = 19
CGM_BAD_TAG = 20
CGM_END_OF_FILE_MARKER = 21
CGM_OTHER_WITH_NON_NEWLINE_WHITESPACE = 22

# A number of character sequences in PGN text which has space separators
# removed imply fully disambiguated moves may be present.  This matters in
# the GAME_FORMAT pattern which treats the destination square of fully
# disambiguated movetext as a pawn move, without the recovery options
# possible in the patterns based on PGN_FORMAT.
# If the PGN text is known to represent playable moves processing based on
# GAME_FORMAT without tracking piece locations is much quicker than based
# on PGN_FORMAT with piece location tracking.
# This pattern allows the existence of necessary fully disambiguated moves
# to be ruled out.  Full disambiguation is not necessary if a position has
# less than 3 queens, bishops, or knights, of the same side.
FULL_DISAMBIGUATION_ALLOWED = r'(?s:([18]=[QB]).*\1|[18]=N|\[\s*FEN\s*")'

# For spotting rejected possible SAN b-pawn move tokens which may be first
# part of bishop move, ignoring case if necessary.
# The token is assumed to not represent a pawn move.
PAWN_MOVE_TOKEN_POSSIBLE_BISHOP = r"\A[Bb][1-8]\Z"

# The parser.PGN.read_games method uses UNTERMINATED when deciding if a PGN Tag
# found in an error sequence should start a new game.
UNTERMINATED = "<{"

# Traditional annotations are mapped to Numeric Annotation Glyphs (NAG).
# About 100 NAGs are defined in the PGN standard.
SUFFIX_ANNOTATION_TO_NAG = {
    "!!": "$3",
    "!?": "$5",
    "!": "$1",
    "??": "$4",
    "?!": "$6",
    "?": "$2",
}

# Seven Tag Roster.
TAG_EVENT = "Event"
TAG_SITE = "Site"
TAG_DATE = "Date"
TAG_ROUND = "Round"
TAG_WHITE = "White"
TAG_BLACK = "Black"
TAG_RESULT = "Result"
# The item list in SEVEN_TAG_ROSTER is long enough to cause a pylint
# duplicate-code report citing pgn_read.core.game module.
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
DEFAULT_TAG_VALUE = "?"
DEFAULT_TAG_DATE_VALUE = "????.??.??"
DEFAULT_TAG_RESULT_VALUE = "*"
DEFAULT_SORT_TAG_VALUE = DEFAULT_TAG_VALUE.replace("?", " ")
DEFAULT_SORT_TAG_RESULT_VALUE = DEFAULT_TAG_RESULT_VALUE.replace("*", " ")
SEVEN_TAG_ROSTER_DEFAULTS = {
    TAG_DATE: DEFAULT_TAG_DATE_VALUE,
    TAG_RESULT: DEFAULT_TAG_RESULT_VALUE,
}

# Supplemental tags with defined default values.
# Other supplmental tags exist; the ones defined here have a default value.
TAG_WHITETITLE = "WhiteTitle"
TAG_BLACKTITLE = "BlackTitle"
TAG_WHITEELO = "WhiteElo"
TAG_BLACKELO = "BlackElo"
TAG_WHITENA = "WhiteNA"
TAG_BLACKNA = "BlackNA"
SUPPLEMENTAL_TAG_ROSTER = (
    TAG_WHITETITLE,
    TAG_BLACKTITLE,
    TAG_WHITEELO,
    TAG_BLACKELO,
    TAG_WHITENA,
    TAG_BLACKNA,
)
DEFAULT_SUPPLEMENTAL_TAG_VALUE = "-"

# FEN Tags.
TAG_FEN = "FEN"
TAG_SETUP = "SetUp"
SETUP_VALUE_FEN_ABSENT = "0"
SETUP_VALUE_FEN_PRESENT = "1"

# PGN constants
PGN_CAPTURE_MOVE = "x"
PGN_PAWN = ""
PGN_KING = "K"
PGN_QUEEN = "Q"
PGN_ROOK = "R"
PGN_BISHOP = "B"
PGN_KNIGHT = "N"
PGN_O_O = "O-O"
PGN_O_O_O = "O-O-O"
PGN_PROMOTION = "="
PGN_NAMED_PIECES = PGN_KING + PGN_QUEEN + PGN_ROOK + PGN_BISHOP + PGN_KNIGHT

# Maximum line length in PGN file for movetext excluding EOL ('\n') is 79.
# Some PGN Tags are allowed to exceed this.
# The rule may not be enforcable for comments, especially any re-exported,
# without disturbing any formatting attempts with EOL and spaces.
PGN_MAXIMUM_LINE_LENGTH = 79
PGN_LINE_SEPARATOR = "\n"
PGN_TOKEN_SEPARATOR = " "
PGN_DOT = "."

# FEN constants
FEN_FIELD_COUNT = 6
FEN_PIECE_PLACEMENT_FIELD_INDEX = 0
FEN_ACTIVE_COLOR_FIELD_INDEX = 1
FEN_CASTLING_AVAILABILITY_FIELD_INDEX = 2
FEN_EN_PASSANT_TARGET_SQUARE_FIELD_INDEX = 3
FEN_HALFMOVE_CLOCK_FIELD_INDEX = 4
FEN_FULLMOVE_NUMBER_FIELD_INDEX = 5
FEN_WHITE_ACTIVE = "w"
FEN_BLACK_ACTIVE = "b"
FEN_FIELD_DELIM = " "
FEN_RANK_DELIM = "/"
FEN_NULL = "-"
FEN_WHITE_KING = "K"
FEN_WHITE_QUEEN = "Q"
FEN_WHITE_ROOK = "R"
FEN_WHITE_BISHOP = "B"
FEN_WHITE_KNIGHT = "N"
FEN_WHITE_PAWN = "P"
FEN_BLACK_KING = "k"
FEN_BLACK_QUEEN = "q"
FEN_BLACK_ROOK = "r"
FEN_BLACK_BISHOP = "b"
FEN_BLACK_KNIGHT = "n"
FEN_BLACK_PAWN = "p"

FEN_TO_PGN = {
    FEN_WHITE_KING: PGN_KING,
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
FEN_PAWNS = {
    FEN_WHITE_PAWN: FEN_WHITE_ACTIVE,
    FEN_BLACK_PAWN: FEN_BLACK_ACTIVE,
}
FEN_INITIAL_CASTLING = (
    FEN_WHITE_KING + FEN_WHITE_QUEEN + FEN_BLACK_KING + FEN_BLACK_QUEEN
)

# Mapping for FEN string to piece-square names: 'Pp' missing because pawns are
# not named in moves, and 'a4' as a piece-square name means a black pawn.
# The item lists in FEN_WHITE_PIECES and FEN_BLACK_PIECES are long enough to
# cause pylint duplicate-code reports citing pgn_read.core.game module.
FEN_WHITE_PIECES = "".join(
    (
        FEN_WHITE_KING,
        FEN_WHITE_QUEEN,
        FEN_WHITE_ROOK,
        FEN_WHITE_BISHOP,
        FEN_WHITE_KNIGHT,
        FEN_WHITE_PAWN,
    )
)
FEN_BLACK_PIECES = "".join(
    (
        FEN_BLACK_KING,
        FEN_BLACK_QUEEN,
        FEN_BLACK_ROOK,
        FEN_BLACK_BISHOP,
        FEN_BLACK_KNIGHT,
        FEN_BLACK_PAWN,
    )
)
FEN_PIECE_NAMES = FEN_WHITE_PIECES + FEN_BLACK_PIECES
FILE_NAMES = "abcdefgh"
RANK_NAMES = "87654321"
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

OTHER_SIDE = {
    FEN_WHITE_ACTIVE: FEN_BLACK_ACTIVE,
    FEN_BLACK_ACTIVE: FEN_WHITE_ACTIVE,
}
SIDE_TO_MOVE_KING = {
    FEN_WHITE_ACTIVE: FEN_WHITE_KING,
    FEN_BLACK_ACTIVE: FEN_BLACK_KING,
}
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
