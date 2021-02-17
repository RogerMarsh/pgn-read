# parser_test.py
# Copyright 2012, 2016 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""parser tests"""

import unittest
import re
import io
import sys

from .. import parser
from .. import constants

test_position_one = (
    'r1bq1rk1/pp1nbppp/2p1pn2/3p2B1/2PP4/2NBPN2/PP3PPP/R2QK2R w KQ - 9 8')
test_position_two = (
    'r1bqk2r/pp1nbppp/2p1pn2/3p2B1/2PP4/2NBP3/PP3PPP/R2QK1NR w KQkq - 7 7')
test_position_three = '7k/4P3/6K1/8/8/8/8/8 w - - 0 70'
test_position_four = 'k7/7R/8/2N5/8/2N3N1/8/K7 w - - 0 70'
test_scores = '''[Event "4NCL"]
[Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"]
[Round "9.36"]
[White "Burnell, Stephen"]
[Black "Johnson, Michael J"]
[Result "1/2-1/2"]
[ECO "C91"]
[WhiteElo "1922"]
[BlackElo "1802"]
[PlyCount "76"]
[EventDate "2011.04.30"]
[WhiteTeam "Braille Chess Association"]
[BlackTeam "Guildford A&DC 3"]

1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Be2 O-O 6. Bg5 c5 7. d5 h6 8. Be3 e6
9. dxe6 Bxe6 10. Qd2 Kh7 11. O-O-O Qa5 12. Qc2 Nc6 13. a3 Nd4 14. Bxd4 cxd4 15.
Nb5 Ng4 16. Bxg4 Bxg4 17. Nf3 Bxf3 18. gxf3 Qb6 19. Qd3 Rac8 20. Kb1 Rc6 21.
Ka2 Rfc8 22. b3 Qc5 23. a4 a6 24. Nxd4 Qe5 25. Rd2 Rc5 26. Ne2 b5 27. Qxd6 bxc4
28. Qxe5 cxb3+ 29. Kxb3 Bxe5 30. f4 Rb8+ 31. Ka2 Rc4 32. Rd3 Bg7 33. e5 Bf8 34.
Rd6 Bxd6 35. exd6 Re4 36. Nc3 Rd4 37. Rd1 Rxd1 38. Nxd1 Rd8 1/2-1/2

[Event "4NCL"]
[Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"]
[Round "9.36"]
[White "Yiamakis, Albert"]
[Black "Murphy, Richard LW"]
[Result "1-0"]
[ECO "D27"]
[WhiteElo "1736"]
[BlackElo "1685"]
[PlyCount "41"]
[EventDate "2011.04.30"]
[BlackTeam "Braille Chess Association"]

1. Nf3 d5 2. c4 c6 3. g3 Nf6 4. Bg2 e6 5. O-O Nbd7 6. d4 Bd6 7. b3 O-O 8. Bb2
Re8 9. Ne5 Bc7 10. Nd2 Nxe5 11. dxe5 Nd7 12. f4 f6 13. e4 fxe5 14. exd5 exd5
15. cxd5 cxd5 16. Bxd5+ Kh8 17. Ne4 exf4 18. Qh5 Nf8 19. Qf7 Ne6 20. Bxe6 Re7
21. Bxg7# 1-0

'''
test_export = ''.join((
    '[Event "4NCL"]',
    '[Site "Barcelo Hotel, Hinckley Island"]',
    '[Date "2011.04.30"]',
    '[Round "9.36"]',
    '[White "Burnell, Stephen"]',
    '[Black "Johnson, Michael J"]',
    '[Result "1/2-1/2"]',
    '[ECO "C91"]',
    '[WhiteElo "1922"]',
    '[BlackElo "1802"]',
    '[PlyCount "76"]',
    '[EventDate "2011.04.30"]',
    '[WhiteTeam "Braille Chess Association"]',
    '[BlackTeam "Guildford A&DC 3"]',
    'd4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5d5h6Be3e6',
    'dxe6Bxe6Qd2Kh7O-O-OQa5Qc2Nc6a3Nd4Bxd4cxd4',
    'Nb5Ng4Bxg4Bxg4Nf3Bxf3gxf3Qb6Qd3Rac8Kb1Rc6',
    'Ka2Rfc8b3Qc5a4a6Nxd4Qe5Rd2Rc5Ne2b5Qxd6bxc4',
    'Qxe5cxb3+Kxb3Bxe5f4Rb8+Ka2Rc4Rd3Bg7e5Bf8',
    'Rd6Bxd6exd6Re4Nc3Rd4Rd1Rxd1Nxd1Rd81/2-1/2',
    '[Event "4NCL"]',
    '[Site "Barcelo Hotel, Hinckley Island"]',
    '[Date "2011.04.30"]',
    '[Round "9.36"]',
    '[White "Yiamakis, Albert"]',
    '[Black "Murphy, Richard LW"]',
    '[Result "1-0"]',
    '[ECO "D27"]',
    '[WhiteElo "1736"]',
    '[BlackElo "1685"]',
    '[PlyCount "41"]',
    '[EventDate "2011.04.30"]',
    '[BlackTeam "Braille Chess Association"]',
    'Nf3d5c4c6g3Nf6Bg2e6O-ONbd7d4Bd6b3O-OBb2',
    'Re8Ne5Bc7Nd2Nxe5dxe5Nd7f4f6e4fxe5exd5exd5',
    'cxd5cxd5Bxd5+Kh8Ne4exf4Qh5Nf8Qf7Ne6Bxe6Re7',
    'Bxg7#1-0',
    ))
test_export_one = ''.join((
    '[Event "4NCL"]',
    '[Site "Barcelo Hotel, Hinckley Island"]',
    '[Date "2011.04.30"]',
    '[Round "9.36"]',
    '[White "Burnell, Stephen"]',
    '[Black "Johnson, Michael J"]',
    '[Result "1/2-1/2"]',
    '[ECO "C91"]',
    '[WhiteElo "1922"]',
    '[BlackElo "1802"]',
    '[PlyCount "76"]',
    '[EventDate "2011.04.30"]',
    '[WhiteTeam "Braille Chess Association"]',
    '[BlackTeam "Guildford A&DC 3"]',
    'd4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5d5h6Be3e6',
    'dxe6Bxe6Qd2Kh7O-O-OQa5Qc2Nc6a3Nd4Bxd4cxd4',
    'Nb5Ng4Bxg4Bxg4Nf3Bxf3gxf3Qb6Qd3Rac8Kb1Rc6',
    'Ka2Rfc8b3Qc5a4a6Nxd4Qe5Rd2Rc5Ne2b5Qxd6bxc4',
    'Qxe5cxb3+Kxb3Bxe5f4Rb8+Ka2Rc4Rd3Bg7e5Bf8',
    'Rd6Bxd6exd6Re4Nc3Rd4Rd1Rxd1Nxd1Rd81/2-1/2',
    ))
test_export_two = ''.join((
    '[Event "4NCL"]',
    '[Site "Barcelo Hotel, Hinckley Island"]',
    '[Date "2011.04.30"]',
    '[Round "9.36"]',
    '[White "Yiamakis, Albert"]',
    '[Black "Murphy, Richard LW"]',
    '[Result "1-0"]',
    '[ECO "D27"]',
    '[WhiteElo "1736"]',
    '[BlackElo "1685"]',
    '[PlyCount "41"]',
    '[EventDate "2011.04.30"]',
    '[BlackTeam "Braille Chess Association"]',
    'Nf3d5c4c6g3Nf6Bg2e6O-O(Nc3Be7;An eol comment\n)Nbd7d4Bd6b3O-OBb2',
    'Re8Ne5Bc7Nd2Nxe5dxe5Nd7f4f6e4fxe5{A comment}exd5exd5',
    'cxd5cxd5Bxd5+$10Kh8Ne4exf4Qh5Nf8Qf7Ne6Bxe6Re7',
    'Bxg7#1-0',
    ))
test_rav_one = ''.join((
    '[Date "2011.04.30"]',
    '[Round "9.36"]',
    '[Result "*"]',
    '[ECO "C91"]',
    '[Opening "Queen Pawn"]',
    '[PlyCount "76"]',
    '[EventDate "2011.04.30"]',
    'd4Nf6c4g6Nc3(Nf3Bg7g3)(g3)Bg7e4d6Be2O-OBg5c5d5h6Be3e6',
    'dxe6{Backward QP}Bxe6Qd2Kh7$11O-O-OQa5*',
    ))


class Pgn___init__(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test___init___PGN(self):
        p = self.pgn
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])
        self.assertEqual(p.collected_game, None)
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.board_bitmap, None)
        self.assertEqual(p.occupied_squares, [])
        self.assertEqual(p.board, [])
        self.assertEqual(p.piece_locations, {})
        self.assertEqual(p.fullmove_number, None)
        self.assertEqual(p.halfmove_count, None)
        self.assertEqual(p.en_passant, None)
        self.assertEqual(p.castling, None)
        self.assertEqual(p.active_side, None)
        self.assertEqual(p.ravstack, [])
        self.assertEqual(p._state, None)
        self.assertEqual(p._move_error_state, None)
        self.assertEqual(p._rewind_state, None)
        self.assertEqual(len(p.__dict__), 19)
        self.assertEqual(set(p.__dict__), {'tokens',
                                           'error_tokens',
                                           'collected_game',
                                           'tags_in_order',
                                           'board_bitmap',
                                           'occupied_squares',
                                           'board',
                                           'piece_locations',
                                           'fullmove_number',
                                           'halfmove_count',
                                           'en_passant',
                                           'castling',
                                           'active_side',
                                           'ravstack',
                                           '_initial_fen',
                                           '_state',
                                           '_move_error_state',
                                           '_rewind_state',
                                           '_despatch_table',
                                           })
        self.assertEqual(
            p._despatch_table,
            [p._searching,
             p._searching_after_error_in_rav,
             p._searching_after_error_in_game,
             p._collecting_tag_pairs,
             p._collecting_movetext,
             p._collecting_non_whitespace_while_searching,
             p._disambiguate_move,
             ])


