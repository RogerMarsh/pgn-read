# test_pgn_files.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""parser tests against selected games from published PGN files.

Most test suites take less than 2 seconds to run.  There are a number of test
suites which take between 400 and 500 seconds to run, where characters are
taken one-at-a-time from the input files and all the characters taken so far
are processed afresh after each character.

'python -m pgn_read.core.tests.test_pgn_files all' includes all the test
suites which take a long time.

"""

import unittest
import os

from .. import parser
from .. import constants
from .. import game


class _StandardTests(unittest.TestCase):

    def do_standard_tests(self, filename, ok_flags, offsets, errors,
                          lengths=None):
        single = ok_flags is None or isinstance(ok_flags, int)
        if single:
            ok_flags = ok_flags,
            offsets = offsets,
            errors = errors,
            lengths = lengths,
        #lengths = (0,) * len(errors)
        ae = self.assertEqual
        games = self.get(filename)
        ae(len(games), len(ok_flags))
        for g, f, o, e, l in zip(games, ok_flags, offsets, errors, lengths):
            ae(g.state, f)
            ae(len(g._text), l)
            ae(g._error_list, o)
            for go, ge in zip(o, e):
                ae(g._text[go], ge)
        if single:
            return games[0]
        else:
            return games


class _StrictPGN(_StandardTests):

    # 4ncl_* means downloaded from 4NCL website 4ncl.co.uk at some time.
    # FIDE_longest_possible_game.pgn downloaded from a file by Jesper Norgaard
    # via a link at www.ecforum.org.uk/viewtopic.php?f=2&t=10411
    # break_* and calgames_* extracted from a download from www.chessdryad.com
    # (It looks like an earlier version of CalBase.pgn at 2020-02-24)
    # twic9nn_* composed from the 900 series files downloaded from
    # https://theweekinchess.com/twic.
    # Little_nn.pgn is successive corrections to an example of non-compliance
    # to the PGN specification given in 'A Little Tutorial on PGN' by Tim
    # Harding at https://portablegamenotation.com.
    # crafty06_* taken from Crafty06.pgn from www.cis.uab.edu/hyatt/crafty/pgn.
    # (Bob Hyatt now retired according to at least one link.)
    filenames = ('4ncl_96-97_01.pgn',
                 '4ncl_96-97_02.pgn',
                 '4ncl_96-97_03.pgn',
                 '4ncl_96-97_04.pgn',
                 '4ncl_96-97_05.pgn',
                 '4ncl_96-97_06.pgn',
                 '4ncl_97-98_07.pgn',
                 'FIDE_longest_possible_game.pgn',
                 'Little_01.pgn',
                 'Little_02.pgn',
                 'Little_03.pgn',
                 'Little_04.pgn',
                 'Little_05.pgn',
                 'Little_06.pgn',
                 'Little_07.pgn',
                 'Little_08.pgn',
                 'Little_09.pgn',
                 'Little_10.pgn',
                 'Little_11.pgn',
                 'Little_12.pgn',
                 'Little_13.pgn',
                 'Little_14.pgn',
                 'Little_15.pgn',
                 'Little_16.pgn',
                 'all_4ncl_1996_2010_08.pgn',
                 'all_4ncl_1996_2010_09.pgn',
                 'all_4ncl_1996_2010_10.pgn',
                 'break_pgn_0_8_1_a.pgn',
                 'break_pgn_0_8_1_b.pgn',
                 'break_pgn_0_8_1_c.pgn',
                 'calgames_01.pgn',
                 'calgames_02.pgn',
                 'calgames_03.pgn',
                 'calgames_04.pgn',
                 'calgames_05.pgn',
                 'calgames_06.pgn',
                 'calgames_07.pgn',
                 'calgames_08.pgn',
                 'calgames_09.pgn',
                 'calgames_10.pgn',
                 'calgames_11.pgn',
                 'crafty06_01.pgn',
                 'crafty06_02.pgn',
                 'crafty06_03.pgn',
                 'twic92n_01.pgn',
                 'twic92n_02.pgn',
                 'twic92n_03.pgn',
                 'twic92n_04.pgn',
                 'twic92n_05.pgn',
                 'twic92n_06.pgn',
                 'twic92n_07.pgn',
                 'twic92n_08.pgn',
                 'twic92n_09.pgn',
                 'twic92n_11.pgn',
                 'twic95n_10.pgn',
                 'twic9nn_error.pgn',
                 )

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameStrictPGN)

    def tearDown(self):
        del self.pgn

    def get(self, filename):
        """Return sequence of Game instances derived from file at path p."""
        p = os.path.join(os.path.dirname(__file__), 'pgn_files', filename)
        return [g for g in self.pgn.read_games(open(p, encoding='iso-8859-1'))]

    def do_game_text_tests(self, game, textlen, state, offset, text_list):
        ignore_case = isinstance(self.pgn, (PGNUpper, PGNLower))
        ae = self.assertEqual
        ae(len(game._text), textlen)
        ae(game.state, state)
        ae(offset+2, len(text_list))
        for gt, tl in zip(game._text, text_list):
            if ignore_case:
                ae(gt.lower(), tl.lower())
            else:
                ae(gt, tl)

    # For test_056_calgames_10 need to collect fens after each move.
    def pgn_positions(self):
        class G(self.pgn._game_class):
            def __init__(self):
                super().__init__()
                self.fens = []
            def modify_board_state(self, position_delta):
                super().modify_board_state(position_delta)
                bs = position_delta[1]
                self.fens.append(
                    game.generate_fen_for_position(
                        self._piece_placement_data.values(),
                        bs[1],
                        bs[2],
                        bs[3],
                        bs[4],
                        bs[5]))
        self.pgn = parser.PGN(game_class=G)

    def do_test_056_calgames_10_fen_tests(self, game):
        ae = self.assertEqual
        ae(game.fens[33],
           '2k1r3/bpp2ppp/p1p5/N3Pb2/n1P2P2/P1B1r3/1P1N2PP/2R1K2R w K - 5 18')
        ae(game.fens[34],
           '2k1r3/bpp2ppp/p1p5/N3Pb2/n1P2P2/P1B1r3/1P1N2PP/2RK3R b - - 6 18')
        ae(len(game.fens) in {76, 38}, True)
        if len(game.fens) == 76:
            ae(game.fens[-1],
               '3r4/1pp1kp2/p1p3pR/4Pr2/4KP2/8/7P/6R1 w - - 3 39')
        else:
            ae(game.fens[-1],
               '2kr4/bpp2ppp/p1p5/N3Pb2/n1P2P2/P1Br4/1P1N2PP/2RKR3 w - - 9 20')


class StrictPGN(_StrictPGN):

    def expected(self, game, pgn, text_pgn, strict_pgn):
        if game._strict_pgn is False:
            return pgn
        elif game._strict_pgn is None:
            return text_pgn
        else:
            return strict_pgn

    def test_001_pgn_file_names(self):
        ae = self.assertEqual
        ae(sorted(os.listdir(os.path.join(os.path.dirname(__file__),
                                          'pgn_files'))),
           sorted(self.filenames))

    def test_002_4ncl_96_97_01_pgn(self):
        self.do_standard_tests('4ncl_96-97_01.pgn', None, [], '', 108)

    def test_003_4ncl_96_97_02_pgn(self):
        self.do_standard_tests('4ncl_96-97_02.pgn', None, [], '', 113)

    def test_004_4ncl_96_97_03_pgn(self):
        self.do_standard_tests('4ncl_96-97_03.pgn', None, [], '', 155)

    def test_005_4ncl_96_97_04_pgn(self):
        self.do_standard_tests('4ncl_96-97_04.pgn', None, [], '', 109)

    def test_006_4ncl_96_97_05_pgn(self):
        self.do_standard_tests('4ncl_96-97_05.pgn', None, [], '', 126)

    def test_007_4ncl_96_97_06_pgn(self):
        self.do_standard_tests('4ncl_96-97_06.pgn', None, [], '', 89)

    def test_008_FIDE_longest_possible_game_pgn(self):
        g = self.do_standard_tests(
            'FIDE_longest_possible_game.pgn', None, [], '', 11798)

    def test_009_break_pgn_0_8_1_a_pgn(self):
        self.do_standard_tests('break_pgn_0_8_1_a.pgn', None, [], '', 81)

    def test_010_break_pgn_0_8_1_b_pgn(self):
        self.do_standard_tests('break_pgn_0_8_1_b.pgn', None, [], '', 189)

    def test_011_break_pgn_0_8_1_c_pgn(self):
        ae = self.assertEqual
        games = self.get('break_pgn_0_8_1_c.pgn')
        ae(len(games), 1)
        g = games[0]
        if g._strict_pgn:
            ae(g.state, 109)
            ae(game.generate_fen_for_position(
                g._piece_placement_data.values(),
                g._active_color,
                g._castling_availability,
                g._en_passant_target_square,
                g._halfmove_clock,
                g._fullmove_number),
               '3r3k/pp2b1rp/2p5/2PpQ3/1P1Pp2P/P3q1PN/5R1K/5R2 b - - 1 43')
            ae(g._text[g.state], ' Rdg8')
        else:
            ae(g.state, None)

    def test_012_twic92n_01_pgn(self):
        self.do_standard_tests('twic92n_01.pgn', None, [], '', 111)

    def test_013_twic92n_02_pgn(self):
        self.do_standard_tests('twic92n_02.pgn', None, [], '', 126)

    def test_014_twic92n_03_pgn(self):
        self.do_standard_tests('twic92n_03.pgn', None, [], '', 96)

    def test_015_twic92n_04_pgn(self):
        self.do_standard_tests('twic92n_04.pgn', None, [], '', 120)

    def test_016_twic92n_05_pgn(self):
        self.do_standard_tests('twic92n_05.pgn', None, [], '', 113)

    def test_017_twic92n_06_pgn(self):
        self.do_standard_tests('twic92n_06.pgn', None, [], '', 103)

    def test_018_twic92n_07_pgn(self):
        self.do_standard_tests('twic92n_07.pgn', None, [], '', 141)

    def test_019_twic92n_08_pgn(self):
        self.do_standard_tests('twic92n_08.pgn', None, [], '', 122)

    def test_020_twic92n_09_pgn(self):
        self.do_standard_tests('twic92n_09.pgn', None, [], '', 115)

    def test_021_twic95n_10_pgn(self):
        self.do_standard_tests('twic95n_10.pgn', None, [], '', 50)

    def test_022_twic9nn_error_pgn(self):
        games = self.do_standard_tests(
            'twic9nn_error.pgn',
            (None, None, None, None, None, None, 14, None, 0, None, 0, 153),
            ([], [], [], [], [], [], [14], [], [0], [], [0], [153]),
            ('', '*', '', '*', '', '', [' ('], '', '', [' Bxc5'], '', ''),
            (13, 1, 13, 1, 14, 1, 18, 16, 1, 18, 1, 155))
        ae = self.assertEqual
        ae(games[0]._text,
           ['[Event "St. Pauli Open 2012"]',
            '[Site "Hamburg GER"]',
            '[Date "2012.07.07"]',
            '[Round "1.18"]',
            '[White "Kahlert,T"]',
            '[Black "Kosovs,Ernst"]',
            '[Result "*"]',
            '[WhiteElo "2229"]',
            '[BlackElo "1974"]',
            '[WhiteFideId "4625242"]',
            '[BlackFideId "12921289"]',
            '[EventDate "2012.07.07"]',
            '*'])
        ae(games[1]._text, ['*'])
        ae(games[2]._text,
           ['[Event "St. Pauli Open 2012"]',
            '[Site "Hamburg GER"]',
            '[Date "2012.07.10"]',
            '[Round "4.7"]',
            '[White "Thingstad,E"]',
            '[Black "Svane,R"]',
            '[Result "*"]',
            '[WhiteElo "2198"]',
            '[BlackElo "2367"]',
            '[WhiteFideId "1506439"]',
            '[BlackFideId "4657101"]',
            '[EventDate "2012.07.07"]',
            '*'])
        ae(games[3]._text, ['*'])
        ae(games[4]._text,
           ['[Event "St. Pauli Open 2012"]',
            '[Site "Hamburg GER"]',
            '[Date "2012.07.13"]',
            '[Round "7.9"]',
            '[White "Hochgraefe,M"]',
            '[Black "Schiele,L"]',
            '[Result "*"]',
            '[WhiteTitle "FM"]',
            '[WhiteElo "2345"]',
            '[BlackElo "2089"]',
            '[WhiteFideId "4615484"]',
            '[BlackFideId "4693868"]',
            '[EventDate "2012.07.07"]',
            '*'])
        ae(games[5]._text, ['*'])
        ae(games[6]._text,
           ['[Event "ch-Commonwealth 2012"]',
            '[Site "Chennai IND"]',
            '[Date "2012.11.28"]',
            '[Round "8"]',
            '[White "Karthikeyan,P2"]',
            '[Black "Adly,A"]',
            '[Result "(+)-(-)"]',
            '[WhiteTitle "IM"]',
            '[BlackTitle "GM"]',
            '[WhiteElo "2414"]',
            '[BlackElo "2607"]',
            '[WhiteFideId "5018226"]',
            '[BlackFideId "10601619"]',
            '[EventDate "2012.11.23"]',
            ' (',
            ' +)-(-) ',
            ' (',
            ' +)-(-)'])
        ae(games[7]._text,
           ['[Event "Dvorkovich Mem 2013"]',
            '[Site "Taganrog RUS"]',
            '[Date "2013.01.17"]',
            '[Round "3.31"]',
            '[White "Golubov,Saveliy"]',
            '[Black "Osipov,Ad"]',
            '[Result "1-0 ff"]',
            '[WhiteElo "2227"]',
            '[BlackElo "2080"]',
            '[ECO "B00"]',
            '[Opening "King\'s pawn opening"]',
            '[WhiteFideId "24176729"]',
            '[BlackFideId "4162641"]',
            '[EventDate "2013.01.15"]',
            'e4',
            '1-0'])
        ae(games[8]._text, [' ff'])
        ae(games[9]._text,
           ['[Event "Dvorkovich Mem 2013"]',
            '[Site "Taganrog RUS"]',
            '[Date "2013.01.21"]',
            '[Round "7.25"]',
            '[White "Baraeva,I"]',
            '[Black "Isaev,Y"]',
            '[Result "1-0 ff"]',
            '[WhiteTitle "WF"]',
            '[BlackTitle "FM"]',
            '[WhiteElo "2159"]',
            '[BlackElo "2238"]',
            '[ECO "A40"]',
            '[Opening "Queen\'s pawn"]',
            '[WhiteFideId "24142565"]',
            '[BlackFideId "4173350"]',
            '[EventDate "2013.01.15"]',
            'd4',
            '1-0'])
        ae(games[10]._text, [' ff'])
        ae(games[11]._text,
           ['[Event "6th Mayors Cup 2013"]',
            '[Site "Mumbai IND"]',
            '[Date "2013.06.05"]',
            '[Round "10"]',
            '[White "Swathi,G"]',
            '[Black "Neelotpal,D"]',
            '[Result "0-1"]',
            '[WhiteTitle "WGM"]',
            '[BlackTitle "GM"]',
            '[WhiteElo "2260"]',
            '[BlackElo "2461"]',
            '[ECO "C55"]',
            '[Opening "Two knights defence (Modern bishop\'s opening)"]',
            '[WhiteFideId "5003474"]',
            '[BlackFideId "5003512"]',
            '[EventDate "2013.05.29"]',
            'e4', 'e5', 'Nf3', 'Nc6', 'Bc4', 'Nf6', 'd3', 'Be7', 'Bb3', 'O-O',
            'Nbd2', 'd6', 'c3', 'Na5', 'Bc2', 'c5', 'O-O', 'Nc6', 'Re1', 'Re8',
            'Nf1', 'h6', 'Ng3', 'Bf8', 'h3', 'Qc7', 'Nh2', 'Be6', 'Qf3', 'Nh7',
            'Nf5', 'Rad8', 'Ng4', 'd5', 'Ba4', 'Kh8', 'h4', 'dxe4', 'dxe4',
            'f6', 'Nge3', 'Qf7', 'Qe2', 'g6', 'Ng3', 'h5', 'b3', 'Qc7', 'Bb2',
            'Bh6', 'Rad1', 'Rxd1', 'Rxd1', 'Rd8', 'Ngf1', 'Rxd1', 'Qxd1', 'a6',
            'Nd5', 'Qd8', 'c4', 'Nd4', 'b4', 'Bf8', 'bxc5', 'Bxc5', 'Nfe3',
            'b5', 'cxb5', 'axb5', 'Bc2', 'Nxc2', 'Nxc2', 'Kg7', 'Qd3', 'Bxd5',
            'exd5', 'Qb6', 'Ne3', 'Nf8', 'Bc1', 'f5', 'Nd1', 'Nd7', 'Qd2',
            'Nf6', 'Bb2', 'Bd4', 'Kf1', 'Nxd5', 'g3', 'b4', 'Bxd4', 'Qxd4',
            'Ke1', 'Qc4', 'Ne3', 'Nxe3', 'Qxe3', 'e4', 'Qb6', 'Qc3', 'Ke2',
            'Qd3', 'Ke1', 'Qb1', 'Ke2', 'Qxa2', 'Ke3', 'Qb3', 'Kf4',
            'Qf3', 'Ke5', 'Qc3', 'Kd5', 'b3', 'Qb7', 'Kh6', 'Qb8', 'b2',
            'Ke6', 'Kh7', 'Qb7', 'Qg7', 'Qb5', 'Qg8', 'Kf6', 'Qf8', 'Ke6',
            'Qg7', 'Qb4', 'g5', 'hxg5', 'e3', 'fxe3', 'f4', 'Kf5', ' b1',
            ' 0-1'])

    def test_023_4ncl_97_98_07_pgn(self):
        self.do_standard_tests('4ncl_97-98_07.pgn', None, [], '', 113)

    def test_024_all_4ncl_1996_2010_08(self):
        self.do_standard_tests('all_4ncl_1996_2010_08.pgn', None, [], '', 322)

    def test_025_all_4ncl_1996_2010_09(self):
        self.do_standard_tests('all_4ncl_1996_2010_09.pgn', None, [], '', 87)

    def test_026_all_4ncl_1996_2010_10(self):
        self.do_standard_tests('all_4ncl_1996_2010_10.pgn', None, [], '', 157)

    def test_027_calgames_01(self):
        self.do_standard_tests('calgames_01.pgn', None, [], '', 56)

    def test_028_calgames_02(self):
        self.do_standard_tests('calgames_02.pgn', None, [], '', 262)

    def test_029_calgames_03(self):
        self.do_standard_tests('calgames_03.pgn', None, [], '', 307)

    def test_030_calgames_04(self):
        ae = self.assertEqual
        games = self.get('calgames_04.pgn')
        ae(len(games), 1)
        g = games[0]
        if g._strict_pgn:
            ae(g.state, 58)
            ae(game.generate_fen_for_position(
                g._piece_placement_data.values(),
                g._active_color,
                g._castling_availability,
                g._en_passant_target_square,
                g._halfmove_clock,
                g._fullmove_number),
               '2b1kb2/1p5q/2n5/4p1p1/1pPpPpP1/3P1P2/1QNB1KNr/5R2 w - - 3 24')
            ae(g._text[g.state], ' Nce1')
        else:
            ae(g.state, None)

    # The other classes which do not force case of whole game to upper or lower
    # give the result expected for a valid game: forcing case happens to make
    # errors in some recursive annotation variations and, or, in the game.
    def test_031_calgames_05(self):
        self.do_standard_tests('calgames_05.pgn', None, [], '', 411)

    # calgames_06.pgn has an error in the Event Tag but rest of game is fine.
    # Test changed after addition of "Bad tag" to PGN regular expression.
    def test_032_calgames_06(self):
        ae = self.assertEqual
        games = self.get('calgames_06.pgn')
        ae(len(games), 1)
        self.do_game_text_tests(
            games[0], 139, 0, 0,
           ['{::Bad Tag::[Event "LA CC Handicap Tour "C""]::Bad Tag::}',
            ' [Site "Los Angeles, CA"]'])
        ae(games[0].is_tag_roster_valid(), False)

    # calgames_07.pgn is calgames_06.pgn with the Event Tag corrected.
    def test_033_calgames_07(self):
        ae = self.assertEqual
        games = self.get('calgames_07.pgn')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text[0], r'[Event "LA CC Handicap Tour \"C\""]')
        ae(games[0]._tags['Event'], r'LA CC Handicap Tour \"C\"')

    # Incrementally adjust little_01.pgn until state is True.
    def test_034_little_01(self):
        ae = self.assertEqual
        games = self.get('Little_01.pgn')
        ae(len(games), 2)
        ae(games[0].state, 6)
        ae(len(games[0]._text), 108)
        ae(games[1].state, 3)
        ae(len(games[1]._text), 3)
        self.do_game_text_tests(
            games[0], 108, 6, 6,
            ['[Event "EM/CL/Q19-2"]', '<br>',
             '[White "Silva, ABC (BRA)"]', '<br>',
             '[Black "Player, Riccardo (ITA)"]', '<br>',
             ' (', ' Result '])
        ae(games[0]._text[2], '[White "Silva, ABC (BRA)"]')

    # Incrementally adjust little_01.pgn until state is True.
    def test_035_little_02(self):
        ae = self.assertEqual
        games = self.get('Little_02.pgn')
        ae(len(games), 2)
        g = games[0]
        ae(g.state, 3)
        self.do_game_text_tests(
            g, 64 if g._strict_pgn is None else 105, 3, 3,
            ['[Event "EM/CL/Q19-2"]',
             '[White "Silva, ABC (BRA)"]',
             '[Black "Player, Riccardo (ITA)"]',
             ' (',
             ' Result '])
        ae(games[1].state, 3)
        ae(len(games[1]._text), 3)

    # Incrementally adjust little_01.pgn until state is True.
    def test_036_little_03(self):
        ae = self.assertEqual
        games = self.get('Little_03.pgn')
        g = games[0]
        if g._strict_pgn is False:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 99, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4 ',
                 '; Ng8-f6 2.c2-c4; e7-e6 3.Nb1c3; Bf8-b4 4.e2-e3; 0-<br>\n'])
            ae(g._text[5],
               'd4')
            ae(games[1]._text, ['</p>', '<p>', '</p>'])
        elif g._strict_pgn is None:
            ae(len(games), 1)
            self.do_game_text_tests(
                g, 48, 7, 7,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4',
                 '; Ng8-f6 2.c2-c4; e7-e6 3.Nb1c3; Bf8-b4 4.e2-e3; 0-<br>\n',
                 ' Ng1', ' -f3',
                 ])
        else:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 99, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4 '])
            ae(g._text[5], ' d2')
            ae(games[1]._text, ['</p>', '<p>', '</p>'])

    # Incrementally adjust little_01.pgn until state is True.
    def test_037_little_04(self):
        ae = self.assertEqual
        games = self.get('Little_04.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        g = games[0]
        if g._strict_pgn is False:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 158, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 143, 12, 12,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', ' Ng1', ' -f3',
                 ])
        else:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 158, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_038_little_05(self):
        ae = self.assertEqual
        games = self.get('Little_05.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        g = games[0]
        if g._strict_pgn is False:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 160, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 141, 20, 20,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'Nf3', 'Nbd7', '<br>', 'Qb3', ' Bb4', ' xNc3',
                 ])
        else:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 160, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_039_little_06(self):
        ae = self.assertEqual
        games = self.get('Little_06.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        g = games[0]
        if g._strict_pgn is False:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 161, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 143, 22, 22,
               ['[Event "EM/CL/Q19-2"]',
                '[White "Silva, ABC (BRA)"]',
                '[Black "Player, Riccardo (ITA)"]',
                '[Result "1/2 - Â"]', '<br>',
                'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Nbd7', '<br>',
                'Qb3', ' Bb4', ' xNc3',
                ])
        else:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 161, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_040_little_07(self):
        ae = self.assertEqual
        games = self.get('Little_07.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        g = games[0]
        if g._strict_pgn is False:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 162, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 145, 24, 24,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                 '<br>', 'Qb3', ' Bb4', ' xNc3',
                 ])
        else:
            ae(len(games), 2)
            self.do_game_text_tests(
                g, 162, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_041_little_08(self):
        ae = self.assertEqual
        games = self.get('Little_08.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        ae(len(games), 2)
        g = games[0]
        if g._strict_pgn is False:
            self.do_game_text_tests(
                g, 164, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            self.do_game_text_tests(
                g, 145, 24, 24,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                 '<br>', 'Qb3', ' Bb4', ' xNc3',
                 ])
        else:
            self.do_game_text_tests(
                g, 164, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_042_little_09(self):
        ae = self.assertEqual
        games = self.get('Little_09.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        ae(len(games), 2)
        g = games[0]
        if g._strict_pgn is False:
            self.do_game_text_tests(
                g, 163, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            self.do_game_text_tests(
                g, 145, 24, 24,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                 '<br>', 'Qb3', ' Bb4', ' xNc3',
                 ])
        else:
            self.do_game_text_tests(
                g, 163, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_043_little_10(self):
        ae = self.assertEqual
        games = self.get('Little_10.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        ae(len(games), 2)
        g = games[0]
        if g._strict_pgn is False:
            self.do_game_text_tests(
                g, 163, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            self.do_game_text_tests(
                g, 138, 26, 26,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                 '<br>', 'Qb3', 'Bxc3', 'bxc3', ' a2', ' -a4',
                 ])
        else:
            self.do_game_text_tests(
                g, 163, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_044_little_11(self):
        ae = self.assertEqual
        games = self.get('Little_11.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        ae(len(games), 2)
        g = games[0]
        if g._strict_pgn is False:
            self.do_game_text_tests(
                g, 164, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            self.do_game_text_tests(
                g, 111, 43, 43,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                 '<br>', 'Qb3', 'Bxc3', 'bxc3', 'Nb6', 'a4', 'a5', '<br>',
                 'Ne5', 'Ng4', 'Nxg4', 'Bxg4', 'f3', 'Be6', '<br>',
                 'Qc2', 'Qh4', 'e4', 'Bd7', 'Be3', '<br>',
                 ' Rf1', ' -b1',
                 ])
        else:
            self.do_game_text_tests(
                g, 164, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_045_little_12(self):
        ae = self.assertEqual
        games = self.get('Little_12.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        ae(len(games), 2)
        g = games[0]
        if g._strict_pgn is False:
            self.do_game_text_tests(
                g, 165, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            self.do_game_text_tests(
                g, 86, 60, 60,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                 '<br>', 'Qb3', 'Bxc3', 'bxc3', 'Nb6', 'a4', 'a5', '<br>',
                 'Ne5', 'Ng4', 'Nxg4', 'Bxg4', 'f3', 'Be6', '<br>', 'Qc2',
                 'Qh4', 'e4', 'Bd7', 'Be3', 'Re7', '<br>', 'Rfb1', 'Bc6', '$1',
                 'Bf2',
                 'Qg5', 'exd5', 'Nxd5', '<br>', 'Bxh7', 'Kh8', 'h4', 'Qf4',
                 'Re1', 'Rae8', '<br>', 'Rxe7', ' Re8', ' xRe7',
                 ])
        else:
            self.do_game_text_tests(
                g, 165, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_046_little_13(self):
        ae = self.assertEqual
        games = self.get('Little_13.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        ae(len(games), 2)
        g = games[0]
        if g._strict_pgn is False:
            self.do_game_text_tests(
                g, 167, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            self.do_game_text_tests(
                g, 86, 60, 60,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                 '<br>', 'Qb3', 'Bxc3', 'bxc3', 'Nb6', 'a4', 'a5', '<br>',
                 'Ne5', 'Ng4', 'Nxg4', 'Bxg4', 'f3', 'Be6', '<br>', 'Qc2',
                 'Qh4', 'e4', 'Bd7', 'Be3', 'Re7', '<br>', 'Rfb1', 'Bc6', '$1',
                 'Bf2',
                 'Qg5', 'exd5', 'Nxd5', '<br>', 'Bxh7', 'Kh8', 'h4', 'Qf4',
                 'Re1', 'Rae8', '<br>', 'Rxe7', ' Re8', ' xRe7',
                 ])
        else:
            self.do_game_text_tests(
                g, 167, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_047_little_14(self):
        ae = self.assertEqual
        games = self.get('Little_14.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        ae(len(games), 2)
        g = games[0]
        if g._strict_pgn is False:
            self.do_game_text_tests(
                g, 173, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif g._strict_pgn is None:
            self.do_game_text_tests(
                g, 86, 60, 60,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                 'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                 '<br>', 'Qb3', 'Bxc3', 'bxc3', 'Nb6', 'a4', 'a5', '<br>',
                 'Ne5', 'Ng4', 'Nxg4', 'Bxg4', 'f3', 'Be6', '<br>', 'Qc2',
                 'Qh4', 'e4', 'Bd7', 'Be3', 'Re7', '<br>', 'Rfb1', 'Bc6',
                 '$1', 'Bf2',
                 'Qg5', 'exd5', 'Nxd5', '<br>', 'Bxh7', 'Kh8', 'h4', 'Qf4',
                 'Re1', 'Rae8', '<br>', 'Rxe7', ' Re8', ' xRe7',
                 ])
        else:
            self.do_game_text_tests(
                g, 173, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])

    # Incrementally adjust little_01.pgn until state is True.
    def test_048_little_15(self):
        ae = self.assertEqual
        games = self.get('Little_15.pgn')
        ae(games[1]._text, ['</p>', '<p>', '</p>'])
        strict_pgn = self.pgn._game_class._strict_pgn
        g = games[0]
        if strict_pgn is False:
            ae(len(games), 2)
            ae(g.state, 6)
            self.do_game_text_tests(
                g, 173, 6, 6,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 'd4', ' -d4  ', ' Ng8'])
        elif strict_pgn is None:
            ae(len(games), 2)
            ae(g.state, None)
            ae(len(g._text), 70)
            ae(g.state, None)
            ae(g._text,
               ['[Event "EM/CL/Q19-2"]',
                '[White "Silva, ABC (BRA)"]',
                '[Black "Player, Riccardo (ITA)"]',
                '[Result "1/2 - Â"]', '<br>',
                'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', '<br>',
                'Bd3', 'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7',
                '<br>', 'Qb3', 'Bxc3', 'bxc3', 'Nb6', 'a4', 'a5', '<br>',
                'Ne5', 'Ng4', 'Nxg4', 'Bxg4', 'f3', 'Be6', '<br>',
                'Qc2', 'Qh4', 'e4', 'Bd7', 'Be3', 'Re7', '<br>',
                'Rfb1', 'Bc6', '$1', 'Bf2', 'Qg5', 'exd5', 'Nxd5', '<br>',
                'Bxh7', 'Kh8', 'h4', 'Qf4', 'Re1', 'Rae8', '<br>',
                'Rxe7', 'Rxe7', 'Be4', 'Ne3', 'Qe2', 'Ng4', '<br>',
                'g3', 'Qd6', 'Qd3', '1-0',
                ])
        else:
            ae(len(games), 2)
            ae(g.state, 5)
            self.do_game_text_tests(
                g, 173, 5, 5,
                ['[Event "EM/CL/Q19-2"]',
                 '[White "Silva, ABC (BRA)"]',
                 '[Black "Player, Riccardo (ITA)"]',
                 '[Result "1/2 - Â"]',
                 '<br>',
                 ' d2', ' -d4  '])
        return games

    # calgames_08.pgn provoked addition of try ... except ... around searches
    # of source squares for a move.
    def test_049_calgames_08(self):
        ae = self.assertEqual
        games = self.get('calgames_08.pgn')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, None)
        ae(g._error_list, [82] if not g._strict_pgn else [82])

    def test_050_calgames_09(self):
        ae = self.assertEqual
        games = self.get('calgames_09.pgn')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, None)
        ae(g._error_list, [417] if not g._strict_pgn else [417])

    def test_051_crafty06_01(self):
        ae = self.assertEqual
        games = self.get('crafty06_01.pgn')
        strict_pgn = self.pgn._game_class._strict_pgn
        ae(len(games), 3)
        gt = games[0]._text
        if strict_pgn is False:
            ae(gt[0], '[Event "ICC 5 3"]')
            ae(gt[2], '[Date "2006.06.13"]')
            ae(gt[4], '[White "crafty"]')
            ae(gt[-1], '1/2-1/2')
            gt = games[1]._text
            ae(gt[0], ' for ')
            ae(gt[2], '; Mon, 4 Dec 2006 12:17:10 -0600\n')
            ae(gt[1], ' <crafty@localhost>')
            ae(gt[-1], ' CST)')
            gt = games[2]._text
            ae(gt[0], '[Event "ICC 5 3"]')
            ae(gt[2], '[Date "2006.06.13"]')
            ae(gt[5], '[Black "crafty"]')
            ae(gt[-1], '1-0')
        elif strict_pgn is None:
            ae(gt[0], '[Event "ICC 5 3"]')
            ae(gt[2], '[Date "2006.06.13"]')
            ae(gt[4], '[White "crafty"]')
            ae(gt[-1], '1/2-1/2')
            gt = games[1]._text
            ae(gt[0], '<crafty@localhost>')
            ae(gt[2], ' (')
            ae(gt[1], '; Mon, 4 Dec 2006 12:17:10 -0600\n')
            ae(gt[-1], ' CST)')
            gt = games[2]._text
            ae(gt[0], '[Event "ICC 5 3"]')
            ae(gt[2], '[Date "2006.06.13"]')
            ae(gt[5], '[Black "crafty"]')
            ae(gt[-1], '1-0')
        else:
            ae(gt[0], '[Event "ICC 5 3"]')
            ae(gt[2], '[Date "2006.06.13"]')
            ae(gt[4], '[White "crafty"]')
            ae(gt[-1], '1/2-1/2')
            gt = games[1]._text
            ae(gt[0], ' for ')
            ae(gt[2], '; Mon, 4 Dec 2006 12:17:10 -0600\n')
            ae(gt[1], ' <crafty@localhost>')
            ae(gt[-1], ' CST)')
            gt = games[2]._text
            ae(gt[0], '[Event "ICC 5 3"]')
            ae(gt[2], '[Date "2006.06.13"]')
            ae(gt[5], '[Black "crafty"]')
            ae(gt[-1], '1-0')

    # Minimum adjustments little_01.pgn until state is True for TextPGN.
    def test_052_little_16(self):
        ae = self.assertEqual
        games = self.get('Little_16.pgn')
        strict_pgn = self.pgn._game_class._strict_pgn
        g = games[0]
        if strict_pgn is False:
            ae(len(games), 2)
            ae(g.state, 9)
            self.do_game_text_tests(
                g, 166, 9, 9,
                ['[Event "EM/CL/Q19-2"]', '<br>',
                 '[White "Silva, ABC (BRA)"]', '<br>',
                 '[Black "Player, Riccardo (ITA)"]', '<br>',
                 '[Result "1/2 - Â"]', '<br>',
                 'd4', ' -d4  ', ' Ng8',
                 ])
        elif strict_pgn is None:
            ae(len(games), 2)
            ae(g.state, None)
            ae(len(g._text), 72)
            ae(g.state, None)
            ae(g._text,
               ['[Event "EM/CL/Q19-2"]', '<br>',
                '[White "Silva, ABC (BRA)"]', '<br>',
                '[Black "Player, Riccardo (ITA)"]', '<br>',
                '[Result "1/2 - Â"]', '<br>',
                'd4', 'Nf6', 'c4', 'e6', 'Nc3', 'Bb4', 'e3', 'O-O', 'Bd3',
                'd5', 'cxd5', 'exd5', 'Nf3', 'Re8', 'O-O', 'Nbd7', '<br>',
                'Qb3', 'Bxc3', 'bxc3', 'Nb6', 'a4', 'a5', '<br>',
                'Ne5', 'Ng4', 'Nxg4', 'Bxg4', 'f3', 'Be6', '<br>',
                'Qc2', 'Qh4', 'e4', 'Bd7', 'Be3', 'Re7', '<br>',
                'Rfb1', 'Bc6', '$1', 'Bf2', 'Qg5', 'exd5', 'Nxd5', '<br>',
                'Bxh7', 'Kh8', 'h4', 'Qf4', 'Re1', 'Rae8', '<br>',
                'Rxe7', 'Rxe7', 'Be4', 'Ne3', 'Qe2', 'Ng4', '<br>',
                'g3', 'Qd6', 'Qd3', '1-0',
                ])
        else:
            ae(len(games), 2)
            ae(g.state, 8)
            self.do_game_text_tests(
                g, 166, 8, 8,
                ['[Event "EM/CL/Q19-2"]', '<br>',
                 '[White "Silva, ABC (BRA)"]', '<br>',
                 '[Black "Player, Riccardo (ITA)"]', '<br>',
                 '[Result "1/2 - Â"]', '<br>',
                 ' d2', ' -d4  ',
                 ])
        return games

    def test_053_twic92n_11_pgn(self):
        g = self.do_standard_tests('twic92n_11.pgn', None, [], '', 82)

    def test_054_crafty06_02(self):
        games = self.do_standard_tests(
            'crafty06_02.pgn',
            (0, None, 1, 7),
            ([0], [], [1], [7]),
            ([' MIME-Version: '], [], [], []),
            (349, 1, 1326, 222))

    def test_055_crafty06_03(self):
        games = self.do_standard_tests(
            'crafty06_03.pgn',
            (0, None, 1, 8),
            ([0], [], [1], [8]),
            ([' MIME-Version: '], [], [], []),
            (557, 1, 1392, 115))

    # calgames_10.pgn added when castling options missing in a samples report.
    def test_056_calgames_10(self):
        self.pgn_positions()
        ae = self.assertEqual
        games = self.get('calgames_10.pgn')
        ae(len(games), 1)
        ae(games[0].state, 52)
        self.do_test_056_calgames_10_fen_tests(games[0])
        #ae(games[0]._text[0], r'[Event "LA CC Handicap Tour \"C\""]')
        #ae(games[0]._tags['Event'], r'LA CC Handicap Tour \"C\"')

    # calgames_11.pgn has multiple, and nested, '--' tokens.
    def test_057_calgames_11(self):
        ae = self.assertEqual
        games = self.get('calgames_11.pgn')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, None)
        ae(g._error_list,
           [112, 198] if not g._strict_pgn else [112, 186, 200])


class StrictPGNOneCharacterAtATime(StrictPGN):

    def get(self, filename):
        """Return sequence of Game instances derived from file at path p.

        Read characters one at a time from file.

        """
        p = os.path.join(os.path.dirname(__file__), 'pgn_files', filename)
        return [g for g in self.pgn.read_games(open(p, encoding='iso-8859-1'),
                                               size=1)]

    def test_008_FIDE_longest_possible_game_pgn(self):
        # This would take a long time!
        pass

    # calgames_06.pgn has an error in the Event Tag but rest of game is fine.
    # Test changed after addition of "Bad tag" to PGN regular expression.
    def test_032_calgames_06(self):
        ae = self.assertEqual
        games = self.get('calgames_06.pgn')
        ae(len(games), 1)
        self.do_game_text_tests(
            games[0], 139, 0, 0,
           [r'{::Bad Tag::[Event "LA CC Handicap Tour "C""]::Bad Tag::}',
            ' [Site "Los Angeles, CA"]'])


class StrictPGNExtendByOneCharacter(StrictPGN):

    def get(self, filename):
        """Return sequence of Game instances derived from file at path p.

        Where possible do two reads of source where the second read is one
        character, the last one in s.

        """
        p = os.path.join(os.path.dirname(__file__), 'pgn_files', filename)
        t = open(p, encoding='iso-8859-1')
        size = max(t.seek(0, os.SEEK_END)-1, 1)
        t.seek(0)
        try:
            return [g for g in self.pgn.read_games(t, size=size)]
        finally:
            t.close()


class _StrictFalseTests:

    # calgames_06.pgn has an error in the Event Tag but rest of game is fine.
    # Test changed after addition of "Bad tag" to PGN regular expression.
    def test_032_calgames_06(self):
        ae = self.assertEqual
        games = self.get('calgames_06.pgn')
        ae(len(games), 1)
        self.do_game_text_tests(
            games[0], 75, None, 0,
           [r'[Event "LA CC Handicap Tour \"C\""]',
            '[Site "Los Angeles, CA"]'])
        ae(games[0].is_tag_roster_valid(), True)

    # calgames_10.pgn added when castling options missing in a samples report.
    def test_056_calgames_10(self):
        self.pgn_positions()
        ae = self.assertEqual
        games = self.get('calgames_10.pgn')
        ae(len(games), 1)
        ae(games[0].state, None)
        self.do_test_056_calgames_10_fen_tests(games[0])
        #ae(games[0]._text[0], r'[Event "LA CC Handicap Tour \"C\""]')
        #ae(games[0]._tags['Event'], r'LA CC Handicap Tour \"C\"')


class PGN(_StrictFalseTests, StrictPGN):

    def setUp(self):
        self.pgn = parser.PGN()


class PGNOneCharacterAtATime(_StrictFalseTests, StrictPGNOneCharacterAtATime):

    def setUp(self):
        self.pgn = parser.PGN()


class PGNExtendByOneCharacter(_StrictFalseTests, StrictPGNExtendByOneCharacter):

    def setUp(self):
        self.pgn = parser.PGN()


class _TextFormatTests:

    def test_022_twic9nn_error_pgn(self):
        games = self.do_standard_tests(
            'twic9nn_error.pgn',
            (None, None, None, None, None, None, 14, None, None, None),
            ([], [], [], [], [], [], [14], [], [], []),
            ('', '*', '', '*', '', '', [' ('], '', '', [' Bxc5'],),
            (13, 1, 13, 1, 14, 1, 18, 16, 18, 154,))
        ae = self.assertEqual
        ae(games[0]._text,
           ['[Event "St. Pauli Open 2012"]',
            '[Site "Hamburg GER"]',
            '[Date "2012.07.07"]',
            '[Round "1.18"]',
            '[White "Kahlert,T"]',
            '[Black "Kosovs,Ernst"]',
            '[Result "*"]',
            '[WhiteElo "2229"]',
            '[BlackElo "1974"]',
            '[WhiteFideId "4625242"]',
            '[BlackFideId "12921289"]',
            '[EventDate "2012.07.07"]',
            '*'])
        ae(games[1]._text, ['*'])
        ae(games[2]._text,
           ['[Event "St. Pauli Open 2012"]',
            '[Site "Hamburg GER"]',
            '[Date "2012.07.10"]',
            '[Round "4.7"]',
            '[White "Thingstad,E"]',
            '[Black "Svane,R"]',
            '[Result "*"]',
            '[WhiteElo "2198"]',
            '[BlackElo "2367"]',
            '[WhiteFideId "1506439"]',
            '[BlackFideId "4657101"]',
            '[EventDate "2012.07.07"]',
            '*'])
        ae(games[3]._text, ['*'])
        ae(games[4]._text,
           ['[Event "St. Pauli Open 2012"]',
            '[Site "Hamburg GER"]',
            '[Date "2012.07.13"]',
            '[Round "7.9"]',
            '[White "Hochgraefe,M"]',
            '[Black "Schiele,L"]',
            '[Result "*"]',
            '[WhiteTitle "FM"]',
            '[WhiteElo "2345"]',
            '[BlackElo "2089"]',
            '[WhiteFideId "4615484"]',
            '[BlackFideId "4693868"]',
            '[EventDate "2012.07.07"]',
            '*'])
        ae(games[5]._text, ['*'])
        ae(games[6]._text,
           ['[Event "ch-Commonwealth 2012"]',
            '[Site "Chennai IND"]',
            '[Date "2012.11.28"]',
            '[Round "8"]',
            '[White "Karthikeyan,P2"]',
            '[Black "Adly,A"]',
            '[Result "(+)-(-)"]',
            '[WhiteTitle "IM"]',
            '[BlackTitle "GM"]',
            '[WhiteElo "2414"]',
            '[BlackElo "2607"]',
            '[WhiteFideId "5018226"]',
            '[BlackFideId "10601619"]',
            '[EventDate "2012.11.23"]',
            ' (',
            ' +)-(-) ',
            ' (',
            ' +)-(-)'])
        ae(games[7]._text,
           ['[Event "Dvorkovich Mem 2013"]',
            '[Site "Taganrog RUS"]',
            '[Date "2013.01.17"]',
            '[Round "3.31"]',
            '[White "Golubov,Saveliy"]',
            '[Black "Osipov,Ad"]',
            '[Result "1-0 ff"]',
            '[WhiteElo "2227"]',
            '[BlackElo "2080"]',
            '[ECO "B00"]',
            '[Opening "King\'s pawn opening"]',
            '[WhiteFideId "24176729"]',
            '[BlackFideId "4162641"]',
            '[EventDate "2013.01.15"]',
            'e4',
            '1-0'])
        ae(games[8]._text,
           ['[Event "Dvorkovich Mem 2013"]',
            '[Site "Taganrog RUS"]',
            '[Date "2013.01.21"]',
            '[Round "7.25"]',
            '[White "Baraeva,I"]',
            '[Black "Isaev,Y"]',
            '[Result "1-0 ff"]',
            '[WhiteTitle "WF"]',
            '[BlackTitle "FM"]',
            '[WhiteElo "2159"]',
            '[BlackElo "2238"]',
            '[ECO "A40"]',
            '[Opening "Queen\'s pawn"]',
            '[WhiteFideId "24142565"]',
            '[BlackFideId "4173350"]',
            '[EventDate "2013.01.15"]',
            'd4',
            '1-0'])
        ae(games[9]._text,
           ['[Event "6th Mayors Cup 2013"]',
            '[Site "Mumbai IND"]',
            '[Date "2013.06.05"]',
            '[Round "10"]',
            '[White "Swathi,G"]',
            '[Black "Neelotpal,D"]',
            '[Result "0-1"]',
            '[WhiteTitle "WGM"]',
            '[BlackTitle "GM"]',
            '[WhiteElo "2260"]',
            '[BlackElo "2461"]',
            '[ECO "C55"]',
            '[Opening "Two knights defence (Modern bishop\'s opening)"]',
            '[WhiteFideId "5003474"]',
            '[BlackFideId "5003512"]',
            '[EventDate "2013.05.29"]',
            'e4', 'e5', 'Nf3', 'Nc6', 'Bc4', 'Nf6', 'd3', 'Be7', 'Bb3', 'O-O',
            'Nbd2', 'd6', 'c3', 'Na5', 'Bc2', 'c5', 'O-O', 'Nc6', 'Re1', 'Re8',
            'Nf1', 'h6', 'Ng3', 'Bf8', 'h3', 'Qc7', 'Nh2', 'Be6', 'Qf3', 'Nh7',
            'Nf5', 'Rad8', 'Ng4', 'd5', 'Ba4', 'Kh8', 'h4', 'dxe4', 'dxe4',
            'f6', 'Nge3', 'Qf7', 'Qe2', 'g6', 'Ng3', 'h5', 'b3', 'Qc7', 'Bb2',
            'Bh6', 'Rad1', 'Rxd1', 'Rxd1', 'Rd8', 'Ngf1', 'Rxd1', 'Qxd1', 'a6',
            'Nd5', 'Qd8', 'c4', 'Nd4', 'b4', 'Bf8', 'bxc5', 'Bxc5', 'Nfe3',
            'b5', 'cxb5', 'axb5', 'Bc2', 'Nxc2', 'Nxc2', 'Kg7', 'Qd3', 'Bxd5',
            'exd5', 'Qb6', 'Ne3', 'Nf8', 'Bc1', 'f5', 'Nd1', 'Nd7', 'Qd2',
            'Nf6', 'Bb2', 'Bd4', 'Kf1', 'Nxd5', 'g3', 'b4', 'Bxd4', 'Qxd4',
            'Ke1', 'Qc4', 'Ne3', 'Nxe3', 'Qxe3', 'e4', 'Qb6', 'Qc3', 'Ke2',
            'Qd3', 'Ke1', 'Qb1', 'Ke2', 'Qxa2', 'Ke3', 'Qb3', 'Kf4',
            'Qf3', 'Ke5', 'Qc3', 'Kd5', 'b3', 'Qb7', 'Kh6', 'Qb8', 'b2',
            'Ke6', 'Kh7', 'Qb7', 'Qg7', 'Qb5', 'Qg8', 'Kf6', 'Qf8', 'Ke6',
            'Qg7', 'Qb4', 'g5', 'hxg5', 'e3', 'fxe3', 'f4', 'Kf5',
            '0-1'])

    # calgames_06.pgn has an error in the Event Tag but rest of game is fine.
    # Test changed after addition of "Bad tag" to PGN regular expression.
    def test_032_calgames_06(self):
        ae = self.assertEqual
        games = self.get('calgames_06.pgn')
        ae(len(games), 1)
        self.do_game_text_tests(
            games[0], 75, None, 0,
           [r'[Event "LA CC Handicap Tour \"C\""]',
            '[Site "Los Angeles, CA"]'])

    # Incrementally adjust little_01.pgn until state is True.
    def test_034_little_01(self):
        ae = self.assertEqual
        games = self.get('Little_01.pgn')
        ae(len(games), 1)
        ae(len(games[0]._text), 68)
        ae(games[0].state, 6)
        ae(games[0]._text[:6], ['[Event "EM/CL/Q19-2"]', '<br>',
                                '[White "Silva, ABC (BRA)"]', '<br>',
                                '[Black "Player, Riccardo (ITA)"]', '<br>'])
        ae(games[0]._text[6], ' (')

    # Incrementally adjust little_01.pgn until state is True.
    def test_035_little_02(self):
        ae = self.assertEqual
        games = self.get('Little_02.pgn')
        ae(len(games), 1)
        ae(len(games[0]._text), 65)
        ae(games[0].state, 3)
        ae(games[0]._text[:6], ['[Event "EM/CL/Q19-2"]',
                                '[White "Silva, ABC (BRA)"]',
                                '[Black "Player, Riccardo (ITA)"]',
                                ' (', ' Result ', ' "1/2 '])
        ae(games[0]._text[6], ' - ')

    def test_054_crafty06_02(self):
        games = self.do_standard_tests(
            'crafty06_02.pgn',
            (52, None, 366, 60),
            ([52], [], [366], [60]),
            ([' ('], [], [], []),
            (222, 1, 805, 120))

    def test_055_crafty06_03(self):
        games = self.do_standard_tests(
            'crafty06_03.pgn',
            (None, None, 216, 46),
            ([], [], [216], [46]),
            (['('], [], [], []),
            (187, 1, 1136, 106))

    # calgames_10.pgn added when castling options missing in a samples report.
    def test_056_calgames_10(self):
        self.pgn_positions()
        ae = self.assertEqual
        games = self.get('calgames_10.pgn')
        ae(len(games), 1)
        ae(games[0].state, None)
        self.do_test_056_calgames_10_fen_tests(games[0])
        #ae(games[0]._text[0], r'[Event "LA CC Handicap Tour \"C\""]')
        #ae(games[0]._tags['Event'], r'LA CC Handicap Tour \"C\"')


class TextPGN(_TextFormatTests, StrictPGN):

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameTextPGN)


class TextPGNOneCharacterAtATime(_TextFormatTests,
                                 StrictPGNOneCharacterAtATime):

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameTextPGN)


class TextPGNExtendByOneCharacter(_TextFormatTests,
                                  StrictPGNExtendByOneCharacter):

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameTextPGN)


class _IgnoreCaseTextPGN:

    def test_034_little_01(self):
        g = self.do_standard_tests('Little_01.pgn', 6, [6], [' ('], 68)

    def test_035_little_02(self):
        g = self.do_standard_tests('Little_02.pgn', 3, [3], [' ('], 65)

    def test_037_little_04(self):
        g = self.do_standard_tests(
            'Little_04.pgn', (12, 3), ([12], []), ([' Ng1'], []), [142, 3])

    def test_038_little_05(self):
        g = self.do_standard_tests(
            'Little_05.pgn', (20, 3), ([20], []), ([' Bb4'], []), [140, 3])

    def test_039_little_06(self):
        g = self.do_standard_tests(
            'Little_06.pgn', (22, 3), ([22], []), ([' Bb4'], []), [142, 3])

    def test_040_little_07(self):
        g = self.do_standard_tests(
            'Little_07.pgn', (24, 3), ([24],[]), ([' Bb4'], []), [144, 3])

    def test_041_little_08(self):
        g = self.do_standard_tests(
            'Little_08.pgn', (24, 3), ([24],[]), ([' Bb4'], []), [144, 3])

    def test_042_little_09(self):
        g = self.do_standard_tests(
            'Little_09.pgn', (24, 3), ([24],[]), ([' Bb4'], []), [144, 3])


class IgnoreCaseTextPGN(_IgnoreCaseTextPGN, TextPGN):

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameIgnoreCasePGN)


class IgnoreCaseTextPGNOneCharacterAtATime(_IgnoreCaseTextPGN,
                                           TextPGNOneCharacterAtATime):

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameIgnoreCasePGN)


class IgnoreCaseTextPGNExtendByOneCharacter(_IgnoreCaseTextPGN,
                                            TextPGNExtendByOneCharacter):

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameIgnoreCasePGN)


class PGNLower(parser.PGN):

    @staticmethod
    def _read_pgn(source, length):
        if isinstance(source, str):
            yield source
            return
        try:
            while True:
                pgntext = source.read(length)
                yield pgntext.lower()
                if not pgntext:
                    break
        finally:
            source.close()


class _IgnoreCasePGNLower:

    def test_002_4ncl_96_97_01_pgn(self):
        g = self.do_standard_tests(
            '4ncl_96-97_01.pgn', 57, [57], [' bxc5'], 162)

    def test_003_4ncl_96_97_02_pgn(self):
        g = self.do_standard_tests(
            '4ncl_96-97_02.pgn', 30, [30], [' bxc4'], 204)

    def test_006_4ncl_96_97_05_pgn(self):
        g = self.do_standard_tests(
            '4ncl_96-97_05.pgn', 52, [52], [' Be4'], 203)

    def test_009_break_pgn_0_8_1_a_pgn(self):
        g = self.do_standard_tests(
            'break_pgn_0_8_1_a.pgn', 47, [47], [' bxc1'], 112)

    def test_010_break_pgn_0_8_1_b_pgn(self):
        g = self.do_standard_tests(
            'break_pgn_0_8_1_b.pgn', 94, [94], [' bxc4'], 278)

    def test_011_break_pgn_0_8_1_c_pgn(self):
        g = self.do_standard_tests('break_pgn_0_8_1_c.pgn', None, [], '', 118)

    def test_013_twic92n_02_pgn(self):
        g = self.do_standard_tests('twic92n_02.pgn', 42, [42], [' bxc4'], 216)

    def test_015_twic92n_04_pgn(self):
        g = self.do_standard_tests('twic92n_04.pgn', 44, [44], [' bxc3'], 196)

    def test_018_twic92n_07_pgn(self):
        g = self.do_standard_tests('twic92n_07.pgn', 85, [85], [' bxc4'], 202)

    # Correct because the FEN tag has been converted to lower-case.
    def test_021_twic95n_10_pgn(self):
        g = self.do_standard_tests('twic95n_10.pgn', 19, [19], [], 82)

    def test_022_twic9nn_error_pgn(self):
        games = self.do_standard_tests(
            'twic9nn_error.pgn',
            (None, None, None, None, None, None, 14, None, None, 81),
            ([], [], [], [], [], [], [14], [], [], [81]),
            ('', '', '', '', '', '', [' ('], '', '', [' bxc5'],),
            (13, 1, 13, 1, 14, 1, 18, 16, 18, 238,))

    def test_023_4ncl_97_98_07_pgn(self):
        g = self.do_standard_tests(
            '4ncl_97-98_07.pgn', 40, [40], [' bxc4'], 191)

    def test_025_all_4ncl_1996_2010_09(self):
        g = self.do_standard_tests(
            'all_4ncl_1996_2010_09.pgn', None, [72], '', 95)

    def test_028_calgames_02(self):
        g = self.do_standard_tests('calgames_02.pgn', None, [47], '', 278)

    def test_029_calgames_03(self):
        g = self.do_standard_tests(
            'calgames_03.pgn', 101, [88, 101], [' bxc5', ' bxc5'], 515)

    def test_030_calgames_04(self):
        g = self.do_standard_tests('calgames_04.pgn', None, [], '', 97)

    def test_031_calgames_05(self):
        g = self.do_standard_tests('calgames_05.pgn', None, [48, 200], '', 434)

    # calgames_06.pgn has an error in the Event Tag but rest of game is fine.
    def test_032_calgames_06(self):
        g = self.do_standard_tests('calgames_06.pgn', 69, [69], [' bxc5'], 79)

    def test_033_calgames_07(self):
        g = self.do_standard_tests('calgames_07.pgn', 69, [69], [' bxc5'], 79)

    def test_034_little_01(self):
        g = self.do_standard_tests('Little_01.pgn', 6, [6], [' ('], 68)

    def test_035_little_02(self):
        g = self.do_standard_tests('Little_02.pgn', 3, [3], [' ('], 65)

    def test_036_little_03(self):
        g = self.do_standard_tests('Little_03.pgn', 7, [7], [' Ng1'], 48)

    def test_037_little_04(self):
        g = self.do_standard_tests(
            'Little_04.pgn', (12, 3), ([12], []), ([' Ng1'], []), [142, 3])

    def test_038_little_05(self):
        g = self.do_standard_tests(
            'Little_05.pgn', (20, 3), ([20], []), ([' Bb4'], []), [140, 3])

    def test_039_little_06(self):
        g = self.do_standard_tests(
            'Little_06.pgn', (22, 3), ([22], []), ([' Bb4'], []), [142, 3])

    def test_040_little_07(self):
        g = self.do_standard_tests(
            'Little_07.pgn', (24, 3), ([24],[]), ([' Bb4'], []), [144, 3])

    def test_041_little_08(self):
        g = self.do_standard_tests(
            'Little_08.pgn', (24, 3), ([24],[]), ([' Bb4'], []), [144, 3])

    def test_042_little_09(self):
        g = self.do_standard_tests(
            'Little_09.pgn', (24, 3), ([24],[]), ([' Bb4'], []), [144, 3])

    def test_043_little_10(self):
        g = self.do_standard_tests(
            'Little_10.pgn', (26, 3), ([26],[]), ([' a2'], []), [138, 3])

    def test_044_little_11(self):
        g = self.do_standard_tests(
            'Little_11.pgn', (43, 3), ([43],[]), ([' Rf1'], []), [111, 3])

    def test_045_little_12(self):
        g = self.do_standard_tests(
            'Little_12.pgn', (60, 3), ([60],[]), ([' Re8'], []), [86, 3])

    def test_046_little_13(self):
        g = self.do_standard_tests(
            'Little_13.pgn', (60, 3), ([60],[]), ([' Re8'], []), [86, 3])

    def test_047_little_14(self):
        g = self.do_standard_tests(
            'Little_14.pgn', (60, 3), ([60],[]), ([' Re8'], []), [86, 3])

    def test_048_little_15(self):
        g = self.do_standard_tests('Little_15.pgn',
                                   (None, 3),
                                   ([], []),
                                   ('', ''),
                                   (70, 3))

    def test_049_calgames_08(self):
        g = self.do_standard_tests(
            'calgames_08.pgn', 52, [52], [' bxc4'], 152)

    def test_050_calgames_09(self):
        g = self.do_standard_tests(
            'calgames_09.pgn', 19, [19], [' bxa3'], 770)

    def test_051_crafty06_01(self):
        games = self.do_standard_tests('crafty06_01.pgn',
                                       (None, 2, None),
                                       ([], [2], []),
                                       ('', [' ('], ''),
                                       (143, 17, 114))

    def test_052_little_16(self):
        g = self.do_standard_tests('Little_16.pgn',
                                   (None, 3),
                                   ([], []),
                                   ('', '</p>'),
                                   (72, 3))

    def test_053_twic92n_11_pgn(self):
        g = self.do_standard_tests('twic92n_11.pgn', 29, [29], '', 141)

    # calgames_10.pgn added when castling options missing in a samples report.
    def test_056_calgames_10(self):
        self.pgn_positions()
        ae = self.assertEqual
        games = self.get('calgames_10.pgn')
        ae(len(games), 1)
        ae(games[0].state, None)
        self.do_test_056_calgames_10_fen_tests(games[0])
        #ae(games[0]._text[0], r'[Event "LA CC Handicap Tour \"C\""]')
        #ae(games[0]._tags['Event'], r'LA CC Handicap Tour \"C\"')

    def test_057_calgames_11(self):
        g = self.do_standard_tests(
            'calgames_11.pgn', None, [112, 198], [' --'], 266)


class TextPGNLower(_IgnoreCasePGNLower, TextPGN):

    def setUp(self):
        self.pgn = PGNLower(game_class=game.GameIgnoreCasePGN)


class TextPGNLowerOneCharacterAtATime(_IgnoreCasePGNLower,
                                      TextPGNOneCharacterAtATime):

    def setUp(self):
        self.pgn = PGNLower(game_class=game.GameIgnoreCasePGN)

    def test_008_FIDE_longest_possible_game_pgn(self):
        # This would take a long time!
        pass


class TextPGNLowerExtendByOneCharacter(_IgnoreCasePGNLower,
                                       TextPGNExtendByOneCharacter):

    def setUp(self):
        self.pgn = PGNLower(game_class=game.GameIgnoreCasePGN)


class PGNUpper(parser.PGN):

    @staticmethod
    def _read_pgn(source, length):
        if isinstance(source, str):
            yield source
            return
        try:
            while True:
                pgntext = source.read(length)
                yield pgntext.upper()
                if not pgntext:
                    break
        finally:
            source.close()


class _IgnoreCasePGNUpper:

    def test_008_FIDE_longest_possible_game_pgn(self):
        g = self.do_standard_tests(
            'FIDE_longest_possible_game.pgn', 2003, [2003], [' Bxa4'], 21616)

    # Correct: earlier black played 'dxc4' from movetext 'DXC4 BXC4' when white
    # had a pawn on 'b3' and a bishop on 'd3'.  'BXC4' is interpreted as 'Bxc4'
    # and the difference does not show until much later when black plays 'DXC4'
    # after the bishop has moved.
    def test_010_break_pgn_0_8_1_b_pgn(self):
        g = self.do_standard_tests(
            'break_pgn_0_8_1_b.pgn', 87, [87], [' dxc4'], 286)

    def test_011_break_pgn_0_8_1_c_pgn(self):
        g = self.do_standard_tests('break_pgn_0_8_1_c.pgn', None, [], '', 118)

    # Correct because the movetext leading up to 'c3' is 'BXC4 NC5 C3' with
    # black playing 'BXC4' with a pawn on b5 and a bishop on e6.
    # 'BXC4' gets treated as 'Bxc4', a piece move, rather than 'bxc4', a pawn
    # move.
    def test_014_twic92n_03_pgn(self):
        g = self.do_standard_tests('twic92n_03.pgn', 73, [73], [' c3'], 118)

    def test_015_twic92n_04_pgn(self):
        g = self.do_standard_tests('twic92n_04.pgn', 70, [70], [' Bxc4'], 169)

    def test_016_twic92n_05_pgn(self):
        g = self.do_standard_tests('twic92n_05.pgn', 41, [41], [' Bxc6'], 186)

    def test_019_twic92n_08_pgn(self):
        g = self.do_standard_tests('twic92n_08.pgn', 27, [27], [' Bxc3'], 228)

    # Correct because the FEN tag has been converted to upper-case.
    def test_021_twic95n_10_pgn(self):
        #g = self.do_standard_tests('twic95n_10.pgn', False, 19, 'O-O-O')
        g = self.do_standard_tests('twic95n_10.pgn', 19, [], [], 82)
        #print(g._text)
        #print(g._text[:19])
        #print(g._text[19:])

    def test_022_twic9nn_error_pgn(self):
        games = self.do_standard_tests(
            'twic9nn_error.pgn',
            (None, None, None, None, None, None, 14, None, None, 80),
            ([], [], [], [], [], [], [14], [], [], [80]),
            ('', '*', '', '*', '', '', [' ('], '', '', [' Bxc5'],),
            (13, 1, 13, 1, 14, 1, 18, 16, 18, 238,))

    def test_024_all_4ncl_1996_2010_08(self):
        g = self.do_standard_tests(
            'all_4ncl_1996_2010_08.pgn', None, [69], '', 330)

    def test_026_all_4ncl_1996_2010_10(self):
        g = self.do_standard_tests(
            'all_4ncl_1996_2010_10.pgn', None, [58, 102],
            [' Bxc2', ' Bxc2'], 198)

    def test_028_calgames_02(self):
        g = self.do_standard_tests(
            'calgames_02.pgn', None, [39], [' Bxc6'], 286)

    def test_029_calgames_03(self):
        g = self.do_standard_tests(
            'calgames_03.pgn', None, [140], [' Bxc2'], 320)

    def test_030_calgames_04(self):
        g = self.do_standard_tests('calgames_04.pgn', None, [], '', 97)
 
    def test_031_calgames_05(self):
        g = self.do_standard_tests(
            'calgames_05.pgn', 157, [117, 157], [' Bxc6', ' Bxc6'], 673)

    # calgames_06.pgn has an error in the Event Tag but rest of game is fine.
    def test_032_calgames_06(self):
        g = self.do_standard_tests('calgames_06.pgn', None, [], '', 75)

    # calgames_07.pgn is calgames_06.pgn with the Event Tag corrected.
    def test_033_calgames_07(self):
        g = self.do_standard_tests('calgames_07.pgn', None, [], '', 75)

    def test_034_little_01(self):
        g = self.do_standard_tests('Little_01.pgn', 6, [6], [' ('], 68)

    def test_035_little_02(self):
        g = self.do_standard_tests('Little_02.pgn', 3, [3], [' ('], 65)

    def test_036_little_03(self):
        g = self.do_standard_tests('Little_03.pgn', 5, [5], [' d2'], 59)

    def test_037_little_04(self):
        g = self.do_standard_tests(
            'Little_04.pgn', (5, 3), ([5], []), ([' d2'], []), [166, 3])

    def test_038_little_05(self):
        g = self.do_standard_tests(
            'Little_05.pgn', (5, 3), ([5], []), ([' d2'], []), [168, 3])

    def test_039_little_06(self):
        g = self.do_standard_tests(
            'Little_06.pgn', (5, 3), ([5], []), ([' d2'], []), [169, 3])

    def test_040_little_07(self):
        g = self.do_standard_tests(
            'Little_07.pgn', (5, 3), ([5],[]), ([' d2'], []), [172, 3])

    def test_041_little_08(self):
        g = self.do_standard_tests(
            'Little_08.pgn', (5, 3), ([5],[]), ([' d2'], []), [172, 3])

    def test_042_little_09(self):
        g = self.do_standard_tests(
            'Little_09.pgn', (5, 3), ([5],[]), ([' d2'], []), [172, 3])

    def test_043_little_10(self):
        g = self.do_standard_tests(
            'Little_10.pgn', (5, 3), ([5],[]), ([' d2'], []), [172, 3])

    def test_044_little_11(self):
        g = self.do_standard_tests(
            'Little_11.pgn', (5, 3), ([5],[]), ([' d2'], []), [173, 3])

    def test_045_little_12(self):
        g = self.do_standard_tests(
            'Little_12.pgn', (5, 3), ([5],[]), ([' d2'], []), [174, 3])

    def test_046_little_13(self):
        g = self.do_standard_tests(
            'Little_13.pgn', (5, 3), ([5],[]), ([' d2'], []), [174, 3])

    def test_047_little_14(self):
        g = self.do_standard_tests(
            'Little_14.pgn', (5, 3), ([5],[]), ([' d2'], []), [174, 3])

    def test_048_little_15(self):
        g = self.do_standard_tests(
            'Little_15.pgn', (5, 3), ([5],[]), ([' d2'], []), [174, 3])

    def test_049_calgames_08(self):
        g = self.do_standard_tests(
            'calgames_08.pgn', None, [82], [' --'], 114)

    def test_050_calgames_09(self):
        g = self.do_standard_tests(
            'calgames_09.pgn', 18, [18], [' Bxa3'], 772)

    def test_051_crafty06_01(self):
        games = self.do_standard_tests('crafty06_01.pgn',
                                       (None, 2, None),
                                       ([], [2], []),
                                       ('', [' ('], ''),
                                       (143, 17, 114))

    def test_052_little_16(self):
        g = self.do_standard_tests(
            'Little_16.pgn', (8, 3), ([8], []), ([' d2'], []), (176, 3))

    def test_053_twic92n_11_pgn(self):
        g = self.do_standard_tests('twic92n_11.pgn', 36, [36], '', 135)


class TextPGNUpper(_IgnoreCasePGNUpper, TextPGN):

    def setUp(self):
        self.pgn = PGNUpper(game_class=game.GameIgnoreCasePGN)


class TextPGNUpperOneCharacterAtATime(_IgnoreCasePGNUpper,
                                      TextPGNOneCharacterAtATime):

    def setUp(self):
        self.pgn = PGNUpper(game_class=game.GameIgnoreCasePGN)

    def test_008_FIDE_longest_possible_game_pgn(self):
        # This would take a long time!
        pass


class TextPGNUpperExtendByOneCharacter(_IgnoreCasePGNUpper,
                                       TextPGNExtendByOneCharacter):

    def setUp(self):
        self.pgn = PGNUpper(game_class=game.GameIgnoreCasePGN)


class ExportPGN(_StrictPGN):

    def read(self, filename):
        """Return sequence of Game instances derived from file at path p."""
        p = os.path.join(os.path.dirname(__file__), 'pgn_files', filename)
        return open(p, encoding='iso-8859-1').read()

    def do_export_tests(self, filename):
        # The export is same as import in some cases for movetext, particularly
        # when neither RAVs nor any form of comment is present.
        # 4NCL PGN files do not sort PGN tags to the PGN specification.
        # TWIC PGN files do sort to the specification but names are not
        # formatted to the specification.
        # The CalBase PGN file is wrong on both counts.
        # So no tests of this program's PGN tag output against the inputs.
        ae = self.assertEqual
        games = self.get(filename)
        text = self.read(filename)
        for g in games:
            if g.state and not g._error_list:
                et = g.get_export_pgn_movetext()
                ae(et in text, True)

    def test_002_4ncl_96_97_01_pgn(self):
        self.do_export_tests('4ncl_96-97_01.pgn')

    def test_003_4ncl_96_97_02_pgn(self):
        self.do_export_tests('4ncl_96-97_02.pgn')

    def test_004_4ncl_96_97_03_pgn(self):
        self.do_export_tests('4ncl_96-97_03.pgn')

    def test_005_4ncl_96_97_04_pgn(self):
        self.do_export_tests('4ncl_96-97_04.pgn')

    def test_006_4ncl_96_97_05_pgn(self):
        self.do_export_tests('4ncl_96-97_05.pgn')

    def test_020_twic92n_09_pgn(self):
        self.do_export_tests('twic92n_09.pgn')


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        do_single_character_tests = sys.argv[1] == 'all'
    else:
        do_single_character_tests = False
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(StrictPGN))
    if do_single_character_tests:
        runner().run(loader(StrictPGNOneCharacterAtATime))
    runner().run(loader(StrictPGNExtendByOneCharacter))
    runner().run(loader(PGN))
    if do_single_character_tests:
        runner().run(loader(PGNOneCharacterAtATime))
    runner().run(loader(PGNExtendByOneCharacter))
    runner().run(loader(TextPGN))
    if do_single_character_tests:
        runner().run(loader(TextPGNOneCharacterAtATime))
    runner().run(loader(TextPGNExtendByOneCharacter))
    runner().run(loader(IgnoreCaseTextPGN))
    if do_single_character_tests:
        runner().run(loader(IgnoreCaseTextPGNOneCharacterAtATime))
    runner().run(loader(IgnoreCaseTextPGNExtendByOneCharacter))
    runner().run(loader(TextPGNLower))
    if do_single_character_tests:
        runner().run(loader(TextPGNLowerOneCharacterAtATime))
    runner().run(loader(TextPGNLowerExtendByOneCharacter))
    runner().run(loader(TextPGNUpper))
    if do_single_character_tests:
        runner().run(loader(TextPGNUpperOneCharacterAtATime))
    runner().run(loader(TextPGNUpperExtendByOneCharacter))
    runner().run(loader(ExportPGN))
