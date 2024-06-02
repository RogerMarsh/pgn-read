# test_read_games.py
# Copyright 2024 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test processing of tokens found by games module at end of buffer.

Added because three errors for PGN Result tag, 'Result "', were seen in
the purchased version of TWIC downloads for weeks 1 through 1500 when
importing into a ChessTab database.  Changing the buffer size from the
default 10,000,000 to 10,000,001 caused the errors to disappear, so there
is nothing wrong with the file being imported.

"""

import unittest
import io

from .. import parser
from .. import constants
from .. import game


class _BasePGN(unittest.TestCase):
    """Provide PGN parser using GameStrictPGN and get() to read PGN text.

    Subclasses override setUp() to use alternatives to GameStrictPGN.

    """

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameStrictPGN)

    def tearDown(self):
        del self.pgn

    def get(self, text, size):
        """Return Game instances derived from text using buffer size bytes."""
        return [g for g in self.pgn.read_games(io.StringIO(text), size)]

    def shared_test(self, games):
        """The tests for all cases."""
        ae = self.assertEqual
        ae(len(games), 2)
        for game in games:
            ae(game.state, None)
        for game, text in zip(games, (self.game1, self.game2)):
            ae("".join(game.pgn_text), self.compare_text(text))


class _NoWhitespacePGN(_BasePGN):
    """Setup input text with no whitespace."""

    def setUp(self):
        super().setUp()
        self.game1 = '[Event"Test1"][Result"*"]e4*'
        self.game2 = '[Event"Test2"][Result"1-0"]d41-0'
        self.len_game1 = len(self.game1)
        self.len_game2 = len(self.game2)
        self.text = "".join((self.game1, self.game2))

    def compare_text(self, text):
        """Return text as original had nothing which parser removes."""
        return text


class _WhitespacePGN(_BasePGN):
    """Setup input text with whitespace similar to PGN file structure."""

    def setUp(self):
        super().setUp()
        self.game1 = '[Event "Test1"]\n[Result "*"]\n1. e4 *\n'
        self.game2 = '[Event "Test2"]\n[Result "1-0"]\n1. d4 1-0\n'
        self.len_game1 = len(self.game1)
        self.len_game2 = len(self.game2)
        self.text = "".join((self.game1, self.game2))

    def compare_text(self, text):
        """Return text with all stuff ignored by parser removed."""
        return text.replace(" ", "").replace("\n", "").replace("1.", "")


class _PGNtests:
    """Provide tests for end of buffer at various points in Results tag.

    Three errors were reported for 'Result "' tokens when importing games
    from the purchased version of TWIC downloads for weeks 1 through 1500
    into a ChessTab database after concatenating the unzipped files in
    week order (1, 2, ..., 1500).

    The errors occur for imports from the separate files too.

    These tests try having the end of buffer occur at various points in
    the Result tag.  One of which gives a token 'Result "'.

    The error is not seen in the tests.

    """

    def test_001_long_buffer(self):
        games = self.get(self.text, self.len_game1 + self.len_game2 + 20)
        self.shared_test(games)

    def test_002_exact_buffer(self):
        games = self.get(self.text, self.len_game1 + self.len_game2)
        self.shared_test(games)

    def test_003_length_game1_buffer(self):
        games = self.get(self.text, self.len_game1)
        self.shared_test(games)

    def test_004_length_game1_plus_1_buffer(self):
        games = self.get(self.text, self.len_game1 + 1)
        self.shared_test(games)

    def test_005_length_game1_minus_1_buffer(self):
        games = self.get(self.text, self.len_game1 - 1)
        self.shared_test(games)

    def test_006_length_game1_minus_2_buffer(self):
        games = self.get(self.text, self.len_game1 - 2)
        self.shared_test(games)

    def test_007_length_game1_minus_3_buffer(self):
        games = self.get(self.text, self.len_game1 - 3)
        self.shared_test(games)

    def test_008_length_game1_minus_4_buffer(self):
        games = self.get(self.text, self.len_game1 - 4)
        self.shared_test(games)

    def test_009_length_game1_minus_5_buffer(self):
        games = self.get(self.text, self.len_game1 - 5)
        self.shared_test(games)

    def test_010_length_game1_minus_6_buffer(self):
        games = self.get(self.text, self.len_game1 - 6)
        self.shared_test(games)

    def test_011_length_game1_minus_7_buffer(self):
        games = self.get(self.text, self.len_game1 - 7)
        self.shared_test(games)

    def test_012_length_game1_minus_8_buffer(self):
        games = self.get(self.text, self.len_game1 - 8)
        self.shared_test(games)

    def test_013_length_game1_minus_9_buffer(self):
        games = self.get(self.text, self.len_game1 - 9)
        self.shared_test(games)

    def test_014_length_game1_minus_10_buffer(self):
        games = self.get(self.text, self.len_game1 - 10)
        self.shared_test(games)

    def test_015_length_game1_minus_11_buffer(self):
        games = self.get(self.text, self.len_game1 - 11)
        self.shared_test(games)

    def test_016_length_game1_minus_12_buffer(self):
        games = self.get(self.text, self.len_game1 - 12)
        self.shared_test(games)

    def test_017_length_game1_minus_13_buffer(self):
        games = self.get(self.text, self.len_game1 - 13)
        self.shared_test(games)


class NoWhitespacePGN(_NoWhitespacePGN, _PGNtests):
    """Do tests with no whitespace."""


class WhitespacePGN(_WhitespacePGN, _PGNtests):
    """Do tests with whitespace."""


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(NoWhitespacePGN))
    runner().run(loader(WhitespacePGN))
