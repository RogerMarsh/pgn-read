# test_constants.py
# Copyright 2012, 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""constants tests"""

import unittest
import re

from .. import constants


class Constants(unittest.TestCase):
    def test_01_values(self):
        ae = self.assertEqual
        ae(
            constants.PGN_TAG,
            r'\[[^"]*"(?:[^\\"]*(?:\\.[^\\"]*)*)"[^\]]*\]',
        )
        ae(constants.BACK_STEP, 1000)
        ae(
            constants.TAG_PAIR,
            r"".join(
                (
                    r"(?#Start Tag)\[\s*",
                    r"(?#Tag Name)([A-Za-z0-9_]+)\s*",
                    r'(?#Tag Value)"((?:[^\\"\t\r\f\v\n]*',
                    r'(?:\\[^\t\r\f\v\n][^\\"\t\r\f\v\n]*)*))"\s*',
                    r"(?#End Tag)(\])",
                )
            ),
        )
        ae(
            constants.GAME_TERMINATION,
            r"(?#Game termination)(1-0|1/2-1/2|0-1|\*)",
        )
        ae(constants.MOVE_NUMBER, r"(?#Move number)([1-9][0-9]*)")
        ae(constants.EOL_COMMENT, r"(?#EOL comment)(;(?:[^\n]*))(?=\n)")
        ae(constants.DOTS, r"(?#Dots)(\.+)")
        ae(constants.COMMENT, r"(?#Comment)(\{[^}]*\})")
        ae(constants.START_RAV, r"(?#Start RAV)(\()")
        ae(constants.END_RAV, r"(?#End RAV)(\))")
        ae(
            constants.NAG,
            r"".join(
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
            ),
        )
        ae(constants.RESERVED, r"(?#Reserved)(<[^>]*>)")
        ae(constants.ESCAPED, r"(?#Escaped)(\A%[^\n]*|\n%[^\n]*)(?=\n)")
        ae(constants.PASS, r"(?#Pass)(--|Z0)")
        ae(constants.CHECK, r"(?#Check indicators)(?<=[1-8QRBNO])([+#])")
        ae(
            constants.TRADITIONAL,
            r"(?#Traditional Annonations)(?<=[1-8QRBNO+#])([!?][!?]?)",
        )
        ae(constants.BAD_COMMENT, r"(?#Bad Comment)(\{[^}]*)")
        ae(constants.BAD_RESERVED, r"(?#Bad Reserved)(<[^>]*)")
        ae(
            constants.TAG_PAIR_DATA_ERROR,
            r'(?#Bad Tag)(\[[^"]*"(?:.*?|[^\\"]*(?:\\.[^\\"]*)*)"\s*\])',
        )
        ae(
            constants.END_OF_FILE_MARKER,
            r'(?#End of file marker)(\032)(?=\[[^"]*".*?"\s*\])',
        )
        ae(constants.TEXT, r"\S+[ \t\r\f\v]*")
        ae(
            constants.TAG_PAIR_FORMAT,
            r"".join(
                (
                    r"(?:\s*)(?:",
                    r"(?#Start Tag)\[\s*",
                    r"(?#Tag Name)([A-Za-z0-9_]+)\s*",
                    r'(?#Tag Value)"((?:[^\\"\t\r\f\v\n]*',
                    r'(?:\\[^\t\r\f\v\n][^\\"\t\r\f\v\n]*)*))"\s*',
                    r"(?#End Tag)(\])",
                    r"|",
                    r"(?#Game termination)(1-0|1/2-1/2|0-1|\*)",
                    r"|",
                    r"(?#EOL comment)(;(?:[^\n]*))(?=\n)",
                    r"|",
                    r"(?#Comment)(\{[^}]*\})",
                    r"|",
                    r"(?#Reserved)(<[^>]*>)",
                    r"|",
                    r"(?#Escaped)(\A%[^\n]*|\n%[^\n]*)(?=\n)",
                    r"|",
                    r"(?#Bad Comment)(\{[^}]*)",
                    r"|",
                    r"(?#Bad Reserved)(<[^>]*)",
                    r"|",
                    r'(?#Bad Tag)(\[[^"]*"(?:.*?',
                    r"|",
                    r'[^\\"]*(?:\\.[^\\"]*)*)"\s*\])',
                    r"|",
                    r'(?#End of file marker)(\032)(?=\[[^"]*".*?"\s*\])',
                    r"|",
                    r"(?#Text)([^[;{<10*\n]+)",
                    r")",
                )
            ),
        )
        ae(
            constants.GAME_FORMAT,
            r"".join(
                (
                    r"(?:\s*)(?:",
                    r"(?#Start Tag)\[\s*",
                    r"(?#Tag Name)([A-Za-z0-9_]+)\s*",
                    r'(?#Tag Value)"((?:[^\\"\t\r\f\v\n]*',
                    r'(?:\\[^\t\r\f\v\n][^\\"\t\r\f\v\n]*)*))"\s*',
                    r"(?#End Tag)(\])",
                    r"|",
                    r"(?#Move symbols)([KQRBN](?:[a-h1-8]?x?)?[a-h][1-8]",
                    r"|",
                    r"[a-h](?:x[a-h])?[1-8](?:=[QRBN])?",
                    r"|",
                    r"O-O-O|O-O|x[a-h][1-8])",
                    r"|",
                    r"(?#Game termination)(1-0|1/2-1/2|0-1|\*)",
                    r"|",
                    r"(?#Move number)([1-9][0-9]*)",
                    r"|",
                    r"(?#Dots)(\.+)",
                    r"|",
                    r"(?#EOL comment)(;(?:[^\n]*))(?=\n)",
                    r"|",
                    r"(?#Comment)(\{[^}]*\})",
                    r"|",
                    r"(?#Start RAV)(\()",
                    r"|",
                    r"(?#End RAV)(\))",
                    r"|",
                    r"(?#Numeric Annotation Glyph)",
                    r"(\$",
                    r"(?:",
                    r"(?:[1-9][0-9](?:(?=[01][-/])|[0-9]))",
                    r"|(?:[1-9](?:(?=[01][-/])|[0-9]))|",
                    r"(?:[1-9])",
                    r")",
                    r")",
                    r"|",
                    r"(?#Reserved)(<[^>]*>)",
                    r"|",
                    r"(?#Escaped)(\A%[^\n]*|\n%[^\n]*)(?=\n)",
                    r"|",
                    r"(?#Pass)(--|Z0)",
                    r"|",
                    r"(?#Check indicators)(?<=[1-8QRBNO])([+#])",
                    r"|",
                    r"(?#Traditional Annonations)",
                    r"(?<=[1-8QRBNO+#])([!?][!?]?)",
                    r"|",
                    r"(?#Bad Comment)(\{[^}]*)",
                    r"|",
                    r"(?#Bad Reserved)(<[^>]*)",
                    r"|",
                    r'(?#Bad Tag)(\[[^"]*"(?:.*?',
                    r"|",
                    r'[^\\"]*(?:\\.[^\\"]*)*)"\s*\])',
                    r"|",
                    r'(?#End of file marker)(\032)(?=\[[^"]*".*?"\s*\])',
                    r"|",
                    r"(?#Text)(\S+[ \t\r\f\v]*)",
                    r")",
                )
            ),
        )
        ae(
            constants.PGN_FORMAT,
            r"".join(
                (
                    r"(?#Start Tag)\[\s*",
                    r"(?#Tag Name)([A-Za-z0-9_]+)\s*",
                    r'(?#Tag Value)"((?:[^\\"\t\r\f\v\n]*',
                    r'(?:\\[^\t\r\f\v\n][^\\"\t\r\f\v\n]*)*))"\s*',
                    r"(?#End Tag)(\])",
                    r"|",
                    r"(?:(?#Moves)",
                    r"(?#Piece)([KQRBN])([a-h1-8]?)(x?)([a-h][1-8])",
                    r"|",
                    r"(?#Pawn)(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])",
                    r"(?:=([QRBN]))))",
                    r"|",
                    r"(?#Castle)(O-O-O|O-O)",
                    r"(?#sevoM))",
                    r"|",
                    r"(?#Game termination)(1-0|1/2-1/2|0-1|\*)",
                    r"|",
                    r"(?#Move number)([1-9][0-9]*)",
                    r"|",
                    r"(?#Dots)(\.+)",
                    r"|",
                    r"(?#EOL comment)(;(?:[^\n]*))(?=\n)",
                    r"|",
                    r"(?#Comment)(\{[^}]*\})",
                    r"|",
                    r"(?#Start RAV)(\()",
                    r"|",
                    r"(?#End RAV)(\))",
                    r"|",
                    r"(?#Numeric Annotation Glyph)",
                    r"(\$",
                    r"(?:",
                    r"(?:[1-9][0-9](?:(?=[01][-/])|[0-9]))",
                    r"|(?:[1-9](?:(?=[01][-/])|[0-9]))|",
                    r"(?:[1-9])",
                    r")",
                    r")",
                    r"|",
                    r"(?#Reserved)(<[^>]*>)",
                    r"|",
                    r"(?#Escaped)(\A%[^\n]*|\n%[^\n]*)(?=\n)",
                    r"|",
                    r"(?#Pass)(--|Z0)",
                    r"|",
                    r"(?#Check indicators)(?<=[1-8QRBNO])([+#])",
                    r"|",
                    r"(?#Traditional Annonations)",
                    r"(?<=[1-8QRBNO+#])([!?][!?]?)",
                    r"|",
                    r"(?#Bad Comment)(\{[^}]*)",
                    r"|",
                    r"(?#Bad Reserved)(<[^>]*)",
                    r"|",
                    r'(?#Bad Tag)(\[[^"]*"(?:.*?',
                    r"|",
                    r'[^\\"]*(?:\\.[^\\"]*)*)"\s*\])',
                    r"|",
                    r'(?#End of file marker)(\032)(?=\[[^"]*".*?"\s*\])',
                )
            ),
        )
        ae(
            constants.PGN_DISAMBIGUATION,
            r"".join((r"(?#Disambiguation PGN)([x-]?[a-h][1-8]",)),
        )
        ae(
            constants.TEXT_DISAMBIGUATION,
            r"".join((r"(?#Disambiguation Text)((?:-|x[QRBN]?)?[a-h][1-8]",)),
        )
        ae(
            constants.IGNORE_CASE_DISAMBIGUATION,
            r"".join(
                (
                    r"(?#Disambiguation Text)",
                    r"((?:(?:-|[xX][QRBNqrbn]?)?[a-hA-H][1-8]",
                    r"(?:=[QRBNqrbn])?)",
                    r"|",
                    r"(?:b[xX][QRBNqrbn]?[a-hA-H][18])",
                    r"|",
                    r"(?#Promotion)=[QRBNqrbn]",
                )
            ),
        )
        ae(
            constants.ANYTHING_ELSE,
            r"".join((r"(?#Anything else)\S+[ \t\r\f\v]*)",)),
        )
        ae(
            constants.IMPORT_FORMAT,
            r"".join(
                (
                    r"(?#Start Tag)\[\s*",
                    r"(?#Tag Name)([A-Za-z0-9_]+)\s*",
                    r'(?#Tag Value)"((?:[^\\"\t\r\f\v\n]*',
                    r'(?:\\[^\t\r\f\v\n][^\\"\t\r\f\v\n]*)*))"\s*',
                    r"(?#End Tag)(\])",
                    r"|",
                    r"(?:(?#Moves)",
                    r"(?#Piece)([KQRBN])([a-h1-8]?)(x?)([a-h][1-8])",
                    r"|",
                    r"(?#Pawn)(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])",
                    r"(?:=([QRBN]))))",
                    r"|",
                    r"(?#Castle)(O-O-O|O-O)",
                    r"(?#sevoM))",
                    r"|",
                    r"(?#Game termination)(1-0|1/2-1/2|0-1|\*)",
                    r"|",
                    r"(?#Move number)([1-9][0-9]*)",
                    r"|",
                    r"(?#Dots)(\.+)",
                    r"|",
                    r"(?#EOL comment)(;(?:[^\n]*))(?=\n)",
                    r"|",
                    r"(?#Comment)(\{[^}]*\})",
                    r"|",
                    r"(?#Start RAV)(\()",
                    r"|",
                    r"(?#End RAV)(\))",
                    r"|",
                    r"(?#Numeric Annotation Glyph)",
                    r"(\$",
                    r"(?:",
                    r"(?:[1-9][0-9](?:(?=[01][-/])|[0-9]))",
                    r"|(?:[1-9](?:(?=[01][-/])|[0-9]))|",
                    r"(?:[1-9])",
                    r")",
                    r")",
                    r"|",
                    r"(?#Reserved)(<[^>]*>)",
                    r"|",
                    r"(?#Escaped)(\A%[^\n]*|\n%[^\n]*)(?=\n)",
                    r"|",
                    r"(?#Pass)(--|Z0)",
                    r"|",
                    r"(?#Check indicators)(?<=[1-8QRBNO])([+#])",
                    r"|",
                    r"(?#Traditional Annonations)",
                    r"(?<=[1-8QRBNO+#])([!?][!?]?)",
                    r"|",
                    r"(?#Bad Comment)(\{[^}]*)",
                    r"|",
                    r"(?#Bad Reserved)(<[^>]*)",
                    r"|",
                    r'(?#Bad Tag)(\[[^"]*"(?:.*?',
                    r"|",
                    r'[^\\"]*(?:\\.[^\\"]*)*)"\s*\])',
                    r"|",
                    r'(?#End of file marker)(\032)(?=\[[^"]*".*?"\s*\])',
                    r"|",
                    r"(?#Disambiguation PGN)([x-]?[a-h][1-8]",
                    r"|",
                    r"(?#Anything else)\S+[ \t\r\f\v]*)",
                )
            ),
        )
        ae(
            constants.TEXT_FORMAT,
            r"".join(
                (
                    r"(?#Start Tag)\[\s*",
                    r"(?#Tag Name)([A-Za-z0-9_]+)\s*",
                    r'(?#Tag Value)"((?:[^\\"\t\r\f\v\n]*',
                    r'(?:\\[^\t\r\f\v\n][^\\"\t\r\f\v\n]*)*))"\s*',
                    r"(?#End Tag)(\])",
                    r"|",
                    r"(?:(?#Moves)",
                    r"(?#Piece)([KQRBN])([a-h1-8]?)([-x]?)([a-h][1-8])",
                    r"|",
                    r"(?#Pawn)(?:([a-h])(?:(?:[2-7][-x]|x)([a-h]))?",
                    r"(?:([2-7])|([18])",
                    r"(?:=?([QRBN]))))",
                    r"|",
                    r"(?#Castle)(O-O-O|O-O|0-0-0|0-0)",
                    r"(?#sevoM))",
                    r"|",
                    r"(?#Game termination)(1-0|1/2-1/2|0-1|\*)",
                    r"|",
                    r"(?#Move number)([1-9][0-9]*)",
                    r"|",
                    r"(?#Dots)(\.+)",
                    r"|",
                    r"(?#EOL comment)(;(?:[^\n]*))(?=\n)",
                    r"|",
                    r"(?#Comment)(\{[^}]*\})",
                    r"|",
                    r"(?#Start RAV)(\()",
                    r"|",
                    r"(?#End RAV)(\))",
                    r"|",
                    r"(?#Numeric Annotation Glyph)",
                    r"(\$",
                    r"(?:",
                    r"(?:[1-9][0-9](?:(?=[01][-/])|[0-9]))",
                    r"|(?:[1-9](?:(?=[01][-/])|[0-9]))|",
                    r"(?:[1-9])",
                    r")",
                    r")",
                    r"|",
                    r"(?#Reserved)(<[^>]*>)",
                    r"|",
                    r"(?#Escaped)(\A%[^\n]*|\n%[^\n]*)(?=\n)",
                    r"|",
                    r"(?#Pass)(--|Z0)",
                    r"|",
                    r"(?#Check indicators)(?<=[1-8QRBNO0])([+#])",
                    r"|",
                    r"(?#Traditional Annonations)",
                    r"(?<=[1-8QRBNO0+#])([!?][!?]?)",
                    r"|",
                    r"(?#Bad Comment)(\{[^}]*)",
                    r"|",
                    r"(?#Bad Reserved)(<[^>]*)",
                    r"|",
                    r'(?#Bad Tag)(\[[^"]*"(?:.*?',
                    r"|",
                    r'[^\\"]*(?:\\.[^\\"]*)*)"\s*\])',
                    r"|",
                    r'(?#End of file marker)(\032)(?=\[[^"]*".*?"\s*\])',
                    r"|",
                    r"(?#Disambiguation Text)((?:-|x[QRBN]?)?[a-h][1-8]",
                    r"|",
                    r"(?#Anything else)\S+[ \t\r\f\v]*)",
                )
            ),
        )
        ae(
            constants.IGNORE_CASE_FORMAT,
            r"".join(
                (
                    r"(?#Start Tag)\[\s*",
                    r"(?#Tag Name)([A-Za-z0-9_]+)\s*",
                    r'(?#Tag Value)"((?:[^\\"\t\r\f\v\n]*',
                    r'(?:\\[^\t\r\f\v\n][^\\"\t\r\f\v\n]*)*))"\s*',
                    r"(?#End Tag)(\])",
                    r"|",
                    r"(?:(?#Moves)",
                    r"(?#Piece)([KQRNkqrn]|B(?![1-8])|b(?![1-8xX]))",
                    r"([a-hA-H1-8]?)([xX]?)([a-hA-H][1-8])",
                    r"|",
                    r"(?#Pawn)(?:([a-hA-H])(?:(?:[2-7][-xX]|[xX])([a-hA-H]))?",
                    r"(?:([2-7])|([18])",
                    r"(?:=([QRBNqrbn]))))",
                    r"|",
                    r"(?#Castle)([Oo0]-[Oo0]-[Oo0]|[Oo0]-[Oo0])",
                    r"(?#sevoM))",
                    r"|",
                    r"(?#Game termination)(1-0|1/2-1/2|0-1|\*)",
                    r"|",
                    r"(?#Move number)([1-9][0-9]*)",
                    r"|",
                    r"(?#Dots)(\.+)",
                    r"|",
                    r"(?#EOL comment)(;(?:[^\n]*))(?=\n)",
                    r"|",
                    r"(?#Comment)(\{[^}]*\})",
                    r"|",
                    r"(?#Start RAV)(\()",
                    r"|",
                    r"(?#End RAV)(\))",
                    r"|",
                    r"(?#Numeric Annotation Glyph)",
                    r"(\$",
                    r"(?:",
                    r"(?:[1-9][0-9](?:(?=[01][-/])|[0-9]))",
                    r"|(?:[1-9](?:(?=[01][-/])|[0-9]))|",
                    r"(?:[1-9])",
                    r")",
                    r")",
                    r"|",
                    r"(?#Reserved)(<[^>]*>)",
                    r"|",
                    r"(?#Escaped)(\A%[^\n]*|\n%[^\n]*)(?=\n)",
                    r"|",
                    r"(?#Pass)(--|Z0)",
                    r"|",
                    r"(?#Check indicators)(?<=[1-8QRBNOqrbno0])([+#])",
                    r"|",
                    r"(?#Traditional Annonations)",
                    r"(?<=[1-8QRBNOqrbno0+#])([!?][!?]?)",
                    r"|",
                    r"(?#Bad Comment)(\{[^}]*)",
                    r"|",
                    r"(?#Bad Reserved)(<[^>]*)",
                    r"|",
                    r'(?#Bad Tag)(\[[^"]*"(?:.*?',
                    r"|",
                    r'[^\\"]*(?:\\.[^\\"]*)*)"\s*\])',
                    r"|",
                    r'(?#End of file marker)(\032)(?=\[[^"]*".*?"\s*\])',
                    r"|",
                    r"(?#Disambiguation Text)",
                    r"((?:(?:-|[xX][QRBNqrbn]?)?[a-hA-H][1-8]",
                    r"(?:=[QRBNqrbn])?)",
                    r"|",
                    r"(?:b[xX][QRBNqrbn]?[a-hA-H][18])",
                    r"|",
                    r"(?#Promotion)=[QRBNqrbn]",
                    r"|",
                    r"(?#Anything else)\S+[ \t\r\f\v]*)",
                )
            ),
        )
        ae(constants.IFG_TAG_NAME, 1)
        ae(constants.IFG_TAG_VALUE, 2)
        ae(constants.IFG_END_TAG, 3)
        ae(constants.IFG_PIECE_MOVE, 4)
        ae(constants.IFG_PIECE_MOVE_FROM_FILE_OR_RANK, 5)
        ae(constants.IFG_PIECE_CAPTURE, 6)
        ae(constants.IFG_PIECE_DESTINATION, 7)
        ae(constants.IFG_PAWN_FROM_FILE, 8)
        ae(constants.IFG_PAWN_CAPTURE_TO_FILE, 9)
        ae(constants.IFG_PAWN_TO_RANK, 10)
        ae(constants.IFG_PAWN_PROMOTE_TO_RANK, 11)
        ae(constants.IFG_PAWN_PROMOTE_PIECE, 12)
        ae(constants.IFG_CASTLES, 13)
        ae(constants.IFG_GAME_TERMINATION, 14)
        ae(constants.IFG_MOVE_NUMBER, 15)
        ae(constants.IFG_DOTS, 16)
        ae(constants.IFG_COMMENT_TO_EOL, 17)
        ae(constants.IFG_COMMENT, 18)
        ae(constants.IFG_START_RAV, 19)
        ae(constants.IFG_END_RAV, 20)
        ae(constants.IFG_NUMERIC_ANNOTATION_GLYPH, 21)
        ae(constants.IFG_RESERVED, 22)
        ae(constants.IFG_ESCAPE, 23)
        ae(constants.IFG_PASS, 24)
        ae(constants.IFG_CHECK_INDICATOR, 25)
        ae(constants.IFG_TRADITIONAL_ANNOTATION, 26)
        ae(constants.IFG_BAD_COMMENT, 27)
        ae(constants.IFG_BAD_RESERVED, 28)
        ae(constants.IFG_BAD_TAG, 29)
        ae(constants.IFG_END_OF_FILE_MARKER, 30)
        ae(constants.IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE, 31)
        ae(constants.DISAMBIGUATE_TEXT, r"\A([x-]?)([a-h][1-8])")
        ae(constants.DISAMBIGUATE_PGN, r"\A[x-]?[a-h][1-8]")
        ae(constants.DISAMBIGUATE_PROMOTION, r"\A=[QRBNqrbn]")
        ae(constants.DG_CAPTURE, 1)
        ae(constants.DG_DESTINATION, 2)
        ae(
            constants.LAN_FORMAT,
            r"(?#Lower case)\A([-x]?)([a-h][1-8])(?:=([qrbn]))?",
        )
        ae(constants.LAN_MOVE_SEPARATOR, "-")
        ae(constants.LAN_CAPTURE_OR_MOVE, 1)
        ae(constants.LAN_DESTINATION, 2)
        ae(constants.LAN_PROMOTE_PIECE, 3)
        ae(
            constants.TEXT_PROMOTION,
            r"(?#Lower case)([a-h](?:[x-][a-h])?[18]=?)([qrbn])",
        )
        ae(constants.TP_MOVE, 1)
        ae(constants.TP_PROMOTE_TO_PIECE, 2)
        ae(constants.TPF_TAG_NAME, 1)
        ae(constants.TPF_TAG_VALUE, 2)
        ae(constants.TPF_END_TAG, 3)
        ae(constants.TPF_GAME_TERMINATION, 4)
        ae(constants.TPF_COMMENT_TO_EOL, 5)
        ae(constants.TPF_COMMENT, 6)
        ae(constants.TPF_RESERVED, 7)
        ae(constants.TPF_ESCAPE, 8)
        ae(constants.TPF_BAD_COMMENT, 9)
        ae(constants.TPF_BAD_RESERVED, 10)
        ae(constants.TPF_BAD_TAG, 11)
        ae(constants.TPF_END_OF_FILE_MARKER, 12)
        ae(constants.TPF_OTHER_WITH_NON_NEWLINE_WHITESPACE, 13)
        ae(
            constants.FULL_DISAMBIGUATION_ALLOWED,
            r'(?s:([18]=[QB]).*\1|[18]=N|\[\s*FEN\s*")',
        )
        ae(constants.PAWN_MOVE_TOKEN_POSSIBLE_BISHOP, r"\A[Bb][1-8]\Z")
        ae(constants.UNTERMINATED, "<{")
        ae(
            constants.SUFFIX_ANNOTATION_TO_NAG,
            {
                "!!": "$3",
                "!?": "$5",
                "!": "$1",
                "??": "$4",
                "?!": "$6",
                "?": "$2",
            },
        )
        ae(constants.TAG_EVENT, "Event")
        ae(constants.TAG_SITE, "Site")
        ae(constants.TAG_DATE, "Date")
        ae(constants.TAG_ROUND, "Round")
        ae(constants.TAG_WHITE, "White")
        ae(constants.TAG_BLACK, "Black")
        ae(constants.TAG_RESULT, "Result")
        ae(
            constants.SEVEN_TAG_ROSTER,
            ("Event", "Site", "Date", "Round", "White", "Black", "Result"),
        )
        ae(constants.DEFAULT_TAG_VALUE, "?")
        ae(constants.DEFAULT_TAG_DATE_VALUE, "????.??.??")
        ae(constants.DEFAULT_TAG_RESULT_VALUE, "*")
        ae(constants.DEFAULT_SORT_TAG_VALUE, " ")
        ae(constants.DEFAULT_SORT_TAG_RESULT_VALUE, " ")
        ae(
            constants.SEVEN_TAG_ROSTER_DEFAULTS,
            {"Date": "????.??.??", "Result": "*"},
        )
        ae(constants.TAG_WHITETITLE, "WhiteTitle")
        ae(constants.TAG_BLACKTITLE, "BlackTitle")
        ae(constants.TAG_WHITEELO, "WhiteElo")
        ae(constants.TAG_BLACKELO, "BlackElo")
        ae(constants.TAG_WHITENA, "WhiteNA")
        ae(constants.TAG_BLACKNA, "BlackNA")
        ae(
            constants.SUPPLEMENTAL_TAG_ROSTER,
            (
                "WhiteTitle",
                "BlackTitle",
                "WhiteElo",
                "BlackElo",
                "WhiteNA",
                "BlackNA",
            ),
        )
        ae(constants.DEFAULT_SUPPLEMENTAL_TAG_VALUE, "-")
        ae(constants.TAG_FEN, "FEN")
        ae(constants.TAG_SETUP, "SetUp")
        ae(constants.SETUP_VALUE_FEN_ABSENT, "0")
        ae(constants.SETUP_VALUE_FEN_PRESENT, "1")
        ae(constants.PGN_CAPTURE_MOVE, "x")
        ae(constants.PGN_PAWN, "")
        ae(constants.PGN_KING, "K")
        ae(constants.PGN_QUEEN, "Q")
        ae(constants.PGN_ROOK, "R")
        ae(constants.PGN_BISHOP, "B")
        ae(constants.PGN_KNIGHT, "N")
        ae(constants.PGN_O_O, "O-O")
        ae(constants.PGN_O_O_O, "O-O-O")
        ae(constants.PGN_PROMOTION, "=")
        ae(constants.PGN_NAMED_PIECES, "KQRBN")
        ae(constants.PGN_MAXIMUM_LINE_LENGTH, 79)
        ae(constants.PGN_LINE_SEPARATOR, "\n")
        ae(constants.PGN_TOKEN_SEPARATOR, " ")
        ae(constants.PGN_DOT, ".")

        ae(constants.FEN_FIELD_COUNT, 6)
        ae(constants.FEN_PIECE_PLACEMENT_FIELD_INDEX, 0)
        ae(constants.FEN_ACTIVE_COLOR_FIELD_INDEX, 1)
        ae(constants.FEN_CASTLING_AVAILABILITY_FIELD_INDEX, 2)
        ae(constants.FEN_EN_PASSANT_TARGET_SQUARE_FIELD_INDEX, 3)
        ae(constants.FEN_HALFMOVE_CLOCK_FIELD_INDEX, 4)
        ae(constants.FEN_FULLMOVE_NUMBER_FIELD_INDEX, 5)
        ae(constants.FEN_WHITE_ACTIVE, "w")
        ae(constants.FEN_BLACK_ACTIVE, "b")
        ae(constants.FEN_FIELD_DELIM, " ")
        ae(constants.FEN_RANK_DELIM, "/")
        ae(constants.FEN_NULL, "-")
        ae(constants.FEN_WHITE_KING, "K")
        ae(constants.FEN_WHITE_QUEEN, "Q")
        ae(constants.FEN_WHITE_ROOK, "R")
        ae(constants.FEN_WHITE_BISHOP, "B")
        ae(constants.FEN_WHITE_KNIGHT, "N")
        ae(constants.FEN_WHITE_PAWN, "P")
        ae(constants.FEN_BLACK_KING, "k")
        ae(constants.FEN_BLACK_QUEEN, "q")
        ae(constants.FEN_BLACK_ROOK, "r")
        ae(constants.FEN_BLACK_BISHOP, "b")
        ae(constants.FEN_BLACK_KNIGHT, "n")
        ae(constants.FEN_BLACK_PAWN, "p")
        ae(
            constants.FEN_TO_PGN,
            {
                "K": "K",
                "Q": "Q",
                "R": "R",
                "B": "B",
                "N": "N",
                "P": "",
                "k": "K",
                "q": "Q",
                "r": "R",
                "b": "B",
                "n": "N",
                "p": "",
            },
        )
        ae(constants.FEN_PAWNS, {"P": "w", "p": "b"})
        ae(constants.FEN_INITIAL_CASTLING, "KQkq")
        ae(constants.FEN_WHITE_PIECES, "KQRBNP")
        ae(constants.FEN_BLACK_PIECES, "kqrbnp")
        ae(constants.FEN_PIECE_NAMES, "KQRBNPkqrbnp")

        ae(constants.FILE_NAMES, "abcdefgh")
        ae(constants.RANK_NAMES, "87654321")
        ae(
            constants.CASTLING_RIGHTS,
            {
                "a1": "Q",
                "h1": "K",
                "a8": "q",
                "h8": "k",
                "e1": "KQ",
                "e8": "kq",
            },
        )
        ae(
            constants.CASTLING_PIECE_FOR_SQUARE,
            {"a1": "R", "h1": "R", "a8": "r", "h8": "r", "e1": "K", "e8": "k"},
        )
        ae(
            constants.CASTLING_MOVE_RIGHTS,
            {
                ("w", "O-O"): "K",
                ("w", "O-O-O"): "Q",
                ("b", "O-O"): "k",
                ("b", "O-O-O"): "q",
            },
        )
        ae(constants.OTHER_SIDE, {"w": "b", "b": "w"})
        ae(constants.SIDE_TO_MOVE_KING, {"w": "K", "b": "k"})
        ae(
            constants.PIECE_TO_KING,
            {
                "K": "K",
                "Q": "K",
                "R": "K",
                "B": "K",
                "N": "K",
                "P": "K",
                "k": "k",
                "q": "k",
                "r": "k",
                "b": "k",
                "n": "k",
                "p": "k",
            },
        )
        ae(
            constants.PROMOTED_PIECE_NAME,
            {
                "w": {"Q": "Q", "R": "R", "B": "B", "N": "N"},
                "b": {"Q": "q", "R": "r", "B": "b", "N": "n"},
            },
        )

    def test_02_import_format_re(self):
        self.assertEqual(bool(re.compile(constants.IMPORT_FORMAT)), True)

    def test_03_disambiguate_text_re(self):
        self.assertEqual(bool(re.compile(constants.DISAMBIGUATE_TEXT)), True)

    def test_04_disambiguate_pgn_re(self):
        self.assertEqual(bool(re.compile(constants.DISAMBIGUATE_PGN)), True)

    def test_05_text_format_re(self):
        self.assertEqual(bool(re.compile(constants.TEXT_FORMAT)), True)

    def test_06_ignore_case_format_re(self):
        self.assertEqual(bool(re.compile(constants.IGNORE_CASE_FORMAT)), True)

    def test_07_disambiguate_promotion_re(self):
        self.assertEqual(
            bool(re.compile(constants.DISAMBIGUATE_PROMOTION)), True
        )

    def test_08_text_promotion_re(self):
        self.assertEqual(bool(re.compile(constants.TEXT_PROMOTION)), True)

    def test_09_pawn_move_token_possible_bishop_re(self):
        self.assertEqual(
            bool(re.compile(constants.PAWN_MOVE_TOKEN_POSSIBLE_BISHOP)), True
        )