class Pgn__start_variation(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        self.pgn_base = parser.PGN()

    def tearDown(self):
        del self.pgn
        del self.pgn_base

    def test__start_variation(self):
        self.pgn._state = True
        self.pgn.occupied_squares[:] = [set(), set()]
        self.pgn.piece_locations = {i:set() for i in 'KQRBNPkqrbnp'}
        self.pgn.ravstack.append(((('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                                    'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                                    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                                   0,
                                   'KQkq',
                                   '-'),
                                  (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                                    'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                                    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                                   1,
                                   'KQkq',
                                   '-')))
        self.pgn._start_variation()
        self.assertEqual(len(self.pgn.__dict__), len(self.pgn_base.__dict__))
        self.assertEqual(self.pgn._state, True)
        self.assertEqual(self.pgn.ravstack[-1],
                         (None,
                          (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                           0,
                           'KQkq',
                           '-')))
        self.assertEqual(self.pgn.ravstack[-2],
                         ((('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                           0,
                           'KQkq',
                           '-'),
                          (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                           1,
                           'KQkq',
                           '-')))


class Pgn__end_variation(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        self.pgn_base = parser.PGN()

    def tearDown(self):
        del self.pgn
        del self.pgn_base

    def test__end_variation_01(self):
        self.pgn._state = True
        self.pgn._end_variation()
        self.assertEqual(len(self.pgn.__dict__), len(self.pgn_base.__dict__))
        self.assertEqual(len(self.pgn.ravstack), 0)
        self.assertEqual(self.pgn._state, True)

    def test__end_variation_02(self):
        self.pgn.ravstack.append((None, 'f'))
        self.pgn._state = True
        self.pgn._end_variation()
        self.assertEqual(len(self.pgn.__dict__), len(self.pgn_base.__dict__))
        self.assertEqual(self.pgn._state, True)
        self.assertEqual(len(self.pgn.ravstack), 0)

    def test__end_variation_03(self):
        self.pgn.ravstack.append((None,
                                  (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                                    'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    '', '', '', '', '', '', '', '',
                                    'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                                    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                                   1,
                                   'KQkq',
                                   '-')))
        self.pgn.ravstack.append(('g', 'h'))
        self.pgn.occupied_squares[:] = [set(), set()]
        self.pgn.piece_locations = {i:set() for i in 'PpKkQRBNqrbn'}
        self.pgn._state = True
        self.pgn._end_variation()
        self.assertEqual(len(self.pgn.__dict__), len(self.pgn_base.__dict__))
        self.assertEqual(self.pgn._state, True)
        self.assertEqual(len(self.pgn.ravstack), 1)
        self.assertEqual(self.pgn.ravstack[-1],
                         (None,
                          (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                           1,
                           'KQkq',
                           '-')))


class Pgn__convert_error_tokens_to_token(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        p = self.pgn
        p.error_tokens.extend(['a', 'b']) 

    def tearDown(self):
        del self.pgn

    def test__convert_error_tokens_to_comment_01(self):
        p = self.pgn
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, ['a', 'b'])
        p._convert_error_tokens_to_token()
        self.assertEqual(len(p.tokens), 1)
        self.assertEqual(p.tokens[-1].group(), '{Error: ab}')
        self.assertEqual(p.error_tokens, ['a', 'b'])

    def test__convert_error_tokens_to_comment_02(self):
        p = self.pgn
        p.tokens.append(None)
        self.assertEqual(p.tokens, [None])
        self.assertEqual(p.error_tokens, ['a', 'b'])
        p._convert_error_tokens_to_token()
        self.assertEqual(len(p.tokens), 2)
        self.assertEqual(p.tokens[-1].group(), '{Error: ab}')
        self.assertEqual(p.error_tokens, ['a', 'b'])


class Pgn__searching(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        p = self.pgn
        p.set_position_fen(test_position_one)
        p._state = constants.PGN_SEARCHING
        p._move_error_state = (
            constants.PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING)

    def tearDown(self):
        del self.pgn

    def test__searching_01(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._searching(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])

    def test__searching_02(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Qc2')
        match = parser.re_tokens.match('Qc2')
        self.assertEqual(match.group(), 'Qc2')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__searching_03(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('h3')
        match = parser.re_tokens.match('h3')
        self.assertEqual(match.group(), 'h3')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__searching_04(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Bxf6')
        match = parser.re_tokens.match('Bxf6')
        self.assertEqual(match.group(), 'Bxf6')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__searching_05(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('cxd5')
        match = parser.re_tokens.match('cxd5')
        self.assertEqual(match.group(), 'cxd5')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__searching_06(self):
        p = self.pgn
        p.set_position_fen(test_position_two)
        #match = parser.re_tokens.fullmatch('Nge2')
        match = parser.re_tokens.match('Nge2')
        self.assertEqual(match.group(), 'Nge2')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__searching_07(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('O-O')
        match = parser.re_tokens.match('O-O')
        self.assertEqual(match.group(), 'O-O')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__searching_08(self):
        p = self.pgn
        p.set_position_fen(test_position_three)
        #match = parser.re_tokens.fullmatch('e8=Q#')
        match = parser.re_tokens.match('e8=Q#')
        self.assertEqual(match.group(), 'e8=Q#')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__searching_09(self):
        p = self.pgn
        match = parser.re_tokens.match('{A comment}')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__searching_10(self):
        p = self.pgn
        match = parser.re_tokens.match('$45')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__searching_11(self):
        p = self.pgn
        match = parser.re_tokens.match(';Comment to EOL\n')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__searching_12(self):
        p = self.pgn
        match = parser.re_tokens.match('(')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_13(self):
        p = self.pgn
        match = parser.re_tokens.match(')')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_14(self):
        p = self.pgn
        match = parser.re_tokens.match('1-0')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_15(self):
        p = self.pgn
        match = parser.re_tokens.match('   ')
        p._searching(match)
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_16(self):
        p = self.pgn
        match = parser.re_tokens.match(' \n   \n\r\t')
        p._searching(match)
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_17(self):
        p = self.pgn
        match = parser.re_tokens.match('1')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_18(self):
        p = self.pgn
        match = parser.re_tokens.match('.')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_19(self):
        p = self.pgn
        match = parser.re_tokens.match('<Reserved>')
        p._searching(match)
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_20(self):
        p = self.pgn
        match = parser.re_tokens.match('any old string')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_21(self):
        p = self.pgn
        match = parser.re_tokens.match('O_O')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_22(self):
        p = parser.PGN()
        p._state = constants.PGN_SEARCHING
        p._move_error_state = (
            constants.PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING)
        fen = '7k/8/8/8/8/8/8/7K w - - 0 60'
        match = parser.re_tokens.match(''.join(('[FEN"', fen, '"]')))
        p._searching(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])
        self.assertEqual(p._initial_fen, fen)

    def test__searching_23(self):
        p = self.pgn
        p.set_position_fen('7k/8/6K1/8/8/1p6/8/8 b - - 0 70')
        #match = parser.re_tokens.fullmatch('b2')
        match = parser.re_tokens.match('b2')
        self.assertEqual(match.group(), 'b2')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__searching_24(self):
        p = self.pgn
        p.set_position_fen('7k/8/6K1/8/8/8/1p6/8 b - - 0 70')
        #match = parser.re_tokens.fullmatch('b1')
        match = parser.re_tokens.match('b1')
        self.assertEqual(match.group(), 'b1')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, ['b1'])


class Pgn__searching_after_error_in_rav(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        #p.ravstack = [None, None]
        #p._ravstack_length = len(p.ravstack)

    def tearDown(self):
        del self.pgn

    def test__searching_after_error_in_rav_01(self):
        p = self.pgn
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u'''
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match('(')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(len(p.tokens), 21)
        self.assertEqual(p.error_tokens, ['u', '('])
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(p._ravstack_length, 3)

    def test__searching_after_error_in_rav_02(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u(v'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        self.assertEqual(p._ravstack_length, 3)
        match = parser.re_tokens.match(')')
        self.assertEqual(p._move_error_state, 2)
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(p._move_error_state, 2)
        self.assertEqual(len(p.tokens), 21)
        self.assertEqual(p.error_tokens, ['u', '(', 'v', ')'])
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(hasattr(p, '_ravstack_length'), True)

    def test__searching_after_error_in_rav_03(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match(')')
        self.assertEqual(p._move_error_state, 2)
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p._move_error_state, 2)
        self.assertEqual(len(p.tokens), 23)
        self.assertEqual(p.tokens[-2].group(), '{Error: u}')
        self.assertEqual(p.tokens[-1].group(), ')')
        self.assertEqual(p.error_tokens, [])
        self.assertEqual(len(p.ravstack), 1)
        self.assertEqual(hasattr(p, '_ravstack_length'), False)

    def test__searching_after_error_in_rav_04(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u(Nbd7(Nxe4'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        self.assertEqual(p._ravstack_length, 4)
        match = parser.re_tokens.match(')')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(len(p.tokens), 21)
        self.assertEqual(p.error_tokens, ['u', '(', 'Nbd7', '(', 'Nxe4', ')'])
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(p._ravstack_length, 3)

    def test__searching_after_error_in_rav_05(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u(Nbd7(Nxe4'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match('*')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p.collected_game[2][-2].group(),
                         '{Error: u(Nbd7(Nxe4}')
        self.assertEqual(p.collected_game[2][-1].group(), '*')
        self.assertEqual(p._state, 0)
        self.assertEqual(hasattr(p, '_ravstack_length'), False)

    def test__searching_after_error_in_rav_06(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u(Nbd7(Nxe4'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p.collected_game[2][-1].group(),
                         '{Error: u(Nbd7(Nxe4}')
        self.assertEqual(p._state, 3)
        self.assertEqual(p._move_error_state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])
        self.assertEqual(hasattr(p, '_ravstack_length'), False)

    def test__searching_after_error_in_rav_07(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match('   ')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(len(p.tokens), 21)
        self.assertEqual(p.tokens[-1].group(), 'b3')
        self.assertEqual(p.error_tokens, ['u', '   '])


class Pgn__searching_after_error_in_game(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        #p.ravstack = [None]

    def tearDown(self):
        del self.pgn

    def test__searching_after_error_in_game_01(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3u6'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match('1/2-1/2')
        p._searching_after_error_in_game(match)
        self.assertEqual(p.collected_game[2][-2].group(), '{Error: u6}')
        self.assertEqual(p.collected_game[2][-1].group(), '1/2-1/2')
        self.assertEqual(p._state, 0)

    def test__searching_after_error_in_game_02(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3u6'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._searching_after_error_in_game(match)
        self.assertEqual(p.collected_game[2][-2].group(), 'Be3')
        self.assertEqual(p.collected_game[2][-1].group(), '{Error: u6}')
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])

    def test__searching_after_error_in_game_03(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3u6'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        #match = parser.re_tokens.fullmatch('dxe6')
        match = parser.re_tokens.match('dxe6')
        self.assertEqual(match.group(), 'dxe6')
        p._searching_after_error_in_game(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(len(p.tokens), 15)
        self.assertEqual(p.tokens[-1].group(), 'Be3')
        self.assertEqual(p.error_tokens, ['u', '6', 'dxe6'])


class Pgn__collecting_tag_pairs(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        p = self.pgn
        p.set_position_fen(test_position_one)
        p._state = constants.PGN_COLLECTING_TAG_PAIRS
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME

    def tearDown(self):
        del self.pgn

    def test__collecting_tag_pairs_01(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])

    def test__collecting_tag_pairs_02(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Qc2')
        match = parser.re_tokens.match('Qc2')
        self.assertEqual(match.group(), 'Qc2')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_tag_pairs_03(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('h3')
        match = parser.re_tokens.match('h3')
        self.assertEqual(match.group(), 'h3')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_tag_pairs_04(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Bxf6')
        match = parser.re_tokens.match('Bxf6')
        self.assertEqual(match.group(), 'Bxf6')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_tag_pairs_05(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('cxd5')
        match = parser.re_tokens.match('cxd5')
        self.assertEqual(match.group(), 'cxd5')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_tag_pairs_06(self):
        p = self.pgn
        p.set_position_fen(test_position_two)
        #match = parser.re_tokens.fullmatch('Nge2')
        match = parser.re_tokens.match('Nge2')
        self.assertEqual(match.group(), 'Nge2')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_tag_pairs_07(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('O-O')
        match = parser.re_tokens.match('O-O')
        self.assertEqual(match.group(), 'O-O')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_tag_pairs_08(self):
        p = self.pgn
        p.set_position_fen(test_position_three)
        #match = parser.re_tokens.fullmatch('e8=Q#')
        match = parser.re_tokens.match('e8=Q#')
        self.assertEqual(match.group(), 'e8=Q#')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_tag_pairs_09(self):
        p = self.pgn
        match = parser.re_tokens.match('0-1')
        p._collecting_tag_pairs(match)
        self.assertEqual(len(p.collected_game), 4)
        self.assertEqual(p.collected_game[2][-1].group(), '0-1')
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_10(self):
        p = self.pgn
        match = parser.re_tokens.match('{A comment}')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_11(self):
        p = self.pgn
        match = parser.re_tokens.match('$45')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_12(self):
        p = self.pgn
        match = parser.re_tokens.match(';Comment to EOL\n')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_13(self):
        p = self.pgn
        match = parser.re_tokens.match('(')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_tag_pairs_14(self):
        p = self.pgn
        match = parser.re_tokens.match(')')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_tag_pairs_15(self):
        p = self.pgn
        match = parser.re_tokens.match('   ')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_16(self):
        p = self.pgn
        match = parser.re_tokens.match(' \n   \n\r\t')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_17(self):
        p = self.pgn
        match = parser.re_tokens.match('1')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_18(self):
        p = self.pgn
        match = parser.re_tokens.match('.')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_19(self):
        p = self.pgn
        match = parser.re_tokens.match('<Reserved>')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_20(self):
        p = self.pgn
        match = parser.re_tokens.match('any old string')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_tag_pairs_21(self):
        p = self.pgn
        match = parser.re_tokens.match('O_O')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_tag_pairs_22(self):
        p = parser.PGN()
        p._state = constants.PGN_SEARCHING
        p._move_error_state = (
            constants.PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING)
        fen = '7k/8/8/8/8/8/8/7K w - - 0 60'
        match = parser.re_tokens.match(''.join(('[FEN"', fen, '"]')))
        p._searching(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])
        self.assertEqual(p._initial_fen, fen)


class Pgn__collecting_movetext(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        p = self.pgn
        p.set_position_fen(test_position_one)
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME

    def tearDown(self):
        del self.pgn

    def test__collecting_movetext_01(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Qc2')
        match = parser.re_tokens.match('Qc2')
        self.assertEqual(match.group(), 'Qc2')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_movetext_02(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('h3')
        match = parser.re_tokens.match('h3')
        self.assertEqual(match.group(), 'h3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_movetext_03(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Bxf6')
        match = parser.re_tokens.match('Bxf6')
        self.assertEqual(match.group(), 'Bxf6')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_movetext_04(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('cxd5')
        match = parser.re_tokens.match('cxd5')
        self.assertEqual(match.group(), 'cxd5')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_movetext_05(self):
        p = self.pgn
        p.set_position_fen(test_position_two)
        #match = parser.re_tokens.fullmatch('Nge2')
        match = parser.re_tokens.match('Nge2')
        self.assertEqual(match.group(), 'Nge2')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_movetext_06(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('O-O')
        match = parser.re_tokens.match('O-O')
        self.assertEqual(match.group(), 'O-O')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_movetext_07(self):
        p = self.pgn
        p.set_position_fen(test_position_three)
        #match = parser.re_tokens.fullmatch('e8=Q#')
        match = parser.re_tokens.match('e8=Q#')
        self.assertEqual(match.group(), 'e8=Q#')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])

    def test__collecting_movetext_08(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 '''
        p = parser.PGN()
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        self.assertEqual(len(p.ravstack), 1)
        match = parser.re_tokens.match('(')
        p._collecting_movetext(match)
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(p._state, 4)
        self.assertEqual(len(p.tokens), 20)
        self.assertEqual(p.tokens[-2].group(), 'Qd2')
        self.assertEqual(p.tokens[-1].group(), '(')
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_09(self):
        p = self.pgn
        match = parser.re_tokens.match(')')
        p._collecting_movetext(match)
        self.assertEqual(p.collected_game, None)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [')'])

    def test__collecting_movetext_10(self):
        p = self.pgn
        match = parser.re_tokens.match('0-1')
        p._collecting_movetext(match)
        self.assertEqual(len(p.collected_game), 4)
        self.assertEqual(p.collected_game[2][-1].group(), '0-1')
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_11(self):
        p = self.pgn
        match = parser.re_tokens.match('{A comment}')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_12(self):
        p = self.pgn
        match = parser.re_tokens.match('$45')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_13(self):
        p = self.pgn
        match = parser.re_tokens.match(';Comment to EOL\n')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_14(self):
        p = self.pgn
        match = parser.re_tokens.match('   ')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_15(self):
        p = self.pgn
        match = parser.re_tokens.match(' \n   \n\r\t')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_16(self):
        p = self.pgn
        match = parser.re_tokens.match('1')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_17(self):
        p = self.pgn
        match = parser.re_tokens.match('.')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_18(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 '''
        p = parser.PGN()
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        self.assertEqual(len(p.ravstack), 1)
        match = parser.re_tokens.match('[Tag"value"]')
        p._collecting_movetext(match)
        self.assertEqual(p.collected_game[2][-2].group(), 'Qd2')
        self.assertEqual(p.collected_game[2][-1].group(), '{Error: }')
        self.assertEqual(len(p.ravstack), 1)
        self.assertEqual(p._state, 3)
        self.assertEqual(p._move_error_state, 2)
        self.assertEqual(p.tags_in_order, [match])
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_19(self):
        p = self.pgn
        match = parser.re_tokens.match('<Reserved>')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_20(self):
        p = self.pgn
        match = parser.re_tokens.match('O_O')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_movetext_21(self):
        p = self.pgn
        match = parser.re_tokens.match('any old string')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_movetext_22(self):
        p = self.pgn
        p.ravstack.insert(0, None)
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_RAV
        match = parser.re_tokens.match('any old string')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])


class Pgn__collecting_non_whitespace_while_searching(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        p = self.pgn
        p.set_position_fen(test_position_one)
        p._state = constants.PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING
        p._move_error_state = p._state

    def tearDown(self):
        del self.pgn

    def test__collecting_non_whitespace_while_searching_01(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._collecting_non_whitespace_while_searching(match)
        self.assertEqual(p.collected_game[2][0].group(), '{Error: }')
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_non_whitespace_while_searching_02(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch(' \n   \n\r\t')
        match = parser.re_tokens.match(' \n   \n\r\t')
        self.assertEqual(match.group(), ' \n   \n\r\t')
        p._collecting_non_whitespace_while_searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [' \n   \n\r\t'])

    def test__collecting_non_whitespace_while_searching_03(self):
        p = self.pgn
        match = parser.re_tokens.match('any old string')
        p._collecting_non_whitespace_while_searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, ['a'])


class Pgn__disambiguate_move(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        p = self.pgn
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        p.set_position_fen(test_position_four)

    def tearDown(self):
        del self.pgn

    def test__disambiguate_move_01(self):
        p = self.pgn
        match = parser.re_tokens.match('Rh3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        p._state = constants.PGN_DISAMBIGUATE_MOVE
        matcha = parser.re_tokens.match('e4')
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])
        p._disambiguate_move(matcha)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(len(p.error_tokens), 1)
        self.assertEqual(p.error_tokens[0], 'Rh3e4')

    def test__disambiguate_move_02(self):
        p = self.pgn
        match = parser.re_tokens.match('Nc3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 6)
        matcha = parser.re_tokens.match('e4')
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])
        p._disambiguate_move(matcha)
        self.assertEqual(p._state, 4)
        self.assertEqual(len(p.tokens), 1)
        self.assertEqual(p.tokens[0].group(), 'Nc3e4')
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])

    def test__disambiguate_move_03(self):
        p = self.pgn
        match = parser.re_tokens.match('Nc3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 6)
        matcha = parser.re_tokens.match('Rh3')
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])
        p._disambiguate_move(matcha)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, ['Nc3Rh3'])

    def test__disambiguate_move_04(self):
        p = self.pgn
        match = parser.re_tokens.match('Nc3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 6)
        p.ravstack.insert(0, None)
        matcha = parser.re_tokens.match('Rh3')
        self.assertEqual(p.tokens, [match])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])
        p._disambiguate_move(matcha)
        self.assertEqual(p._state, 1)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, ['Nc3Rh3'])


class Pgn_read_games(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_scores)
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_read_games_01(self):
        p = self.pgn
        for y in p.read_games(self.test_scores, size=40):
            self.assertEqual(bool(y.group(constants.IFG_TERMINATION)), True)


class Pgn_get_games(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_get_games_01(self):
        p = self.pgn
        for y in p.get_games(test_scores):
            self.assertEqual(bool(y.group(constants.IFG_TERMINATION)), True)


class Pgn_read_first_game(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_scores)
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_read_first_game_01(self):
        p = self.pgn
        self.assertEqual(
            bool(p.read_first_game(self.test_scores, size=40
                                   ).group(constants.IFG_TERMINATION)),
            True)


class Pgn_get_first_game(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_get_first_game_01(self):
        p = self.pgn
        self.assertEqual(
            bool(p.get_first_game(test_scores
                                  ).group(constants.IFG_TERMINATION)),
            True)


class Pgn_collect_token(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_collect_token_01(self):
        p = self.pgn
        self.assertEqual(p.tokens, [])
        p.collect_token(None)
        self.assertEqual(p.tokens, [None])


class Pgn_collect_game_tokens(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_collect_game_tokens_01(self):
        p = self.pgn
        self.assertEqual(p.collected_game, None)
        p.collect_game_tokens()
        self.assertEqual(p.collected_game, ([], {}, [], []))

    def test_collect_game_tokens_02(self):
        p = self.pgn
        next(p.get_games(test_scores))
        self.assertEqual(len(p.collected_game), 4)
        self.assertEqual(len(p.collected_game[0]), 14)
        self.assertEqual(len(p.collected_game[1]), 14)
        self.assertEqual(set([t.group(2) for t in p.collected_game[0]]),
                         set(p.collected_game[1]))
        self.assertEqual(p.collected_game[1],
                         {'Event': '4NCL',
                          'Site': 'Barcelo Hotel, Hinckley Island',
                          'Date': '2011.04.30',
                          'Round': '9.36',
                          'White': 'Burnell, Stephen',
                          'Black': 'Johnson, Michael J',
                          'Result': '1/2-1/2',
                          'ECO': 'C91',
                          'WhiteElo': '1922',
                          'BlackElo': '1802',
                          'PlyCount': '76',
                          'EventDate': '2011.04.30',
                          'WhiteTeam': 'Braille Chess Association',
                          'BlackTeam': 'Guildford A&DC 3',
                          })
        self.assertEqual(len(p.collected_game[2]), 77)
        self.assertEqual([t.group() for t in p.collected_game[2][:5]],
                         ['d4', 'Nf6', 'c4', 'g6', 'Nc3'])
        self.assertEqual([t.group() for t in p.collected_game[2][-5:]],
                         ['Rd1', 'Rxd1', 'Nxd1', 'Rd8', '1/2-1/2'])
        self.assertEqual(len(p.collected_game[3]), 0)


class Pgn_reset_position(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        self.pgn_base = parser.PGN()

    def tearDown(self):
        del self.pgn
        del self.pgn_base

    def test_reset_position_01(self):
        p = self.pgn
        self.assertRaisesRegex(
            TypeError,
            "'NoneType' object is not iterable",
            p.reset_position,
            *(None,))

    def test_reset_position_02(self):
        if sys.version_info[:2] < (3,5):
            msg = "need more than 3 values to unpack"
        else:
            msg = "not enough values to unpack \(expected 4, got 3\)"
        p = self.pgn
        self.assertRaisesRegex(
            ValueError,
            msg,
            p.reset_position,
            *((None,None,None),))

    def test_reset_position_03(self):
        p = self.pgn
        self.assertRaisesRegex(
            ValueError,
            "too many values to unpack \(expected 4\)",
            p.reset_position,
            *((None,None,None,None,None),))

    def test_reset_position_04(self):
        p = self.pgn
        self.assertRaisesRegex(
            TypeError,
            "'NoneType' object is not iterable",
            p.reset_position,
            *((None,None,None,None),))

    def test_reset_position_05(self):
        p = self.pgn
        self.assertRaisesRegex(
            IndexError,
            "list index out of range",
            p.reset_position,
            *((('', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', 'K',
                'k', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', ''),
               None,
               None,
               None),))

    def test_reset_position_06(self):
        p = self.pgn
        p.occupied_squares[:] = [set(), set()]
        self.assertRaisesRegex(
            KeyError,
            "K",
            p.reset_position,
            *((('', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', 'K',
                'k', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', '',
                '', '', '', '', '', '', '', ''),
               None,
               None,
               None),))

    def test_reset_position_07(self):
        p = self.pgn
        self.assertEqual(p.board, [])
        self.assertEqual(p.occupied_squares, [])
        self.assertEqual(p.piece_locations, {})
        self.assertEqual(p.active_side, None)
        self.assertEqual(p.castling, None)
        self.assertEqual(p.en_passant, None)
        p.occupied_squares[:] = [set(), set()]
        p.piece_locations = {i:set() for i in 'PpKkQRBNqrbn'}
        p.reset_position(((12, 12, 12, 12, 12, 12, 12, 12,
                           12, 12, 12, 12, 12, 12, 12, 12,
                           12, 12, 12, 12, 12, 12, 12, 'K',
                           'k', 12, 12, 12, 12, 12, 12, 12,
                           12, 12, 12, 12, 12, 12, 12, 12,
                           12, 12, 12, 12, 12, 12, 12, 12,
                           12, 12, 12, 12, 12, 12, 12, 12,
                           12, 12, 12, 12, 12, 12, 12, 12),
                          'a',
                          'b',
                          'c'),)
        self.assertEqual(p.board, [12, 12, 12, 12, 12, 12, 12, 12,
                                   12, 12, 12, 12, 12, 12, 12, 12,
                                   12, 12, 12, 12, 12, 12, 12, 'K',
                                   'k', 12, 12, 12, 12, 12, 12, 12,
                                   12, 12, 12, 12, 12, 12, 12, 12,
                                   12, 12, 12, 12, 12, 12, 12, 12,
                                   12, 12, 12, 12, 12, 12, 12, 12,
                                   12, 12, 12, 12, 12, 12, 12, 12])
        self.assertEqual(p.occupied_squares, [{23}, {24}])
        self.assertEqual(p.piece_locations,
                         {'P':set(),'p':set(),
                          'K':{23}, 'k':{24},'Q':set(),'R':set(),
                          'B':set(),'N':set(),
                          'q':set(),'r':set(),'b':set(),'n':set()})
        self.assertEqual(p.board_bitmap, (1<<23) + (1<<24))
        self.assertEqual(p.active_side, 'a')
        self.assertEqual(p.castling, 'b')
        self.assertEqual(p.en_passant, 'c')


class Pgn_set_position_fen(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        self.pgn_base = parser.PGN()

    def tearDown(self):
        del self.pgn
        del self.pgn_base

    def test_set_position_fen_01(self):
        p = self.pgn
        pend = self.pgn_base
        p.set_position_fen()
        self.assertEqual(p._state, None)
        self.assertEqual(len(p.__dict__), len(pend.__dict__))

    def test_set_position_fen_02(self):
        self.assertRaisesRegex(
            AttributeError,
            "'bool' object has no attribute 'split'",
            self.pgn.set_position_fen,
            *(True,))

    def test_set_position_fen_04(self):
        p = self.pgn
        pend = self.pgn_base
        p.set_position_fen(fen='8/8/7K/k7/8/8/8/8 w - - 5 60')
        self.assertEqual(p._state, None)
        self.assertEqual(len(p.__dict__), len(pend.__dict__))
        self.assertEqual(p.ravstack, [(None,
                                       (('', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', 'K',
                                         'k', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', ''),
                                        0, '-', '-'))])
        self.assertEqual(p._initial_fen, '8/8/7K/k7/8/8/8/8 w - - 5 60')

    def test_default_fen(self):
        p = self.pgn
        p.set_position_fen()
        self.assertEqual(p._state, None)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.collected_game, None)
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.board_bitmap, 18446462598732906495)
        self.assertEqual(p.board_bitmap,
                         (sum([1<<i for i in range(16)]) +
                          sum([1<<i for i in range(48, 64)])))
        self.assertEqual(p.occupied_squares,
                         [{48, 49, 50, 51, 52, 53, 54, 55,
                           56, 57, 58, 59, 60, 61, 62, 63},
                          {0, 1, 2, 3, 4, 5, 6, 7,
                           8, 9, 10, 11, 12, 13, 14, 15}])
        self.assertEqual(p.board,
                         ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                          'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                          'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'])
        self.assertEqual(p.piece_locations,
                         {'P':{48, 49, 50, 51, 52, 53, 54, 55},
                          'p':{8, 9, 10, 11, 12, 13, 14, 15},
                          'K':{60},
                          'k':{4},
                          'Q':{59},
                          'R':{56, 63},
                          'B':{58, 61},
                          'N':{57, 62},
                          'q':{3},
                          'r':{0, 7},
                          'b':{2, 5},
                          'n':{1, 6}})
        self.assertEqual(p.fullmove_number, 1)
        self.assertEqual(p.halfmove_count, 0)
        self.assertEqual(p.en_passant, '-')
        self.assertEqual(p.castling, 'KQkq')
        self.assertEqual(p.active_side, 0)
        self.assertEqual(p.ravstack,
                         [(None,
                           (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                             'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                             'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                            0,
                            'KQkq',
                            '-'))])
        self.assertEqual(p._state, None)
        self.assertEqual(p._initial_fen, True)

    def test_initial_fen(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, None)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.collected_game, None)
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.board_bitmap, 18446462598732906495)
        self.assertEqual(p.occupied_squares,
                         [{48, 49, 50, 51, 52, 53, 54, 55,
                           56, 57, 58, 59, 60, 61, 62, 63},
                          {0, 1, 2, 3, 4, 5, 6, 7,
                           8, 9, 10, 11, 12, 13, 14, 15}])
        self.assertEqual(p.board,
                         ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                          'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                          'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'])
        self.assertEqual(p.piece_locations,
                         {'P':{48, 49, 50, 51, 52, 53, 54, 55},
                          'p':{8, 9, 10, 11, 12, 13, 14, 15},
                          'K':{60},
                          'k':{4},
                          'Q':{59},
                          'R':{56, 63},
                          'B':{58, 61},
                          'N':{57, 62},
                          'q':{3},
                          'r':{0, 7},
                          'b':{2, 5},
                          'n':{1, 6}})
        self.assertEqual(p.fullmove_number, 1)
        self.assertEqual(p.halfmove_count, 0)
        self.assertEqual(p.en_passant, '-')
        self.assertEqual(p.castling, 'KQkq')
        self.assertEqual(p.active_side, 0)
        self.assertEqual(p.ravstack,
                         [(None,
                           (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                             'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                             'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                            0,
                            'KQkq',
                            '-'))])
        self.assertEqual(p._state, None)
        self.assertEqual(
            p._initial_fen,
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    def test_initial_fen_errors_01(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 a')
        self.assertEqual(p._state, 2)
        self.assertEqual(p._initial_fen, None)

    def test_initial_fen_errors_02(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - a 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_03(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq a 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_04(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w a - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_05(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR a KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_06(self):
        p = self.pgn
        p.set_position_fen(
            fen='a w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_07(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNa w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_08(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/7/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_09(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/9/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_10(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_11(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_12(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppp1pppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_13(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/ppp1ppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_14(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_15(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_16(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBRR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_17(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KKkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_18(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/7P/8/PPPPPP1P/RNBQKBNR w KQkq h3 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_19(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/7P/8/PPPPPPPN/RNBQKB1R b KQkq h6 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_20(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/7N/7P/PPPPPPP1/RNBQKB1R b KQkq h3 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_21(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/7N/8/PPPPPPP1/RNBQKB1R b KQkq h3 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_22(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkb1r/pppppppn/8/7p/8/8/PPPPPPPP/RNBQKBNR w KQkq h6 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_23(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkb1r/ppppppp1/7n/7p/8/8/PPPPPPPP/RNBQKBNR w KQkq h6 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_24(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkb1r/ppppppp1/8/7n/8/8/PPPPPPPP/RNBQKBNR w KQkq h6 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_25(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppp1p/8/8/5Pp1/8/PPPPP1PP/RNBQKBNR b KQkq f3 0 1')
        self.assertEqual(p._state, None)

    def test_initial_fen_errors_26(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppp1p/8/5Pp1/8/8/PPPPP1PP/RNBQKB1R w KQkq g6 0 1')
        self.assertEqual(p._state, None)

    def test_initial_fen_errors_27(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/7N/8/PPPPPPPP/RNBQKB1R b KQkq - 0 1')
        self.assertEqual(p._state, None)

    def test_initial_fen_errors_28(self):
        p = self.pgn
        p.set_position_fen(
            fen='4k3/6N1/8/8/8/8/8/4K3 w - - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_29(self):
        p = self.pgn
        p.set_position_fen(
            fen='4k3/8/8/8/8/6b1/2n3n1/4K3 w - - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_30(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkb1r/pppppppp/8/7n/8/8/PPPPPPPP/RNBQKB1R w KQkq - 0 1')
        self.assertEqual(p._state, None)

    def test_initial_fen_errors_31(self):
        p = self.pgn
        p.set_position_fen(fen='any string which is not a fen')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_32(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnp/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_33(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnP/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_34(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNP w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_35(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNp w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_36(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/n7/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_37(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/7N/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_38(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbkkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_39(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBKKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_40(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkb1r/pppppppp/8/p7/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_41(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/7P/8/PPPPPPPP/RNBQKB1R w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_42(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnqqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_43(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNQQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_44(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBK1BNR w Kkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_45(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBK1BNR w Qkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_46(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbk1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQk - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_47(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbk1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_48(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBN1 w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_49(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/1NBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_50(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbn1/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)

    def test_initial_fen_errors_51(self):
        p = self.pgn
        p.set_position_fen(
            fen='1nbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, 2)


class Pgn_add_move_to_game(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        self.pgn_base = parser.PGN()

    def tearDown(self):
        del self.pgn
        del self.pgn_base

    def test__add_move_to_game_01(self):
        if sys.version_info[:2] < (3,5):
            msg = "tuple indices must be integers, not NoneType"
        else:
            msg = "tuple indices must be integers or slices, not NoneType"
        p = self.pgn
        pend = self.pgn_base
        self.assertRaisesRegex(
            TypeError,
            msg,
            p.add_move_to_game)

    def test__add_move_to_game_02(self):
        p = self.pgn
        pend = self.pgn_base
        p.set_position_fen()
        self.assertEqual(p._state, None)
        p.add_move_to_game()
        self.assertEqual(len(p.__dict__), len(pend.__dict__))
        self.assertEqual(len(p.ravstack), 1)
        self.assertEqual(p.ravstack[-1],
                         ((('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                           0,
                           'KQkq',
                           '-'),
                          (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                           1,
                           'KQkq',
                           '-')))
        self.assertEqual(p._state, None)


class Pgn__play_disambiguated_move(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        #self.matchfrom = parser.re_tokens.fullmatch('Be4')
        #self.match = parser.re_disambiguate_error.fullmatch('Be4d5')
        #self.matcherror = parser.re_disambiguate_error.fullmatch('Be4d6')
        self.matchfrom = parser.re_tokens.match('Be4')
        self.match = parser.re_disambiguate_error.match('Be4d5')
        self.matcherror = parser.re_disambiguate_error.match('Be4d6')
        self.assertEqual(self.matchfrom.group(), 'Be4')
        self.assertEqual(self.match.group(), 'Be4d5')
        self.assertEqual(self.matcherror.group(), 'Be4d6')
        p = self.pgn
        p.set_position_fen('8/8/4B3/8/2B1B3/8/8/k3K3 w - - 0 60')
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        p.tokens.append(self.matchfrom)

    def tearDown(self):
        del self.pgn

    def unchanged_after_valid_move(self):
        p = self.pgn
        self.assertEqual(p.tokens, [self.match])
        self.assertEqual(p.error_tokens, [])
        self.assertEqual(p._state, 4)
        self.assertEqual(p._move_error_state, 2)

    def changed_after_invalid_move(self):
        p = self.pgn
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [self.matcherror.group()])
        self.assertEqual(p._state, 2)
        self.assertEqual(p._move_error_state, 2)

    def unchanged_before_move(self):
        p = self.pgn
        self.assertEqual(p.tokens, [self.matchfrom])
        self.assertEqual(p.error_tokens, [])
        self.assertEqual(p._state, 4)
        self.assertEqual(p._move_error_state, 2)

    def changed_after_illegal_move(self):
        p = self.pgn
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [self.match.group()])
        self.assertEqual(p._state, 2)
        self.assertEqual(p._move_error_state, 2)

    def test_play_disambiguated_move_00(self):
        self.unchanged_before_move()

    def test_play_disambiguated_move_01(self):
        p = self.pgn
        self.assertRaisesRegex(
            TypeError,
            ''.join(("_play_disambiguated_move\(\) missing 1 required ",
                     "positional argument: 'pgn_tosquare'")),
            p._play_disambiguated_move,
            *(None,None))
        self.unchanged_before_move()

    def test_play_disambiguated_move_02(self):
        p = self.pgn
        self.assertRaisesRegex(
            TypeError,
            ''.join(("_play_disambiguated_move\(\) takes 4 positional ",
                     "arguments but 5 were given")),
            p._play_disambiguated_move,
            *(None,None,None,None))
        self.unchanged_before_move()

    def test_play_disambiguated_move_03(self):
        p = self.pgn
        p.tokens[-1] = self.matcherror
        p._play_disambiguated_move('B', 'e4', 'd6')
        self.changed_after_invalid_move()

    def test_play_disambiguated_move_04(self):
        p = self.pgn
        p.tokens[-1] = self.match
        p._play_disambiguated_move('B', 'e4', 'd5')
        self.unchanged_after_valid_move()

    def test_play_disambiguated_move_05(self):
        p = self.pgn
        p.set_position_fen('8/8/4B3/4r3/2B1B3/8/8/k3K3 w - - 0 60')
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        p.tokens[-1] = self.match
        p._play_disambiguated_move('B', 'e4', 'd5')
        self.changed_after_illegal_move()

    def test_play_disambiguated_move_06(self):
        p = self.pgn
        p.set_position_fen('8/8/4B3/8/2B5/5B2/8/k3K3 w - - 0 60')
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        p.tokens[-1] = self.match
        p._play_disambiguated_move('B', 'e4', 'd5')
        self.changed_after_illegal_move()

    def test_play_disambiguated_move_07(self):
        p = self.pgn
        p.set_position_fen('8/8/4B3/8/2B1N3/5B2/8/k3K3 w - - 0 60')
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        p.tokens[-1] = self.match
        p._play_disambiguated_move('B', 'f3', 'd5')
        self.changed_after_illegal_move()

    def test_play_disambiguated_move_08(self):
        p = self.pgn
        p.set_position_fen('8/8/4B3/3P4/2B1B3/8/8/k3K3 w - - 0 60')
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        p.tokens[-1] = self.match
        p._play_disambiguated_move('B', 'e4', 'd5')
        self.changed_after_illegal_move()


class Pgn__illegal_play_move(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test__illegal_play_move(self):
        p = self.pgn
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        m = parser.re_tokens.match('e4')
        p.tokens.append(m)
        self.assertEqual(p._state, None)
        self.assertEqual(p._move_error_state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p.tokens, [m])
        self.assertEqual(p.error_tokens, [])
        p._illegal_play_move()
        self.assertEqual(p._state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p._move_error_state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, ['e4'])


class Pgn__illegal_play_castles(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test__illegal_play_castles(self):
        p = self.pgn
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        m = parser.re_tokens.match('e4')
        p.tokens.append(m)
        self.assertEqual(p._state, None)
        self.assertEqual(p._move_error_state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p.tokens, [m])
        self.assertEqual(p.error_tokens, [])
        p._illegal_play_castles()
        self.assertEqual(p._state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p._move_error_state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, ['e4'])


class Pgn__illegal_play_disambiguated_move(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test__illegal_play_disambiguated_move(self):
        p = self.pgn
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        m = parser.re_tokens.match('e4')
        p.tokens.append(m)
        self.assertEqual(p._state, None)
        self.assertEqual(p._move_error_state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p.tokens, [m])
        self.assertEqual(p.error_tokens, [])
        p._illegal_play_disambiguated_move()
        self.assertEqual(p._state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p._move_error_state,
                         constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, ['e4'])


class Pgn_is_tag_roster_valid(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_is_tag_roster_valid_01(self):
        p = self.pgn
        p.collected_game = (p.tags_in_order, {}, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_02(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = []
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_03(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_04(self):
        p = self.pgn
        tags = {'a':'text'}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_05(self):
        p = self.pgn
        tags = {'Event':'t',
                'Site':'t',
                'Date':'t',
                'Round':'t',
                'White':'t',
                'Black':'t',
                'Result':'t'}
        p.tags_in_order = [None]*7
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), True)


class Pgn_is_movetext_valid(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_is_movetext_valid_01(self):
        p = self.pgn
        p.collected_game = (p.tags_in_order, {}, p.tokens, p.error_tokens)
        self.assertEqual(p.is_movetext_valid(), True)

    def test_is_movetext_valid_02(self):
        p = self.pgn
        p.collected_game = (p.tags_in_order, {}, p.tokens, ['a'])
        self.assertEqual(p.is_movetext_valid(), False)


class Pgn_is_pgn_valid(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_is_pgn_valid_01(self):
        p = self.pgn
        p.collected_game = (p.tags_in_order, {}, p.tokens, p.error_tokens)
        self.assertEqual(p.is_pgn_valid(), False)


class Pgn_get_fen_string(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_get_fen_string_01(self):
        p = self.pgn
        p.set_position_fen('3k4/7R/2q5/2p5/3p4/1P1B4/2P5/6K1 b - - 15 47')
        p._play_move('K', '', '', 'e8', '')
        s = parser.get_fen_string(p.ravstack[-1][-1])
        self.assertEqual(s, '4k3/7R/2q5/2p5/3p4/1P1B4/2P5/6K1 w - - 0 1')

    def test_get_position_string_02(self):
        p = self.pgn
        p.set_position_fen('3k4/7R/2q5/2p5/3p4/1P1B4/2P5/6K1 b - - 15 47')
        s = parser.get_fen_string(p.ravstack[-1][-1])
        self.assertEqual(s.encode('iso-8859-1'),
                         b'3k4/7R/2q5/2p5/3p4/1P1B4/2P5/6K1 b - - 0 1')


class RealGamesPGN(unittest.TestCase):
    # A test for each game which exposed a problem.
    # The text is copied unchanged from source where possible.

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_01(self):
        # self.pgn._state set to False when processing move 13. ... Rb8
        # Obvious thought is it thinks the black king is still on e8 despite
        # 12. ... O-O.
        # The setting is delayed until black's 14th move by transposing white's
        # 13th and 14th moves.
        # Putting self.pgn._fen.__dict__ in the self.assertNotEqual() call's
        # message proved both active_side_king and inactive_side_king still
        # referred to the king's original squares despite the castling moves.
        game = ''.join(("""[Event "4NCL/Div1a/WGHK1 vs. OXF1"]
[Site "Sunningdale ENG"]
[Date "2009.10.24"]
[Round "1.4"]
[White "White, Michael JR"]
[Black "Hanley, Craig A"]
[Result "0-1"]
[ECO "C45"]
[WhiteElo "2227"]
[BlackElo "2429"]
[PlyCount "60"]
[EventDate "2009.10.24"]
[SourceDate "2009.10.24"]

1. e4 e5 2. Nf3 Nc6 3. d4 exd4 4. Nxd4 Bc5 5. Be3 Qf6 6. c3 Nge7 7. Bc4 Ne5 8.
Be2 Qg6 9. O-O d6 10. f4 Qxe4 11. Bf2 N5c6 12. Nb5 O-O 13. Nxc7 Rb8 14. Nd2 Qg6
15. b4 Bxf2+ 16. Rxf2 Bf5 17. Nc4 Rfd8 18. Ne3 d5 19. b5 Rbc8 20. Nexd5 Nxd5
21. Nxd5 Be4 22. c4 Bxd5 23. cxd5 Nb4 24. Bf3 Qb6 25. Qb3 Rc2 26. Raf1 Rdc8 27.
Bd1 Rxf2 28. Rxf2 Qd4 29. Kf1 Rc1 30. Ke2 Nxd5 0-1
"""))
        p = self.pgn
        p.get_first_game(game)
        self.assertEqual(sorted(i for i in p.collected_game[1].items()),
                         sorted([('Event', '4NCL/Div1a/WGHK1 vs. OXF1'),
                                 ('Site', 'Sunningdale ENG'),
                                 ('Date', '2009.10.24'),
                                 ('Round', '1.4'),
                                 ('White', 'White, Michael JR'),
                                 ('Black', 'Hanley, Craig A'),
                                 ('Result', '0-1'),
                                 ('ECO', 'C45'),
                                 ('WhiteElo', '2227'),
                                 ('BlackElo', '2429'),
                                 ('PlyCount', '60'),
                                 ('EventDate', '2009.10.24'),
                                 ('SourceDate', '2009.10.24')]))
        manual_tokens = '''
e4 e5 Nf3 Nc6 d4 exd4 Nxd4 Bc5 Be3 Qf6 c3 Nge7 Bc4 Ne5
Be2 Qg6 O-O d6 f4 Qxe4 Bf2 N5c6 Nb5 O-O Nxc7 Rb8 Nd2 Qg6
b4 Bxf2+ Rxf2 Bf5 Nc4 Rfd8 Ne3 d5 b5 Rbc8 Nexd5 Nxd5
Nxd5 Be4 c4 Bxd5 cxd5 Nb4 Bf3 Qb6 Qb3 Rc2 Raf1 Rdc8
Bd1 Rxf2 Rxf2 Qd4 Kf1 Rc1 Ke2 Nxd5 0-1
'''.split()
        for e, t in enumerate(p.collected_game[2]):
            self.assertEqual((e, t.group()), (e, manual_tokens[e]))

    def test_02(self):
        # self.pgn._state set to False when processing move 15. ... fxg3
        # self.pgn._fen.en_passant equals 'g4'.  It should be 'g3'.
        # FEN_EN_PASSANT_TARGET_RANK added to fen_constants.py and used in
        # _play_move() method in fen.py to modify setting of en_passant.
        # FEN_WHITE_CAPTURE_EN_PASSANT and FEN_BLACK_CAPTURE_EN_PASSANT added
        # to enable this.
        game = ''.join(("""[Event "4NCL/Div1a/ADS vs. WGHK1"]
[Site "Sunningdale ENG"]
[Date "2009.10.25"]
[Round "2.6"]
[White "Broomfield, Matthew P"]
[Black "Swindells, Jonathan E"]
[Result "1-0"]
[ECO "E92"]
[WhiteElo "2339"]
[BlackElo "2170"]
[PlyCount "90"]
[EventDate "2009.10.25"]
[SourceDate "2009.10.24"]

1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O 6. Be2 e5 7. Be3 Nc6 8. d5
Ne7 9. Nd2 Ne8 10. b4 f5 11. f3 f4 12. Bf2 g5 13. c5 Rf6 14. Nc4 Rg6 15. g4
fxg3 16. hxg3 g4 17. fxg4 Bh6 18. Ne3 a5 19. Nf5 Bg5 20. bxa5 Rxa5 21. Qb3 Nxf5
22. gxf5 Rh6 23. Rxh6 Bxh6 24. Rd1 Kg7 25. Qb4 Ra8 26. a4 dxc5 27. Bxc5 Qg5 28.
Bf8+ Kf7 29. Bh5+ Qxh5 30. Qe7+ Kg8 31. Bxh6 Qh1+ 32. Kf2 Qh2+ 33. Kf3 Qh5+ 34.
Kg2 Qxh6 35. Qxe8+ Qf8 36. Qxe5 Bd7 37. d6 cxd6 38. Rxd6 Bxa4 39. Nd5 Qg7 40.
f6 Qf7 41. Nb6 Qa2+ 42. Kh3 Ra5 43. Rd8+ Kf7 44. Qe7+ Kg6 45. Qg7+ Kh5 1-0
"""))
        p = self.pgn
        p.get_first_game(game)
        self.assertEqual(sorted(i for i in p.collected_game[1].items()),
                         sorted([('Event', '4NCL/Div1a/ADS vs. WGHK1'),
                                 ('Site', 'Sunningdale ENG'),
                                 ('Date', '2009.10.25'),
                                 ('Round', '2.6'),
                                 ('White', 'Broomfield, Matthew P'),
                                 ('Black', 'Swindells, Jonathan E'),
                                 ('Result', '1-0'),
                                 ('ECO', 'E92'),
                                 ('WhiteElo', '2339'),
                                 ('BlackElo', '2170'),
                                 ('PlyCount', '90'),
                                 ('EventDate', '2009.10.25'),
                                 ('SourceDate', '2009.10.24')]))
        manual_tokens = '''
d4 Nf6 c4 g6 Nc3 Bg7 e4 d6 Nf3 O-O Be2 e5 Be3 Nc6 d5
Ne7 Nd2 Ne8 b4 f5 f3 f4 Bf2 g5 c5 Rf6 Nc4 Rg6 g4
fxg3 hxg3 g4 fxg4 Bh6 Ne3 a5 Nf5 Bg5 bxa5 Rxa5 Qb3 Nxf5
gxf5 Rh6 Rxh6 Bxh6 Rd1 Kg7 Qb4 Ra8 a4 dxc5 Bxc5 Qg5
Bf8+ Kf7 Bh5+ Qxh5 Qe7+ Kg8 Bxh6 Qh1+ Kf2 Qh2+ Kf3 Qh5+
Kg2 Qxh6 Qxe8+ Qf8 Qxe5 Bd7 d6 cxd6 Rxd6 Bxa4 Nd5 Qg7
f6 Qf7 Nb6 Qa2+ Kh3 Ra5 Rd8+ Kf7 Qe7+ Kg6 Qg7+ Kh5 1-0
'''.split()
        for e, t in enumerate(p.collected_game[2]):
            self.assertEqual((e, t.group()), (e, manual_tokens[e]))

    def test_03(self):
        # Internal board description not adjusted corrrectly after a pawn
        # promotion.  Specifically the piece_locations attribute added in
        # the pgn_dev_3520 branch.
        game = ''.join(("""[Event "NCL967 SW Dragons-Midland Mons"]
[Site "Rd1"]
[Date "1996.10.19"]
[Round "1.8"]
[White "Regan, Natasha"]
[Black "Blackburn, Sandra"]
[Result "1-0"]
[ECO "C00"]
[WhiteElo "2155"]
[PlyCount "79"]
[EventDate "1996.10.19"]
[Source "J.Saunders"]
[SourceDate "1998.06.06"]

1. e4 e6 2. d4 c6 3. e5 Be7 4. Nc3 d5 5. Qg4 g6 6. Bd3 Qb6 7. Nf3 h5 8. Qf4 Bd7
9. a4 a5 10. O-O Na6 11. Ng5 Bxg5 12. Qxg5 Ne7 13. Qf6 Rg8 14. Bg5 Qd8 15. Rfe1
c5 16. Nb5 Bxb5 17. Bxb5+ Nc6 18. Qxd8+ Rxd8 19. Bxd8 Kxd8 20. Bxa6 bxa6 21.
dxc5 Nd4 22. Rac1 Kc7 23. c4 Rd8 24. Kf1 Nb3 25. cxd5 Nxc1 26. d6+ Kc6 27. Rxc1
Rb8 28. Rc2 Rb4 29. Ke2 Re4+ 30. Kf3 Rxe5 31. Rd2 Kd7 32. c6+ Kd8 33. c7+ Kd7
34. Rc2 Rf5+ 35. Ke4 Kxd6 36. c8=Q Re5+ 37. Kf3 Rf5+ 38. Ke2 Re5+ 39. Kf1 Rd5
40. Qc7# 1-0
"""))
        p = self.pgn
        p.get_first_game(game)
        self.assertEqual(sorted(i for i in p.collected_game[1].items()),
                         sorted([('Event', 'NCL967 SW Dragons-Midland Mons'),
                                 ('Site', 'Rd1'),
                                 ('Date', '1996.10.19'),
                                 ('Round', '1.8'),
                                 ('White', 'Regan, Natasha'),
                                 ('Black', 'Blackburn, Sandra'),
                                 ('Result', '1-0'),
                                 ('ECO', 'C00'),
                                 ('WhiteElo', '2155'),
                                 ('PlyCount', '79'),
                                 ('EventDate', '1996.10.19'),
                                 ('Source', 'J.Saunders'),
                                 ('SourceDate', '1998.06.06')]))
        manual_tokens = '''
e4 e6 d4 c6 e5 Be7 Nc3 d5 Qg4 g6 Bd3 Qb6 Nf3 h5 Qf4 Bd7
a4 a5 O-O Na6 Ng5 Bxg5 Qxg5 Ne7 Qf6 Rg8 Bg5 Qd8 Rfe1
c5 Nb5 Bxb5 Bxb5+ Nc6 Qxd8+ Rxd8 Bxd8 Kxd8 Bxa6 bxa6
dxc5 Nd4 Rac1 Kc7 c4 Rd8 Kf1 Nb3 cxd5 Nxc1 d6+ Kc6 Rxc1
Rb8 Rc2 Rb4 Ke2 Re4+ Kf3 Rxe5 Rd2 Kd7 c6+ Kd8 c7+ Kd7
Rc2 Rf5+ Ke4 Kxd6 c8=Q Re5+ Kf3 Rf5+ Ke2 Re5+ Kf1 Rd5
Qc7# 1-0
'''.split()
        for e, t in enumerate(p.collected_game[2]):
            self.assertEqual((e, t.group()), (e, manual_tokens[e]))

    def test_04(self):
        # Problem exposed by Howell-Kourtseva from All_4NCL_1996_2010.pgn
        # introduced since revision 3520 in the pgn_dev_3520 branch.
        # The '{' and '}' tokens disrupt the odd and even tests somehow,
        # but getting past that the move which fails is '18... Bxd3'.
        # 18... Be4 is accepted which means the black pawn on e6 seems to
        # be not there, leaving black in check so Bxd3 is illegal.
        # No black pieces have the bit for their square set.  So it is
        # initialisation probably.
        game = ''.join(("""[Event "4NCL/Div1a/CAMB1 vs. JUTK"]
[Site "Sunningdale ENG"]
[Date "2009.10.25"]
[Round "2.8"]
[White "Howell, Chris I"]
[Black "Kourtseva, Julie"]
[Result "1-0"]
[ECO "B01"]
[WhiteElo "2077"]
[BlackElo "1706"]
[Annotator "Howell, Chris"]
[PlyCount "151"]
[EventDate "2009.10.25"]
[EventCountry "ENG"]
[SourceDate "2009.10.24"]

1. e4 d5 2. exd5 Qxd5 3. Nf3 c6 4. Nc3 Qa5 5. Bc4 Bf5 6. O-O e6 7. d3 Be7 8.
Bd2 $146 (8. Be3 Nf6 9. h3 Nbd7 10. a3 Qc7 11. Qd2 Bd6 12. Rfe1 Ne5 13. Nxe5
Bxe5 14. d4 Bd6 15. Bd3 Bg6 16. Ne2 Nd5 17. c3 Nxe3 18. Qxe3 Bxd3 19. Qxd3
O-O-O 20. Qc2 Rdg8 21. b4 h5 22. a4 g5 23. b5 h4 24. Qe4 Qd7 25. bxc6 Qxc6 26.
Qxc6+ bxc6 27. f3 Kc7 28. Rab1 Re8 29. Nc1 Bf4 30. Rd1 Rb8 {1-0 Yurkina,
Y-Gelivanova,Y/Dagomys 2004}) 8... Qc7 9. Nd4 Bg6 10. Qf3 $1 Bf6 $6 11. Nb3 $2
(11. Bf4 $1 e5 12. Bg3 Nd7 13. h4 h5 14. a4 $14) 11... Ne7 $2 (11... Nd7 $14)
12. Bf4 Be5 13. Bxe5 Qxe5 14. Rfe1 Qc7 15. Nd4 O-O $2 (15... e5 16. Qg3 Nd7 17.
Nf3 $16) 16. Bxe6 $1 Qd8 $5 17. Bb3 Nd7 18. a4 $6 (18. Qf4 $1 $18) 18... Nc5
19. Bc4 Re8 20. Nb3 $6 (20. Qf4 $1) 20... Nxb3 21. Bxb3 Nf5 22. Bc4 $2 (22.
Rxe8+ Qxe8 23. Qe4 $16) 22... Nd4 23. Rxe8+ Qxe8 24. Qd1 Qe7 25. Qd2 (25. Ne4
$1 $16) 25... Re8 26. h3 Qb4 27. Re1 Rxe1+ 28. Qxe1 h6 29. Qe8+ Kh7 30. Bxf7
Bxf7 31. Qxf7 Qxb2 32. Ne4 Qa1+ 33. Kh2 Ne2 34. Ng5+ hxg5 35. Qh5+ Kg8 36. Qe8+
Kh7 37. Qxe2 Qxa4 38. Qh5+ Kg8 39. c4 Qc2 40. Qe8+ Kh7 41. Qe4+ Kh8 42. Qd4 Qa2
43. h4 gxh4 44. Qxh4+ Kg8 45. Qd8+ Kh7 46. Qh4+ Kg8 47. g4 Qb2 48. Kg2 Qd4 49.
Qg3 Qd8 (49... a5 $1) 50. g5 g6 51. Qe3 Qd7 52. Kf1 c5 53. Ke2 b6 54. Qe4 Kf7
55. Qf4+ Ke8 56. Kd2 Qe7 57. Qg4 Kf8 {(=)} 58. f4 Qf7 59. Kc2 Kg7 60. Qf3 b5
61. Qe4 $1 bxc4 62. dxc4 Kg8 63. Kb3 $1 Kg7 64. Qe5+ Kg8 65. Qd5 Kg7 66. Qxf7+
Kxf7 67. Ka4 Ke6 68. Kb5 Kf5 69. Kxc5 Kxf4 {Diagram #} 70. Kc6 $3 (70. Kb5 Ke4
71. Kc6 $3 $18) (70. Kd4 $4 Kxg5 71. c5 Kf6 72. Kd5 Ke7 73. Kc6 g5 74. Kb7 g4
75. c6 g3 76. c7 g2 77. c8=Q g1=Q 78. Qc7+ Ke6 79. Qc6+ Kf5 80. Qb5+ Kg6 81.
Qa6+ Kf5 82. Qxa7 $11) 70... Kxg5 71. c5 $1 a5 72. Kb5 $1 a4 73. Kxa4 $1 Kf6
74. Kb5 (74. Ka5 $18) 74... Ke7 75. Kb6 Kd8 76. Kb7 $1 1-0
"""))
        p = self.pgn
        p.get_first_game(game)
        self.assertEqual(sorted(i for i in p.collected_game[1].items()),
                         sorted([('Event', '4NCL/Div1a/CAMB1 vs. JUTK'),
                                 ('Site', 'Sunningdale ENG'),
                                 ('Date', '2009.10.25'),
                                 ('Round', '2.8'),
                                 ('White', 'Howell, Chris I'),
                                 ('Black', 'Kourtseva, Julie'),
                                 ('Result', '1-0'),
                                 ('ECO', 'B01'),
                                 ('WhiteElo', '2077'),
                                 ('BlackElo', '1706'),
                                 ('Annotator', 'Howell, Chris'),
                                 ('PlyCount', '151'),
                                 ('EventDate', '2009.10.25'),
                                 ('EventCountry', 'ENG'),
                                 ('SourceDate', '2009.10.24'),]))
        manual_tokens = '''
e4 d5 exd5 Qxd5 Nf3 c6 Nc3 Qa5 Bc4 Bf5 O-O e6 d3 Be7
Bd2 $146 ( Be3 Nf6 h3 Nbd7 a3 Qc7 Qd2 Bd6 Rfe1 Ne5 Nxe5
Bxe5 d4 Bd6 Bd3 Bg6 Ne2 Nd5 c3 Nxe3 Qxe3 Bxd3 Qxd3
O-O-O Qc2 Rdg8 b4 h5 a4 g5 b5 h4 Qe4 Qd7 bxc6 Qxc6
Qxc6+ bxc6 f3 Kc7 Rab1 Re8 Nc1 Bf4 Rd1 Rb8
'''.split()
        manual_tokens.extend(['{1-0 Yurkina,\nY-Gelivanova,Y/Dagomys 2004}'])
        manual_tokens.extend('''
) Qc7 Nd4 Bg6 Qf3 $1 Bf6 $6 Nb3 $2
( Bf4 $1 e5 Bg3 Nd7 h4 h5 a4 $14 ) Ne7 $2 ( Nd7 $14 )
Bf4 Be5 Bxe5 Qxe5 Rfe1 Qc7 Nd4 O-O $2 ( e5 Qg3 Nd7
Nf3 $16 ) Bxe6 $1 Qd8 $5 Bb3 Nd7 a4 $6 ( Qf4 $1 $18 ) Nc5
Bc4 Re8 Nb3 $6 ( Qf4 $1 ) Nxb3 Bxb3 Nf5 Bc4 $2 (
Rxe8+ Qxe8 Qe4 $16 ) Nd4 Rxe8+ Qxe8 Qd1 Qe7 Qd2 ( Ne4
$1 $16 ) Re8 h3 Qb4 Re1 Rxe1+ Qxe1 h6 Qe8+ Kh7 Bxf7
Bxf7 Qxf7 Qxb2 Ne4 Qa1+ Kh2 Ne2 Ng5+ hxg5 Qh5+ Kg8 Qe8+
Kh7 Qxe2 Qxa4 Qh5+ Kg8 c4 Qc2 Qe8+ Kh7 Qe4+ Kh8 Qd4 Qa2
h4 gxh4 Qxh4+ Kg8 Qd8+ Kh7 Qh4+ Kg8 g4 Qb2 Kg2 Qd4
Qg3 Qd8 ( a5 $1 ) g5 g6 Qe3 Qd7 Kf1 c5 Ke2 b6 Qe4 Kf7
Qf4+ Ke8 Kd2 Qe7 Qg4 Kf8 {(=)} f4 Qf7 Kc2 Kg7 Qf3 b5
Qe4 $1 bxc4 dxc4 Kg8 Kb3 $1 Kg7 Qe5+ Kg8 Qd5 Kg7 Qxf7+
Kxf7 Ka4 Ke6 Kb5 Kf5 Kxc5 Kxf4
'''.split())
        manual_tokens.extend(['{Diagram #}'])
        manual_tokens.extend('''
Kc6 $3 ( Kb5 Ke4
Kc6 $3 $18 ) ( Kd4 $4 Kxg5 c5 Kf6 Kd5 Ke7 Kc6 g5 Kb7 g4
c6 g3 c7 g2 c8=Q g1=Q Qc7+ Ke6 Qc6+ Kf5 Qb5+ Kg6
Qa6+ Kf5 Qxa7 $11 ) Kxg5 c5 $1 a5 Kb5 $1 a4 Kxa4 $1 Kf6
Kb5 ( Ka5 $18 ) Ke7 Kb6 Kd8 Kb7 $1 1-0
'''.split())
        for e, t in enumerate(p.collected_game[2]):
            self.assertEqual((e, t.group()), (e, manual_tokens[e]))

    def test_05(self):
        # Problem exposed by Howell-Kourtseva from All_4NCL_1996_2010.pgn
        # after the pgn_dev_3520 branch was merged into trunk.
        # The NAG immediately before the termination was not recognised when
        # game score was read from database record because all whitespace had
        # been removed.
        game = ''.join(("""[Event "4NCL/Div1a/CAMB1 vs. JUTK"]
[Site "Sunningdale ENG"]
[Date "2009.10.25"]
[Round "2.8"]
[White "Howell, Chris I"]
[Black "Kourtseva, Julie"]
[Result "1-0"]
[ECO "B01"]
[WhiteElo "2077"]
[BlackElo "1706"]
[Annotator "Howell, Chris"]
[PlyCount "151"]
[EventDate "2009.10.25"]
[EventCountry "ENG"]
[SourceDate "2009.10.24"]

e4d5exd5Qxd5Nf3c6Nc3Qa5Bc4Bf5O-Oe6d3Be7
Bd2$146(Be3Nf6h3Nbd7a3Qc7Qd2Bd6Rfe1Ne5Nxe5
Bxe5d4Bd6Bd3Bg6Ne2Nd5c3Nxe3Qxe3Bxd3Qxd3
O-O-OQc2Rdg8b4h5a4g5b5h4Qe4Qd7bxc6Qxc6
Qxc6+bxc6f3Kc7Rab1Re8Nc1Bf4Rd1Rb8{1-0 Yurkina,
Y-Gelivanova,Y/Dagomys 2004})Qc7Nd4Bg6Qf3$1Bf6$6Nb3$2
(Bf4$1e5Bg3Nd7h4h5a4$14)Ne7$2(Nd7$14)
Bf4Be5Bxe5Qxe5Rfe1Qc7Nd4O-O$2(e5Qg3Nd7
Nf3$16)Bxe6$1Qd8$5Bb3Nd7a4$6(Qf4$1$18)Nc5
Bc4Re8Nb3$6(Qf4$1)Nxb3Bxb3Nf5Bc4$2(
Rxe8+Qxe8Qe4$16)Nd4Rxe8+Qxe8Qd1Qe7Qd2(Ne4
$1$16)Re8h3Qb4Re1Rxe1+Qxe1h6Qe8+Kh7Bxf7
Bxf7Qxf7Qxb2Ne4Qa1+Kh2Ne2Ng5+hxg5Qh5+Kg8Qe8+
Kh7Qxe2Qxa4Qh5+Kg8c4Qc2Qe8+Kh7Qe4+Kh8Qd4Qa2
h4gxh4Qxh4+Kg8Qd8+Kh7Qh4+Kg8g4Qb2Kg2Qd4
Qg3Qd8(a5$1)g5g6Qe3Qd7Kf1c5Ke2b6Qe4Kf7
Qf4+Ke8Kd2Qe7Qg4Kf8{(=)}f4Qf7Kc2Kg7Qf3b5
Qe4$1bxc4dxc4Kg8Kb3$1Kg7Qe5+Kg8Qd5Kg7Qxf7+
Kxf7Ka4Ke6Kb5Kf5Kxc5Kxf4{Diagram #}Kc6$3(Kb5Ke4
Kc6$3$18)(Kd4$4Kxg5c5Kf6Kd5Ke7Kc6g5Kb7g4
c6g3c7g2c8=Qg1=QQc7+Ke6Qc6+Kf5Qb5+Kg6
Qa6+Kf5Qxa7$11)Kxg5c5$1a5Kb5$1a4Kxa4$1Kf6
Kb5(Ka5$18)Ke7Kb6Kd8Kb7$11-0
"""))
        p = self.pgn
        p.get_first_game(game)
        self.assertEqual(sorted(i for i in p.collected_game[1].items()),
                         sorted([('Event', '4NCL/Div1a/CAMB1 vs. JUTK'),
                                 ('Site', 'Sunningdale ENG'),
                                 ('Date', '2009.10.25'),
                                 ('Round', '2.8'),
                                 ('White', 'Howell, Chris I'),
                                 ('Black', 'Kourtseva, Julie'),
                                 ('Result', '1-0'),
                                 ('ECO', 'B01'),
                                 ('WhiteElo', '2077'),
                                 ('BlackElo', '1706'),
                                 ('Annotator', 'Howell, Chris'),
                                 ('PlyCount', '151'),
                                 ('EventDate', '2009.10.25'),
                                 ('EventCountry', 'ENG'),
                                 ('SourceDate', '2009.10.24'),]))
        manual_tokens = '''
e4 d5 exd5 Qxd5 Nf3 c6 Nc3 Qa5 Bc4 Bf5 O-O e6 d3 Be7
Bd2 $146 ( Be3 Nf6 h3 Nbd7 a3 Qc7 Qd2 Bd6 Rfe1 Ne5 Nxe5
Bxe5 d4 Bd6 Bd3 Bg6 Ne2 Nd5 c3 Nxe3 Qxe3 Bxd3 Qxd3
O-O-O Qc2 Rdg8 b4 h5 a4 g5 b5 h4 Qe4 Qd7 bxc6 Qxc6
Qxc6+ bxc6 f3 Kc7 Rab1 Re8 Nc1 Bf4 Rd1 Rb8
'''.split()
        manual_tokens.extend(['{1-0 Yurkina,\nY-Gelivanova,Y/Dagomys 2004}'])
        manual_tokens.extend('''
) Qc7 Nd4 Bg6 Qf3 $1 Bf6 $6 Nb3 $2
( Bf4 $1 e5 Bg3 Nd7 h4 h5 a4 $14 ) Ne7 $2 ( Nd7 $14 )
Bf4 Be5 Bxe5 Qxe5 Rfe1 Qc7 Nd4 O-O $2 ( e5 Qg3 Nd7
Nf3 $16 ) Bxe6 $1 Qd8 $5 Bb3 Nd7 a4 $6 ( Qf4 $1 $18 ) Nc5
Bc4 Re8 Nb3 $6 ( Qf4 $1 ) Nxb3 Bxb3 Nf5 Bc4 $2 (
Rxe8+ Qxe8 Qe4 $16 ) Nd4 Rxe8+ Qxe8 Qd1 Qe7 Qd2 ( Ne4
$1 $16 ) Re8 h3 Qb4 Re1 Rxe1+ Qxe1 h6 Qe8+ Kh7 Bxf7
Bxf7 Qxf7 Qxb2 Ne4 Qa1+ Kh2 Ne2 Ng5+ hxg5 Qh5+ Kg8 Qe8+
Kh7 Qxe2 Qxa4 Qh5+ Kg8 c4 Qc2 Qe8+ Kh7 Qe4+ Kh8 Qd4 Qa2
h4 gxh4 Qxh4+ Kg8 Qd8+ Kh7 Qh4+ Kg8 g4 Qb2 Kg2 Qd4
Qg3 Qd8 ( a5 $1 ) g5 g6 Qe3 Qd7 Kf1 c5 Ke2 b6 Qe4 Kf7
Qf4+ Ke8 Kd2 Qe7 Qg4 Kf8 {(=)} f4 Qf7 Kc2 Kg7 Qf3 b5
Qe4 $1 bxc4 dxc4 Kg8 Kb3 $1 Kg7 Qe5+ Kg8 Qd5 Kg7 Qxf7+
Kxf7 Ka4 Ke6 Kb5 Kf5 Kxc5 Kxf4
'''.split())
        manual_tokens.extend(['{Diagram #}'])
        manual_tokens.extend('''
Kc6 $3 ( Kb5 Ke4
Kc6 $3 $18 ) ( Kd4 $4 Kxg5 c5 Kf6 Kd5 Ke7 Kc6 g5 Kb7 g4
c6 g3 c7 g2 c8=Q g1=Q Qc7+ Ke6 Qc6+ Kf5 Qb5+ Kg6
Qa6+ Kf5 Qxa7 $11 ) Kxg5 c5 $1 a5 Kb5 $1 a4 Kxa4 $1 Kf6
Kb5 ( Ka5 $18 ) Ke7 Kb6 Kd8 Kb7 $1 1-0
'''.split())
        for e, t in enumerate(p.collected_game[2]):
            self.assertEqual((e, t.group()), (e, manual_tokens[e]))

    def test_06(self):
        # Problem exposed by Butterworth-Russant from All_4NCL_1996_2010.pgn
        # introduced since revision 3520 in the pgn_dev_3520 branch.
        # The game starts from a position defined by FEN, presumably because
        # the early score is lost.
        game = ''.join(("""[Event "4NCL/Div4/SL03 vs. GREN"]
[Site "West Bromwich ENG"]
[Date "2003.11.22"]
[Round "1.6"]
[White "Butterworth, Paul"]
[Black "Russant, Stuart"]
[Result "0-1"]
[WhiteElo "1608"]
[BlackElo "1208"]
[SetUp "1"]
[FEN "r3k2r/ppp1qppp/2n5/8/1b1P4/2NBnQ2/PP3PPP/2R2RK1 b kq - 0 14"]
[PlyCount "23"]
[EventDate "2003.11.22"]

14... Nxf1 15. Kxf1 O-O 16. Nd5 Qd6 17. a3 Qxh2 18. g3 Qh6 19. Rc4 Bd6 20. Ne3
Rad8 21. Ng4 Qh3+ 22. Kg1 Rde8 23. Bf1 Re1 24. Ne3 Re8 25. Ng2 Rxf1+ 0-1
"""))
        p = self.pgn
        p.get_first_game(game)
        self.assertEqual(
            sorted(i for i in p.collected_game[1].items()),
            sorted([
                ('Event', '4NCL/Div4/SL03 vs. GREN'),
                ('Site', 'West Bromwich ENG'),
                ('Date', '2003.11.22'),
                ('Round', '1.6'),
                ('White', 'Butterworth, Paul'),
                ('Black', 'Russant, Stuart'),
                ('Result', '0-1'),
                ('WhiteElo', '1608'),
                ('BlackElo', '1208'),
                ('SetUp', '1'),
                ('FEN',
                 'r3k2r/ppp1qppp/2n5/8/1b1P4/2NBnQ2/PP3PPP/2R2RK1 b kq - 0 14'),
                ('PlyCount', '23'),
                ('EventDate', '2003.11.22')]))
        manual_tokens = '''
Nxf1 Kxf1 O-O Nd5 Qd6 a3 Qxh2 g3 Qh6 Rc4 Bd6 Ne3
Rad8 Ng4 Qh3+ Kg1 Rde8 Bf1 Re1 Ne3 Re8 Ng2 Rxf1+ 0-1
'''.split()
        for e, t in enumerate(p.collected_game[2]):
            self.assertEqual((e, t.group()), (e, manual_tokens[e]))


class Pgn_is_active_king_attacked(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_is_active_king_attacked_01(self):
        self.pgn.set_position_fen(fen='6k1/8/8/8/8/8/K6R/8 b - - 0 1')
        self.assertEqual(self.pgn.is_active_king_attacked(), False)

    def test_is_active_king_attacked_02(self):
        self.pgn.set_position_fen(fen='7k/8/8/8/8/8/K6R/8 b - - 0 1')
        self.assertEqual(self.pgn.is_active_king_attacked(), True)


class Pgn_is_square_attacked_by_side(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_is_square_attacked_by_side_01(self):
        self.pgn.set_position_fen(fen='6k1/8/8/8/8/8/K6R/8 w - - 0 1')
        self.assertEqual(self.pgn.is_square_attacked_by_side(23, 0), True)

    def test_is_square_attacked_by_side_02(self):
        self.pgn.set_position_fen(fen='7k/8/8/8/8/8/K6R/8 b - - 0 1')
        self.assertEqual(self.pgn.is_square_attacked_by_side(23, 1), False)

    def test_is_square_attacked_by_side_03(self):
        self.pgn.set_position_fen(fen='6k1/8/8/8/8/8/K6R/8 w - - 0 1')
        self.assertEqual(self.pgn.is_square_attacked_by_side(15, 0), True)

    def test_is_square_attacked_by_side_04(self):
        self.pgn.set_position_fen(fen='7k/8/8/8/8/8/K6R/8 b - - 0 1')
        self.assertEqual(self.pgn.is_square_attacked_by_side(15, 1), True)

    def test_is_square_attacked_by_side_05(self):
        self.pgn.set_position_fen(fen='6k1/8/8/8/8/8/K6R/8 w - - 0 1')
        self.assertEqual(self.pgn.is_square_attacked_by_side(14, 0), False)

    def test_is_square_attacked_by_side_06(self):
        self.pgn.set_position_fen(fen='7k/8/8/8/8/8/K6R/8 b - - 0 1')
        self.assertEqual(self.pgn.is_square_attacked_by_side(14, 1), True)

    def test_is_square_attacked_by_side_07(self):
        self.pgn.set_position_fen(fen='6k1/8/8/8/8/8/K6R/8 w - - 0 1')
        self.assertEqual(self.pgn.is_square_attacked_by_side(13, 0), False)

    def test_is_square_attacked_by_side_08(self):
        self.pgn.set_position_fen(fen='7k/8/8/8/8/8/K6R/8 b - - 0 1')
        self.assertEqual(self.pgn.is_square_attacked_by_side(13, 1), False)


class Pgn_count_attacks_on_square_by_side(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()

    def tearDown(self):
        del self.pgn

    def test_count_attacks_on_square_by_side_01(self):
        p = self.pgn
        p.set_position_fen(fen='6k1/8/8/8/8/8/2K4R/8 w - - 0 1')
        self.assertEqual(p.count_attacks_on_square_by_side(7, 0), 1)
        self.assertEqual(p.count_attacks_on_square_by_side(15, 0), 1)
        self.assertEqual(p.count_attacks_on_square_by_side(23, 0), 1)
        self.assertEqual(p.count_attacks_on_square_by_side(22, 0), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(48, 0), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(49, 0), 1)
        self.assertEqual(p.count_attacks_on_square_by_side(50, 0), 1)
        self.assertEqual(p.count_attacks_on_square_by_side(51, 0), 2)
        self.assertEqual(p.count_attacks_on_square_by_side(52, 0), 1)
        self.assertEqual(p.count_attacks_on_square_by_side(56, 0), 0)

    def test_count_attacks_on_square_by_side_02(self):
        p = self.pgn
        p.set_position_fen(fen='6k1/8/8/8/8/8/2K4R/8 b - - 0 1')
        self.assertEqual(p.count_attacks_on_square_by_side(7, 1), 1)
        self.assertEqual(p.count_attacks_on_square_by_side(15, 1), 1)
        self.assertEqual(p.count_attacks_on_square_by_side(23, 1), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(22, 1), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(48, 1), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(49, 1), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(50, 1), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(51, 1), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(52, 1), 0)
        self.assertEqual(p.count_attacks_on_square_by_side(56, 1), 0)


class Pgn__play_move(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        p = self.pgn
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME

        # A re.match object, rather than None, in the real case.
        self.match = parser.re_tokens.match('e4')
        p.tokens.append(self.match)

    def tearDown(self):
        del self.pgn

    def unchanged_after_valid_move(self):
        p = self.pgn
        self.assertEqual(p.tokens, [self.match])
        self.assertEqual(p.error_tokens, [])
        self.assertEqual(p._state, 4)
        self.assertEqual(p._move_error_state, 2)

    def changed_after_invalid_move(self):
        p = self.pgn
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, ['e4'])
        self.assertEqual(p._state, 2)
        self.assertEqual(p._move_error_state, 2)

    def test_play_move_00(self):
        self.unchanged_after_valid_move()

    def test_play_move_01(self):
        self.pgn.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 a')
        self.assertRaisesRegex(
            KeyError,
            "None",
            self.pgn._play_move,
            *(None, None, None, None, None,))
        self.assertEqual(self.pgn.tokens, [self.match])
        self.assertEqual(self.pgn.error_tokens, [])
        self.assertEqual(self.pgn._state, 2)
        self.assertEqual(self.pgn._move_error_state, 2)

    def test_play_move_02(self):
        self.pgn.set_position_fen()
        self.pgn._play_move('', '', '', 'e4', None)
        self.unchanged_after_valid_move()
        self.assertEqual(self.pgn.en_passant, 'e3')

    def test_play_move_03(self):
        self.pgn.set_position_fen()
        self.pgn._play_move('Q', '', '', 'd4', None)
        self.changed_after_invalid_move()

    def test_play_move_04(self):
        self.pgn.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1')
        self.pgn._play_move('Q', '', '', 'd4', None)
        self.unchanged_after_valid_move()

    def test_play_move_05(self):
        self.pgn.set_position_fen(fen='1n6/8/b7/1N6/4N3/3K4/8/7k w - - 0 1')
        self.pgn._play_move('N', '', '', 'd6', None)
        self.unchanged_after_valid_move()
        self.assertEqual(self.pgn.en_passant, '-')

    def test_play_move_06(self):
        self.pgn.set_position_fen(fen='8/8/8/2k1K3/8/8/8/8 w - - 0 1')
        self.pgn._play_move('K', '', '', 'd6', None)
        self.changed_after_invalid_move()

    def test_play_move_07(self):
        self.pgn.set_position_fen(fen='8/8/8/2k1K3/8/8/8/8 w - - 0 1')
        self.pgn._play_move('K', '', '', 'e6', None)
        self.unchanged_after_valid_move()

    def test_play_move_08(self):
        self.pgn.set_position_fen(fen='8/8/4B3/8/4B3/8/8/k6K w - - 0 1')
        self.pgn._play_move('B', '', '', 'e4', None)
        self.changed_after_invalid_move()

    def test_play_move_09(self):
        # The first part of Be4d5
        self.pgn.set_position_fen(fen='8/8/4B3/8/2B1B3/8/8/k6K w - - 0 1')
        self.pgn._play_move('B', '', '', 'e4', None)
        self.assertEqual(self.pgn.tokens, [self.match])
        self.assertEqual(self.pgn.error_tokens, [])
        self.assertEqual(self.pgn._state, 6)
        self.assertEqual(self.pgn._move_error_state, 2)

    def test_play_move_10(self):
        # The second part of Be4d5, no pawn on d4
        self.pgn.set_position_fen(fen='8/8/4B3/8/2B1B3/8/8/k6K w - - 0 1')
        self.pgn._play_move('', '', '', 'd5', None)
        self.changed_after_invalid_move()

    def test_play_move_11(self):
        # The second part of Be4d5, pawn on d4
        self.pgn.set_position_fen(fen='8/8/4B3/8/2BPB3/8/8/k6K w - - 0 1')
        self.pgn._play_move('', '', '', 'd5', None)
        self.unchanged_after_valid_move()

    def test_play_move_12(self):
        self.pgn.set_position_fen(fen='8/3k4/3P4/3K4/8/8/8/8 w - - 0 1')
        self.pgn._play_move('', '', '', 'd7', None)
        self.changed_after_invalid_move()

    def test_play_move_13(self):
        self.pgn.set_position_fen(fen='8/3k4/3P4/3K4/8/8/8/8 w - - 0 1')
        self.pgn._play_move('K', '', '', 'd6', None)
        self.changed_after_invalid_move()

    def test_play_move_14(self):
        self.pgn.set_position_fen(fen='8/3k4/3P4/3K4/8/8/8/8 w - - 0 1')
        self.pgn._play_move('K', '', '', 'd4', None)
        self.unchanged_after_valid_move()

    def test_play_move_15(self):
        self.pgn.set_position_fen(fen='3k4/8/8/8/8/8/8/R3K3 w Q - 0 60')
        self.assertRaisesRegex(
            KeyError,
            "None",
            self.pgn._play_move,
            *(None, None, None, None, None))
        self.unchanged_after_valid_move()

    def test_play_move_16(self):
        self.pgn.set_position_fen(fen='8/8/3k1p2/8/3pP3/8/3K4/8 b - e3 0 60')
        self.pgn._play_move('K', '', 'x', 'c5', None)
        self.changed_after_invalid_move()


class Pgn__play_castles(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGN()
        p = self.pgn
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME

        # A re.match object, rather than None, in the real case.
        self.match = parser.re_tokens.match('e4')
        p.tokens.append(self.match)

    def tearDown(self):
        del self.pgn

    def unchanged_after_valid_move(self):
        p = self.pgn
        self.assertEqual(p.tokens, [self.match])
        self.assertEqual(p.error_tokens, [])
        self.assertEqual(p._state, 4)
        self.assertEqual(p._move_error_state, 2)

    def changed_after_invalid_move(self):
        p = self.pgn
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, ['e4'])
        self.assertEqual(p._state, 2)
        self.assertEqual(p._move_error_state, 2)

    def test_play_castles_00(self):
        self.unchanged_after_valid_move()

    def test_play_castles_01(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w Kkq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'Kkq')

    def test_play_castles_02(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R b KQk - 0 1')
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQk')

    def test_play_castles_03(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R x KQkq - 0 1')
        self.assertRaisesRegex(
            TypeError,
            "argument of type 'NoneType' is not iterable",
            self.pgn._play_castles,
            *('O-O',))
        self.assertEqual(self.pgn.tokens, [self.match])
        self.assertEqual(self.pgn.error_tokens, [])
        self.assertEqual(self.pgn._state, 2)
        self.assertEqual(self.pgn._move_error_state, 2)

    def test_play_castles_04(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        self.pgn.active_side = 2
        self.assertRaisesRegex(
            IndexError,
            "list index out of range",
            self.pgn._play_castles,
            *('O-O-O',))
        self.unchanged_after_valid_move()

    def test_play_castles_05(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w Qkq - 0 1')
        self.pgn._play_castles('O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'Qkq')

    def test_play_castles_06(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R b KQq - 0 1')
        self.pgn._play_castles('O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQq')

    def test_play_castles_07(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R x KQkq - 0 1')
        self.assertRaisesRegex(
            TypeError,
            "argument of type 'NoneType' is not iterable",
            self.pgn._play_castles,
            *('O-O',))
        self.assertEqual(self.pgn.tokens, [self.match])
        self.assertEqual(self.pgn.error_tokens, [])
        self.assertEqual(self.pgn._state, 2)
        self.assertEqual(self.pgn._move_error_state, 2)

    def test_play_castles_08(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        self.pgn.active_side = 2
        self.assertRaisesRegex(
            IndexError,
            "list index out of range",
            self.pgn._play_castles,
            *('O-O',))
        self.unchanged_after_valid_move()

    def test_play_castles_09(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        self.pgn._play_castles('Kf1')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_10(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        self.pgn.board[56] = 6
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_11(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        #self.pgn.active_side_king = 5
        self.pgn._play_castles('O-O-O')

    def test_play_castles_12(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        self.pgn.board[60] = 5
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_13(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn.board[0] = 6
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_14(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
        #self.pgn.active_side_king = 52
        self.pgn._play_castles('O-O-O')

    def test_play_castles_15(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn.board[4] = 8
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_16(self):
        self.pgn.set_position_fen(fen='rn2k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_17(self):
        self.pgn.set_position_fen(fen='r3k2r/5P2/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_18(self):
        self.pgn.set_position_fen(fen='r3k2r/2P5/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_19(self):
        self.pgn.set_position_fen(fen='r3k1nr/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn._play_castles('O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_20(self):
        self.pgn.set_position_fen(fen='rn2k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_21(self):
        self.pgn.set_position_fen(fen='rn1qk2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.changed_after_invalid_move()
        self.assertEqual(self.pgn.castling, 'KQkq')

    def test_play_castles_22(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.unchanged_after_valid_move()
        self.assertEqual(self.pgn.castling, 'kq')

        # Added to fit parser_test.RealGamesPGN.test_01
        #self.assertEqual(nf.inactive_side_king, 58)
        #self.assertEqual(nf.active_side_king, 4)

    def test_play_castles_23(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.unchanged_after_valid_move()
        self.assertEqual(self.pgn.castling, 'KQ')

        # Added to fit parser_test.RealGamesPGN.test_01
        #self.assertEqual(nf.inactive_side_king, 2)
        #self.assertEqual(nf.active_side_king, 60)

    def test_play_castles_24(self):
        self.pgn.set_position_fen(fen='r3k2r/8/8/8/8/8/8/R3K2R b kq - 0 1')
        self.pgn._play_castles('O-O-O')
        self.unchanged_after_valid_move()
        self.assertEqual(self.pgn.castling, '-')

        # Added to fit parser_test.RealGamesPGN.test_01
        #self.assertEqual(nf.inactive_side_king, 2)
        #self.assertEqual(nf.active_side_king, 60)

    def test_play_castles_25(self):
        self.pgn.set_position_fen(fen='4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1')
        self.pgn._play_castles('O-O')
        self.unchanged_after_valid_move()
        self.assertEqual(self.pgn.castling, '-')
        for e, s in enumerate(self.pgn.board):
            if e == 60:
                self.assertEqual(s, '')
            elif e == 61:
                self.assertEqual(s, 'R')
            elif e == 62:
                self.assertEqual(s, 'K')
            elif e == 63:
                self.assertEqual(s, '')
            else:
                self.assertEqual(s, self.pgn.board[e])

        # Added to fit parser_test.RealGamesPGN.test_01
        #self.assertEqual(nf.inactive_side_king, 62)
        #self.assertEqual(nf.active_side_king, 4)


class PgnDisplayMoves___init__(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNDisplayMoves()

    def tearDown(self):
        del self.pgn

    def test___init___PGNDisplayMoves(self):
        p = self.pgn
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])
        self.assertEqual(p.collected_game, None)
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.board_bitmap, None)
        self.assertEqual(p.occupied_squares, [])
        self.assertEqual(p.board, [])
        self.assertEqual(p.piece_locations, {})
        self.assertEqual(p.fullmove_number, None)
        self.assertEqual(p.halfmove_count, None)
        self.assertEqual(p.en_passant, None)
        self.assertEqual(p.castling, None)
        self.assertEqual(p.active_side, None)
        self.assertEqual(p.ravstack, [])
        self.assertEqual(p._state, None)
        self.assertEqual(p._move_error_state, None)
        self.assertEqual(p._rewind_state, None)
        self.assertEqual(p.moves, [])
        self.assertEqual(len(p.__dict__), 20)
        self.assertEqual(set(p.__dict__), {'tokens',
                                           'error_tokens',
                                           'collected_game',
                                           'tags_in_order',
                                           'board_bitmap',
                                           'occupied_squares',
                                           'board',
                                           'piece_locations',
                                           'fullmove_number',
                                           'halfmove_count',
                                           'en_passant',
                                           'castling',
                                           'active_side',
                                           'ravstack',
                                           '_initial_fen',
                                           '_state',
                                           '_move_error_state',
                                           '_rewind_state',
                                           '_despatch_table',
                                           'moves',
                                           })
        self.assertEqual(
            p._despatch_table,
            [p._searching,
             p._searching_after_error_in_rav,
             p._searching_after_error_in_game,
             p._collecting_tag_pairs,
             p._collecting_movetext,
             p._collecting_non_whitespace_while_searching,
             p._disambiguate_move,
             ])


class PgnDisplayMoves_set_position_fen(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNDisplayMoves()
        self.pgn_base = parser.PGNDisplayMoves()

    def tearDown(self):
        del self.pgn
        del self.pgn_base

    def test_set_position_fen_01(self):
        p = self.pgn
        pend = self.pgn_base
        p.set_position_fen()
        self.assertEqual(p._state, None)
        self.assertEqual(len(p.__dict__), len(pend.__dict__))

    def test_set_position_fen_02(self):
        self.assertRaisesRegex(
            AttributeError,
            "'bool' object has no attribute 'split'",
            self.pgn.set_position_fen,
            *(True,))

    def test_set_position_fen_04(self):
        p = self.pgn
        pend = self.pgn_base
        p.set_position_fen(fen='8/8/7K/k7/8/8/8/8 w - - 5 60')
        self.assertEqual(p._state, None)
        self.assertEqual(len(p.__dict__), len(pend.__dict__))
        self.assertEqual(p.ravstack, [(None,
                                       (('', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', 'K',
                                         'k', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', '',
                                         '', '', '', '', '', '', '', ''),
                                        0, '-', '-'))])
        self.assertEqual(p._initial_fen, '8/8/7K/k7/8/8/8/8 w - - 5 60')

    def test_default_fen(self):
        p = self.pgn
        p.set_position_fen()
        self.assertEqual(p._state, None)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.collected_game, None)
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.board_bitmap, 18446462598732906495)
        self.assertEqual(p.board_bitmap,
                         (sum([1<<i for i in range(16)]) +
                          sum([1<<i for i in range(48, 64)])))
        self.assertEqual(p.occupied_squares,
                         [{48, 49, 50, 51, 52, 53, 54, 55,
                           56, 57, 58, 59, 60, 61, 62, 63},
                          {0, 1, 2, 3, 4, 5, 6, 7,
                           8, 9, 10, 11, 12, 13, 14, 15}])
        self.assertEqual(p.board,
                         ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                          'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                          'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'])
        self.assertEqual(p.piece_locations,
                         {'P':{48, 49, 50, 51, 52, 53, 54, 55},
                          'p':{8, 9, 10, 11, 12, 13, 14, 15},
                          'K':{60},
                          'k':{4},
                          'Q':{59},
                          'R':{56, 63},
                          'B':{58, 61},
                          'N':{57, 62},
                          'q':{3},
                          'r':{0, 7},
                          'b':{2, 5},
                          'n':{1, 6}})
        self.assertEqual(p.fullmove_number, 1)
        self.assertEqual(p.halfmove_count, 0)
        self.assertEqual(p.en_passant, '-')
        self.assertEqual(p.castling, 'KQkq')
        self.assertEqual(p.active_side, 0)
        self.assertEqual(p.ravstack,
                         [(None,
                           (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                             'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                             'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                            0,
                            'KQkq',
                            '-'))])
        self.assertEqual(p._state, None)
        self.assertEqual(p._initial_fen, True)
        self.assertEqual(p.moves, [(None,
                                    (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                                      'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                                      'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                                     0,
                                     'KQkq',
                                     '-'))])

    def test_initial_fen(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._state, None)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.collected_game, None)
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.board_bitmap, 18446462598732906495)
        self.assertEqual(p.occupied_squares,
                         [{48, 49, 50, 51, 52, 53, 54, 55,
                           56, 57, 58, 59, 60, 61, 62, 63},
                          {0, 1, 2, 3, 4, 5, 6, 7,
                           8, 9, 10, 11, 12, 13, 14, 15}])
        self.assertEqual(p.board,
                         ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                          'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          '', '', '', '', '', '', '', '',
                          'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                          'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'])
        self.assertEqual(p.piece_locations,
                         {'P':{48, 49, 50, 51, 52, 53, 54, 55},
                          'p':{8, 9, 10, 11, 12, 13, 14, 15},
                          'K':{60},
                          'k':{4},
                          'Q':{59},
                          'R':{56, 63},
                          'B':{58, 61},
                          'N':{57, 62},
                          'q':{3},
                          'r':{0, 7},
                          'b':{2, 5},
                          'n':{1, 6}})
        self.assertEqual(p.fullmove_number, 1)
        self.assertEqual(p.halfmove_count, 0)
        self.assertEqual(p.en_passant, '-')
        self.assertEqual(p.castling, 'KQkq')
        self.assertEqual(p.active_side, 0)
        self.assertEqual(p.ravstack,
                         [(None,
                           (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                             'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             '', '', '', '', '', '', '', '',
                             'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                             'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                            0,
                            'KQkq',
                            '-'))])
        self.assertEqual(p._state, None)
        self.assertEqual(
            p._initial_fen,
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p.moves, [(None,
                                    (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                                      'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                                      'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                                     0,
                                     'KQkq',
                                     '-'))])

    def test_initial_fen_errors_01(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 a')
        self.assertEqual(p._state, 2)
        self.assertEqual(p._initial_fen, None)
        self.assertEqual(p.moves, [])


class PgnDisplayMoves_add_move_to_game(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNDisplayMoves()
        self.pgn_base = parser.PGNDisplayMoves()

    def tearDown(self):
        del self.pgn
        del self.pgn_base

    def test__add_move_to_game_01(self):
        if sys.version_info[:2] < (3,5):
            msg = "tuple indices must be integers, not NoneType"
        else:
            msg = "tuple indices must be integers or slices, not NoneType"
        p = self.pgn
        pend = self.pgn_base
        self.assertRaisesRegex(
            TypeError,
            msg,
            p.add_move_to_game)

    def test__add_move_to_game_02(self):
        p = self.pgn
        pend = self.pgn_base
        p.set_position_fen()
        self.assertEqual(p._state, None)
        self.assertEqual(len(p.moves), 1)
        p.tokens.append(None)
        p.add_move_to_game()
        self.assertEqual(len(p.__dict__), len(pend.__dict__))
        self.assertEqual(len(p.ravstack), 1)
        self.assertEqual(p.ravstack[-1],
                         ((('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                           0,
                            'KQkq',
                            '-'),
                          (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                            'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '', '',
                            'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                            'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                           1,
                           'KQkq',
                           '-')))
        self.assertEqual(p._state, None)
        self.assertEqual(len(p.moves), 2)
        self.assertEqual(len(p.tokens), 1)

        self.assertEqual(p.moves, [(None,
                                    (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                                      'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                                      'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                                     0,
                                     'KQkq',
                                     '-')),
                                   (None,
                                    (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                                      'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      '', '', '', '', '', '', '', '',
                                      'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                                      'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                                     1,
                                     'KQkq',
                                     '-'))])


class PgnDisplayMoves_collect_token(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNDisplayMoves()

    def tearDown(self):
        del self.pgn

    def test_collect_token_01(self):
        p = self.pgn
        p.ravstack = [(True, False)]
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.moves, [])
        p.collect_token(None)
        self.assertEqual(p.tokens, [None])
        self.assertEqual(p.moves, [(None, False)])


class PgnDisplayMoves_collect_game_tokens(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNDisplayMoves()

    def tearDown(self):
        del self.pgn

    def test_collect_game_tokens_01(self):
        p = self.pgn
        self.assertEqual(p.collected_game, None)
        p.collect_game_tokens()
        self.assertEqual(p.collected_game, ([], {}, [], [], []))

    def test_collect_game_tokens_02(self):
        p = self.pgn
        next(p.get_games(test_scores))
        self.assertEqual(len(p.collected_game), 5)
        self.assertEqual(len(p.collected_game[0]), 14)
        self.assertEqual(len(p.collected_game[1]), 14)
        self.assertEqual(set([t.group(2) for t in p.collected_game[0]]),
                         set(p.collected_game[1]))
        self.assertEqual(p.collected_game[1],
                         {'Event': '4NCL',
                          'Site': 'Barcelo Hotel, Hinckley Island',
                          'Date': '2011.04.30',
                          'Round': '9.36',
                          'White': 'Burnell, Stephen',
                          'Black': 'Johnson, Michael J',
                          'Result': '1/2-1/2',
                          'ECO': 'C91',
                          'WhiteElo': '1922',
                          'BlackElo': '1802',
                          'PlyCount': '76',
                          'EventDate': '2011.04.30',
                          'WhiteTeam': 'Braille Chess Association',
                          'BlackTeam': 'Guildford A&DC 3',
                          })
        self.assertEqual(len(p.collected_game[2]), 77)
        self.assertEqual([t.group() for t in p.collected_game[2][:5]],
                         ['d4', 'Nf6', 'c4', 'g6', 'Nc3'])
        self.assertEqual([t.group() for t in p.collected_game[2][-5:]],
                         ['Rd1', 'Rxd1', 'Nxd1', 'Rd8', '1/2-1/2'])
        self.assertEqual(len(p.collected_game[3]), 0)
        self.assertEqual(len(p.collected_game[4]), 78)
        psm_count = 0
        for r in p.moves:
            psm_count += len([b for b in r[-1][0] if b != ''])
        self.assertEqual(psm_count, 1902)


class PgnDisplay__add_token_to_text(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNDisplay()
        p = self.pgn
        self.text = []
        self.token = 'ddddd'

    def tearDown(self):
        del self.pgn

    def test__add_token_to_text_01(self):
        p = self.pgn
        self.assertEqual(p._add_token_to_text(self.token, self.text, 0), 5)
        self.assertEqual(self.text, ['ddddd'])

    def test__add_token_to_text_02(self):
        p = self.pgn
        self.assertEqual(p._add_token_to_text(self.token*16, self.text, 0), 80)
        self.assertEqual(self.text, ['ddddd'*16])

    def test__add_token_to_text_03(self):
        p = self.pgn
        self.assertEqual(p._add_token_to_text(self.token*16, self.text, 1), 80)
        self.assertEqual(self.text, ['\n', 'ddddd'*16])

    def test__add_token_to_text_03(self):
        p = self.pgn
        self.assertEqual(p._add_token_to_text(self.token*15, self.text, 1), 77)
        self.assertEqual(self.text, [' ', 'ddddd'*15])


class PgnDisplay_get_export_pgn_movetext(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_export_two)
        self.pgn = parser.PGNDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_export_pgn_movetext_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_export_pgn_movetext(),
            ''.join(
                ('\n1. Nf3 d5 2. c4 c6 3. g3 Nf6 4. Bg2 e6 5. O-O ( 5. Nc3 ',
                 'Be7 ;An eol comment\n) 5... Nbd7 6. d4 Bd6 7. b3 O-O ',
                 '8. Bb2 Re8 9. Ne5 Bc7 10. Nd2 Nxe5 11. dxe5 Nd7\n12. f4 ',
                 'f6 13. e4 fxe5 {A comment} 14. exd5 exd5 15. cxd5 cxd5 ',
                 '16. Bxd5+ $10\n16... Kh8 17. Ne4 exf4 18. Qh5 Nf8 19. ',
                 'Qf7 Ne6 20. Bxe6 Re7 21. Bxg7# 1-0\n\n')))


class PgnDisplay_get_archive_movetext(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_export_two)
        self.pgn = parser.PGNDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_archive_movetext_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_archive_movetext(),
            ''.join(
                ('\n1. Nf3 d5 2. c4 c6 3. g3 Nf6 4. Bg2 e6 5. O-O ',
                 'Nbd7 6. d4 Bd6 7. b3 O-O ',
                 '8. Bb2\nRe8 9. Ne5 Bc7 10. Nd2 Nxe5 11. dxe5 Nd7 12. f4 ',
                 'f6 13. e4 fxe5 14. exd5 exd5\n15. cxd5 cxd5 ',
                 '16. Bxd5+ Kh8 17. Ne4 exf4 18. Qh5 Nf8 19. ',
                 'Qf7 Ne6 20. Bxe6 Re7\n21. Bxg7# 1-0\n\n')))


class PgnDisplay_get_export_pgn_rav_movetext(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_export_two)
        self.pgn = parser.PGNDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_export_pgn_rav_movetext_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_export_pgn_rav_movetext(),
            ''.join(
                ('\n1. Nf3 d5 2. c4 c6 3. g3 Nf6 4. Bg2 e6 5. O-O ( 5. Nc3 ',
                 'Be7 ) 5... Nbd7 6. d4\nBd6 7. b3 O-O ',
                 '8. Bb2 Re8 9. Ne5 Bc7 10. Nd2 Nxe5 11. dxe5 Nd7 12. f4 ',
                 'f6 13. e4\nfxe5 14. exd5 exd5 15. cxd5 cxd5 ',
                 '16. Bxd5+ Kh8 17. Ne4 exf4 18. Qh5 Nf8 19. ',
                 'Qf7\nNe6 20. Bxe6 Re7 21. Bxg7# 1-0\n\n')))


class PgnDisplay_get_non_seven_tag_roster_tags(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_export_two)
        self.pgn = parser.PGNDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_non_seven_tag_roster_tags_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_non_seven_tag_roster_tags(),
            '\n'.join(('[BlackElo "1685"]',
                       '[BlackTeam "Braille Chess Association"]',
                       '[ECO "D27"]',
                       '[EventDate "2011.04.30"]',
                       '[PlyCount "41"]',
                       '[WhiteElo "1736"]',
                       )))


class PgnDisplay_get_seven_tag_roster_tags(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_export_two)
        self.pgn = parser.PGNDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_seven_tag_roster_tags_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_seven_tag_roster_tags(),
            ['"2011.04.30"',
             ''.join(('[Event "4NCL"]\n',
                      '[Site "Barcelo Hotel, Hinckley Island"]\n',
                      '[Date "2011.04.30"]\n',
                      )),
             3,
             ''.join(('[Round "9.36"]\n',
                      '[White "Yiamakis, Albert"]\n',
                      '[Black "Murphy, Richard LW"]\n',
                      '[Result "1-0"]\n',
                      )),
             ])


class PgnDisplay_get_export_pgn_elements(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_export_two)
        self.pgn = parser.PGNDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_export_pgn_elements_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_export_pgn_elements(),
            (['"2011.04.30"',
              ''.join(('[Event "4NCL"]\n',
                       '[Site "Barcelo Hotel, Hinckley Island"]\n',
                       '[Date "2011.04.30"]\n',
                       )),
              3,
              ''.join(('[Round "9.36"]\n',
                       '[White "Yiamakis, Albert"]\n',
                       '[Black "Murphy, Richard LW"]\n',
                       '[Result "1-0"]\n',
                       )),
              ],
             ''.join(
                 ('\n1. Nf3 d5 2. c4 c6 3. g3 Nf6 4. Bg2 e6 5. O-O ( 5. Nc3 ',
                  'Be7 ;An eol comment\n) 5... Nbd7 6. d4 Bd6 7. b3 O-O ',
                  '8. Bb2 Re8 9. Ne5 Bc7 10. Nd2 Nxe5 11. dxe5 Nd7\n12. f4 ',
                  'f6 13. e4 fxe5 {A comment} 14. exd5 exd5 15. cxd5 cxd5 ',
                  '16. Bxd5+ $10\n16... Kh8 17. Ne4 exf4 18. Qh5 Nf8 19. ',
                  'Qf7 Ne6 20. Bxe6 Re7 21. Bxg7# 1-0\n\n')),
             '\n'.join(('[BlackElo "1685"]',
                        '[BlackTeam "Braille Chess Association"]',
                        '[ECO "D27"]',
                        '[EventDate "2011.04.30"]',
                        '[PlyCount "41"]',
                        '[WhiteElo "1736"]',
                        )),
             ))


class PgnDisplay_get_archive_pgn_elements(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_export_two)
        self.pgn = parser.PGNDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_archive_pgn_elements_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_archive_pgn_elements(),
            (['"2011.04.30"',
              ''.join(('[Event "4NCL"]\n',
                       '[Site "Barcelo Hotel, Hinckley Island"]\n',
                       '[Date "2011.04.30"]\n',
                       )),
              3,
              ''.join(('[Round "9.36"]\n',
                       '[White "Yiamakis, Albert"]\n',
                       '[Black "Murphy, Richard LW"]\n',
                       '[Result "1-0"]\n',
                       )),
              ],
             ''.join(
                 ('\n1. Nf3 d5 2. c4 c6 3. g3 Nf6 4. Bg2 e6 5. O-O ',
                  'Nbd7 6. d4 Bd6 7. b3 O-O ',
                  '8. Bb2\nRe8 9. Ne5 Bc7 10. Nd2 Nxe5 11. dxe5 Nd7 12. f4 ',
                  'f6 13. e4 fxe5 14. exd5 exd5\n15. cxd5 cxd5 ',
                  '16. Bxd5+ Kh8 17. Ne4 exf4 18. Qh5 Nf8 19. ',
                  'Qf7 Ne6 20. Bxe6 Re7\n21. Bxg7# 1-0\n\n')),
             ))


class PgnDisplay_get_export_pgn_rav_elements(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_export_two)
        self.pgn = parser.PGNDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_export_pgn_rav_elements_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_export_pgn_rav_elements(),
            (['"2011.04.30"',
              ''.join(('[Event "4NCL"]\n',
                       '[Site "Barcelo Hotel, Hinckley Island"]\n',
                       '[Date "2011.04.30"]\n',
                       )),
              3,
              ''.join(('[Round "9.36"]\n',
                       '[White "Yiamakis, Albert"]\n',
                       '[Black "Murphy, Richard LW"]\n',
                       '[Result "1-0"]\n',
                       )),
              ],
             ''.join(
                 ('\n1. Nf3 d5 2. c4 c6 3. g3 Nf6 4. Bg2 e6 5. O-O ( 5. Nc3 ',
                  'Be7 ) 5... Nbd7 6. d4\nBd6 7. b3 O-O ',
                  '8. Bb2 Re8 9. Ne5 Bc7 10. Nd2 Nxe5 11. dxe5 Nd7 12. f4 ',
                  'f6 13. e4\nfxe5 14. exd5 exd5 15. cxd5 cxd5 ',
                  '16. Bxd5+ Kh8 17. Ne4 exf4 18. Qh5 Nf8 19. ',
                  'Qf7\nNe6 20. Bxe6 Re7 21. Bxg7# 1-0\n\n')),
             '\n'.join(('[BlackElo "1685"]',
                        '[BlackTeam "Braille Chess Association"]',
                        '[ECO "D27"]',
                        '[EventDate "2011.04.30"]',
                        '[PlyCount "41"]',
                        '[WhiteElo "1736"]',
                        )),
             ))


class PgnEdit__convert_error_tokens_to_comment(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNEdit()
        self.pgn.ravstack = [(True, False)]

    def tearDown(self):
        del self.pgn

    def test__convert_error_tokens_to_comment_01(self):
        p = self.pgn
        p.error_tokens.extend(['a', 'b']) 
        self.assertEqual(p.tokens, [])
        p._convert_error_tokens_to_token()
        self.assertEqual(len(p.tokens), 1)
        self.assertEqual(p.tokens[-1].group(), 'ab')
        self.assertEqual(p.error_tokens, [])

    def test__convert_error_tokens_to_comment_02(self):
        p = self.pgn
        p.error_tokens.extend(['a', 'b']) 
        p.tokens.append(None)
        self.assertEqual(p.tokens, [None])
        p._convert_error_tokens_to_token()
        self.assertEqual(len(p.tokens), 2)
        self.assertEqual(p.tokens[-1].group(), 'ab')
        self.assertEqual(p.error_tokens, [])

    def test__convert_error_tokens_to_comment_03(self):
        p = self.pgn
        p.error_tokens.extend(['a', 'w']) 
        self.assertEqual(p.tokens, [])
        p._convert_error_tokens_to_token()
        self.assertEqual(len(p.tokens), 1)
        self.assertEqual(p.tokens[-1].group(), '{Error: aw}')
        self.assertEqual(p.error_tokens, ['a', 'w'])

    def test__convert_error_tokens_to_comment_04(self):
        p = self.pgn
        p.error_tokens.extend(['a', 'w']) 
        p.tokens.append(None)
        self.assertEqual(p.tokens, [None])
        p._convert_error_tokens_to_token()
        self.assertEqual(len(p.tokens), 2)
        self.assertEqual(p.tokens[-1].group(), '{Error: aw}')
        self.assertEqual(p.error_tokens, ['a', 'w'])


class PgnMove___init__(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNMove()
        self.pgn_base = parser.PGN()

    def tearDown(self):
        del self.pgn
        del self.pgn_base

    def test___init__01(self):
        p = self.pgn
        self.assertEqual(len(p.__dict__), len(self.pgn_base.__dict__) + 1)
        self.assertEqual(len(p.__dict__), 20)
        self.assertEqual(p._initial_position, None)


class PgnMove_is_movetext_valid(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNMove()

    def tearDown(self):
        del self.pgn

    def test_is_movetext_valid_01(self):
        p = self.pgn
        p.collected_game = (None, None, (True,), False)
        self.assertEqual(p.is_movetext_valid(), True)

    def test_is_movetext_valid_02(self):
        p = self.pgn
        p.collected_game = (None, None, (True,), True)
        self.assertEqual(p.is_movetext_valid(), True)

    def test_is_movetext_valid_03(self):
        p = self.pgn
        p.collected_game = (None, None, (True, True), False)
        self.assertEqual(p.is_movetext_valid(), False)


class PgnMove_set_position_fen(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNMove()

    def tearDown(self):
        del self.pgn

    def test_set_position_fen_01(self):
        p = self.pgn
        p.set_position_fen(fen='')
        self.assertEqual(p._initial_position, None)

    def test_set_position_fen_02(self):
        p = self.pgn
        p.set_position_fen()
        self.assertEqual(p._initial_position,
                         (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                           'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                           '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '',
                           'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                           'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                          0,
                          'KQkq',
                          '-'))

    def test_set_position_fen_03(self):
        p = self.pgn
        p.set_position_fen(
            fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(p._initial_position,
                         (('r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
                           'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
                           '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '',
                           'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                           'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'),
                          0,
                          'KQkq',
                          '-'))


class PgnRepertoireDisplay_is_tag_roster_valid(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNRepertoireDisplay()

    def tearDown(self):
        del self.pgn

    def test_is_tag_roster_valid_01(self):
        p = self.pgn
        p.collected_game = (p.tags_in_order, {}, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_02(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = []
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_03(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_04(self):
        p = self.pgn
        tags = {'a':'text'}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_05(self):
        p = self.pgn
        tags = {'Opening':'t'}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), True)

test_rav_one = ''.join((
    '[Date "2011.04.30"]',
    '[Round "9.36"]',
    '[Result "*"]',
    '[ECO "C91"]',
    '[Opening "Queen Pawn"]',
    '[PlyCount "76"]',
    '[EventDate "2011.04.30"]',
    'd4Nf6c4g6Nc3(Nf3Bg7g3)(g3)Bg7e4d6Be2O-OBg5c5d5h6Be3e6',
    'dxe6{Backward QP}Bxe6Qd2Kh7$11O-O-OQa5*',
    ))

class PgnRepertoireDisplay_get_export_repertoire_text(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_rav_one)
        self.pgn = parser.PGNRepertoireDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_export_repertoire_text_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_export_repertoire_text(),
            ''.join(['[Opening "Queen Pawn"]\n',
                     '[Result "*"]\n',
                     '[Date "2011.04.30"]\n',
                     '[ECO "C91"]\n',
                     '[EventDate "2011.04.30"]\n',
                     '[PlyCount "76"]\n',
                     '[Round "9.36"]\n',
                     '\n1. d4 Nf6 2. c4 g6 3. Nc3 ( 3. Nf3 Bg7 4. g3 ) ( 3. ',
                     'g3 ) 3... Bg7 4. e4 d6 5.\nBe2 O-O 6. Bg5 c5 7. d5 h6 ',
                     '8. Be3 e6 9. dxe6 {Backward QP} 9... Bxe6 10. Qd2\nKh7 ',
                     '$11 11. O-O-O Qa5 *\n\n',
                     ]))


class PgnRepertoireDisplay_get_export_repertoire_rav_text(unittest.TestCase):

    def setUp(self):
        self.test_scores = io.StringIO(test_rav_one)
        self.pgn = parser.PGNRepertoireDisplay()
        self.pgn.read_first_game(self.test_scores)

    def tearDown(self):
        del self.pgn

    def test_get_export_repertoire_rav_text_01(self):
        p = self.pgn
        self.assertEqual(
            p.get_export_repertoire_rav_text(),
            ''.join(['[Opening "Queen Pawn"]\n',
                     '[Result "*"]\n',
                     '[Date "2011.04.30"]\n',
                     '[ECO "C91"]\n',
                     '[EventDate "2011.04.30"]\n',
                     '[PlyCount "76"]\n',
                     '[Round "9.36"]\n',
                     '\n1. d4 Nf6 2. c4 g6 3. Nc3 ( 3. Nf3 Bg7 4. g3 ) ( 3. ',
                     'g3 ) 3... Bg7 4. e4 d6 5.\nBe2 O-O 6. Bg5 c5 7. d5 h6 ',
                     '8. Be3 e6 9. dxe6 Bxe6 10. Qd2 Kh7 11. O-O-O Qa5 *\n\n',
                     ]))


class PgnRepertoireUpdate_is_tag_roster_valid(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNRepertoireUpdate()

    def tearDown(self):
        del self.pgn

    def test_is_tag_roster_valid_01(self):
        p = self.pgn
        p.collected_game = (p.tags_in_order, {}, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_02(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = []
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_03(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_04(self):
        p = self.pgn
        tags = {'a':'text'}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_05(self):
        p = self.pgn
        tags = {'Opening':'t'}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), True)


class PgnTags__collecting_movetext(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNTags()
        p = self.pgn
        p.set_position_fen(test_position_one)
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME

    def tearDown(self):
        del self.pgn

    def test__collecting_movetext_01(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Qc2')
        match = parser.re_tokens.match('Qc2')
        self.assertEqual(match.group(), 'Qc2')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_02(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('h3')
        match = parser.re_tokens.match('h3')
        self.assertEqual(match.group(), 'h3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_03(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Bxf6')
        match = parser.re_tokens.match('Bxf6')
        self.assertEqual(match.group(), 'Bxf6')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_04(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('cxd5')
        match = parser.re_tokens.match('cxd5')
        self.assertEqual(match.group(), 'cxd5')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_05(self):
        p = self.pgn
        p.set_position_fen(test_position_two)
        #match = parser.re_tokens.fullmatch('Nge2')
        match = parser.re_tokens.match('Nge2')
        self.assertEqual(match.group(), 'Nge2')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_06(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('O-O')
        match = parser.re_tokens.match('O-O')
        self.assertEqual(match.group(), 'O-O')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_07(self):
        p = self.pgn
        p.set_position_fen(test_position_three)
        #match = parser.re_tokens.fullmatch('e8=Q#')
        match = parser.re_tokens.match('e8=Q#')
        self.assertEqual(match.group(), 'e8=Q#')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_08(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 '''
        p = parser.PGNTags()
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        self.assertEqual(len(p.ravstack), 1)
        match = parser.re_tokens.match('(')
        p._collecting_movetext(match)
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(p._state, 4)
        self.assertEqual(len(p.tokens), 0)
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_09(self):
        p = self.pgn
        match = parser.re_tokens.match(')')
        p._collecting_movetext(match)
        self.assertEqual(p.collected_game, None)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_10(self):
        p = self.pgn
        match = parser.re_tokens.match('0-1')
        p._collecting_movetext(match)
        self.assertEqual(len(p.collected_game), 4)
        self.assertEqual(p.collected_game[2], [])
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_11(self):
        p = self.pgn
        match = parser.re_tokens.match('{A comment}')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_12(self):
        p = self.pgn
        match = parser.re_tokens.match('$45')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_13(self):
        p = self.pgn
        match = parser.re_tokens.match(';Comment to EOL\n')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_14(self):
        p = self.pgn
        match = parser.re_tokens.match('   ')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_15(self):
        p = self.pgn
        match = parser.re_tokens.match(' \n   \n\r\t')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_16(self):
        p = self.pgn
        match = parser.re_tokens.match('1')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_17(self):
        p = self.pgn
        match = parser.re_tokens.match('.')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_18(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 '''
        p = parser.PGNTags()
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        self.assertEqual(len(p.ravstack), 1)
        match = parser.re_tokens.match('[Tag"value"]')
        p._collecting_movetext(match)
        self.assertEqual(len(p.ravstack), 1)
        self.assertEqual(p._state, 3)
        self.assertEqual(p._move_error_state, 2)
        self.assertEqual(p.tags_in_order, [match])
        self.assertEqual(p.tokens, [])

    def test__collecting_movetext_19(self):
        p = self.pgn
        match = parser.re_tokens.match('<Reserved>')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_20(self):
        p = self.pgn
        match = parser.re_tokens.match('O_O')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_21(self):
        p = self.pgn
        match = parser.re_tokens.match('any old string')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_movetext_22(self):
        p = self.pgn
        p.ravstack.insert(0, None)
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_RAV
        match = parser.re_tokens.match('any old string')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])


class PgnTags__collecting_tag_pairs(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNTags()
        p = self.pgn
        p.set_position_fen(test_position_one)
        p._state = constants.PGN_COLLECTING_TAG_PAIRS
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME

    def tearDown(self):
        del self.pgn

    def test__collecting_tag_pairs_01(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])

    def test__collecting_tag_pairs_02(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Qc2')
        match = parser.re_tokens.match('Qc2')
        self.assertEqual(match.group(), 'Qc2')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_tag_pairs_03(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('h3')
        match = parser.re_tokens.match('h3')
        self.assertEqual(match.group(), 'h3')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_tag_pairs_04(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Bxf6')
        match = parser.re_tokens.match('Bxf6')
        self.assertEqual(match.group(), 'Bxf6')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_tag_pairs_05(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('cxd5')
        match = parser.re_tokens.match('cxd5')
        self.assertEqual(match.group(), 'cxd5')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_tag_pairs_06(self):
        p = self.pgn
        p.set_position_fen(test_position_two)
        #match = parser.re_tokens.fullmatch('Nge2')
        match = parser.re_tokens.match('Nge2')
        self.assertEqual(match.group(), 'Nge2')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_tag_pairs_07(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('O-O')
        match = parser.re_tokens.match('O-O')
        self.assertEqual(match.group(), 'O-O')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_tag_pairs_08(self):
        p = self.pgn
        p.set_position_fen(test_position_three)
        #match = parser.re_tokens.fullmatch('e8=Q#')
        match = parser.re_tokens.match('e8=Q#')
        self.assertEqual(match.group(), 'e8=Q#')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__collecting_tag_pairs_09(self):
        p = self.pgn
        match = parser.re_tokens.match('0-1')
        p._collecting_tag_pairs(match)
        self.assertEqual(len(p.collected_game), 4)
        self.assertEqual(p.collected_game[2], [])
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_10(self):
        p = self.pgn
        match = parser.re_tokens.match('{A comment}')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_11(self):
        p = self.pgn
        match = parser.re_tokens.match('$45')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_12(self):
        p = self.pgn
        match = parser.re_tokens.match(';Comment to EOL\n')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_13(self):
        p = self.pgn
        match = parser.re_tokens.match('(')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_tag_pairs_14(self):
        p = self.pgn
        match = parser.re_tokens.match(')')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_tag_pairs_15(self):
        p = self.pgn
        match = parser.re_tokens.match('   ')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_16(self):
        p = self.pgn
        match = parser.re_tokens.match(' \n   \n\r\t')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_17(self):
        p = self.pgn
        match = parser.re_tokens.match('1')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_18(self):
        p = self.pgn
        match = parser.re_tokens.match('.')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_19(self):
        p = self.pgn
        match = parser.re_tokens.match('<Reserved>')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__collecting_tag_pairs_20(self):
        p = self.pgn
        match = parser.re_tokens.match('any old string')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__collecting_tag_pairs_21(self):
        p = self.pgn
        match = parser.re_tokens.match('O_O')
        p._collecting_tag_pairs(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])


class PgnTags__disambiguate_move(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNTags()
        p = self.pgn
        p._state = constants.PGN_COLLECTING_MOVETEXT
        p._move_error_state = constants.PGN_SEARCHING_AFTER_ERROR_IN_GAME
        p.set_position_fen(test_position_four)

    def tearDown(self):
        del self.pgn

    def test__disambiguate_move_01(self):
        p = self.pgn
        match = parser.re_tokens.match('Rh3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        p._state = constants.PGN_DISAMBIGUATE_MOVE
        matcha = parser.re_tokens.match('e4')
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])
        p._disambiguate_move(matcha)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])

    def test__disambiguate_move_02(self):
        p = self.pgn
        match = parser.re_tokens.match('Nc3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        matcha = parser.re_tokens.match('e4')
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])
        p._disambiguate_move(matcha)
        self.assertEqual(p._state, 4)
        self.assertEqual(len(p.tokens), 0)
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])

    def test__disambiguate_move_03(self):
        p = self.pgn
        match = parser.re_tokens.match('Nc3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        matcha = parser.re_tokens.match('Rh3')
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])
        p._disambiguate_move(matcha)
        self.assertEqual(p._state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])

    def test__disambiguate_move_04(self):
        p = self.pgn
        match = parser.re_tokens.match('Nc3')
        p._collecting_movetext(match)
        self.assertEqual(p._state, 4)
        p.ravstack.insert(0, None)
        matcha = parser.re_tokens.match('Rh3')
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])
        p._disambiguate_move(matcha)
        self.assertEqual(p._state, 1)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [])
        self.assertEqual(p.error_tokens, [])


class PgnTags__end_variation(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNTags()
        self.pgn.ravstack.append(True)

    def tearDown(self):
        del self.pgn

    def test__end_variation_01(self):
        p = self.pgn
        self.assertEqual(p.ravstack, [True])
        p._end_variation()
        self.assertEqual(p.ravstack, [])
        p._end_variation()
        self.assertEqual(p.ravstack, [])


class PgnTags__searching(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNTags()
        p = self.pgn
        p.set_position_fen(test_position_one)
        p._state = constants.PGN_SEARCHING
        p._move_error_state = (
            constants.PGN_COLLECTING_NON_WHITESPACE_WHILE_SEARCHING)

    def tearDown(self):
        del self.pgn

    def test__searching_01(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._searching(match)
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])

    def test__searching_02(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Qc2')
        match = parser.re_tokens.match('Qc2')
        self.assertEqual(match.group(), 'Qc2')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__searching_03(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('h3')
        match = parser.re_tokens.match('h3')
        self.assertEqual(match.group(), 'h3')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__searching_04(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('Bxf6')
        match = parser.re_tokens.match('Bxf6')
        self.assertEqual(match.group(), 'Bxf6')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__searching_05(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('cxd5')
        match = parser.re_tokens.match('cxd5')
        self.assertEqual(match.group(), 'cxd5')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__searching_06(self):
        p = self.pgn
        p.set_position_fen(test_position_two)
        #match = parser.re_tokens.fullmatch('Nge2')
        match = parser.re_tokens.match('Nge2')
        self.assertEqual(match.group(), 'Nge2')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__searching_07(self):
        p = self.pgn
        #match = parser.re_tokens.fullmatch('O-O')
        match = parser.re_tokens.match('O-O')
        self.assertEqual(match.group(), 'O-O')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__searching_08(self):
        p = self.pgn
        p.set_position_fen(test_position_three)
        #match = parser.re_tokens.fullmatch('e8=Q#')
        match = parser.re_tokens.match('e8=Q#')
        self.assertEqual(match.group(), 'e8=Q#')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])

    def test__searching_09(self):
        p = self.pgn
        match = parser.re_tokens.match('{A comment}')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_10(self):
        p = self.pgn
        match = parser.re_tokens.match('$45')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_11(self):
        p = self.pgn
        match = parser.re_tokens.match(';Comment to EOL\n')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_12(self):
        p = self.pgn
        match = parser.re_tokens.match('(')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_13(self):
        p = self.pgn
        match = parser.re_tokens.match(')')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_14(self):
        p = self.pgn
        match = parser.re_tokens.match('1-0')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_15(self):
        p = self.pgn
        match = parser.re_tokens.match('   ')
        p._searching(match)
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_16(self):
        p = self.pgn
        match = parser.re_tokens.match(' \n   \n\r\t')
        p._searching(match)
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_17(self):
        p = self.pgn
        match = parser.re_tokens.match('1')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_18(self):
        p = self.pgn
        match = parser.re_tokens.match('.')
        p._searching(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_19(self):
        p = self.pgn
        match = parser.re_tokens.match('<Reserved>')
        p._searching(match)
        self.assertEqual(p._state, 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])

    def test__searching_20(self):
        p = self.pgn
        match = parser.re_tokens.match('any old string')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])

    def test__searching_21(self):
        p = self.pgn
        match = parser.re_tokens.match('O_O')
        p._searching(match)
        self.assertEqual(p._state, 5)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [match.group()])


class PgnTags__searching_after_error_in_game(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNTags()

    def tearDown(self):
        del self.pgn

    def test__searching_after_error_in_game_01(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3u6'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match('1/2-1/2')
        p._searching_after_error_in_game(match)
        self.assertEqual(p.collected_game[2], [])
        self.assertEqual([t.group() for t in p.collected_game[0]],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(p._state, 0)

    def test__searching_after_error_in_game_02(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3u6'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._searching_after_error_in_game(match)
        self.assertEqual(p.collected_game[2], [])
        self.assertEqual([t.group() for t in p.collected_game[0]],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(p._state, 3)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])

    def test__searching_after_error_in_game_03(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3u6'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        #match = parser.re_tokens.fullmatch('dxe6')
        match = parser.re_tokens.match('dxe6')
        self.assertEqual(match.group(), 'dxe6')
        p._searching_after_error_in_game(match)
        self.assertEqual(p._state, 2)
        self.assertEqual(len(p.tokens), 0)
        self.assertEqual([t.group() for t in p.tags_in_order],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(p.error_tokens, [])


class PgnTags__searching_after_error_in_rav(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNTags()

    def tearDown(self):
        del self.pgn

    def test__searching_after_error_in_rav_01(self):
        p = self.pgn
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u'''
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match('(')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(len(p.tokens), 0)
        self.assertEqual(p.error_tokens, [])
        self.assertEqual([t.group() for t in p.tags_in_order],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(p._ravstack_length, 3)

    def test__searching_after_error_in_rav_02(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u(v'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        self.assertEqual(p._ravstack_length, 3)
        match = parser.re_tokens.match(')')
        self.assertEqual(p._move_error_state, 2)
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(p._move_error_state, 2)
        self.assertEqual(len(p.tokens), 0)
        self.assertEqual(p.error_tokens, [])
        self.assertEqual([t.group() for t in p.tags_in_order],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(hasattr(p, '_ravstack_length'), True)

    def test__searching_after_error_in_rav_03(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match(')')
        self.assertEqual(p._move_error_state, 2)
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 4)
        self.assertEqual(p._move_error_state, 2)
        self.assertEqual(len(p.tokens), 0)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.error_tokens, [])
        self.assertEqual([t.group() for t in p.tags_in_order],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(hasattr(p, '_ravstack_length'), False)

    def test__searching_after_error_in_rav_04(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u(Nbd7(Nxe4'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        self.assertEqual(p._ravstack_length, 4)
        match = parser.re_tokens.match(')')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(len(p.tokens), 0)
        self.assertEqual(p.error_tokens, [])
        self.assertEqual([t.group() for t in p.tags_in_order],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(len(p.ravstack), 2)
        self.assertEqual(p._ravstack_length, 3)

    def test__searching_after_error_in_rav_05(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u(Nbd7(Nxe4'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match('*')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p.collected_game[2], [])
        self.assertEqual([t.group() for t in p.collected_game[0]],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(p._state, 0)
        self.assertEqual(hasattr(p, '_ravstack_length'), False)

    def test__searching_after_error_in_rav_06(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u(Nbd7(Nxe4'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        #match = parser.re_tokens.fullmatch('[Tag"value"]')
        match = parser.re_tokens.match('[Tag"value"]')
        self.assertEqual(match.group(), '[Tag"value"]')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p.collected_game[2], [])
        self.assertEqual([t.group() for t in p.collected_game[0]],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(p._state, 3)
        self.assertEqual(p._move_error_state, 2)
        self.assertEqual(p.tokens, [])
        self.assertEqual(p.tags_in_order, [match])
        self.assertEqual(hasattr(p, '_ravstack_length'), False)

    def test__searching_after_error_in_rav_07(self):
        gamescore = '''[Event "4NCL"][Site "Barcelo Hotel, Hinckley Island"]
[Date "2011.04.30"][Round "9.36"][White "Burnell, Stephen"]
[Black "Johnson, Michael J"][Result "1/2-1/2"]d4Nf6c4g6Nc3Bg7e4d6Be2O-OBg5c5
d5h6Be3e6dxe6Bxe6 10. Qd2 (b3u'''
        p = self.pgn
        try:
            p.get_first_game(gamescore)
        except StopIteration:
            pass
        match = parser.re_tokens.match('   ')
        p._searching_after_error_in_rav(match)
        self.assertEqual(p._state, 1)
        self.assertEqual(len(p.tokens), 0)
        self.assertEqual([t.group() for t in p.tags_in_order],
                         ['[Event "4NCL"]',
                          '[Site "Barcelo Hotel, Hinckley Island"]',
                          '[Date "2011.04.30"]',
                          '[Round "9.36"]',
                          '[White "Burnell, Stephen"]',
                          '[Black "Johnson, Michael J"]',
                          '[Result "1/2-1/2"]',
                          ])
        self.assertEqual(p.error_tokens, [])


class PgnTags__start_variation(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNTags()

    def tearDown(self):
        del self.pgn

    def test__start_variation_01(self):
        p = self.pgn
        self.assertEqual(p.ravstack, [])
        p._start_variation()
        self.assertEqual(p.ravstack, [None])


class PgnRepertoireTags_is_tag_roster_valid(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNRepertoireTags()

    def tearDown(self):
        del self.pgn

    def test_is_tag_roster_valid_01(self):
        p = self.pgn
        p.collected_game = (p.tags_in_order, {}, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_02(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = []
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_03(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_04(self):
        p = self.pgn
        tags = {'a':'text'}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_05(self):
        p = self.pgn
        tags = {'Opening':'t'}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), True)


class PgnAnalysis_is_tag_roster_valid(unittest.TestCase):

    def setUp(self):
        self.pgn = parser.PGNAnalysis()

    def tearDown(self):
        del self.pgn

    def test_is_tag_roster_valid_01(self):
        p = self.pgn
        p.collected_game = (p.tags_in_order, {}, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), True)

    def test_is_tag_roster_valid_02(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = []
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_03(self):
        p = self.pgn
        tags = {'a':''}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), False)

    def test_is_tag_roster_valid_04(self):
        p = self.pgn
        tags = {'a':'text'}
        p.tags_in_order = [None]
        p.collected_game = (p.tags_in_order, tags, p.tokens, p.error_tokens)
        self.assertEqual(p.is_tag_roster_valid(), True)


def _check_nothing_done(case, p, pend):
    case.assertEqual(len(p.__dict__), len(pend.__dict__))
    for k, v in pend.__dict__.items():
        if k not in {'_despatch_table'}:
            case.assertEqual(p.__dict__[k], v)
        else:
            for ke, ve in zip(p.__dict__[k], v):
                case.assertEqual(ke.__name__, ve.__name__)


if __name__ == '__main__':
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(Pgn___init__))
    runner().run(loader(Pgn_reset_position))
    runner().run(loader(Pgn__start_variation))
    runner().run(loader(Pgn__end_variation))
    runner().run(loader(Pgn__illegal_play_move))
    runner().run(loader(Pgn__illegal_play_castles))
    runner().run(loader(Pgn__illegal_play_disambiguated_move))
    runner().run(loader(Pgn_set_position_fen))
    runner().run(loader(Pgn_add_move_to_game))
    runner().run(loader(Pgn_is_active_king_attacked))
    runner().run(loader(Pgn_is_square_attacked_by_side))
    runner().run(loader(Pgn_count_attacks_on_square_by_side))
    runner().run(loader(Pgn__play_move))
    runner().run(loader(Pgn__play_castles))
    runner().run(loader(Pgn__play_disambiguated_move))
    runner().run(loader(Pgn__convert_error_tokens_to_token))
    runner().run(loader(Pgn__searching))
    runner().run(loader(Pgn__searching_after_error_in_rav))
    runner().run(loader(Pgn__searching_after_error_in_game))
    runner().run(loader(Pgn__collecting_tag_pairs))
    runner().run(loader(Pgn__collecting_movetext))
    runner().run(loader(Pgn__collecting_non_whitespace_while_searching))
    runner().run(loader(Pgn__disambiguate_move))
    runner().run(loader(Pgn_read_games))
    runner().run(loader(Pgn_get_games))
    runner().run(loader(Pgn_read_first_game))
    runner().run(loader(Pgn_get_first_game))
    runner().run(loader(Pgn_collect_token))
    runner().run(loader(Pgn_collect_game_tokens))
    runner().run(loader(Pgn_is_tag_roster_valid))
    runner().run(loader(Pgn_is_movetext_valid))
    runner().run(loader(Pgn_is_pgn_valid))
    runner().run(loader(PgnDisplayMoves___init__))
    runner().run(loader(PgnDisplayMoves_set_position_fen))
    runner().run(loader(PgnDisplayMoves_add_move_to_game))
    runner().run(loader(PgnDisplayMoves_collect_token))
    runner().run(loader(PgnDisplayMoves_collect_game_tokens))
    runner().run(loader(PgnDisplay__add_token_to_text))
    runner().run(loader(PgnDisplay_get_export_pgn_movetext))
    runner().run(loader(PgnDisplay_get_archive_movetext))
    runner().run(loader(PgnDisplay_get_export_pgn_rav_movetext))
    runner().run(loader(PgnDisplay_get_non_seven_tag_roster_tags))
    runner().run(loader(PgnDisplay_get_seven_tag_roster_tags))
    runner().run(loader(PgnDisplay_get_export_pgn_elements))
    runner().run(loader(PgnDisplay_get_archive_pgn_elements))
    runner().run(loader(PgnDisplay_get_export_pgn_rav_elements))
    runner().run(loader(PgnEdit__convert_error_tokens_to_comment))
    runner().run(loader(PgnMove___init__))
    runner().run(loader(PgnMove_is_movetext_valid))
    runner().run(loader(PgnMove_set_position_fen))
    runner().run(loader(PgnRepertoireDisplay_is_tag_roster_valid))
    runner().run(loader(PgnRepertoireDisplay_get_export_repertoire_text))
    runner().run(loader(PgnRepertoireDisplay_get_export_repertoire_rav_text))
    runner().run(loader(PgnRepertoireUpdate_is_tag_roster_valid))
    runner().run(loader(PgnTags__start_variation))
    runner().run(loader(PgnTags__end_variation))
    runner().run(loader(PgnTags__collecting_movetext))
    runner().run(loader(PgnTags__collecting_tag_pairs))
    runner().run(loader(PgnTags__disambiguate_move))
    runner().run(loader(PgnTags__searching))
    runner().run(loader(PgnTags__searching_after_error_in_game))
    runner().run(loader(PgnTags__searching_after_error_in_rav))
    runner().run(loader(PgnRepertoireTags_is_tag_roster_valid))
    runner().run(loader(PgnAnalysis_is_tag_roster_valid))
    runner().run(loader(Pgn_get_fen_string))
    runner().run(loader(RealGamesPGN))
