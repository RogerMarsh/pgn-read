# test_movetext_read_games.py
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

from .. import movetext_parser


class _BasePGN(unittest.TestCase):
    """Provide PGN parser using GameStrictPGN and get() to read PGN text.

    Subclasses override setUp() to use alternatives to GameStrictPGN.

    """

    def setUp(self):
        self.pgn = movetext_parser.PGNMoveText()

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


class _NoWhitespaceCommentPGN(_BasePGN):
    """Setup input text with no whitespace."""

    def setUp(self):
        super().setUp()
        self.game1 = '[Event"Test1"][Result"*"]e4{over\nnewline}*'
        self.game2 = '[Event"Test2"][Result"1-0"]d41-0'
        self.len_game1 = len(self.game1)
        self.len_game2 = len(self.game2)
        self.text = "".join((self.game1, self.game2))

    def compare_text(self, text):
        """Return text as original had nothing which parser removes."""
        return text


class _WhitespaceCommentPGN(_BasePGN):
    """Setup input text with whitespace similar to PGN file structure."""

    def setUp(self):
        super().setUp()
        self.game1 = '[Event "Test1"]\n[Result "*"]\n1. e4 {over\nnewline} *\n'
        self.game2 = '[Event "Test2"]\n[Result "1-0"]\n1. d4 1-0\n'
        self.len_game1 = len(self.game1)
        self.len_game2 = len(self.game2)
        self.text = "".join((self.game1, self.game2))

    def compare_text(self, text):
        """Return text with all stuff ignored by parser removed."""
        text = text.replace(" ", "").replace("\n", "").replace("1.", "")
        return text.replace("overnewline", "over\nnewline")


class _NoWhitespaceReservedPGN(_BasePGN):
    """Setup input text with no whitespace."""

    def setUp(self):
        super().setUp()
        self.game1 = '[Event"Test1"][Result"*"]e4<over\nnewline>*'
        self.game2 = '[Event"Test2"][Result"1-0"]d41-0'
        self.len_game1 = len(self.game1)
        self.len_game2 = len(self.game2)
        self.text = "".join((self.game1, self.game2))

    def compare_text(self, text):
        """Return text as original had nothing which parser removes."""
        return text


class _WhitespaceReservedPGN(_BasePGN):
    """Setup input text with whitespace similar to PGN file structure."""

    def setUp(self):
        super().setUp()
        self.game1 = '[Event "Test1"]\n[Result "*"]\n1. e4 <over\nnewline> *\n'
        self.game2 = '[Event "Test2"]\n[Result "1-0"]\n1. d4 1-0\n'
        self.len_game1 = len(self.game1)
        self.len_game2 = len(self.game2)
        self.text = "".join((self.game1, self.game2))

    def compare_text(self, text):
        """Return text with all stuff ignored by parser removed."""
        text = text.replace(" ", "").replace("\n", "").replace("1.", "")
        return text.replace("overnewline", "over\nnewline")


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

    def test_001_all_buffer_lengths(self):
        for length in range(1, self.len_game1 + self.len_game2 + 2):
            games = self.get(self.text, length)
            self.shared_test(games)


class NoWhitespacePGN(_NoWhitespacePGN, _PGNtests):
    """Do tests with no whitespace."""


class WhitespacePGN(_WhitespacePGN, _PGNtests):
    """Do tests with whitespace."""


class NoWhitespaceCommentPGN(_NoWhitespaceCommentPGN, _PGNtests):
    """Do tests with no whitespace."""


class WhitespaceCommentPGN(_WhitespaceCommentPGN, _PGNtests):
    """Do tests with whitespace."""


class NoWhitespaceReservedPGN(_NoWhitespaceCommentPGN, _PGNtests):
    """Do tests with no whitespace."""


class WhitespaceReservedPGN(_WhitespaceCommentPGN, _PGNtests):
    """Do tests with whitespace."""


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(NoWhitespacePGN))
    runner().run(loader(WhitespacePGN))
    runner().run(loader(NoWhitespaceCommentPGN))
    runner().run(loader(WhitespaceCommentPGN))
    runner().run(loader(NoWhitespaceReservedPGN))
    runner().run(loader(WhitespaceReservedPGN))
