# constants_test.py
# Copyright 2012 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""constants tests"""

import unittest
from copy import copy, deepcopy
import re

from pgn.core import constants


class ConstantsFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__raises(self):
        """"""
        pass

    def test__copy(self):
        """"""
        pass

    def test__assumptions(self):
        """"""
        msg = 'Failure of this test invalidates all other tests'


class RegularExpressions(unittest.TestCase):

    def setUp(self):
        self.games = ''.join((
            '[Event "4NCL-9899A BA1-BA2"]',
            '[Site "Rd1-Warwick"]',
            '[Date "1998.10.24"]',
            '[Round "1.2"]',
            '[White "Lewis, Andrew P"]',
            '[Black "Rogers, Jonathan"]',
            '[Result "1/2-1/2"]',
            '[ECO "A10"]',
            '[WhiteElo "2275"]',
            '[BlackElo "2355"]',
            '[PlyCount "74"]',
            '[EventDate "1998.10.24"]',
            '\n',
            '1. c4 e6 2. Nf3 f5 3. g3 Nf6 4. Bg2 Be7 5. O-O O-O 6. b3 Ne4 7. Bb2 Bf6 8. Qc1',
            'Nc6 9. d3 Bxb2 10. Qxb2 Qf6 11. Qxf6 Nxf6 12. Nc3 d6 13. Rab1 Bd7 14. Rfc1 a6',
            '15. b4 h6 16. d4 Rae8 17. e3 Nd8 18. a4 g5 19. a5 f4 20. exf4 gxf4 21. b5 fxg3',
            '22. hxg3 Ng4 23. Rb2 Kg7 24. Ne4 Nf7 25. Nh2 Nxh2 26. Kxh2 Rb8 27. Kg1 Rfc8 28.',
            'Rcb1 axb5 29. cxb5 Ra8 30. Ra2 Ra7 31. a6 Rca8 32. Nc3 d5 33. Nxd5 exd5 34.',
            'Bxd5 Rd8 35. axb7 Rxa2 36. Bxa2 Nd6 37. b6 c6 1/2-1/2',
            '\r\n',
            '[Event"National Club: Gosport - Wood Green"]',
            '[Site"Gosport"]',
            '[Date"1989.05.07"]',
            '[Round"QFinal"]',
            '[White"Sowray P J"]',
            '[  Black  "Mar\"sh R"   ]  \n ',
            '[Result"1-0"]',
            'e4c6d4d5exd5cxd5c4Nf6c5e6Nc3b6b4a5Bf4axb4Nb5Na6Qa4Bd7',
            'Bc7Nxc5Qd1Qc8dxc5bxc5Nf3Qb7Nd6Bxd6Bxd6Qb6Be5Ke7Be2Ne4O-Of6Bb2Nc3',
            'Bxc3bxc3Qd3(Qb3)Ra3Rfb1Qa7Qc2g6Rb3d4Bc4Rxb3Bxb3Qa6a4Rb8a5e5Bd5Rb2',
            'Qe4Bf5Qh4Qd3(c2(g5))g4Rb1Rxb1Qxb1Kg2Kd6Qxf6Kxd5Qxe5Kc6gxf5Qxf5',
            'Qe8*Kc7Qe7Kc8Ne5c2Qxc5Kd8Qxd4Ke8Qe3Kf8Kg3Qc8Nd3Kg8f4Qc6....Nc1\r\n\r\nQa4   Qb3',
            '1-0*',
            '\n',
            ))

        self.splitter_output = [
            '',
            '[Event "4NCL-9899A BA1-BA2"][Site "Rd1-Warwick"][Date "1998.10.24"][Round "1.2"][White "Lewis, Andrew P"][Black "Rogers, Jonathan"][Result "1/2-1/2"][ECO "A10"][WhiteElo "2275"][BlackElo "2355"][PlyCount "74"][EventDate "1998.10.24"]\n',
            '1. c4 e6 2. Nf3 f5 3. g3 Nf6 4. Bg2 Be7 5. O-O O-O 6. b3 Ne4 7. Bb2 Bf6 8. Qc1Nc6 9. d3 Bxb2 10. Qxb2 Qf6 11. Qxf6 Nxf6 12. Nc3 d6 13. Rab1 Bd7 14. Rfc1 a615. b4 h6 16. d4 Rae8 17. e3 Nd8 18. a4 g5 19. a5 f4 20. exf4 gxf4 21. b5 fxg322. hxg3 Ng4 23. Rb2 Kg7 24. Ne4 Nf7 25. Nh2 Nxh2 26. Kxh2 Rb8 27. Kg1 Rfc8 28.Rcb1 axb5 29. cxb5 Ra8 30. Ra2 Ra7 31. a6 Rca8 32. Nc3 d5 33. Nxd5 exd5 34.Bxd5 Rd8 35. axb7 Rxa2 36. Bxa2 Nd6 37. b6 c6 1/2-1/2\r\n',
            '[Event"National Club: Gosport - Wood Green"][Site"Gosport"][Date"1989.05.07"][Round"QFinal"][White"Sowray P J"][  Black  "Mar"sh R"   ]  \n [Result"1-0"]',
            'e4c6d4d5exd5cxd5c4Nf6c5e6Nc3b6b4a5Bf4axb4Nb5Na6Qa4Bd7Bc7Nxc5Qd1Qc8dxc5bxc5Nf3Qb7Nd6Bxd6Bxd6Qb6Be5Ke7Be2Ne4O-Of6Bb2Nc3Bxc3bxc3Qd3(Qb3)Ra3Rfb1Qa7Qc2g6Rb3d4Bc4Rxb3Bxb3Qa6a4Rb8a5e5Bd5Rb2Qe4Bf5Qh4Qd3(c2(g5))g4Rb1Rxb1Qxb1Kg2Kd6Qxf6Kxd5Qxe5Kc6gxf5Qxf5Qe8*Kc7Qe7Kc8Ne5c2Qxc5Kd8Qxd4Ke8Qe3Kf8Kg3Qc8Nd3Kg8f4Qc6....Nc1\r\n\r\nQa4   Qb31-0*\n',
            ]
        self.tags_output = [
            '',
            ('Event', '4NCL-9899A BA1-BA2'),
            '',
            ('Site', 'Rd1-Warwick'),
            '',
            ('Date', '1998.10.24'),
            '',
            ('Round', '1.2'),
            '',
            ('White', 'Lewis, Andrew P'),
            '',
            ('Black', 'Rogers, Jonathan'),
            '',
            ('Result', '1/2-1/2'),
            '',
            ('ECO', 'A10'),
            '',
            ('WhiteElo', '2275'),
            '',
            ('BlackElo', '2355'),
            '',
            ('PlyCount', '74'),
            '',
            ('EventDate', '1998.10.24'),
            '\n',
            '',
            ('Event', 'National Club: Gosport - Wood Green'),
            '',
            ('Site', 'Gosport'),
            '',
            ('Date', '1989.05.07'),
            '',
            ('Round', 'QFinal'),
            '',
            ('White', 'Sowray P J'),
            '',
            ('Black', 'Mar"sh R'),
            '  \n ',
            ('Result', '1-0'),
            '',
            ]
        self.moves_output = [
            '', '1', '', '.', '', ' ', '', 'c4', '', ' ', '', 'e6', '', ' ',
            '', '2', '', '.', '', ' ', '', 'Nf3', '', ' ', '', 'f5', '', ' ',
            '', '3', '', '.', '', ' ', '', 'g3', '', ' ', '', 'Nf6', '', ' ',
            '', '4', '', '.', '', ' ', '', 'Bg2', '', ' ', '', 'Be7', '', ' ',
            '', '5', '', '.', '', ' ', '', 'O-O', '', ' ', '', 'O-O', '', ' ',
            '', '6', '', '.', '', ' ', '', 'b3', '', ' ', '', 'Ne4', '', ' ',
            '', '7', '', '.', '', ' ', '', 'Bb2', '', ' ', '', 'Bf6', '', ' ',
            '', '8', '', '.', '', ' ', '', 'Qc1', '', 'Nc6', '', ' ', '', '9',
            '', '.', '', ' ', '', 'd3', '', ' ', '', 'Bxb2', '', ' ', '', '10',
            '', '.', '', ' ', '', 'Qxb2', '', ' ', '', 'Qf6', '', ' ', '',
            '11', '', '.', '', ' ', '', 'Qxf6', '', ' ', '', 'Nxf6', '', ' ',
            '', '12', '', '.', '', ' ', '', 'Nc3', '', ' ', '', 'd6', '', ' ',
            '', '13', '', '.', '', ' ', '', 'Rab1', '', ' ', '', 'Bd7', '',
            ' ', '', '14', '', '.', '', ' ', '', 'Rfc1', '', ' ', '', 'a6', '',
            '15', '', '.', '', ' ', '', 'b4', '', ' ', '', 'h6', '', ' ', '',
            '16', '', '.', '', ' ', '', 'd4', '', ' ', '', 'Rae8', '', ' ', '',
            '17', '', '.', '', ' ', '', 'e3', '', ' ', '', 'Nd8', '', ' ', '',
            '18', '', '.', '', ' ', '', 'a4', '', ' ', '', 'g5', '', ' ', '',
            '19', '', '.', '', ' ', '', 'a5', '', ' ', '', 'f4', '', ' ', '',
            '20', '', '.', '', ' ', '', 'exf4', '', ' ', '', 'gxf4', '', ' ',
            '', '21', '', '.', '', ' ', '', 'b5', '', ' ', '', 'fxg3', '',
            '22', '', '.', '', ' ', '', 'hxg3', '', ' ', '', 'Ng4', '', ' ',
            '', '23', '', '.', '', ' ', '', 'Rb2', '', ' ', '', 'Kg7', '', ' ',
            '', '24', '', '.', '', ' ', '', 'Ne4', '', ' ', '', 'Nf7', '', ' ',
            '', '25', '', '.', '', ' ', '', 'Nh2', '', ' ', '', 'Nxh2', '',
            ' ', '', '26', '', '.', '', ' ', '', 'Kxh2', '', ' ', '', 'Rb8',
            '', ' ', '', '27', '', '.', '', ' ', '', 'Kg1', '', ' ', '',
            'Rfc8', '', ' ', '', '28', '', '.', '', 'Rcb1', '', ' ', '',
            'axb5', '', ' ', '', '29', '', '.', '', ' ', '', 'cxb5', '', ' ',
            '', 'Ra8', '', ' ', '', '30', '', '.', '', ' ', '', 'Ra2', '', ' ',
            '', 'Ra7', '', ' ', '', '31', '', '.', '', ' ', '', 'a6', '', ' ',
            '', 'Rca8', '', ' ', '', '32', '', '.', '', ' ', '', 'Nc3', '',
            ' ', '', 'd5', '', ' ', '', '33', '', '.', '', ' ', '', 'Nxd5', '',
            ' ', '', 'exd5', '', ' ', '', '34', '', '.', '', 'Bxd5', '', ' ',
            '', 'Rd8', '', ' ', '', '35', '', '.', '', ' ', '', 'axb7', '',
            ' ', '', 'Rxa2', '', ' ', '', '36', '', '.', '', ' ', '', 'Bxa2',
            '', ' ', '', 'Nd6', '', ' ', '', '37', '', '.', '', ' ', '', 'b6',
            '', ' ', '', 'c6', '', ' ', '', '1/2-1/2', '', '\r', '', '\n', '',

            '', 'e4', '', 'c6', '', 'd4', '', 'd5', '', 'exd5', '', 'cxd5', '',
            'c4', '', 'Nf6', '', 'c5', '', 'e6', '', 'Nc3', '', 'b6', '', 'b4',
            '', 'a5', '', 'Bf4', '', 'axb4', '', 'Nb5', '', 'Na6', '', 'Qa4',
            '', 'Bd7', '', 'Bc7', '', 'Nxc5', '', 'Qd1', '', 'Qc8', '', 'dxc5',
            '', 'bxc5', '', 'Nf3', '', 'Qb7', '', 'Nd6', '', 'Bxd6', '',
            'Bxd6', '', 'Qb6', '', 'Be5', '', 'Ke7', '', 'Be2', '', 'Ne4', '',
            'O-O', '', 'f6', '', 'Bb2', '', 'Nc3', '', 'Bxc3', '', 'bxc3', '',
            'Qd3', '', '(', '', 'Qb3', '', ')', '', 'Ra3', '', 'Rfb1', '',
            'Qa7', '', 'Qc2', '', 'g6', '', 'Rb3', '', 'd4', '', 'Bc4', '',
            'Rxb3', '', 'Bxb3', '', 'Qa6', '', 'a4', '', 'Rb8', '', 'a5', '',
            'e5', '', 'Bd5', '', 'Rb2', '', 'Qe4', '', 'Bf5', '', 'Qh4', '',
            'Qd3', '', '(', '', 'c2', '', '(', '', 'g5', '', ')', '', ')', '',
            'g4', '', 'Rb1', '', 'Rxb1', '', 'Qxb1', '', 'Kg2', '', 'Kd6', '',
            'Qxf6', '', 'Kxd5', '', 'Qxe5', '', 'Kc6', '', 'gxf5', '', 'Qxf5',
            '', 'Qe8', '', '*', '', 'Kc7', '', 'Qe7', '', 'Kc8', '', 'Ne5', '',
            'c2', '', 'Qxc5', '', 'Kd8', '', 'Qxd4', '', 'Ke8', '', 'Qe3', '',
            'Kf8', '', 'Kg3', '', 'Qc8', '', 'Nd3', '', 'Kg8', '', 'f4', '',
            'Qc6', '', '.', '', '.', '', '.', '', '.', '', 'Nc1', '', '\r', '',
            '\n', '', '\r', '', '\n', '', 'Qa4', '', ' ', '', ' ', '', ' ', '',
            'Qb3', '', '1-0', '', '*', '', '\n', '',
            ]

        self.splitter = re.compile(constants.SPLIT_INTO_GAMES)
        self.moves = re.compile(constants.SPLIT_INTO_TOKENS)
        self.tags = re.compile(constants.SPLIT_INTO_TAGS)

    def tearDown(self):
        pass

    def test__raises(self):
        """"""
        pass

    def test__copy(self):
        """"""
        pass

    def test__assumptions(self):
        """"""
        msg = 'Failure of this test invalidates all other tests'
        s = self.splitter.split(self.games)
        self.assertEqual(len(s), len(self.splitter_output), msg)
        for e, t in enumerate(s):
            self.assertEqual(t, self.splitter_output[e])
        s.pop(0)
        while s:
            tagtext = s.pop(0)
            if s:
                movetext = s.pop(0)
            else:
                movetext = ''
            for t in self.tags.split(tagtext):
                st = t.strip()
                if st:
                    f, v = st.split('"', 1)
                    f = f[1:].strip()
                    v = v.rsplit('"', 1)[0]
                    self.assertEqual((f, v), self.tags_output.pop(0), msg)
                else:
                    self.assertEqual(t, self.tags_output.pop(0), msg)
            for t in self.moves.split(movetext):
                self.assertEqual(t, self.moves_output.pop(0), msg)
        self.assertEqual(0, len(self.moves_output), msg)
        self.assertEqual(0, len(self.tags_output), msg)


def suite__cf():
    return unittest.TestLoader().loadTestsFromTestCase(ConstantsFunctions)


def suite__re():
    return unittest.TestLoader().loadTestsFromTestCase(RegularExpressions)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite__cf())
    unittest.TextTestRunner(verbosity=2).run(suite__re())
