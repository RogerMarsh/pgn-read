# test_zero_in_movetext.py
# Copyright 2026 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test problem cases."""

import unittest

from .. import parser
from .. import movetext_parser
from .. import tagpair_parser


class ZeroInMoveText(unittest.TestCase):
    """Generate '0' tokens from PGN streams.

    This class added to investigate how '0' movetext tokens might be
    generated from large PGN files such as downloads from LiChess.

    The tests show, at least at small scale, that ' 0 ' token is generated
    only if a bare '0' appears in the movetext.  The loop on len(text)
    suggests the position of the bare '0' relative to end of buffer is
    not relevant.
    """

    def t_001_movetext_move_no_zero(self):
        parser = self.parser
        ae = self.assertEqual
        texts = (
            'd4 10 d5 1-0\n\ne4 10 e5 1/2-1/2',
            'd4 20 g6 1-0\n\ne4 20 c6 1/2-1/2',
            'd4 25 g6 1-0\n\ne4 25 c6 { 0 } 1/2-1/2',
        )
        for text in texts:
            for size in range(1, len(text) + 1):
                with self.subTest(size=size, text=text):
                    for game in parser.read_games(text, size=size):
                        ae(" 0 " not in game.pgn_text, True)

    def t_002_movetext_leading_zero(self):
        parser = self.parser
        ae = self.assertEqual
        texts = (
            'd4 010 d5 1-0\n\ne4 10 e5 1/2-1/2',
            'd4 020 g6 1-0\n\ne4 20 c6 1/2-1/2',
            'd4 025 g6 1-0\n\ne4 25 c6 { 0 } 1/2-1/2',
        )
        for text in texts:
            for size in range(1, len(text) + 1):
                with self.subTest(size=size, text=text):
                    for count, game in enumerate(
                        parser.read_games(text, size=size)
                    ):
                        ae(" 0 " not in game.pgn_text, True)
                        if not count:
                            ae(game.state, 1)
                            ae(game.pgn_text[1].strip().startswith("0"), True)
                        else:
                            ae(game.state is None, True)

    def t_003_movetext_move_bare_zero(self):
        parser = self.parser
        ae = self.assertEqual
        text = 'd4 0 d5 1-0\n\ne4 10 e5 1/2-1/2'
        for size in range(1, len(text) + 1):
            with self.subTest(size=size, text=text):
                for count, game in enumerate(
                    parser.read_games(text, size=size)
                ):
                    if count:
                        ae(" 0 " not in game.pgn_text, True)
                        ae(game.state is None, True)
                    else:
                        ae(" 0 " in game.pgn_text, True)
                        ae(game.state, 1)


class PGN(ZeroInMoveText):

    def setUp(self):
        self.parser = parser.PGN()

    def test_001_movetext_move_no_zero(self):
        self.t_001_movetext_move_no_zero()

    def test_002_movetext_leading_zero(self):
        self.t_002_movetext_leading_zero()

    def test_003_movetext_move_bare_zero(self):
        self.t_003_movetext_move_bare_zero()


class PGNMoveText(ZeroInMoveText):

    def setUp(self):
        self.parser = movetext_parser.PGNMoveText()

    def test_001_movetext_move_no_zero(self):
        self.t_001_movetext_move_no_zero()

    def test_002_movetext_leading_zero(self):
        self.t_002_movetext_leading_zero()

    def test_003_movetext_move_bare_zero(self):
        self.t_003_movetext_move_bare_zero()


class PGNTagPair(ZeroInMoveText):

    def setUp(self):
        self.parser = tagpair_parser.PGNTagPair()

    def test_001_movetext_move_no_zero(self):
        self.t_001_movetext_move_no_zero()

    def test_002_movetext_leading_zero(self):
        parser = self.parser
        ae = self.assertEqual
        texts = (
            'd4 010 d5 1-0\n\ne4 10 e5 1/2-1/2',
            'd4 020 g6 1-0\n\ne4 20 c6 1/2-1/2',
            'd4 025 g6 1-0\n\ne4 25 c6 { 0 } 1/2-1/2',
        )
        for text in texts:
            for size in range(1, len(text) + 1):
                with self.subTest(size=size, text=text):
                    for count, game in enumerate(
                        parser.read_games(text, size=size)
                    ):
                        ae(" 0 " not in game.pgn_text, True)
                        if not count:
                            ae(game.state, 0)
                            ae(game.pgn_text, [])
                        else:
                            ae(game.state, 0)
                            ae(game.pgn_text, [])

    def test_003_movetext_move_bare_zero(self):
        parser = self.parser
        ae = self.assertEqual
        text = 'd4 0 d5 1-0\n\ne4 10 e5 1/2-1/2'
        for size in range(1, len(text) + 1):
            with self.subTest(size=size, text=text):
                for count, game in enumerate(
                    parser.read_games(text, size=size)
                ):
                    if count:
                        ae(" 0 " not in game.pgn_text, True)
                        ae(game.state is None, False)
                    else:
                        ae(" 0 " in game.pgn_text, False)
                        ae(game.state, 0)
                    ae(game.pgn_text, [])


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(PGN))
    runner().run(loader(PGNMoveText))
    runner().run(loader(PGNTagPair))
