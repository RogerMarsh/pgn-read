# test_add_token_to_game.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""parser.add_token_to_game tests"""

import unittest
import io

from .. import parser
from .. import game


class Game(unittest.TestCase):

    def setUp(self):
        self.text = '[A"a"]e4e5(e6){comment}<reserved>$5Nf33...Nf6*'

    def tearDown(self):
        pass

    def test_01(self):
        g = game.GameIgnoreCasePGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', '{comment}', '<reserved>',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_02(self):
        g = game.GameTextPGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', '{comment}', '<reserved>',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_03(self):
        g = game.Game()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', '{comment}', '<reserved>',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_04(self):
        g = game.GameStrictPGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', '{comment}', '<reserved>',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)


class GameNewline(unittest.TestCase):

    def setUp(self):
        self.text = '[A"a"]e4\ne5(e6);EOL comment\n%Escaped\n$5Nf33...Nf6*'

    def tearDown(self):
        pass

    def test_01(self):
        g = game.GameIgnoreCasePGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', ';EOL comment\n',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_02(self):
        g = game.GameTextPGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', ';EOL comment\n',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_03(self):
        g = game.Game()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', ';EOL comment\n',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_04(self):
        g = game.GameStrictPGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', ';EOL comment\n',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)


class GameNonPGNText(unittest.TestCase):

    def setUp(self):
        self.text = '[A"a"]e4\ne5(e6) arbitrary non-PGN text $5Nf33...Nf6*'

    def tearDown(self):
        pass

    def test_01(self):
        g = game.GameIgnoreCasePGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_02(self):
        g = game.GameTextPGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_03(self):
        g = game.Game()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')',
             '$5', 'Nf3', 'Nf6', '*'])
        self.assertEqual(g.state, None)

    def test_04(self):
        g = game.GameStrictPGN()
        me = parser.add_token_to_game(self.text, g)
        while me < len(self.text):
            me = parser.add_token_to_game(self.text, g, pos=me)
            self.assertEqual(me is not None, True)
        self.assertEqual(me, len(self.text))
        self.assertEqual(
            g._text,
            ['[A"a"]', 'e4', 'e5', '(', 'e6', ')', 'arbitrary ', 'non-PGN ',
             'text ', '$5', 'Nf3', '3', '...', 'Nf6', '*'])
        self.assertEqual(g.state, 6)


if __name__ == '__main__':
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(Game))
    runner().run(loader(GameNewline))
    runner().run(loader(GameNonPGNText))
