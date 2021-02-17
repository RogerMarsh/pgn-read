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
        ae(constants.PGN_FORMAT,
           r''.join(
               (r'(?#Start Tag)\[\s*',
                r'(?#Tag Name)([A-Za-z0-9_]+)\s*',
                r'(?#Tag Value)"((?:[^\\"]|\\.)*)"\s*',
                r'(?#End Tag)(\])',
                r'|',
                r'(?:(?#Moves)',
                r'(?#Piece)([KQRBN])([a-h1-8]?)(x?)([a-h][1-8])',
                r'|',
                r'(?#Pawn)(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])',
                r'(?:=([QRBN]))))',
                r'|',
                r'(?#Castle)(O-O-O|O-O)',
                r'(?#sevoM))',
                r'(?#Suffix)[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                r'|',
                r'(?#Game termination)(1-0|1/2-1/2|0-1|\*)',
                r'|',
                r'(?#Move number)([1-9][0-9]*)',
                r'|',
                r'(?#Dots)(\.+)',
                r'|',
                r'(?#EOL comment)(;(?:[^\n]*))',
                r'|',
                r'(?#Comment)(\{[^}]*\})',
                r'|',
                r'(?#Start RAV)(\()',
                r'|',
                r'(?#End RAV)(\))',
                r'|',
                r'(?#Numeric Annotation Glyph)(\$(?:[1-9][0-9]{0,2}))',
                r'|',
                r'(?#Reserved)(<[^>]*>)',
                r'|',
                r'(?#Escaped)(\A%[^\n]*|\n%[^\n]*)',
                r'|',
                r'(?#Pass)(--)',
                )))
        ae(constants.PGN_DISAMBIGUATION,
           r''.join(
               (r'(?#Disambiguation PGN)(x?[a-h][1-8]',
                r'[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                )))
        ae(constants.TEXT_DISAMBIGUATION,
           r''.join(
               (r'(?#Disambiguation Text)((?:-|x[QRBN]?)[a-h][1-8]',
                r'[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                )))
        ae(constants.ANYTHING_ELSE,
           r''.join(
               (r'(?#Anything else)\S+[ \t\r\f\v]*)',
                )))
        ae(constants.IMPORT_FORMAT,
           r''.join(
               (r'(?#Start Tag)\[\s*',
                r'(?#Tag Name)([A-Za-z0-9_]+)\s*',
                r'(?#Tag Value)"((?:[^\\"]|\\.)*)"\s*',
                r'(?#End Tag)(\])',
                r'|',
                r'(?:(?#Moves)',
                r'(?#Piece)([KQRBN])([a-h1-8]?)(x?)([a-h][1-8])',
                r'|',
                r'(?#Pawn)(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])',
                r'(?:=([QRBN]))))',
                r'|',
                r'(?#Castle)(O-O-O|O-O)',
                r'(?#sevoM))',
                r'(?#Suffix)[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                r'|',
                r'(?#Game termination)(1-0|1/2-1/2|0-1|\*)',
                r'|',
                r'(?#Move number)([1-9][0-9]*)',
                r'|',
                r'(?#Dots)(\.+)',
                r'|',
                r'(?#EOL comment)(;(?:[^\n]*))',
                r'|',
                r'(?#Comment)(\{[^}]*\})',
                r'|',
                r'(?#Start RAV)(\()',
                r'|',
                r'(?#End RAV)(\))',
                r'|',
                r'(?#Numeric Annotation Glyph)(\$(?:[1-9][0-9]{0,2}))',
                r'|',
                r'(?#Reserved)(<[^>]*>)',
                r'|',
                r'(?#Escaped)(\A%[^\n]*|\n%[^\n]*)',
                r'|',
                r'(?#Pass)(--)',
                r'|',
                r'(?#Disambiguation PGN)(x?[a-h][1-8]',
                r'[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                r'|',
                r'(?#Anything else)\S+[ \t\r\f\v]*)',
                )))
        ae(constants.TEXT_FORMAT,
           r''.join(
               (r'(?#Start Tag)\[\s*',
                r'(?#Tag Name)([A-Za-z0-9_]+)\s*',
                r'(?#Tag Value)"((?:[^\\"]|\\.)*)"\s*',
                r'(?#End Tag)(\])',
                r'|',
                r'(?:(?#Moves)',
                r'(?#Piece)([KQRBN])([a-h1-8]?)(x?)([a-h][1-8])',
                r'|',
                r'(?#Pawn)(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])',
                r'(?:=?([QRBN]))))',
                r'|',
                r'(?#Castle)(O-O-O|O-O|0-0-0|0-0)',
                r'(?#sevoM))',
                r'(?#Suffix)[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                r'|',
                r'(?#Game termination)(1-0|1/2-1/2|0-1|\*)',
                r'|',
                r'(?#Move number)([1-9][0-9]*)',
                r'|',
                r'(?#Dots)(\.+)',
                r'|',
                r'(?#EOL comment)(;(?:[^\n]*))',
                r'|',
                r'(?#Comment)(\{[^}]*\})',
                r'|',
                r'(?#Start RAV)(\()',
                r'|',
                r'(?#End RAV)(\))',
                r'|',
                r'(?#Numeric Annotation Glyph)(\$(?:[1-9][0-9]{0,2}))',
                r'|',
                r'(?#Reserved)(<[^>]*>)',
                r'|',
                r'(?#Escaped)(\A%[^\n]*|\n%[^\n]*)',
                r'|',
                r'(?#Pass)(--)',
                r'|',
                r'(?#Disambiguation Text)((?:-|x[QRBN]?)[a-h][1-8]',
                r'[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                r'|',
                r'(?#Anything else)\S+[ \t\r\f\v]*)',
                )))
        ae(constants.IGNORE_CASE_FORMAT,
           r''.join(
               (r'(?#Ignore case)(?i)',
                r'(?#Start Tag)\[\s*',
                r'(?#Tag Name)([a-z0-9_]+)\s*',
                r'(?#Tag Value)"((?:[^\\"]|\\.)*)"\s*',
                r'(?#End Tag)(\])',
                r'|',
                r'(?:(?#Moves)',
                r'(?#Piece)([KQRBN])([a-h1-8]?)(x?)([a-h][1-8])',
                r'|',
                r'(?#Pawn)(?:([a-h])(?:x([a-h]))?(?:([2-7])|([18])',
                r'(?:=?([QRBN]))))',
                r'|',
                r'(?#Castle)(O-O-O|O-O|0-0-0|0-0)',
                r'(?#sevoM))',
                r'(?#Suffix)[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                r'|',
                r'(?#Game termination)(1-0|1/2-1/2|0-1|\*)',
                r'|',
                r'(?#Move number)([1-9][0-9]*)',
                r'|',
                r'(?#Dots)(\.+)',
                r'|',
                r'(?#EOL comment)(;(?:[^\n]*))',
                r'|',
                r'(?#Comment)(\{[^}]*\})',
                r'|',
                r'(?#Start RAV)(\()',
                r'|',
                r'(?#End RAV)(\))',
                r'|',
                r'(?#Numeric Annotation Glyph)(\$(?:[1-9][0-9]{0,2}))',
                r'|',
                r'(?#Reserved)(<[^>]*>)',
                r'|',
                r'(?#Escaped)(\A%[^\n]*|\n%[^\n]*)',
                r'|',
                r'(?#Pass)(--)',
                r'|',
                r'(?#Disambiguation Text)((?:-|x[QRBN]?)[a-h][1-8]',
                r'[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?',
                r'|',
                r'(?#Anything else)\S+[ \t\r\f\v]*)',
                )))
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
        ae(constants.IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE, 25)
        ae(constants.DISAMBIGUATE_TEXT,
           r'\A(x?)([a-h][1-8])[+#]?(?:!!|!\?|!|\?\?|\?!|\?)?')
        ae(constants.DISAMBIGUATE_PGN,
           r'\Ax?[a-h][1-8][+#]?(?:!!|!\?|!|\?\?|\?!|\?)?')
        ae(constants.DG_CAPTURE, 1)
        ae(constants.DG_DESTINATION, 2)
        ae(constants.LAN_FORMAT,
           r''.join((r'\A([-x]?)([a-h][1-8])(?:=(QRBN))?',
                     r'\s*([+#]?)\s*((?:!!|!\?|!|\?\?|\?!|\?)?)')))
        ae(constants.LAN_CAPTURE_OR_MOVE, 1)
        ae(constants.LAN_DESTINATION, 2)
        ae(constants.LAN_PROMOTE_PIECE, 3)
        ae(constants.LAN_CHECK_INDICATOR, 4)
        ae(constants.LAN_SUFFIX_ANNOTATION, 5)
        ae(constants.TEXT_PROMOTION,
           r''.join((r'(?#Lower case)([a-h](?:[x-][a-h])?[18]=?)([qrbn])',
                     r'\s*([+#]?)\s*((?:!!|!\?|!|\?\?|\?!|\?)?)')))
        ae(constants.TP_MOVE, 1)
        ae(constants.TP_PROMOTE_TO_PIECE, 2)
        ae(constants.TP_CHECK_INDICATOR, 3)
        ae(constants.TP_SUFFIX_ANNOTATION, 4)
        ae(constants.TAG_EVENT, 'Event')
        ae(constants.TAG_SITE, 'Site')
        ae(constants.TAG_DATE, 'Date')
        ae(constants.TAG_ROUND, 'Round')
        ae(constants.TAG_WHITE, 'White')
        ae(constants.TAG_BLACK, 'Black')
        ae(constants.TAG_RESULT, 'Result')
        ae(constants.SEVEN_TAG_ROSTER,
           ('Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result'))
        ae(constants.DEFAULT_TAG_VALUE, '?')
        ae(constants.DEFAULT_TAG_DATE_VALUE, '????.??.??')
        ae(constants.DEFAULT_TAG_RESULT_VALUE, '*')
        ae(constants.DEFAULT_SORT_TAG_VALUE, ' ')
        ae(constants.DEFAULT_SORT_TAG_RESULT_VALUE, ' ')
        ae(constants.SEVEN_TAG_ROSTER_DEFAULTS,
           {'Date': '????.??.??', 'Result': '*'})
        ae(constants.TAG_FEN, 'FEN')
        ae(constants.TAG_SETUP, 'SetUp')
        ae(constants.SETUP_VALUE_FEN_ABSENT, '0')
        ae(constants.SETUP_VALUE_FEN_PRESENT, '1')
        ae(constants.PGN_PAWN, '')
        ae(constants.PGN_KING, 'K')
        ae(constants.PGN_QUEEN, 'Q')
        ae(constants.PGN_ROOK, 'R')
        ae(constants.PGN_BISHOP, 'B')
        ae(constants.PGN_KNIGHT, 'N')
        ae(constants.PGN_O_O, 'O-O')
        ae(constants.PGN_O_O_O, 'O-O-O')
        ae(constants.PGN_PROMOTION, '=')
        ae(constants.PGN_NAMED_PIECES, 'KQRBN')
        ae(constants.PGN_MAXIMUM_LINE_LENGTH, 79)
        ae(constants.PGN_LINE_SEPARATOR, '\n')
        ae(constants.PGN_TOKEN_SEPARATOR, ' ')
        ae(constants.PGN_DOT, '.')

        ae(constants.FEN_FIELD_COUNT, 6)
        ae(constants.FEN_PIECE_PLACEMENT_FIELD_INDEX, 0)
        ae(constants.FEN_ACTIVE_COLOR_FIELD_INDEX, 1)
        ae(constants.FEN_CASTLING_AVAILABILITY_FIELD_INDEX, 2)
        ae(constants.FEN_EN_PASSANT_TARGET_SQUARE_FIELD_INDEX, 3)
        ae(constants.FEN_HALFMOVE_CLOCK_FIELD_INDEX, 4)
        ae(constants.FEN_FULLMOVE_NUMBER_FIELD_INDEX, 5)
        ae(constants.FEN_WHITE_ACTIVE, 'w')
        ae(constants.FEN_BLACK_ACTIVE, 'b')
        ae(constants.FEN_FIELD_DELIM, ' ')
        ae(constants.FEN_RANK_DELIM, '/')
        ae(constants.FEN_NULL, '-')
        ae(constants.FEN_WHITE_KING, 'K')
        ae(constants.FEN_WHITE_QUEEN, 'Q')
        ae(constants.FEN_WHITE_ROOK, 'R')
        ae(constants.FEN_WHITE_BISHOP, 'B')
        ae(constants.FEN_WHITE_KNIGHT, 'N')
        ae(constants.FEN_WHITE_PAWN, 'P')
        ae(constants.FEN_BLACK_KING, 'k')
        ae(constants.FEN_BLACK_QUEEN, 'q')
        ae(constants.FEN_BLACK_ROOK, 'r')
        ae(constants.FEN_BLACK_BISHOP, 'b')
        ae(constants.FEN_BLACK_KNIGHT, 'n')
        ae(constants.FEN_BLACK_PAWN, 'p')
        ae(constants.FEN_TO_PGN,
           {'K':'K', 'Q':'Q', 'R':'R', 'B':'B', 'N':'N', 'P':'',
            'k':'K', 'q':'Q', 'r':'R', 'b':'B', 'n':'N', 'p':''},
           )
        ae(constants.FEN_PAWNS, {'P':'w', 'p':'b'})
        ae(constants.FEN_INITIAL_CASTLING, 'KQkq')
        ae(constants.FEN_WHITE_PIECES, 'KQRBNP')
        ae(constants.FEN_BLACK_PIECES, 'kqrbnp')
        ae(constants.FEN_PIECE_NAMES, 'KQRBNPkqrbnp')

        ae(constants.FILE_NAMES, 'abcdefgh')
        ae(constants.RANK_NAMES, '87654321')
        ae(constants.CASTLING_RIGHTS,
           {'a1':'Q', 'h1':'K', 'a8':'q', 'h8':'k', 'e1':'KQ', 'e8':'kq'})
        ae(constants.CASTLING_PIECE_FOR_SQUARE,
           {'a1':'R', 'h1':'R', 'a8':'r', 'h8':'r', 'e1':'K', 'e8':'k'})
        ae(constants.CASTLING_MOVE_RIGHTS,
           {('w', 'O-O'):'K', ('w', 'O-O-O'):'Q',
            ('b', 'O-O'):'k', ('b', 'O-O-O'):'q',
            })
        ae(constants.OTHER_SIDE, {'w':'b', 'b':'w'})
        ae(constants.PIECE_TO_KING,
           {'K':'K', 'Q':'K', 'R':'K', 'B':'K', 'N':'K', 'P':'K',
            'k':'k', 'q':'k', 'r':'k', 'b':'k', 'n':'k', 'p':'k'},
           )
        ae(constants.PROMOTED_PIECE_NAME,
           {'w':{'Q':'Q', 'R':'R', 'B':'B', 'N':'N'},
            'b':{'Q':'q', 'R':'r', 'B':'b', 'N':'n'},
            })

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


class RookMoves(unittest.TestCase):

    def test_01_rook_moves(self):
        self.assertEqual(
            constants.ROOK_MOVES,
            {'a8': {'a4', 'a1', 'b8', 'f8', 'a7', 'a2', 'a6',
                    'a5', 'd8', 'c8', 'h8', 'g8', 'e8', 'a3'},
             'a7': {'b7', 'a4', 'a1', 'g7', 'e7', 'f7', 'a2',
                    'h7', 'a6', 'a5', 'a8', 'd7', 'c7', 'a3'},
             'a6': {'g6', 'a4', 'b6', 'a1', 'f6', 'a7', 'a2',
                    'e6', 'a5', 'd6', 'a8', 'c6', 'h6', 'a3'},
             'a5': {'d5', 'a4', 'c5', 'a1', 'b5', 'e5', 'g5',
                    'a7', 'a2', 'a6', 'h5', 'a8', 'f5', 'a3'},
             'a4': {'c4', 'a1', 'a7', 'a2', 'a6', 'h4', 'g4',
                    'a5', 'b4', 'a8', 'd4', 'f4', 'e4', 'a3'},
             'a3': {'d3', 'f3', 'a4', 'a1', 'b3', 'a7', 'c3',
                    'a2', 'a6', 'a5', 'g3', 'a8', 'e3', 'h3'},
             'a2': {'a4', 'f2', 'a1', 'e2', 'a7', 'a6', 'g2',
                    'a5', 'h2', 'b2', 'a8', 'c2', 'd2', 'a3'},
             'a1': {'a4', 'c1', 'h1', 'a7', 'a2', 'f1', 'a6',
                    'b1', 'a5', 'g1', 'a8', 'e1', 'd1', 'a3'},
             'b8': {'h8', 'b3', 'b5', 'f8', 'b1', 'b4', 'b2',
                    'd8', 'b6', 'c8', 'a8', 'g8', 'e8', 'b7'},
             'b7': {'b8', 'b3', 'b5', 'g7', 'f7', 'a7', 'e7',
                    'h7', 'b1', 'b4', 'b2', 'b6', 'd7', 'c7'},
             'b6': {'g6', 'b8', 'b3', 'b5', 'f6', 'e6', 'a6',
                    'b1', 'b4', 'b2', 'd6', 'c6', 'h6', 'b7'},
             'b5': {'d5', 'c5', 'b8', 'b3', 'e5', 'g5', 'b1',
                    'b4', 'a5', 'b2', 'h5', 'b6', 'f5', 'b7'},
             'b4': {'a4', 'c4', 'b8', 'b3', 'b5', 'b1', 'h4',
                    'g4', 'b2', 'b6', 'd4', 'f4', 'e4', 'b7'},
             'b3': {'d3', 'f3', 'e3', 'b8', 'b5', 'c3', 'a3',
                    'b1', 'b4', 'g3', 'b2', 'b6', 'h3', 'b7'},
             'b2': {'f2', 'e2', 'b8', 'b3', 'b5', 'a2', 'b1',
                    'g2', 'b4', 'h2', 'b6', 'c2', 'd2', 'b7'},
             'b1': {'c1', 'a1', 'b8', 'b3', 'b5', 'h1', 'f1',
                    'b4', 'b2', 'g1', 'b6', 'e1', 'd1', 'b7'},
             'c8': {'h8', 'c5', 'c4', 'c1', 'b8', 'f8', 'c3',
                    'c6', 'd8', 'c2', 'a8', 'e8', 'g8', 'c7'},
             'c7': {'c5', 'c4', 'c1', 'g7', 'e7', 'f7', 'c3',
                    'a7', 'h7', 'c6', 'c8', 'c2', 'd7', 'b7'},
             'c6': {'c5', 'b6', 'c4', 'c1', 'f6', 'c3', 'e6',
                    'a6', 'c8', 'd6', 'c2', 'c7', 'h6', 'g6'},
             'c5': {'d5', 'c4', 'c1', 'b5', 'e5', 'g5', 'c3',
                    'a5', 'h5', 'c6', 'c8', 'f5', 'c2', 'c7'},
             'c4': {'c5', 'a4', 'c1', 'c3', 'g4', 'b4', 'c6',
                    'c8', 'c2', 'd4', 'f4', 'c7', 'e4', 'h4'},
             'c3': {'d3', 'f3', 'c5', 'c4', 'c1', 'b3', 'a3',
                    'g3', 'c6', 'c8', 'e3', 'c2', 'c7', 'h3'},
             'c2': {'c5', 'f2', 'c4', 'c1', 'e2', 'c3', 'a2',
                    'g2', 'h2', 'c6', 'c8', 'b2', 'd2', 'c7'},
             'c1': {'c5', 'c4', 'a1', 'h1', 'c3', 'f1', 'b1',
                    'c6', 'c8', 'g1', 'c2', 'c7', 'd1', 'e1'},
             'd8': {'d5', 'd3', 'd2', 'h8', 'b8', 'f8', 'g8',
                    'd6', 'c8', 'a8', 'd4', 'd7', 'e8', 'd1'},
             'd7': {'d5', 'd3', 'd2', 'g7', 'e7', 'f7', 'a7',
                    'h7', 'd6', 'd8', 'd4', 'c7', 'd1', 'b7'},
             'd6': {'d5', 'd3', 'd2', 'b6', 'h6', 'f6', 'e6',
                    'a6', 'd8', 'c6', 'd4', 'd7', 'd1', 'g6'},
             'd5': {'d3', 'd2', 'c5', 'b5', 'e5', 'g5', 'a5',
                    'h5', 'd6', 'd8', 'f5', 'd4', 'd7', 'd1'},
             'd4': {'d5', 'd3', 'd2', 'a4', 'e4', 'c4', 'g4',
                    'b4', 'd6', 'd8', 'f4', 'd7', 'd1', 'h4'},
             'd3': {'d5', 'd2', 'f3', 'b3', 'c3', 'a3', 'g3',
                    'd6', 'd8', 'e3', 'd4', 'd7', 'd1', 'h3'},
             'd2': {'d5', 'd3', 'f2', 'e2', 'a2', 'g2', 'h2',
                    'd6', 'd8', 'b2', 'c2', 'd4', 'd7', 'd1'},
             'd1': {'d5', 'd3', 'd2', 'c1', 'a1', 'h1', 'f1',
                    'b1', 'd6', 'd8', 'g1', 'd4', 'd7', 'e1'},
             'e8': {'h8', 'e2', 'b8', 'e5', 'f8', 'e6', 'g8',
                    'd8', 'c8', 'e3', 'a8', 'e7', 'e4', 'e1'},
             'e7': {'b7', 'd7', 'e2', 'g7', 'c7', 'e5', 'f7',
                    'a7', 'e6', 'h7', 'e3', 'e8', 'e4', 'e1'},
             'e6': {'g6', 'b6', 'e2', 'h6', 'e5', 'f6', 'a6',
                    'd6', 'c6', 'e3', 'e7', 'e8', 'e4', 'e1'},
             'e5': {'d5', 'c5', 'e2', 'b5', 'g5', 'e6', 'a5',
                    'h5', 'f5', 'e3', 'e7', 'e8', 'e4', 'e1'},
             'e4': {'a4', 'c4', 'e2', 'e5', 'e6', 'h4', 'g4',
                    'b4', 'e3', 'd4', 'f4', 'e7', 'e8', 'e1'},
             'e3': {'d3', 'f3', 'e2', 'b3', 'e5', 'c3', 'e6',
                    'a3', 'g3', 'e7', 'e8', 'h3', 'e4', 'e1'},
             'e2': {'d2', 'f2', 'e5', 'e6', 'a2', 'g2', 'h2',
                    'b2', 'e3', 'c2', 'e7', 'e8', 'e4', 'e1'},
             'e1': {'d1', 'c1', 'e2', 'a1', 'h1', 'e5', 'e6',
                    'f1', 'b1', 'g1', 'e3', 'e7', 'e8', 'e4'},
             'f8': {'h8', 'f3', 'f2', 'b8', 'f7', 'f6', 'f1',
                    'd8', 'f5', 'c8', 'a8', 'f4', 'g8', 'e8'},
             'f7': {'f3', 'f2', 'g7', 'e7', 'f8', 'f6', 'a7',
                    'h7', 'f1', 'f5', 'f4', 'd7', 'c7', 'b7'},
             'f6': {'f3', 'f2', 'b6', 'f7', 'f8', 'e6', 'f1',
                    'a6', 'd6', 'f5', 'c6', 'f4', 'h6', 'g6'},
             'f5': {'d5', 'f3', 'f2', 'c5', 'b5', 'f7', 'f8',
                    'f6', 'e5', 'g5', 'f1', 'a5', 'h5', 'f4'},
             'f4': {'f3', 'f2', 'a4', 'c4', 'f7', 'f8', 'f6',
                    'f1', 'g4', 'b4', 'f5', 'd4', 'e4', 'h4'},
             'f3': {'d3', 'f2', 'b3', 'f7', 'f8', 'f6', 'c3',
                    'f1', 'a3', 'g3', 'f5', 'e3', 'f4', 'h3'},
             'f2': {'f3', 'e2', 'f7', 'f8', 'f6', 'a2', 'f1',
                    'g2', 'h2', 'b2', 'f5', 'c2', 'f4', 'd2'},
             'f1': {'f3', 'f2', 'c1', 'a1', 'h1', 'f7', 'f8',
                    'f6', 'b1', 'g1', 'f5', 'f4', 'd1', 'e1'},
             'g8': {'h8', 'g6', 'g7', 'b8', 'g5', 'f8', 'g2',
                    'g3', 'g1', 'd8', 'c8', 'a8', 'e8', 'g4'},
             'g7': {'g6', 'b7', 'd7', 'g5', 'f7', 'e7', 'a7',
                    'h7', 'g2', 'g3', 'g1', 'g8', 'c7', 'g4'},
             'g6': {'b6', 'g7', 'g5', 'f6', 'e6', 'a6', 'g2',
                    'g3', 'g1', 'd6', 'c6', 'g8', 'h6', 'g4'},
             'g5': {'d5', 'g6', 'c5', 'g7', 'b5', 'e5', 'g2',
                    'a5', 'g3', 'g1', 'h5', 'f5', 'g8', 'g4'},
             'g4': {'g6', 'a4', 'c4', 'g7', 'g5', 'h4', 'g2',
                    'b4', 'g3', 'g1', 'd4', 'f4', 'g8', 'e4'},
             'g3': {'g6', 'd3', 'f3', 'g7', 'b3', 'g5', 'c3',
                    'a3', 'g2', 'g1', 'e3', 'g8', 'h3', 'g4'},
             'g2': {'g6', 'd2', 'f2', 'e2', 'g7', 'g5', 'a2',
                    'h2', 'g3', 'g1', 'b2', 'c2', 'g8', 'g4'},
             'g1': {'g6', 'e1', 'c1', 'a1', 'g7', 'h1', 'g5',
                    'f1', 'b1', 'g2', 'g3', 'g8', 'd1', 'g4'},
             'h8': {'h1', 'b8', 'f8', 'h7', 'h2', 'h5', 'd8',
                    'c8', 'a8', 'g8', 'e8', 'h3', 'h6', 'h4'},
             'h7': {'b7', 'h1', 'g7', 'e7', 'f7', 'a7', 'h2',
                    'h5', 'h8', 'd7', 'c7', 'h3', 'h6', 'h4'},
             'h6': {'g6', 'h1', 'f6', 'h7', 'e6', 'a6', 'h2',
                    'h5', 'd6', 'c6', 'b6', 'h8', 'h3', 'h4'},
             'h5': {'d5', 'c5', 'h1', 'b5', 'e5', 'g5', 'h7',
                    'h2', 'a5', 'f5', 'h8', 'h3', 'h6', 'h4'},
             'h4': {'e4', 'a4', 'c4', 'h1', 'h7', 'g4', 'h2',
                    'h5', 'b4', 'h8', 'd4', 'f4', 'h3', 'h6'},
             'h3': {'d3', 'f3', 'h1', 'b3', 'c3', 'h7', 'a3',
                    'h2', 'h5', 'g3', 'e3', 'h8', 'h6', 'h4'},
             'h2': {'c2', 'f2', 'h1', 'e2', 'h7', 'a2', 'h5',
                    'g2', 'b2', 'h8', 'd2', 'h3', 'h6', 'h4'},
             'h1': {'d1', 'c1', 'a1', 'h7', 'f1', 'b1', 'h2',
                    'h5', 'g1', 'h8', 'e1', 'h3', 'h6', 'h4'}})


class BishopMoves(unittest.TestCase):

    def test_01_bishop_moves(self):
        self.assertEqual(
            constants.BISHOP_MOVES,
            {'a8': {'d5', 'f3', 'h1', 'g2', 'c6', 'e4', 'b7'},
             'a7': {'c5', 'f2', 'b6', 'b8', 'g1', 'e3', 'd4'},
             'a6': {'d3', 'c4', 'e2', 'b5', 'f1', 'c8', 'b7'},
             'a5': {'c3', 'b4', 'd8', 'b6', 'd2', 'c7', 'e1'},
             'a4': {'b3', 'b5', 'c6', 'c2', 'd7', 'e8', 'd1'},
             'a3': {'c5', 'c1', 'f8', 'b4', 'b2', 'd6', 'e7'},
             'a2': {'d5', 'c4', 'b3', 'f7', 'e6', 'b1', 'g8'},
             'a1': {'g7', 'f6', 'e5', 'c3', 'b2', 'h8', 'd4'},
             'b8': {'e5', 'a7', 'h2', 'g3', 'd6', 'f4', 'c7'},
             'b7': {'d5', 'f3', 'h1', 'a6', 'g2', 'c6', 'a8', 'c8', 'e4'},
             'b6': {'c5', 'f2', 'a7', 'a5', 'g1', 'd8', 'e3', 'd4', 'c7'},
             'b5': {'d3', 'a4', 'c4', 'e2', 'f1', 'a6', 'c6', 'd7', 'e8'},
             'b4': {'c5', 'e7', 'f8', 'c3', 'a3', 'a5', 'd6', 'd2', 'e1'},
             'b3': {'d5', 'a4', 'c4', 'f7', 'e6', 'a2', 'c2', 'g8', 'd1'},
             'b2': {'c1', 'a1', 'g7', 'f6', 'e5', 'c3', 'h8', 'd4', 'a3'},
             'b1': {'d3', 'a2', 'h7', 'f5', 'c2', 'e4', 'g6'},
             'c8': {'b7', 'e6', 'a6', 'f5', 'd7', 'h3', 'g4'},
             'c7': {'b8', 'e5', 'h2', 'a5', 'g3', 'd6', 'd8', 'b6', 'f4'},
             'c6': {'d5', 'f3', 'a4', 'h1', 'b5', 'g2', 'a8',
                    'd7', 'e8', 'e4', 'b7'},
             'c5': {'f2', 'b6', 'f8', 'a7', 'b4', 'g1', 'd6',
                    'e3', 'd4', 'e7', 'a3'},
             'c4': {'d5', 'd3', 'e2', 'b3', 'b5', 'f7', 'e6',
                    'f1', 'a6', 'a2', 'g8'},
             'c3': {'a1', 'g7', 'f6', 'e5', 'b4', 'a5', 'b2',
                    'h8', 'd4', 'd2', 'e1'},
             'c2': {'d3', 'e4', 'a4', 'b3', 'h7', 'b1', 'f5', 'd1', 'g6'},
             'c1': {'g5', 'b2', 'e3', 'f4', 'd2', 'h6', 'a3'},
             'd8': {'g5', 'f6', 'a5', 'b6', 'e7', 'c7', 'h4'},
             'd7': {'a4', 'b5', 'e6', 'c8', 'f5', 'c6', 'e8', 'h3', 'g4'},
             'd6': {'c5', 'b8', 'e5', 'f8', 'h2', 'b4', 'g3',
                    'f4', 'e7', 'c7', 'a3'},
             'd5': {'f3', 'c4', 'h1', 'b3', 'f7', 'e6', 'a2',
                    'g2', 'c6', 'a8', 'g8', 'e4', 'b7'},
             'd4': {'c5', 'f2', 'b6', 'a1', 'g7', 'f6', 'e5',
                    'a7', 'c3', 'g1', 'b2', 'e3', 'h8'},
             'd3': {'c4', 'e2', 'b5', 'h7', 'f1', 'a6', 'b1',
                    'f5', 'c2', 'e4', 'g6'},
             'd2': {'c1', 'g5', 'c3', 'b4', 'a5', 'e3', 'f4', 'h6', 'e1'},
             'd1': {'f3', 'a4', 'e2', 'b3', 'h5', 'c2', 'g4'},
             'e8': {'a4', 'b5', 'f7', 'h5', 'c6', 'd7', 'g6'},
             'e7': {'c5', 'g5', 'f6', 'f8', 'a3', 'b4', 'd8', 'd6', 'h4'},
             'e6': {'d5', 'c4', 'b3', 'f7', 'a2', 'g8', 'c8',
                    'f5', 'd7', 'h3', 'g4'},
             'e5': {'a1', 'b8', 'g7', 'f6', 'c3', 'h2', 'g3',
                    'd6', 'b2', 'h8', 'd4', 'f4', 'c7'},
             'e4': {'d5', 'f3', 'd3', 'g6', 'h1', 'h7', 'b1',
                    'g2', 'c6', 'a8', 'f5', 'c2', 'b7'},
             'e3': {'c5', 'f2', 'b6', 'c1', 'g5', 'a7', 'g1',
                    'd4', 'f4', 'd2', 'h6'},
             'e2': {'d3', 'f3', 'c4', 'b5', 'f1', 'a6', 'h5', 'd1', 'g4'},
             'e1': {'f2', 'c3', 'h4', 'b4', 'a5', 'g3', 'd2'},
             'f8': {'c5', 'g7', 'b4', 'd6', 'e7', 'h6', 'a3'},
             'f7': {'d5', 'c4', 'b3', 'e6', 'a2', 'h5', 'g8', 'e8', 'g6'},
             'f6': {'a1', 'g7', 'g5', 'e5', 'c3', 'd8', 'b2',
                    'h8', 'd4', 'e7', 'h4'},
             'f5': {'d3', 'g6', 'e6', 'h7', 'b1', 'c8', 'c2',
                    'd7', 'h3', 'e4', 'g4'},
             'f4': {'c1', 'b8', 'g5', 'e5', 'h2', 'g3', 'd6',
                    'e3', 'd2', 'c7', 'h6'},
             'f3': {'d5', 'd1', 'h1', 'e2', 'g4', 'g2', 'h5',
                    'c6', 'a8', 'e4', 'b7'},
             'f2': {'c5', 'b6', 'a7', 'h4', 'g3', 'g1', 'e3', 'd4', 'e1'},
             'f1': {'d3', 'c4', 'e2', 'b5', 'a6', 'g2', 'h3'},
             'g8': {'d5', 'c4', 'b3', 'f7', 'h7', 'e6', 'a2'},
             'g7': {'a1', 'f6', 'f8', 'e5', 'c3', 'b2', 'h8', 'd4', 'h6'},
             'g6': {'d3', 'f7', 'h7', 'b1', 'h5', 'f5', 'c2', 'e8', 'e4'},
             'g5': {'d2', 'c1', 'f6', 'd8', 'e3', 'f4', 'e7', 'h6', 'h4'},
             'g4': {'f3', 'e2', 'e6', 'h5', 'c8', 'f5', 'd7', 'h3', 'd1'},
             'g3': {'f2', 'b8', 'e5', 'h4', 'h2', 'd6', 'f4', 'c7', 'e1'},
             'g2': {'d5', 'f3', 'h1', 'f1', 'c6', 'a8', 'h3', 'e4', 'b7'},
             'g1': {'c5', 'f2', 'b6', 'a7', 'h2', 'e3', 'd4'},
             'h8': {'a1', 'g7', 'f6', 'e5', 'c3', 'b2', 'd4'},
             'h7': {'d3', 'b1', 'f5', 'c2', 'g8', 'e4', 'g6'},
             'h6': {'c1', 'g7', 'g5', 'f8', 'e3', 'f4', 'd2'},
             'h5': {'f3', 'e2', 'f7', 'g4', 'e8', 'd1', 'g6'},
             'h4': {'e1', 'f2', 'g5', 'f6', 'g3', 'd8', 'e7'},
             'h3': {'e6', 'f1', 'g2', 'c8', 'f5', 'd7', 'g4'},
             'h2': {'b8', 'e5', 'g3', 'd6', 'g1', 'f4', 'c7'},
             'h1': {'d5', 'f3', 'g2', 'c6', 'a8', 'e4', 'b7'}})


class KnightMoves(unittest.TestCase):

    def test_01_knight_moves(self):
        self.assertEqual(
            constants.KNIGHT_MOVES,
            {'a8': {'c7', 'b6'},
             'a7': {'b5', 'c6', 'c8'},
             'a6': {'b4', 'c5', 'c7', 'b8'},
             'a5': {'b3', 'c6', 'c4', 'b7'},
             'a4': {'c5', 'c3', 'b2', 'b6'},
             'a3': {'c2', 'b5', 'b1', 'c4'},
             'a2': {'b4', 'c3', 'c1'},
             'a1': {'c2', 'b3'},
             'b8': {'a6', 'd7', 'c6'},
             'b7': {'d8', 'c5', 'a5', 'd6'},
             'b6': {'d5', 'a4', 'c4', 'c8', 'a8', 'd7'},
             'b5': {'c3', 'a7', 'd6', 'd4', 'c7', 'a3'},
             'b4': {'d5', 'd3', 'a2', 'a6', 'c6', 'c2'},
             'b3': {'c5', 'c1', 'a1', 'a5', 'd4', 'd2'},
             'b2': {'d3', 'a4', 'c4', 'd1'},
             'b1': {'d2', 'c3', 'a3'},
             'c8': {'e7', 'a7', 'd6', 'b6'},
             'c7': {'d5', 'b5', 'e6', 'a6', 'a8', 'e8'},
             'c6': {'b8', 'e5', 'a7', 'a5', 'b4', 'd8', 'd4', 'e7'},
             'c5': {'d3', 'a4', 'b3', 'e6', 'a6', 'd7', 'e4', 'b7'},
             'c4': {'b6', 'e5', 'a5', 'd6', 'b2', 'e3', 'd2', 'a3'},
             'c3': {'d5', 'e4', 'a4', 'e2', 'b5', 'a2', 'b1', 'd1'},
             'c2': {'a1', 'b4', 'e3', 'd4', 'e1', 'a3'},
             'c1': {'b3', 'd3', 'a2', 'e2'},
             'd8': {'f7', 'c6', 'e6', 'b7'},
             'd7': {'c5', 'b8', 'e5', 'f6', 'f8', 'b6'},
             'd6': {'c4', 'b5', 'f7', 'c8', 'f5', 'e8', 'e4', 'b7'},
             'd5': {'e3', 'f6', 'c3', 'b4', 'b6', 'f4', 'e7', 'c7'},
             'd4': {'f3', 'e2', 'b3', 'b5', 'e6', 'c6', 'f5', 'c2'},
             'd3': {'f2', 'c5', 'c1', 'e5', 'b4', 'b2', 'f4', 'e1'},
             'd2': {'f3', 'c4', 'b3', 'f1', 'b1', 'e4'},
             'd1': {'f2', 'c3', 'b2', 'e3'},
             'e8': {'f6', 'c7', 'd6', 'g7'},
             'e7': {'d5', 'c6', 'c8', 'f5', 'g8', 'g6'},
             'e6': {'c5', 'g7', 'g5', 'f8', 'd8', 'd4', 'f4', 'c7'},
             'e5': {'f3', 'd3', 'c4', 'f7', 'g4', 'c6', 'd7', 'g6'},
             'e4': {'f2', 'c5', 'g5', 'f6', 'c3', 'g3', 'd6', 'd2'},
             'e3': {'d5', 'c4', 'f1', 'g2', 'f5', 'c2', 'd1', 'g4'},
             'e2': {'c1', 'c3', 'g3', 'g1', 'd4', 'f4'},
             'e1': {'c2', 'f3', 'g2', 'd3'},
             'f8': {'e6', 'd7', 'h7', 'g6'},
             'f7': {'g5', 'e5', 'd6', 'd8', 'h8', 'h6'},
             'f6': {'d5', 'h7', 'h5', 'g8', 'd7', 'e8', 'e4', 'g4'},
             'f5': {'g7', 'g3', 'd6', 'e3', 'd4', 'e7', 'h6', 'h4'},
             'f4': {'d5', 'd3', 'e2', 'e6', 'g2', 'h5', 'h3', 'g6'},
             'f3': {'e1', 'g5', 'e5', 'h2', 'g1', 'd4', 'd2', 'h4'},
             'f2': {'d3', 'e4', 'h1', 'h3', 'd1', 'g4'},
             'f1': {'h2', 'd2', 'g3', 'e3'},
             'g8': {'f6', 'e7', 'h6'},
             'g7': {'f5', 'h5', 'e8', 'e6'},
             'g6': {'e5', 'f8', 'h8', 'f4', 'e7', 'h4'},
             'g5': {'f3', 'f7', 'e6', 'h7', 'e4', 'h3'},
             'g4': {'f2', 'e5', 'f6', 'h2', 'e3', 'h6'},
             'g3': {'e2', 'h1', 'f1', 'h5', 'f5', 'e4'},
             'g2': {'f4', 'e1', 'e3', 'h4'},
             'g1': {'f3', 'e2', 'h3'},
             'h8': {'f7', 'g6'},
             'h7': {'g5', 'f6', 'f8'},
             'h6': {'f7', 'g8', 'f5', 'g4'},
             'h5': {'f4', 'f6', 'g3', 'g7'},
             'h4': {'f3', 'g2', 'f5', 'g6'},
             'h3': {'g5', 'f4', 'f2', 'g1'},
             'h2': {'f3', 'g4', 'f1'},
             'h1': {'f2', 'g3'}})


class KingMoves(unittest.TestCase):

    def test_01_king_moves(self):
        self.assertEqual(
            constants.KING_MOVES,
            {'a8': {'b8', 'a7', 'b7'},
             'a7': {'b8', 'a6', 'a8', 'b6', 'b7'},
             'a6': {'b5', 'a7', 'a5', 'b6', 'b7'},
             'a5': {'a4', 'b5', 'a6', 'b4', 'b6'},
             'a4': {'b3', 'b5', 'b4', 'a5', 'a3'},
             'a3': {'a4', 'b3', 'a2', 'b4', 'b2'},
             'a2': {'a1', 'b3', 'b1', 'b2', 'a3'},
             'a1': {'b1', 'b2', 'a2'},
             'b8': {'a7', 'c8', 'a8', 'c7', 'b7'},
             'b7': {'b8', 'a7', 'a6', 'c6', 'c8', 'b6', 'a8', 'c7'},
             'b6': {'c5', 'b5', 'a7', 'a6', 'a5', 'c6', 'c7', 'b7'},
             'b5': {'c5', 'a4', 'c4', 'a6', 'b4', 'a5', 'c6', 'b6'},
             'b4': {'c5', 'a4', 'c4', 'b3', 'b5', 'c3', 'a5', 'a3'},
             'b3': {'a4', 'c4', 'c3', 'a2', 'b4', 'b2', 'c2', 'a3'},
             'b2': {'c1', 'a1', 'b3', 'c3', 'a2', 'b1', 'c2', 'a3'},
             'b1': {'c1', 'a1', 'a2', 'b2', 'c2'},
             'c8': {'b8', 'd8', 'd7', 'c7', 'b7'},
             'c7': {'b8', 'd8', 'd6', 'b6', 'c6', 'c8', 'd7', 'b7'},
             'c6': {'d5', 'c5', 'b5', 'd6', 'b6', 'd7', 'c7', 'b7'},
             'c5': {'d5', 'c4', 'b5', 'b4', 'd6', 'c6', 'b6', 'd4'},
             'c4': {'d5', 'd3', 'c5', 'b3', 'b5', 'c3', 'b4', 'd4'},
             'c3': {'d3', 'c4', 'b3', 'b4', 'b2', 'c2', 'd4', 'd2'},
             'c2': {'d3', 'c1', 'b3', 'c3', 'b1', 'b2', 'd2', 'd1'},
             'c1': {'b1', 'b2', 'c2', 'd2', 'd1'},
             'd8': {'c7', 'e7', 'c8', 'd7', 'e8'},
             'd7': {'c7', 'e6', 'c6', 'd6', 'c8', 'd8', 'e7', 'e8'},
             'd6': {'d5', 'c5', 'd7', 'e5', 'e6', 'c6', 'e7', 'c7'},
             'd5': {'c5', 'c4', 'e5', 'e6', 'c6', 'd6', 'd4', 'e4'},
             'd4': {'d5', 'd3', 'c5', 'c4', 'e5', 'c3', 'e3', 'e4'},
             'd3': {'c4', 'e2', 'c3', 'e3', 'c2', 'd4', 'd2', 'e4'},
             'd2': {'d3', 'c1', 'e2', 'c3', 'e3', 'c2', 'd1', 'e1'},
             'd1': {'c1', 'e2', 'c2', 'd2', 'e1'},
             'e8': {'d7', 'f7', 'f8', 'd8', 'e7'},
             'e7': {'f6', 'f8', 'f7', 'e6', 'd6', 'd8', 'd7', 'e8'},
             'e6': {'d5', 'e7', 'e5', 'f6', 'f7', 'd6', 'f5', 'd7'},
             'e5': {'d5', 'f6', 'e6', 'd6', 'f5', 'd4', 'f4', 'e4'},
             'e4': {'d5', 'f3', 'd3', 'e5', 'f5', 'e3', 'd4', 'f4'},
             'e3': {'f3', 'd3', 'f2', 'e2', 'd4', 'f4', 'd2', 'e4'},
             'e2': {'f3', 'd3', 'f2', 'f1', 'e3', 'd2', 'd1', 'e1'},
             'e1': {'f2', 'e2', 'f1', 'd2', 'd1'},
             'f8': {'g7', 'f7', 'g8', 'e7', 'e8'},
             'f7': {'g7', 'e7', 'f6', 'f8', 'e6', 'g8', 'e8', 'g6'},
             'f6': {'g7', 'g5', 'e5', 'f7', 'e6', 'f5', 'e7', 'g6'},
             'f5': {'g5', 'e5', 'f6', 'e6', 'g4', 'f4', 'e4', 'g6'},
             'f4': {'f3', 'g5', 'e5', 'g3', 'f5', 'e3', 'e4', 'g4'},
             'f3': {'f2', 'e2', 'g2', 'g3', 'e3', 'f4', 'e4', 'g4'},
             'f2': {'f3', 'e2', 'f1', 'g2', 'g3', 'g1', 'e3', 'e1'},
             'f1': {'f2', 'e2', 'g2', 'g1', 'e1'},
             'g8': {'g7', 'f7', 'f8', 'h7', 'h8'},
             'g7': {'f6', 'f7', 'f8', 'h7', 'h8', 'g8', 'h6', 'g6'},
             'g6': {'g7', 'g5', 'f6', 'f7', 'h7', 'h5', 'f5', 'h6'},
             'g5': {'g6', 'f6', 'h4', 'h5', 'f5', 'f4', 'h6', 'g4'},
             'g4': {'f3', 'g5', 'h5', 'g3', 'f5', 'f4', 'h3', 'h4'},
             'g3': {'f3', 'f2', 'g4', 'g2', 'h2', 'f4', 'h3', 'h4'},
             'g2': {'f3', 'f2', 'h1', 'f1', 'h2', 'g3', 'g1', 'h3'},
             'g1': {'f2', 'h1', 'f1', 'g2', 'h2'},
             'h8': {'g8', 'h7', 'g7'},
             'h7': {'g7', 'h8', 'g8', 'h6', 'g6'},
             'h6': {'g7', 'g5', 'h7', 'h5', 'g6'},
             'h5': {'g6', 'g5', 'h4', 'h6', 'g4'},
             'h4': {'g5', 'h5', 'g3', 'h3', 'g4'},
             'h3': {'g4', 'g2', 'h2', 'g3', 'h4'},
             'h2': {'h1', 'g2', 'g3', 'g1', 'h3'},
             'h1': {'h2', 'g2', 'g1'}})


class EnPassant(unittest.TestCase):

    def test_01_en_passant_target_squares(self):
        self.assertEqual(
            constants.EN_PASSANT_TARGET_SQUARES,
            {'w': {('a5', 'a7'): 'a6',
                   ('b5', 'b7'): 'b6',
                   ('c5', 'c7'): 'c6',
                   ('d5', 'd7'): 'd6',
                   ('e5', 'e7'): 'e6',
                   ('f5', 'f7'): 'f6',
                   ('g5', 'g7'): 'g6',
                   ('h5', 'h7'): 'h6'},
             'b': {('a4', 'a2'): 'a3',
                   ('b4', 'b2'): 'b3',
                   ('c4', 'c2'): 'c3',
                   ('d4', 'd2'): 'd3',
                   ('e4', 'e2'): 'e3',
                   ('f4', 'f2'): 'f3',
                   ('g4', 'g2'): 'g3',
                   ('h4', 'h2'): 'h3'},
             'axb6': 'b5',
             'bxc6': 'c5',
             'bxa6': 'a5',
             'cxd6': 'd5',
             'cxb6': 'b5',
             'dxe6': 'e5',
             'dxc6': 'c5',
             'exf6': 'f5',
             'exd6': 'd5',
             'fxg6': 'g5',
             'fxe6': 'e5',
             'gxh6': 'h5',
             'gxf6': 'f5',
             'hxg6': 'g5',
             'axb3': 'b4',
             'bxc3': 'c4',
             'bxa3': 'a4',
             'cxd3': 'd4',
             'cxb3': 'b4',
             'dxe3': 'e4',
             'dxc3': 'c4',
             'exf3': 'f4',
             'exd3': 'd4',
             'fxg3': 'g4',
             'fxe3': 'e4',
             'gxh3': 'h4',
             'gxf3': 'f4',
             'hxg3': 'g4'})


class WhitePawnMoves(unittest.TestCase):

    def test_01_white_pawn_moves(self):
        self.assertEqual(
            constants.WHITE_PAWN_MOVES,
            {'a3': {'a2'}, 'a4': {'a2', 'a3'}, 'a5': {'a4'},
             'a6': {'a5'}, 'a7': {'a6'}, 'a8': {'a7'},
             'b3': {'b2'}, 'b4': {'b3', 'b2'}, 'b5': {'b4'},
             'b6': {'b5'}, 'b7': {'b6'}, 'b8': {'b7'},
             'c3': {'c2'}, 'c4': {'c2', 'c3'}, 'c5': {'c4'},
             'c6': {'c5'}, 'c7': {'c6'}, 'c8': {'c7'},
             'd3': {'d2'}, 'd4': {'d3', 'd2'}, 'd5': {'d4'},
             'd6': {'d5'}, 'd7': {'d6'}, 'd8': {'d7'},
             'e3': {'e2'}, 'e4': {'e2', 'e3'}, 'e5': {'e4'},
             'e6': {'e5'}, 'e7': {'e6'}, 'e8': {'e7'},
             'f3': {'f2'}, 'f4': {'f3', 'f2'}, 'f5': {'f4'},
             'f6': {'f5'}, 'f7': {'f6'}, 'f8': {'f7'},
             'g3': {'g2'}, 'g4': {'g2', 'g3'}, 'g5': {'g4'},
             'g6': {'g5'}, 'g7': {'g6'}, 'g8': {'g7'},
             'h3': {'h2'}, 'h4': {'h2', 'h3'}, 'h5': {'h4'},
             'h6': {'h5'}, 'h7': {'h6'}, 'h8': {'h7'}})


class BlackPawnMoves(unittest.TestCase):

    def test_01_white_pawn_moves(self):
        self.assertEqual(
            constants.BLACK_PAWN_MOVES,
            {'a6': {'a7'}, 'a5': {'a6', 'a7'}, 'a4': {'a5'},
             'a3': {'a4'}, 'a2': {'a3'}, 'a1': {'a2'},
             'b6': {'b7'}, 'b5': {'b7', 'b6'}, 'b4': {'b5'},
             'b3': {'b4'}, 'b2': {'b3'}, 'b1': {'b2'},
             'c6': {'c7'}, 'c5': {'c7', 'c6'}, 'c4': {'c5'},
             'c3': {'c4'}, 'c2': {'c3'}, 'c1': {'c2'},
             'd6': {'d7'}, 'd5': {'d7', 'd6'}, 'd4': {'d5'},
             'd3': {'d4'}, 'd2': {'d3'}, 'd1': {'d2'},
             'e6': {'e7'}, 'e5': {'e7', 'e6'}, 'e4': {'e5'},
             'e3': {'e4'}, 'e2': {'e3'}, 'e1': {'e2'},
             'f6': {'f7'}, 'f5': {'f6', 'f7'}, 'f4': {'f5'},
             'f3': {'f4'}, 'f2': {'f3'}, 'f1': {'f2'},
             'g6': {'g7'}, 'g5': {'g7', 'g6'}, 'g4': {'g5'},
             'g3': {'g4'}, 'g2': {'g3'}, 'g1': {'g2'},
             'h6': {'h7'}, 'h5': {'h7', 'h6'}, 'h4': {'h5'},
             'h3': {'h4'}, 'h2': {'h3'}, 'h1': {'h2'}})


class WhitePawnCaptures(unittest.TestCase):

    def test_01_white_pawn_captures(self):
        self.assertEqual(
            constants.WHITE_PAWN_CAPTURES,
            {'a3': {'b2'}, 'a4': {'b3'}, 'a5': {'b4'},
             'a6': {'b5'}, 'a7': {'b6'}, 'a8': {'b7'},
             'b3': {'c2', 'a2'}, 'b4': {'c3', 'a3'}, 'b5': {'a4', 'c4'},
             'b6': {'c5', 'a5'}, 'b7': {'a6', 'c6'}, 'b8': {'a7', 'c7'},
             'c3': {'d2', 'b2'}, 'c4': {'b3', 'd3'}, 'c5': {'d4', 'b4'},
             'c6': {'d5', 'b5'}, 'c7': {'d6', 'b6'}, 'c8': {'d7', 'b7'},
             'd3': {'c2', 'e2'}, 'd4': {'c3', 'e3'}, 'd5': {'c4', 'e4'},
             'd6': {'e5', 'c5'}, 'd7': {'c6', 'e6'}, 'd8': {'e7', 'c7'},
             'e3': {'d2', 'f2'}, 'e4': {'f3', 'd3'}, 'e5': {'d4', 'f4'},
             'e6': {'d5', 'f5'}, 'e7': {'f6', 'd6'}, 'e8': {'f7', 'd7'},
             'f3': {'g2', 'e2'}, 'f4': {'g3', 'e3'}, 'f5': {'e4', 'g4'},
             'f6': {'g5', 'e5'}, 'f7': {'e6', 'g6'}, 'f8': {'e7', 'g7'},
             'g3': {'h2', 'f2'}, 'g4': {'f3', 'h3'}, 'g5': {'f4', 'h4'},
             'g6': {'h5', 'f5'}, 'g7': {'f6', 'h6'}, 'g8': {'f7', 'h7'},
             'h3': {'g2'}, 'h4': {'g3'}, 'h5': {'g4'},
             'h6': {'g5'}, 'h7': {'g6'}, 'h8': {'g7'}})


class BlackPawnCaptures(unittest.TestCase):

    def test_01_white_pawn_captures(self):
        self.assertEqual(
            constants.BLACK_PAWN_CAPTURES,
            {'a1': {'b2'}, 'a2': {'b3'}, 'a3': {'b4'},
             'a4': {'b5'}, 'a5': {'b6'}, 'a6': {'b7'},
             'b1': {'c2', 'a2'}, 'b2': {'c3', 'a3'}, 'b3': {'a4', 'c4'},
             'b4': {'c5', 'a5'}, 'b5': {'a6', 'c6'}, 'b6': {'a7', 'c7'},
             'c1': {'d2', 'b2'}, 'c2': {'b3', 'd3'}, 'c3': {'d4', 'b4'},
             'c4': {'d5', 'b5'}, 'c5': {'d6', 'b6'}, 'c6': {'d7', 'b7'},
             'd1': {'c2', 'e2'}, 'd2': {'c3', 'e3'}, 'd3': {'c4', 'e4'},
             'd4': {'e5', 'c5'}, 'd5': {'c6', 'e6'}, 'd6': {'e7', 'c7'},
             'e1': {'d2', 'f2'}, 'e2': {'f3', 'd3'}, 'e3': {'d4', 'f4'},
             'e4': {'d5', 'f5'}, 'e5': {'f6', 'd6'}, 'e6': {'f7', 'd7'},
             'f1': {'g2', 'e2'}, 'f2': {'g3', 'e3'}, 'f3': {'e4', 'g4'},
             'f4': {'g5', 'e5'}, 'f5': {'e6', 'g6'}, 'f6': {'e7', 'g7'},
             'g1': {'h2', 'f2'}, 'g2': {'f3', 'h3'}, 'g3': {'f4', 'h4'},
             'g4': {'h5', 'f5'}, 'g5': {'f6', 'h6'}, 'g6': {'f7', 'h7'},
             'h1': {'g2'}, 'h2': {'g3'}, 'h3': {'g4'},
             'h4': {'g5'}, 'h5': {'g6'}, 'h6': {'g7'}})


class QueenMoves(unittest.TestCase):

    def test_01_queen_moves(self):
        self.assertEqual(
            constants.QUEEN_MOVES,
            {'a8': {'f3', 'h1', 'f8', 'a6', 'a5', 'g8', 'a3', 'd5', 'b7',
                    'a4', 'a1', 'b8', 'a7', 'a2', 'g2', 'd8', 'c8', 'c6',
                    'h8', 'e8', 'e4'},
             'a7': {'c5', 'f7', 'h7', 'a6', 'a5', 'b6', 'd4', 'd7', 'c7',
                    'a3', 'b7', 'a4', 'f2', 'a1', 'g7', 'b8', 'a2', 'g1',
                    'a8', 'e3', 'e7'},
             'a6': {'f1', 'a5', 'd6', 'b6', 'h6', 'a3', 'b7', 'd3', 'a4',
                    'c4', 'a1', 'e2', 'b5', 'f6', 'a7', 'a2', 'e6', 'c6',
                    'a8', 'c8', 'g6'},
             'a5': {'c5', 'c3', 'a6', 'h5', 'b4', 'b6', 'c7', 'a3', 'd5',
                    'a4', 'a1', 'b5', 'e5', 'g5', 'a7', 'a2', 'd8', 'a8',
                    'f5', 'd2', 'e1'},
             'a4': {'d1', 'b3', 'a6', 'a5', 'b4', 'd4', 'd7', 'a3', 'c4',
                    'a1', 'b5', 'a7', 'a2', 'h4', 'c6', 'a8', 'c2', 'f4',
                    'e8', 'e4', 'g4'},
             'a3': {'f3', 'c5', 'c1', 'b3', 'f8', 'c3', 'a6', 'a5', 'b4',
                    'b2', 'd6', 'd3', 'a4', 'a1', 'a7', 'a2', 'g3', 'a8',
                    'e3', 'e7', 'h3'},
             'a2': {'b3', 'f7', 'a6', 'b1', 'h2', 'a5', 'b2', 'g8', 'a3',
                    'd5', 'a4', 'f2', 'c4', 'a1', 'e2', 'a7', 'e6', 'g2',
                    'a8', 'c2', 'd2'},
             'a1': {'c1', 'h1', 'c3', 'f1', 'a6', 'b1', 'a5', 'b2', 'd4',
                    'a3', 'a4', 'g7', 'f6', 'e5', 'a7', 'a2', 'g1', 'a8',
                    'h8', 'd1', 'e1'},
             'b8': {'b3', 'f8', 'b1', 'h2', 'b4', 'b2', 'd6', 'b6', 'g8',
                    'c7', 'b7', 'b5', 'e5', 'a7', 'g3', 'd8', 'c8', 'a8',
                    'h8', 'f4', 'e8'},
             'b7': {'f3', 'h1', 'b3', 'f7', 'h7', 'a6', 'b1', 'b4', 'b2',
                    'b6', 'd7', 'c7', 'd5', 'b8', 'g7', 'b5', 'a7', 'g2',
                    'c6', 'a8', 'c8', 'e7', 'e4'},
             'b6': {'c5', 'e3', 'b3', 'a6', 'b1', 'b4', 'a5', 'b2', 'd6',
                    'd4', 'c7', 'h6', 'b7', 'f2', 'b8', 'b5', 'f6', 'a7',
                    'e6', 'c6', 'g1', 'd8', 'g6'},
             'b5': {'c5', 'b3', 'f1', 'a6', 'b1', 'b4', 'a5', 'b2', 'h5',
                    'b6', 'd7', 'b7', 'd5', 'd3', 'a4', 'c4', 'e2', 'b8',
                    'g5', 'e5', 'c6', 'f5', 'e8'},
             'b4': {'d2', 'c5', 'b3', 'f8', 'c3', 'b1', 'a5', 'b2', 'd6',
                    'b6', 'd4', 'e1', 'b7', 'a3', 'a4', 'c4', 'b8', 'b5',
                    'h4', 'f4', 'e7', 'e4', 'g4'},
             'b3': {'f3', 'f7', 'c3', 'b1', 'b4', 'b2', 'b6', 'g8', 'b7',
                    'a3', 'd3', 'd5', 'a4', 'c4', 'b8', 'b5', 'e6', 'a2',
                    'g3', 'e3', 'c2', 'd1', 'h3'},
             'b2': {'h8', 'c1', 'b3', 'c3', 'b1', 'h2', 'b4', 'b6', 'd4',
                    'b7', 'a3', 'f2', 'e2', 'b8', 'a1', 'b5', 'g7', 'f6',
                    'e5', 'a2', 'g2', 'c2', 'd2'},
             'b1': {'g6', 'e4', 'c1', 'h1', 'b3', 'h7', 'f1', 'b4', 'b2',
                    'b6', 'b7', 'd3', 'a1', 'b8', 'b5', 'a2', 'g1', 'f5',
                    'c2', 'd1', 'e1'},
             'c8': {'h8', 'c5', 'c1', 'f8', 'c3', 'a6', 'g8', 'c7', 'd7',
                    'b7', 'c4', 'b8', 'e6', 'g4', 'c6', 'd8', 'a8', 'c2',
                    'f5', 'e8', 'h3'},
             'c7': {'c5', 'c1', 'f7', 'c3', 'h7', 'h2', 'a5', 'd6', 'b6',
                    'd7', 'b7', 'c4', 'g7', 'b8', 'e5', 'a7', 'g3', 'c6',
                    'c8', 'd8', 'c2', 'f4', 'e7'},
             'c6': {'f3', 'c5', 'c1', 'h1', 'c3', 'a6', 'd6', 'b6', 'd7',
                    'c7', 'h6', 'b7', 'd5', 'a4', 'c4', 'b5', 'f6', 'e6',
                    'g2', 'c8', 'a8', 'c2', 'e8', 'e4', 'g6'},
             'c5': {'e3', 'c1', 'f8', 'c3', 'a5', 'h5', 'b4', 'd6', 'b6',
                    'd4', 'c7', 'a3', 'd5', 'f2', 'c4', 'b5', 'e5', 'g5',
                    'a7', 'c6', 'c8', 'f5', 'c2', 'g1', 'e7'},
             'c4': {'c5', 'c1', 'b3', 'f7', 'c3', 'f1', 'a6', 'b4', 'd4',
                    'g8', 'c7', 'd5', 'd3', 'a4', 'e2', 'b5', 'e6', 'a2',
                    'g4', 'c6', 'c8', 'c2', 'f4', 'e4', 'h4'},
             'c3': {'h8', 'f3', 'c5', 'c1', 'b3', 'b4', 'a5', 'b2', 'd4',
                    'e1', 'c7', 'a3', 'd3', 'c4', 'a1', 'g7', 'f6', 'e5',
                    'g3', 'c6', 'c8', 'e3', 'c2', 'd2', 'h3'},
             'c2': {'d1', 'c5', 'c1', 'b3', 'c3', 'h7', 'b1', 'h2', 'b2',
                    'c7', 'd3', 'f2', 'a4', 'c4', 'e2', 'a2', 'g2', 'c6',
                    'c8', 'f5', 'd2', 'e4', 'g6'},
             'c1': {'c5', 'e3', 'h1', 'c3', 'f1', 'b1', 'b2', 'c7', 'h6',
                    'a3', 'c4', 'a1', 'g5', 'c6', 'c8', 'g1', 'c2', 'f4',
                    'd2', 'd1', 'e1'},
             'd8': {'f8', 'a5', 'd6', 'b6', 'd4', 'd7', 'g8', 'c7', 'd5',
                    'd3', 'b8', 'g5', 'f6', 'e7', 'c8', 'a8', 'h8', 'd2',
                    'e8', 'd1', 'h4'},
             'd7': {'d2', 'f7', 'h7', 'd6', 'd4', 'c7', 'b7', 'd5', 'd3',
                    'a4', 'g7', 'b5', 'a7', 'e6', 'g4', 'd8', 'c8', 'f5',
                    'c6', 'e7', 'e8', 'd1', 'h3'},
             'd6': {'c5', 'f8', 'a6', 'h2', 'b4', 'b6', 'd4', 'd7', 'c7',
                    'h6', 'a3', 'd5', 'd3', 'b8', 'e7', 'f6', 'e5', 'e6',
                    'g3', 'd8', 'c6', 'f4', 'd2', 'd1', 'g6'},
             'd5': {'f3', 'e4', 'c5', 'h1', 'b3', 'f7', 'a5', 'h5', 'd6',
                    'd4', 'd7', 'g8', 'b7', 'd3', 'c4', 'b5', 'e5', 'g5',
                    'e6', 'a2', 'g2', 'd8', 'f5', 'c6', 'a8', 'd2', 'd1'},
             'd4': {'e4', 'c5', 'c3', 'b4', 'd6', 'b2', 'b6', 'd7', 'd5',
                    'd3', 'a4', 'f2', 'c4', 'a1', 'g7', 'f6', 'e5', 'a7',
                    'g4', 'd8', 'g1', 'e3', 'h8', 'f4', 'd2', 'd1', 'h4'},
             'd3': {'f3', 'e4', 'g6', 'b3', 'c3', 'h7', 'f1', 'a6', 'b1',
                    'd6', 'd4', 'd7', 'a3', 'd5', 'c4', 'e2', 'b5', 'g3',
                    'd8', 'f5', 'e3', 'c2', 'd2', 'd1', 'h3'},
             'd2': {'c1', 'c3', 'h2', 'b4', 'a5', 'd6', 'b2', 'd4', 'd7',
                    'h6', 'd5', 'd3', 'f2', 'e2', 'g5', 'a2', 'g2', 'd8',
                    'e3', 'c2', 'f4', 'd1', 'e1'},
             'd1': {'f3', 'c1', 'h1', 'b3', 'f1', 'b1', 'h5', 'd6', 'd4',
                    'd7', 'd5', 'd3', 'a4', 'a1', 'e2', 'g4', 'd8', 'g1',
                    'c2', 'd2', 'e1'},
             'e8': {'g6', 'f7', 'f8', 'h5', 'g8', 'd7', 'a4', 'e2', 'b8',
                    'b5', 'e5', 'e6', 'd8', 'c8', 'e3', 'h8', 'a8', 'c6',
                    'e7', 'e4', 'e1'},
             'e7': {'c5', 'f7', 'f8', 'h7', 'b4', 'd6', 'd7', 'c7', 'b7',
                    'a3', 'e2', 'g7', 'g5', 'e5', 'f6', 'a7', 'e6', 'h4',
                    'd8', 'e3', 'e8', 'e4', 'e1'},
             'e6': {'g6', 'b3', 'f7', 'a6', 'd6', 'b6', 'g8', 'd7', 'h3',
                    'h6', 'd5', 'c4', 'e2', 'e5', 'f6', 'a2', 'g4', 'c6',
                    'c8', 'e3', 'f5', 'e7', 'e8', 'e4', 'e1'},
             'e5': {'c5', 'c3', 'h2', 'a5', 'h5', 'd6', 'b2', 'd4', 'c7',
                    'd5', 'e2', 'a1', 'b8', 'b5', 'g5', 'g7', 'f6', 'e6',
                    'g3', 'f5', 'e3', 'h8', 'f4', 'e7', 'e8', 'e4', 'e1'},
             'e4': {'f3', 'g6', 'h1', 'h7', 'b1', 'b4', 'd4', 'b7', 'd5',
                    'd3', 'c2', 'a4', 'c4', 'e2', 'e5', 'e6', 'g4', 'h4',
                    'g2', 'c6', 'a8', 'e3', 'f5', 'f4', 'e7', 'e8', 'e1'},
             'e3': {'f3', 'd2', 'c5', 'c1', 'b3', 'c3', 'b6', 'd4', 'h3',
                    'h6', 'a3', 'd3', 'f2', 'e2', 'g5', 'e5', 'a7', 'e6',
                    'g3', 'g1', 'f4', 'e7', 'e8', 'e4', 'e1'},
             'e2': {'d2', 'f3', 'd1', 'f1', 'a6', 'h2', 'h5', 'b2', 'd3',
                    'f2', 'c4', 'b5', 'e5', 'e6', 'a2', 'g4', 'g2', 'e3',
                    'c2', 'e7', 'e8', 'e4', 'e1'},
             'e1': {'d1', 'd2', 'c1', 'h1', 'c3', 'f1', 'b1', 'b4', 'a5',
                    'f2', 'e2', 'a1', 'e5', 'e6', 'g3', 'g1', 'e3', 'e7',
                    'e8', 'e4', 'h4'},
             'f8': {'f3', 'c5', 'f7', 'f1', 'b4', 'd6', 'g8', 'h6', 'a3',
                    'f2', 'b8', 'g7', 'f6', 'd8', 'f5', 'c8', 'h8', 'a8',
                    'f4', 'e7', 'e8'},
             'f7': {'f3', 'b3', 'f8', 'h7', 'f1', 'h5', 'd7', 'c7', 'g8',
                    'b7', 'd5', 'f2', 'c4', 'g7', 'f6', 'a7', 'e6', 'a2',
                    'f5', 'f4', 'e7', 'e8', 'g6'},
             'f6': {'f3', 'f7', 'f8', 'c3', 'f1', 'a6', 'd6', 'b2', 'b6',
                    'd4', 'h6', 'f2', 'a1', 'g7', 'g5', 'e5', 'e6', 'h4',
                    'c6', 'f5', 'd8', 'h8', 'f4', 'e7', 'g6'},
             'f5': {'f3', 'c5', 'f7', 'f8', 'h7', 'f1', 'b1', 'a5', 'h5',
                    'd7', 'h3', 'd5', 'd3', 'f2', 'b5', 'f6', 'e5', 'g5',
                    'e6', 'g4', 'c8', 'c2', 'f4', 'e4', 'g6'},
             'f4': {'f3', 'c1', 'f7', 'f8', 'f1', 'h2', 'b4', 'd6', 'd4',
                    'c7', 'h6', 'f2', 'a4', 'c4', 'b8', 'g5', 'f6', 'e5',
                    'g4', 'g3', 'f5', 'e3', 'd2', 'e4', 'h4'},
             'f3': {'e4', 'h1', 'b3', 'f7', 'f8', 'c3', 'f1', 'h5', 'a3',
                    'd5', 'd3', 'b7', 'f2', 'e2', 'f6', 'g4', 'g2', 'g3',
                    'c6', 'f5', 'e3', 'a8', 'f4', 'd1', 'h3'},
             'f2': {'f3', 'c5', 'f7', 'f8', 'f1', 'h2', 'b2', 'b6', 'd4',
                    'e1', 'e2', 'f6', 'a7', 'a2', 'g2', 'g3', 'g1', 'f5',
                    'e3', 'c2', 'f4', 'd2', 'h4'},
             'f1': {'f3', 'c1', 'h1', 'f7', 'f8', 'a6', 'b1', 'h3', 'd3',
                    'f2', 'c4', 'a1', 'e2', 'b5', 'f6', 'g2', 'g1', 'f5',
                    'f4', 'd1', 'e1'},
             'g8': {'g6', 'b3', 'f7', 'f8', 'h7', 'd5', 'c4', 'g7', 'b8',
                    'g5', 'e6', 'a2', 'g2', 'g3', 'g1', 'd8', 'c8', 'h8',
                    'a8', 'e8', 'g4'},
             'g7': {'g6', 'f7', 'f8', 'c3', 'h7', 'b2', 'd4', 'g8', 'd7',
                    'c7', 'h6', 'b7', 'a1', 'g5', 'f6', 'e5', 'a7', 'g2',
                    'g3', 'g1', 'h8', 'e7', 'g4'},
             'g6': {'f7', 'h7', 'a6', 'b1', 'h5', 'd6', 'b6', 'g8', 'h6',
                    'd3', 'g7', 'g5', 'f6', 'e6', 'g2', 'g3', 'g1', 'c6',
                    'f5', 'c2', 'e8', 'e4', 'g4'},
             'g5': {'g6', 'c5', 'e3', 'c1', 'a5', 'h5', 'g8', 'h6', 'd5',
                    'g7', 'b5', 'e5', 'f6', 'e7', 'h4', 'g2', 'g3', 'g1',
                    'f5', 'd8', 'f4', 'd2', 'g4'},
             'g4': {'g6', 'f3', 'd1', 'b4', 'h5', 'd4', 'g8', 'd7', 'h3',
                    'a4', 'c4', 'e2', 'g7', 'g5', 'e6', 'g2', 'g3', 'g1',
                    'c8', 'f5', 'f4', 'e4', 'h4'},
             'g3': {'f3', 'g6', 'b3', 'c3', 'h2', 'd6', 'g8', 'c7', 'h3',
                    'e1', 'a3', 'd3', 'f2', 'g7', 'b8', 'g5', 'e5', 'h4',
                    'g2', 'g1', 'e3', 'f4', 'g4'},
             'g2': {'g6', 'f3', 'h1', 'f1', 'h2', 'b2', 'g8', 'h3', 'b7',
                    'd5', 'f2', 'e2', 'g7', 'g5', 'a2', 'g3', 'g1', 'c6',
                    'a8', 'c2', 'd2', 'e4', 'g4'},
             'g1': {'g6', 'c5', 'c1', 'h1', 'f1', 'b1', 'h2', 'b6', 'd4',
                    'g8', 'e1', 'f2', 'a1', 'g7', 'g5', 'a7', 'g2', 'g3',
                    'e3', 'd1', 'g4'},
             'h8': {'h1', 'f8', 'c3', 'h7', 'h2', 'h5', 'b2', 'd4', 'g8',
                    'h3', 'h6', 'a1', 'b8', 'g7', 'f6', 'e5', 'd8', 'c8',
                    'a8', 'e8', 'h4'},
             'h7': {'g6', 'h1', 'f7', 'b1', 'h2', 'h5', 'd7', 'c7', 'h3',
                    'h6', 'b7', 'c2', 'd3', 'g8', 'g7', 'a7', 'f5', 'h8',
                    'e7', 'e4', 'h4'},
             'h6': {'g6', 'c1', 'h1', 'f8', 'h7', 'a6', 'h2', 'h5', 'd6',
                    'b6', 'h3', 'g7', 'g5', 'f6', 'e6', 'c6', 'e3', 'h8',
                    'f4', 'd2', 'h4'},
             'h5': {'f3', 'g6', 'c5', 'h1', 'f7', 'h7', 'h2', 'a5', 'h3',
                    'h6', 'd5', 'e2', 'b5', 'e5', 'g5', 'g4', 'f5', 'h8',
                    'e8', 'd1', 'h4'},
             'h4': {'h1', 'h7', 'h2', 'h5', 'b4', 'd4', 'e1', 'h6', 'a4',
                    'f2', 'c4', 'g5', 'f6', 'g4', 'g3', 'd8', 'h8', 'f4',
                    'e7', 'e4', 'h3'},
             'h3': {'f3', 'h1', 'b3', 'c3', 'h7', 'f1', 'h2', 'h5', 'd7',
                    'h6', 'a3', 'd3', 'e6', 'g4', 'g2', 'g3', 'c8', 'f5',
                    'e3', 'h8', 'h4'},
             'h2': {'h1', 'h7', 'h5', 'b2', 'd6', 'c7', 'h3', 'h6', 'c2',
                    'f2', 'e2', 'b8', 'e5', 'a2', 'g2', 'g3', 'g1', 'h8',
                    'f4', 'd2', 'h4'},
             'h1': {'f3', 'e4', 'c1', 'h7', 'f1', 'b1', 'h2', 'h5', 'e1',
                    'h3', 'h6', 'b7', 'd5', 'a1', 'g2', 'g1', 'c6', 'a8',
                    'h8', 'd1', 'h4'}})


class PointToPoint(unittest.TestCase):

    def verify_square_combination(self, sq1, sq2):
        ae = self.assertEqual
        ptp = constants.POINT_TO_POINT
        if sq1 == sq2:
            ae((sq1, sq2) in ptp, False,
               ' '.join((repr((sq1, sq2)), 'in POINT_TO_POINT')))
            return
        f1, r1 = sq1
        f2, r2 = sq2
        if not ((f1 == f2 or
                 r1 == r2 or
                 (ord(f1) + ord(r1) == ord(f2) + ord(r2)) or
                 (ord(f1) - ord(r1) == ord(f2) - ord(r2)))):
            ae((sq1, sq2) in ptp, False,
               ' '.join((repr((sq1, sq2)), 'in POINT_TO_POINT')))
            return
        ref = ptp[sq1, sq2]
        ae(ref is ptp[sq2, sq1], True,
           ' '.join((repr((sq1, sq2)), 'is not', repr((sq2, sq1)),
                      'in POINT_TO_POINT')))
        if f1 == f2:
            ae(ref[2] is constants.FILE_ATTACKS[sq1][1], True,
               ' '.join(('POINT_TO_POINT'+repr([sq1, sq2])+'[2]', 'is not',
                         ''.join(('FILE_ATTACKS[', sq1, '][1]')),
                          )))
        elif r1 == r2:
            ae(ref[2] is constants.RANK_ATTACKS[sq1][1], True,
               ' '.join(('POINT_TO_POINT'+repr([sq1, sq2])+'[2]', 'is not',
                         ''.join(('RANK_ATTACKS[', sq1, '][1]')),
                          )))
        elif ord(f1) + ord(r1) == ord(f2) + ord(r2):
            ae(ref[2] is constants.LRD_DIAGONAL_ATTACKS[sq1][1], True,
               ' '.join(('POINT_TO_POINT'+repr([sq1, sq2])+'[2]', 'is not',
                         ''.join(('LRD_DIAGONAL_ATTACKS[', sq1, '][1]')),
                          )))
        elif ord(f1) - ord(r1) == ord(f2) - ord(r2):
            ae(ref[2] is constants.RLD_DIAGONAL_ATTACKS[sq1][1], True,
               ' '.join(('POINT_TO_POINT'+repr([sq1, sq2])+'[2]', 'is not',
                         ''.join(('RLD_DIAGONAL_ATTACKS[', sq1, '][1]')),
                          )))
        else:
            ae(True, False,
               ' '.join((repr((sq1, sq2)), 'unknown line in POINT_TO_POINT')))
        isq1 = ref[2].index(sq1)
        isq2 = ref[2].index(sq2)
        if isq2 > isq1:
            ae(ref[2].index(sq1), ref[0] - 1,
               ' '.join(('POINT_TO_POINT'+repr([sq1, sq2])+'[0]',
                         'does not fit position of', sq1, 'in',
                         'POINT_TO_POINT'+repr([sq1, sq2])+'[2]')))
            ae(ref[2].index(sq2), ref[1],
               ' '.join(('POINT_TO_POINT'+repr([sq1, sq2])+'[1]',
                         'does not fit position of', sq2, 'in',
                         'POINT_TO_POINT'+repr([sq1, sq2])+'[2]')))
        else:
            ae(ref[2].index(sq2), ref[0] - 1,
               ' '.join(('POINT_TO_POINT'+repr([sq1, sq2])+'[0]',
                         'does not fit position of', sq1, 'in',
                         'POINT_TO_POINT'+repr([sq1, sq2])+'[2]')))
            ae(ref[2].index(sq1), ref[1],
               ' '.join(('POINT_TO_POINT'+repr([sq1, sq2])+'[1]',
                         'does not fit position of', sq2, 'in',
                         'POINT_TO_POINT'+repr([sq1, sq2])+'[2]')))

    def test_01_point_to_point(self):
        fn = constants.FILE_NAMES
        rn = constants.RANK_NAMES
        for ef, f in enumerate(fn):
            for er, r in enumerate(rn):
                sq1 = f + r
                self.verify_square_combination(sq1, sq1)
                for fi in range(ef+1):
                    for ri in range(er+1):
                        sq2 = fn[fi] + rn[ri]
                        self.verify_square_combination(sq1, sq2)


class RankAttacks(unittest.TestCase):

    def test_01_rank_attacks(self):
        self.assertEqual(
            constants.RANK_ATTACKS,
            {'a8': (0, ('a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8')),
             'b8': (1, ('a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8')),
             'c8': (2, ('a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8')),
             'd8': (3, ('a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8')),
             'e8': (4, ('a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8')),
             'f8': (5, ('a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8')),
             'g8': (6, ('a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8')),
             'h8': (7, ('a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8')),
             'a7': (0, ('a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7')),
             'b7': (1, ('a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7')),
             'c7': (2, ('a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7')),
             'd7': (3, ('a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7')),
             'e7': (4, ('a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7')),
             'f7': (5, ('a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7')),
             'g7': (6, ('a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7')),
             'h7': (7, ('a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7')),
             'a6': (0, ('a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6')),
             'b6': (1, ('a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6')),
             'c6': (2, ('a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6')),
             'd6': (3, ('a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6')),
             'e6': (4, ('a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6')),
             'f6': (5, ('a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6')),
             'g6': (6, ('a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6')),
             'h6': (7, ('a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6')),
             'a5': (0, ('a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5')),
             'b5': (1, ('a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5')),
             'c5': (2, ('a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5')),
             'd5': (3, ('a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5')),
             'e5': (4, ('a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5')),
             'f5': (5, ('a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5')),
             'g5': (6, ('a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5')),
             'h5': (7, ('a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5')),
             'a4': (0, ('a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4')),
             'b4': (1, ('a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4')),
             'c4': (2, ('a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4')),
             'd4': (3, ('a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4')),
             'e4': (4, ('a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4')),
             'f4': (5, ('a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4')),
             'g4': (6, ('a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4')),
             'h4': (7, ('a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4')),
             'a3': (0, ('a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3')),
             'b3': (1, ('a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3')),
             'c3': (2, ('a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3')),
             'd3': (3, ('a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3')),
             'e3': (4, ('a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3')),
             'f3': (5, ('a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3')),
             'g3': (6, ('a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3')),
             'h3': (7, ('a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3')),
             'a2': (0, ('a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2')),
             'b2': (1, ('a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2')),
             'c2': (2, ('a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2')),
             'd2': (3, ('a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2')),
             'e2': (4, ('a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2')),
             'f2': (5, ('a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2')),
             'g2': (6, ('a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2')),
             'h2': (7, ('a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2')),
             'a1': (0, ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1')),
             'b1': (1, ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1')),
             'c1': (2, ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1')),
             'd1': (3, ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1')),
             'e1': (4, ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1')),
             'f1': (5, ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1')),
             'g1': (6, ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1')),
             'h1': (7, ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'))})

    def test_02_rank_attacks(self):
        ae = self.assertEqual
        ra = constants.RANK_ATTACKS
        for k, v in ra.items():
            ref = v[1][0]
            ae(ra[k][1] is ra[ref][1], True,
               ' '.join(('RANK_ATTACKS['+k+'][1]', 'is not',
                         'RANK_ATTACKS['+ref+'][1]')))


class FileAttacks(unittest.TestCase):

    def test_01_file_attacks(self):
        self.assertEqual(
            constants.FILE_ATTACKS,
            {'a1': (0, ('a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8')),
             'a2': (1, ('a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8')),
             'a3': (2, ('a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8')),
             'a4': (3, ('a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8')),
             'a5': (4, ('a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8')),
             'a6': (5, ('a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8')),
             'a7': (6, ('a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8')),
             'a8': (7, ('a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8')),
             'b1': (0, ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8')),
             'b2': (1, ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8')),
             'b3': (2, ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8')),
             'b4': (3, ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8')),
             'b5': (4, ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8')),
             'b6': (5, ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8')),
             'b7': (6, ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8')),
             'b8': (7, ('b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8')),
             'c1': (0, ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')),
             'c2': (1, ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')),
             'c3': (2, ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')),
             'c4': (3, ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')),
             'c5': (4, ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')),
             'c6': (5, ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')),
             'c7': (6, ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')),
             'c8': (7, ('c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8')),
             'd1': (0, ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8')),
             'd2': (1, ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8')),
             'd3': (2, ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8')),
             'd4': (3, ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8')),
             'd5': (4, ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8')),
             'd6': (5, ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8')),
             'd7': (6, ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8')),
             'd8': (7, ('d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8')),
             'e1': (0, ('e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8')),
             'e2': (1, ('e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8')),
             'e3': (2, ('e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8')),
             'e4': (3, ('e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8')),
             'e5': (4, ('e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8')),
             'e6': (5, ('e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8')),
             'e7': (6, ('e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8')),
             'e8': (7, ('e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8')),
             'f1': (0, ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8')),
             'f2': (1, ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8')),
             'f3': (2, ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8')),
             'f4': (3, ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8')),
             'f5': (4, ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8')),
             'f6': (5, ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8')),
             'f7': (6, ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8')),
             'f8': (7, ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8')),
             'g1': (0, ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8')),
             'g2': (1, ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8')),
             'g3': (2, ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8')),
             'g4': (3, ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8')),
             'g5': (4, ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8')),
             'g6': (5, ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8')),
             'g7': (6, ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8')),
             'g8': (7, ('g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8')),
             'h1': (0, ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')),
             'h2': (1, ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')),
             'h3': (2, ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')),
             'h4': (3, ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')),
             'h5': (4, ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')),
             'h6': (5, ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')),
             'h7': (6, ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8')),
             'h8': (7, ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'))})

    def test_02_file_attacks(self):
        ae = self.assertEqual
        fa = constants.FILE_ATTACKS
        for k, v in fa.items():
            ref = v[1][0]
            ae(fa[k][1] is fa[ref][1], True,
               ' '.join(('FILE_ATTACKS['+k+'][1]', 'is not',
                         'FILE_ATTACKS['+ref+'][1]')))


class LeftRightDownDiagonalAttacks(unittest.TestCase):

    def test_01_lrd_diagonal_attacks(self):
        self.assertEqual(
            constants.LRD_DIAGONAL_ATTACKS,
            {'a8': (0, ('a8', 'b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1')),
             'b7': (1, ('a8', 'b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1')),
             'c6': (2, ('a8', 'b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1')),
             'd5': (3, ('a8', 'b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1')),
             'e4': (4, ('a8', 'b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1')),
             'f3': (5, ('a8', 'b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1')),
             'g2': (6, ('a8', 'b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1')),
             'h1': (7, ('a8', 'b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1')),
             'b8': (0, ('b8', 'c7', 'd6', 'e5', 'f4', 'g3', 'h2')),
             'c7': (1, ('b8', 'c7', 'd6', 'e5', 'f4', 'g3', 'h2')),
             'd6': (2, ('b8', 'c7', 'd6', 'e5', 'f4', 'g3', 'h2')),
             'e5': (3, ('b8', 'c7', 'd6', 'e5', 'f4', 'g3', 'h2')),
             'f4': (4, ('b8', 'c7', 'd6', 'e5', 'f4', 'g3', 'h2')),
             'g3': (5, ('b8', 'c7', 'd6', 'e5', 'f4', 'g3', 'h2')),
             'h2': (6, ('b8', 'c7', 'd6', 'e5', 'f4', 'g3', 'h2')),
             'c8': (0, ('c8', 'd7', 'e6', 'f5', 'g4', 'h3')),
             'd7': (1, ('c8', 'd7', 'e6', 'f5', 'g4', 'h3')),
             'e6': (2, ('c8', 'd7', 'e6', 'f5', 'g4', 'h3')),
             'f5': (3, ('c8', 'd7', 'e6', 'f5', 'g4', 'h3')),
             'g4': (4, ('c8', 'd7', 'e6', 'f5', 'g4', 'h3')),
             'h3': (5, ('c8', 'd7', 'e6', 'f5', 'g4', 'h3')),
             'd8': (0, ('d8', 'e7', 'f6', 'g5', 'h4')),
             'e7': (1, ('d8', 'e7', 'f6', 'g5', 'h4')),
             'f6': (2, ('d8', 'e7', 'f6', 'g5', 'h4')),
             'g5': (3, ('d8', 'e7', 'f6', 'g5', 'h4')),
             'h4': (4, ('d8', 'e7', 'f6', 'g5', 'h4')),
             'e8': (0, ('e8', 'f7', 'g6', 'h5')),
             'f7': (1, ('e8', 'f7', 'g6', 'h5')),
             'g6': (2, ('e8', 'f7', 'g6', 'h5')),
             'h5': (3, ('e8', 'f7', 'g6', 'h5')),
             'f8': (0, ('f8', 'g7', 'h6')),
             'g7': (1, ('f8', 'g7', 'h6')),
             'h6': (2, ('f8', 'g7', 'h6')),
             'g8': (0, ('g8', 'h7')),
             'h7': (1, ('g8', 'h7')),
             'h8': (0, ('h8',)),
             'a7': (0, ('a7', 'b6', 'c5', 'd4', 'e3', 'f2', 'g1')),
             'b6': (1, ('a7', 'b6', 'c5', 'd4', 'e3', 'f2', 'g1')),
             'c5': (2, ('a7', 'b6', 'c5', 'd4', 'e3', 'f2', 'g1')),
             'd4': (3, ('a7', 'b6', 'c5', 'd4', 'e3', 'f2', 'g1')),
             'e3': (4, ('a7', 'b6', 'c5', 'd4', 'e3', 'f2', 'g1')),
             'f2': (5, ('a7', 'b6', 'c5', 'd4', 'e3', 'f2', 'g1')),
             'g1': (6, ('a7', 'b6', 'c5', 'd4', 'e3', 'f2', 'g1')),
             'a6': (0, ('a6', 'b5', 'c4', 'd3', 'e2', 'f1')),
             'b5': (1, ('a6', 'b5', 'c4', 'd3', 'e2', 'f1')),
             'c4': (2, ('a6', 'b5', 'c4', 'd3', 'e2', 'f1')),
             'd3': (3, ('a6', 'b5', 'c4', 'd3', 'e2', 'f1')),
             'e2': (4, ('a6', 'b5', 'c4', 'd3', 'e2', 'f1')),
             'f1': (5, ('a6', 'b5', 'c4', 'd3', 'e2', 'f1')),
             'a5': (0, ('a5', 'b4', 'c3', 'd2', 'e1')),
             'b4': (1, ('a5', 'b4', 'c3', 'd2', 'e1')),
             'c3': (2, ('a5', 'b4', 'c3', 'd2', 'e1')),
             'd2': (3, ('a5', 'b4', 'c3', 'd2', 'e1')),
             'e1': (4, ('a5', 'b4', 'c3', 'd2', 'e1')),
             'a4': (0, ('a4', 'b3', 'c2', 'd1')),
             'b3': (1, ('a4', 'b3', 'c2', 'd1')),
             'c2': (2, ('a4', 'b3', 'c2', 'd1')),
             'd1': (3, ('a4', 'b3', 'c2', 'd1')),
             'a3': (0, ('a3', 'b2', 'c1')),
             'b2': (1, ('a3', 'b2', 'c1')),
             'c1': (2, ('a3', 'b2', 'c1')),
             'a2': (0, ('a2', 'b1')),
             'b1': (1, ('a2', 'b1')),
             'a1': (0, ('a1',))})

    def test_02_lrd_diagonal_attacks(self):
        ae = self.assertEqual
        lrda = constants.LRD_DIAGONAL_ATTACKS
        for k, v in lrda.items():
            ref = v[1][0]
            ae(lrda[k][1] is lrda[ref][1], True,
               ' '.join(('LRD_DIAGONAL_ATTACKS['+k+'][1]', 'is not',
                         'LRD_DIAGONAL_ATTACKS['+ref+'][1]')))


class RightLeftDownDiagonalAttacks(unittest.TestCase):

    def test_01_rld_diagonal_attacks(self):
        self.assertEqual(
            constants.RLD_DIAGONAL_ATTACKS,
            {'a8': (0, ('a8',)),
             'a7': (0, ('a7', 'b8')),
             'b8': (1, ('a7', 'b8')),
             'a6': (0, ('a6', 'b7', 'c8')),
             'b7': (1, ('a6', 'b7', 'c8')),
             'c8': (2, ('a6', 'b7', 'c8')),
             'a5': (0, ('a5', 'b6', 'c7', 'd8')),
             'b6': (1, ('a5', 'b6', 'c7', 'd8')),
             'c7': (2, ('a5', 'b6', 'c7', 'd8')),
             'd8': (3, ('a5', 'b6', 'c7', 'd8')),
             'a4': (0, ('a4', 'b5', 'c6', 'd7', 'e8')),
             'b5': (1, ('a4', 'b5', 'c6', 'd7', 'e8')),
             'c6': (2, ('a4', 'b5', 'c6', 'd7', 'e8')),
             'd7': (3, ('a4', 'b5', 'c6', 'd7', 'e8')),
             'e8': (4, ('a4', 'b5', 'c6', 'd7', 'e8')),
             'a3': (0, ('a3', 'b4', 'c5', 'd6', 'e7', 'f8')),
             'b4': (1, ('a3', 'b4', 'c5', 'd6', 'e7', 'f8')),
             'c5': (2, ('a3', 'b4', 'c5', 'd6', 'e7', 'f8')),
             'd6': (3, ('a3', 'b4', 'c5', 'd6', 'e7', 'f8')),
             'e7': (4, ('a3', 'b4', 'c5', 'd6', 'e7', 'f8')),
             'f8': (5, ('a3', 'b4', 'c5', 'd6', 'e7', 'f8')),
             'a2': (0, ('a2', 'b3', 'c4', 'd5', 'e6', 'f7', 'g8')),
             'b3': (1, ('a2', 'b3', 'c4', 'd5', 'e6', 'f7', 'g8')),
             'c4': (2, ('a2', 'b3', 'c4', 'd5', 'e6', 'f7', 'g8')),
             'd5': (3, ('a2', 'b3', 'c4', 'd5', 'e6', 'f7', 'g8')),
             'e6': (4, ('a2', 'b3', 'c4', 'd5', 'e6', 'f7', 'g8')),
             'f7': (5, ('a2', 'b3', 'c4', 'd5', 'e6', 'f7', 'g8')),
             'g8': (6, ('a2', 'b3', 'c4', 'd5', 'e6', 'f7', 'g8')),
             'a1': (0, ('a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8')),
             'b2': (1, ('a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8')),
             'c3': (2, ('a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8')),
             'd4': (3, ('a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8')),
             'e5': (4, ('a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8')),
             'f6': (5, ('a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8')),
             'g7': (6, ('a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8')),
             'h8': (7, ('a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8')),
             'h1': (0, ('h1',)),
             'g1': (0, ('g1', 'h2')),
             'h2': (1, ('g1', 'h2')),
             'f1': (0, ('f1', 'g2', 'h3')),
             'g2': (1, ('f1', 'g2', 'h3')),
             'h3': (2, ('f1', 'g2', 'h3')),
             'e1': (0, ('e1', 'f2', 'g3', 'h4')),
             'f2': (1, ('e1', 'f2', 'g3', 'h4')),
             'g3': (2, ('e1', 'f2', 'g3', 'h4')),
             'h4': (3, ('e1', 'f2', 'g3', 'h4')),
             'd1': (0, ('d1', 'e2', 'f3', 'g4', 'h5')),
             'e2': (1, ('d1', 'e2', 'f3', 'g4', 'h5')),
             'f3': (2, ('d1', 'e2', 'f3', 'g4', 'h5')),
             'g4': (3, ('d1', 'e2', 'f3', 'g4', 'h5')),
             'h5': (4, ('d1', 'e2', 'f3', 'g4', 'h5')),
             'c1': (0, ('c1', 'd2', 'e3', 'f4', 'g5', 'h6')),
             'd2': (1, ('c1', 'd2', 'e3', 'f4', 'g5', 'h6')),
             'e3': (2, ('c1', 'd2', 'e3', 'f4', 'g5', 'h6')),
             'f4': (3, ('c1', 'd2', 'e3', 'f4', 'g5', 'h6')),
             'g5': (4, ('c1', 'd2', 'e3', 'f4', 'g5', 'h6')),
             'h6': (5, ('c1', 'd2', 'e3', 'f4', 'g5', 'h6')),
             'b1': (0, ('b1', 'c2', 'd3', 'e4', 'f5', 'g6', 'h7')),
             'c2': (1, ('b1', 'c2', 'd3', 'e4', 'f5', 'g6', 'h7')),
             'd3': (2, ('b1', 'c2', 'd3', 'e4', 'f5', 'g6', 'h7')),
             'e4': (3, ('b1', 'c2', 'd3', 'e4', 'f5', 'g6', 'h7')),
             'f5': (4, ('b1', 'c2', 'd3', 'e4', 'f5', 'g6', 'h7')),
             'g6': (5, ('b1', 'c2', 'd3', 'e4', 'f5', 'g6', 'h7')),
             'h7': (6, ('b1', 'c2', 'd3', 'e4', 'f5', 'g6', 'h7'))})

    def test_02_rld_diagonal_attacks(self):
        ae = self.assertEqual
        rlda = constants.RLD_DIAGONAL_ATTACKS
        for k, v in rlda.items():
            ref = v[1][0]
            ae(rlda[k][1] is rlda[ref][1], True,
               ' '.join(('RLD_DIAGONAL_ATTACKS['+k+'][1]', 'is not',
                         'RLD_DIAGONAL_ATTACKS['+ref+'][1]')))


class SourceSquares(unittest.TestCase):

    def test_01_source_squares(self):
        ai = self.assertIs
        css = constants.SOURCE_SQUARES
        ai(css[constants.PGN_KING], constants.KING_MOVES)
        ai(css[constants.PGN_QUEEN], constants.QUEEN_MOVES)
        ai(css[constants.PGN_ROOK], constants.ROOK_MOVES)
        ai(css[constants.PGN_BISHOP], constants.BISHOP_MOVES)
        ai(css[constants.PGN_KNIGHT], constants.KNIGHT_MOVES)
        ai(css[constants.FEN_WHITE_PAWN], constants.WHITE_PAWN_MOVES)
        ai(css[constants.FEN_BLACK_PAWN], constants.BLACK_PAWN_MOVES)
        ai(css[constants.FEN_WHITE_PAWN + constants.PGN_CAPTURE_MOVE],
           constants.WHITE_PAWN_CAPTURES)
        ai(css[constants.FEN_BLACK_PAWN + constants.PGN_CAPTURE_MOVE],
           constants.BLACK_PAWN_CAPTURES)


class FENSourceSquares(unittest.TestCase):

    def test_01_fen_source_squares(self):
        ai = self.assertIs
        cfss = constants.FEN_SOURCE_SQUARES
        ai(cfss[constants.FEN_WHITE_KING], constants.KING_MOVES)
        ai(cfss[constants.FEN_WHITE_QUEEN], constants.QUEEN_MOVES)
        ai(cfss[constants.FEN_WHITE_ROOK], constants.ROOK_MOVES)
        ai(cfss[constants.FEN_WHITE_BISHOP], constants.BISHOP_MOVES)
        ai(cfss[constants.FEN_WHITE_KNIGHT], constants.KNIGHT_MOVES)
        ai(cfss[constants.FEN_WHITE_PAWN], constants.WHITE_PAWN_CAPTURES)
        ai(cfss[constants.FEN_BLACK_KING], constants.KING_MOVES)
        ai(cfss[constants.FEN_BLACK_QUEEN], constants.QUEEN_MOVES)
        ai(cfss[constants.FEN_BLACK_ROOK], constants.ROOK_MOVES)
        ai(cfss[constants.FEN_BLACK_BISHOP], constants.BISHOP_MOVES)
        ai(cfss[constants.FEN_BLACK_KNIGHT], constants.KNIGHT_MOVES)
        ai(cfss[constants.FEN_BLACK_PAWN], constants.BLACK_PAWN_CAPTURES)


if __name__ == '__main__':
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(Constants))
    runner().run(loader(RookMoves))
    runner().run(loader(BishopMoves))
    runner().run(loader(KnightMoves))
    runner().run(loader(KingMoves))
    runner().run(loader(EnPassant))
    runner().run(loader(WhitePawnMoves))
    runner().run(loader(BlackPawnMoves))
    runner().run(loader(WhitePawnCaptures))
    runner().run(loader(BlackPawnCaptures))
    runner().run(loader(QueenMoves))
    runner().run(loader(PointToPoint))
    runner().run(loader(RankAttacks))
    runner().run(loader(FileAttacks))
    runner().run(loader(LeftRightDownDiagonalAttacks))
    runner().run(loader(RightLeftDownDiagonalAttacks))
    runner().run(loader(SourceSquares))
    runner().run(loader(FENSourceSquares))