class CountConstants(unittest.TestCase):
    def test_01_count_constants(self):
        self.assertEqual(
            sorted([c for c in dir(constants) if not c.startswith("_")]),
            [
                "ANYTHING_ELSE",
                "BACK_STEP",
                "BAD_COMMENT",
                "BAD_RESERVED",
                "CASTLING_MOVE_RIGHTS",
                "CASTLING_PIECE_FOR_SQUARE",
                "CASTLING_RIGHTS",
                "CGM_BAD_COMMENT",
                "CGM_BAD_RESERVED",
                "CGM_BAD_TAG",
                "CGM_CHECK_INDICATOR",
                "CGM_COMMENT",
                "CGM_COMMENT_TO_EOL",
                "CGM_DOTS",
                "CGM_END_OF_FILE_MARKER",
                "CGM_END_RAV",
                "CGM_END_TAG",
                "CGM_ESCAPE",
                "CGM_GAME_TERMINATION",
                "CGM_MOVE_NUMBER",
                "CGM_MOVE_SYMBOLS",
                "CGM_NUMERIC_ANNOTATION_GLYPH",
                "CGM_OTHER_WITH_NON_NEWLINE_WHITESPACE",
                "CGM_PASS",
                "CGM_RESERVED",
                "CGM_START_RAV",
                "CGM_TAG_NAME",
                "CGM_TAG_VALUE",
                "CGM_TRADITIONAL_ANNOTATION",
                "CHECK",
                "COMMENT",
                "DEFAULT_SORT_TAG_RESULT_VALUE",
                "DEFAULT_SORT_TAG_VALUE",
                "DEFAULT_SUPPLEMENTAL_TAG_VALUE",
                "DEFAULT_TAG_DATE_VALUE",
                "DEFAULT_TAG_RESULT_VALUE",
                "DEFAULT_TAG_VALUE",
                "DG_CAPTURE",
                "DG_DESTINATION",
                "DISAMBIGUATE_PGN",
                "DISAMBIGUATE_PROMOTION",
                "DISAMBIGUATE_TEXT",
                "DOTS",
                "END_OF_FILE_MARKER",
                "END_RAV",
                "EOL_COMMENT",
                "ESCAPED",
                "FEN_ACTIVE_COLOR_FIELD_INDEX",
                "FEN_BLACK_ACTIVE",
                "FEN_BLACK_BISHOP",
                "FEN_BLACK_KING",
                "FEN_BLACK_KNIGHT",
                "FEN_BLACK_PAWN",
                "FEN_BLACK_PIECES",
                "FEN_BLACK_QUEEN",
                "FEN_BLACK_ROOK",
                "FEN_CASTLING_AVAILABILITY_FIELD_INDEX",
                "FEN_EN_PASSANT_TARGET_SQUARE_FIELD_INDEX",
                "FEN_FIELD_COUNT",
                "FEN_FIELD_DELIM",
                "FEN_FULLMOVE_NUMBER_FIELD_INDEX",
                "FEN_HALFMOVE_CLOCK_FIELD_INDEX",
                "FEN_INITIAL_CASTLING",
                "FEN_NULL",
                "FEN_PAWNS",
                "FEN_PIECE_NAMES",
                "FEN_PIECE_PLACEMENT_FIELD_INDEX",
                "FEN_RANK_DELIM",
                "FEN_TO_PGN",
                "FEN_WHITE_ACTIVE",
                "FEN_WHITE_BISHOP",
                "FEN_WHITE_KING",
                "FEN_WHITE_KNIGHT",
                "FEN_WHITE_PAWN",
                "FEN_WHITE_PIECES",
                "FEN_WHITE_QUEEN",
                "FEN_WHITE_ROOK",
                "FILE_NAMES",
                "FULL_DISAMBIGUATION_ALLOWED",
                "GAME_FORMAT",
                "GAME_TERMINATION",
                "IFG_BAD_COMMENT",
                "IFG_BAD_RESERVED",
                "IFG_BAD_TAG",
                "IFG_CASTLES",
                "IFG_CHECK_INDICATOR",
                "IFG_COMMENT",
                "IFG_COMMENT_TO_EOL",
                "IFG_DOTS",
                "IFG_END_OF_FILE_MARKER",
                "IFG_END_RAV",
                "IFG_END_TAG",
                "IFG_ESCAPE",
                "IFG_GAME_TERMINATION",
                "IFG_MOVE_NUMBER",
                "IFG_NUMERIC_ANNOTATION_GLYPH",
                "IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE",
                "IFG_PASS",
                "IFG_PAWN_CAPTURE_TO_FILE",
                "IFG_PAWN_FROM_FILE",
                "IFG_PAWN_PROMOTE_PIECE",
                "IFG_PAWN_PROMOTE_TO_RANK",
                "IFG_PAWN_TO_RANK",
                "IFG_PIECE_CAPTURE",
                "IFG_PIECE_DESTINATION",
                "IFG_PIECE_MOVE",
                "IFG_PIECE_MOVE_FROM_FILE_OR_RANK",
                "IFG_RESERVED",
                "IFG_START_RAV",
                "IFG_TAG_NAME",
                "IFG_TAG_VALUE",
                "IFG_TRADITIONAL_ANNOTATION",
                "IGNORE_CASE_DISAMBIGUATION",
                "IGNORE_CASE_FORMAT",
                "IMPORT_FORMAT",
                "LAN_CAPTURE_OR_MOVE",
                "LAN_DESTINATION",
                "LAN_FORMAT",
                "LAN_MOVE_SEPARATOR",
                "LAN_PROMOTE_PIECE",
                "MOVE_NUMBER",
                "NAG",
                "OTHER_SIDE",
                "PASS",
                "PAWN_MOVE_TOKEN_POSSIBLE_BISHOP",
                "PGN_BISHOP",
                "PGN_CAPTURE_MOVE",
                "PGN_DISAMBIGUATION",
                "PGN_DOT",
                "PGN_FORMAT",
                "PGN_KING",
                "PGN_KNIGHT",
                "PGN_LINE_SEPARATOR",
                "PGN_MAXIMUM_LINE_LENGTH",
                "PGN_NAMED_PIECES",
                "PGN_O_O",
                "PGN_O_O_O",
                "PGN_PAWN",
                "PGN_PROMOTION",
                "PGN_QUEEN",
                "PGN_ROOK",
                "PGN_TAG",
                "PGN_TOKEN_SEPARATOR",
                "PIECE_TO_KING",
                "PROMOTED_PIECE_NAME",
                "RANK_NAMES",
                "RESERVED",
                "SETUP_VALUE_FEN_ABSENT",
                "SETUP_VALUE_FEN_PRESENT",
                "SEVEN_TAG_ROSTER",
                "SEVEN_TAG_ROSTER_DEFAULTS",
                "SIDE_TO_MOVE_KING",
                "START_RAV",
                "SUFFIX_ANNOTATION_TO_NAG",
                "SUPPLEMENTAL_TAG_ROSTER",
                "TAG_BLACK",
                "TAG_BLACKELO",
                "TAG_BLACKNA",
                "TAG_BLACKTITLE",
                "TAG_DATE",
                "TAG_EVENT",
                "TAG_FEN",
                "TAG_PAIR",
                "TAG_PAIR_DATA_ERROR",
                "TAG_PAIR_FORMAT",
                "TAG_RESULT",
                "TAG_ROUND",
                "TAG_SETUP",
                "TAG_SITE",
                "TAG_WHITE",
                "TAG_WHITEELO",
                "TAG_WHITENA",
                "TAG_WHITETITLE",
                "TEXT",
                "TEXT_DISAMBIGUATION",
                "TEXT_FORMAT",
                "TEXT_PROMOTION",
                "TPF_BAD_COMMENT",
                "TPF_BAD_RESERVED",
                "TPF_BAD_TAG",
                "TPF_COMMENT",
                "TPF_COMMENT_TO_EOL",
                "TPF_END_OF_FILE_MARKER",
                "TPF_END_TAG",
                "TPF_ESCAPE",
                "TPF_GAME_TERMINATION",
                "TPF_OTHER_WITH_NON_NEWLINE_WHITESPACE",
                "TPF_RESERVED",
                "TPF_TAG_NAME",
                "TPF_TAG_VALUE",
                "TP_MOVE",
                "TP_PROMOTE_TO_PIECE",
                "TRADITIONAL",
                "UNTERMINATED",
            ],
        )


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(Constants))
    runner().run(loader(CountConstants))
