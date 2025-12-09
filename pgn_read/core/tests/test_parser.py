# test_parser.py
# Copyright 2012, 2016, 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test processing of tokens found by methods in games module."""

import unittest
import io

from .. import parser
from .. import constants
from .. import gamedata
from .. import game
from .. import game_strict_pgn
from .. import game_text_pgn
from .. import game_ignore_case_pgn


class _BasePGN(unittest.TestCase):
    """Provide PGN parser using GameStrictPGN and get() to read PGN text.

    Subclasses override setUp() to use alternatives to GameStrictPGN.

    """

    def setUp(self):
        self.pgn = parser.PGN(game_class=game_strict_pgn.GameStrictPGN)

    def tearDown(self):
        del self.pgn

    def get(self, s):
        """Return sequence of Game instances derived from s."""
        return [g for g in self.pgn.read_games(io.StringIO(s))]

    def b_is_bishop_or_b_pawn(self, fen, string, tokens, state):
        """Run subTest where side does not matter."""
        ae = self.assertEqual
        with self.subTest(string=string, tokens=tokens, state=state):
            games = self.get("".join((['[SetUp"1"]', fen, string])))
            ae(len(games), 1)
            ae(games[0]._text, ['[SetUp"1"]', fen] + tokens)
            ae(games[0].state, state)


class StrictPGN(_BasePGN):
    """Provide tests for GameStrictPGN version of parser.

    Subclasses overrride specific tests where the outcome is different.

    If a subclass defines an extra test it should be added here too if the
    outcome is different, or defined here instead if the outcome is the same.

    """

    def test_001_null_string(self):
        ae = self.assertEqual
        games = self.get("")
        ae(len(games), 0)

    # _NonStrictText version gives no games.
    def test_002_a_character(self):
        ae = self.assertEqual
        games = self.get("A")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" A"])

    # _NonStrictText version gives no games.
    def test_003_a_word(self):
        ae = self.assertEqual
        games = self.get("abcdef123")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" abcdef123"])

    # _NonStrictText version gives no games.
    def test_004_a_sentence(self):
        ae = self.assertEqual
        games = self.get("The cat sat on the mat")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(
            games[0]._text,
            [" The ", " cat ", " sat ", " on ", " the ", " mat"],
        )

    def test_005_bare_star(self):
        ae = self.assertEqual
        games = self.get("*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ["*"])

    def test_006_bare_tag(self):
        ae = self.assertEqual
        games = self.get('[A"a"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]'])

    def test_007_bare_tag(self):
        ae = self.assertEqual
        games = self.get('[A "a"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]'])

    def test_008_tag_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "*"])

    def test_008_01_tag_escaped_quotes_and_star(self):
        ae = self.assertEqual
        games = self.get(r'[A"a\""]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, [r'[A"a\""]', "*"])
        ae(games[0]._tags, {"A": r"a\""})

    def test_008_02_tag_escaped_backslash_and_star(self):
        ae = self.assertEqual
        games = self.get(r'[A"a\\"]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, [r'[A"a\\"]', "*"])
        ae(games[0]._tags, {"A": r"a\\"})

    def test_008_03_tag_right_bracket_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a]"]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a]"]', "*"])
        ae(games[0]._tags, {"A": "a]"})

    def test_008_04_tag_left_bracket_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a["]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a["]', "*"])
        ae(games[0]._tags, {"A": "a["})

    # _NonStrictText ignores semicolon and text after.
    def test_008_05_tag_and_semicolon_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"];*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " ;*"])

    # _NonStrictText ignores percent and text after.
    def test_008_06_tag_and_percent_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " %*"])

    def test_009_tag_and_star(self):
        ae = self.assertEqual
        games = self.get('[A "a"]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "*"])

    # Added len(pgntext) test in parser.PGN.read_games to pass this test.
    def test_010_bare_legal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get("e3")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e3"])

    # Added to identify scope of len(pgntext) test in parser.PGN.read_games.
    def test_010_1_bare_legal_move_sequence_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get("e3e6")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e3", "e6"])

    # Added to identify scope of len(pgntext) test in parser.PGN.read_games.
    def test_010_2_bare_legal_move_and_tag_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('e3[A "a"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e3", ' [A "a"]'])

    def test_011_bare_illegal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get("e6")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" e6"])

    def test_012_legal_move_in_default_initial_position_and_star(self):
        ae = self.assertEqual
        games = self.get("e3*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ["e3", "*"])

    def test_013_illegal_move_in_default_initial_position_and_star(self):
        ae = self.assertEqual
        games = self.get("e6*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" e6", " *"])

    def test_014_tag_and_legal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e3')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', "e3"])

    def test_015_tag_and_illegal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e6')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " e6"])

    def test_016_tag_and_legal_move_in_default_initial_position_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e3", "*"])

    def test_017_tag_and_illegal_move_in_default_initial_position_and_star(
        self,
    ):
        ae = self.assertEqual
        games = self.get('[A"a"]e6*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " e6", " *"])

    def test_018_legal_game_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]**')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "*"])
        ae(games[1]._state, None)
        ae(games[1]._text, ["*"])

    def test_019_legal_game_and_star_and_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]**[B"b"]1-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "*"])
        ae(games[1]._state, None)
        ae(games[1]._text, ["*"])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', "1-0"])

    def test_020_legal_game_and_star_and_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4**[B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1]._state, None)
        ae(games[1]._text, ["*"])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', "d4", "1-0"])

    # _NonStrictText version gives just games[0].
    def test_021_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"]d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff[B"b"]d41-0'])

    # _NonStrictText version gives two games.
    # games[1].state is None and 'ff[B"b"]' token is lost.
    def test_022_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff[B"b"] ', " d4", " 1-0"])

    # _NonStrictText version gives two games.
    # games[1].state is None and 'ff[B"b"]' token is lost.
    def test_023_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] 1. d4 1-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff[B"b"] ', " 1", ".", " d4", " 1-0"])

    # _NonStrictText version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    def test_024_legal_game_gash_space_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff [B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, 0)
        ae(games[1]._text, [" ff "])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', "d4", "1-0"])

    # _NonStrictText version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    def test_025_legal_game_gash_newline_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff\n[B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, 0)
        ae(games[1]._text, [" ff"])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', "d4", "1-0"])

    # _NonStrictText version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    def test_026_legal_game_gash_space_newline_legal_game_both_with_moves(
        self,
    ):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff \n[B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, 0)
        ae(games[1]._text, [" ff "])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', "d4", "1-0"])

    # This one, with realistic tags and movetext, occurs in a TWIC file.
    def test_027_legal_game_and_star_and_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"] 1. e4 * * [B"b"] 1. d4 1-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1]._state, None)
        ae(games[1]._text, ["*"])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', "d4", "1-0"])

    # _NonStrictText version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    # This one, with realistic tags and movetext, occurs in a TWIC file.
    def test_028_legal_game_and_gash_and_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]1. e4 1-0 ff [B"b"] 1. d4 1-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "1-0"])
        ae(games[1].state, 0)
        ae(games[1]._text, [" ff "])
        ae(games[0].state, None)
        ae(games[2]._text, ['[B"b"]', "d4", "1-0"])

    def test_029_bare_move_number(self):
        ae = self.assertEqual
        games = self.get("12")
        ae(len(games), 0)

    def test_029_01_move_number_and_star(self):
        ae = self.assertEqual
        games = self.get("12*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ["*"])

    def test_030_bare_dot(self):
        ae = self.assertEqual
        games = self.get(".")
        ae(len(games), 0)

    def test_030_01_dot_and_star(self):
        ae = self.assertEqual
        games = self.get(".*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ["*"])

    def test_031_bare_move_numbers_and_dots(self):
        ae = self.assertEqual
        games = self.get("12. ... 13. 14 11. ... 50. 51. 3.")
        ae(len(games), 0)

    def test_032_legal_game_with_move_numbers_and_dots(self):
        ae = self.assertEqual
        games = self.get(
            '[A"a"] 1. e4 12. ... 13. d5 14 11. ... 50 . 51 3. 1-0'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "d5", "1-0"])

    def test_033_illegal_game_with_move_numbers_and_dots(self):
        ae = self.assertEqual
        games = self.get(
            '[A"a"] 1. e4 12. ... 13. d4 14 11. ... 50 . 51 3. 1-0'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[A"a"]',
                "e4",
                " d4",
                " 14",
                " 11",
                ".",
                "...",
                " 50",
                ".",
                " 51",
                " 3",
                ".",
                " 1-0",
            ],
        )

    def test_034_legal_game_move_numbers_and_dots_newline_not_space(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    '[A"a"]\n1.\ne4\n12.\n...\n13.\nd5\n14',
                    "\n11.\n...\n50\n.\n51\n3.\n1-0",
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "d5", "1-0"])

    def test_035_illegal_game_move_numbers_and_dots_newline_not_space(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    '[A"a"]\n1.\ne4\n12.\n...\n13.\nd4\n14',
                    "\n11.\n...\n50\n.\n51\n3.\n1-0",
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[A"a"]',
                "e4",
                " d4",
                " 14",
                " 11",
                ".",
                "...",
                " 50",
                ".",
                " 51",
                " 3",
                ".",
                " 1-0",
            ],
        )

    def test_036_illegal_game_and_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"] 1. e4 d4 2. e5 0-1 [B"b"] 1. d4 d5 1-0')
        ae(len(games), 2)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', "e4", " d4", " 2", ".", " e5", " 0-1"])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', "d4", "d5", "1-0"])

    def test_037_illegal_game_and_legal_game_with_newline_not_space(self):
        ae = self.assertEqual
        games = self.get(
            '[A"a"]\n1.\ne4\nd4\n2.\ne5\n0-1\n[B"b"]\n1.\nd4\nd5\n1-0'
        )
        ae(len(games), 2)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', "e4", " d4", " 2", ".", " e5", " 0-1"])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', "d4", "d5", "1-0"])

    def test_038_bare_eol_comment(self):
        ae = self.assertEqual
        games = self.get(";c\n")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, [";c\n"])

    def test_039_tag_and_eol_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"];c\n')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', ";c\n"])

    def test_040_tag_and_eol_comment_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"];c\n*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', ";c\n", "*"])

    def test_041_tag_and_eol_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"];c{c}<r>e4(d4)[B"b"]%e\n*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', ';c{c}<r>e4(d4)[B"b"]%e\n', "*"])

    def test_042_bare_comment(self):
        ae = self.assertEqual
        games = self.get("{C}")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["{C}"])

    def test_043_tag_and_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C}')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', "{C}"])

    def test_044_tag_and_comment_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "{C}", "*"])

    def test_045_tag_and_comment_with_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{Cx\ny}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "{Cx\ny}", "*"])

    def test_046_tag_and_move_comment_with_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]c4{Cx\ny}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "c4", "{Cx\ny}", "*"])

    def test_047_tag_and_comment_wrapping_eol_comment_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{Cx;x\ny}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "{Cx;x\ny}", "*"])

    def test_048_tag_and_move_comment_wrapping_eol_comment_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]c4{Cx;x\ny}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "c4", "{Cx;x\ny}", "*"])

    def test_049_tag_and_comment_wrapping_escape_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{Cx\n%yy}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "{Cx\n%yy}", "*"])

    def test_050_tag_and_move_comment_wrapping_escape_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]c4{Cx\n%yy}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "c4", "{Cx\n%yy}", "*"])

    def test_051_tag_and_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"]%e\n}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '{C;c\n<r>e4(d4)[B"b"]%e\n}', "*"])

    # _NonStrictText version gives error too.
    def test_051_1_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' {C;c\n<r>e4(d4)[B"b"'])

    # _NonStrictText version gives error too.
    def test_051_2_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' {C;c\n<r>e4(d4)[B"b"]'])

    def test_052_tag_and_comment_wrapping_tokens_no_tag_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)%e\n}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "{C;c\n<r>e4(d4)%e\n}", "*"])

    def test_053_bare_numeric_annotation_glyph(self):
        ae = self.assertEqual
        games = self.get("$32")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["$32"])

    def test_054_tag_and_numeric_annotation_glyph(self):
        ae = self.assertEqual
        games = self.get('[A"a"]$32')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', "$32"])

    def test_055_tag_and_numeric_annotation_glyph_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]$32*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "$32", "*"])

    def test_056_bare_reserved(self):
        ae = self.assertEqual
        games = self.get("<r>")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["<r>"])

    def test_057_tag_and_reserved(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r>')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', "<r>"])

    def test_058_tag_and_reserved_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "<r>", "*"])

    def test_059_tag_and_reserved_with_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<rd\ne>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "<rd\ne>", "*"])

    def test_060_tag_and_move_reserved_with_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3<rd\ne>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "Nf3", "<rd\ne>", "*"])

    def test_061_tag_and_reserved_wrapping_escape_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<rx\n%yy>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "<rx\n%yy>", "*"])

    def test_062_tag_and_move_reserved_wrapping_escape_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]c4<rx\n%yy>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "c4", "<rx\n%yy>", "*"])

    def test_063_tag_and_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"]%e\n>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '<r;c\n{C}e4(d4)[B"b"]%e\n>', "*"])

    # _NonStrictText version gives error too.
    def test_063_1_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' <r;c\n{C}e4(d4)[B"b"'])

    # _NonStrictText version gives error too.
    def test_063_2_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' <r;c\n{C}e4(d4)[B"b"]'])

    def test_064_tag_and_reserved_wrapping_tokens_no_tag_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)%e\n>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "<r;c\n{C}e4(d4)%e\n>", "*"])

    # _NonStrictText version gives error without captured text.
    def test_065_bare_escaped(self):
        ae = self.assertEqual
        games = self.get("%Run for your life!")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" %Run ", " for ", " your ", " life!"])

    # _NonStrictText version gives error without captured text.
    def test_065_01_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get("%Run for your life!*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" %Run ", " for ", " your ", " life!*"])

    def test_065_02_escaped_and_newline(self):
        ae = self.assertEqual
        games = self.get("%Run for your life!\n")
        ae(len(games), 0)

    def test_065_03_escaped_and_newline_and_star(self):
        ae = self.assertEqual
        games = self.get("%Run for your life!\n*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ["*"])

    # _NonStrictText version gives error too, but '%!' token is lost.
    def test_066_tag_and_escaped(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " %!"])

    # _NonStrictText version gives error too, but '%!*' token is lost.
    def test_067_tag_and_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " %!*"])

    # _NonStrictText version gives one game, having lost the '%!\n' token.
    def test_068_tag_and_terminated_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!\n*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " %!", " *"])

    # _NonStrictText version gives one game, having lost the
    # '%!{C}<r>e4(d4)[B"b"]%e' token.
    def test_069_tag_and_terminated_escaped_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!{C}<r>e4(d4)[B"b"]%e\n*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' %!{C}<r>e4(d4)[B"b"]%e', " *"])

    def test_070_castles_O_O_and_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-OKe7*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]',
                "O-O",
                "Ke7",
                "*",
            ],
        )

    def test_071_castles_O_O_O_and_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-O-OKe7*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]',
                "O-O-O",
                "Ke7",
                "*",
            ],
        )

    # _NonStrictText version gives error too, but '-' token is lost.
    def test_072_castles_O_O_incomplete_0(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-O-'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]',
                "O-O",
                " -",
            ],
        )

    def test_073_castles_O_O_O(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-O-O'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]', "O-O-O"],
        )

    def test_074_bare_rav_start(self):
        ae = self.assertEqual
        games = self.get("(")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" ("])

    def test_075_bare_rav_end(self):
        ae = self.assertEqual
        games = self.get(")")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" )"])

    def test_076_bare_rav(self):
        ae = self.assertEqual
        games = self.get("()")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " )"])

    def test_077_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get("(*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " *"])

    def test_078_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get(")*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" )", " *"])

    def test_079_rav_and_star(self):
        ae = self.assertEqual
        games = self.get("()*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " )", " *"])

    def test_080_tag_and_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"](*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " (", " *"])

    def test_081_tag_and_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"])*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " )", " *"])

    def test_082_tag_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]()*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', " (", " )", " *"])

    def test_083_tag_and_move_and_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 2)
        ae(games[0].state, 4)
        ae(games[0]._text, ['[A"a"]', "Nf3", "(", "*"])

    def test_084_tag_and_move_and_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', "Nf3", " )", " *"])

    def test_085_tag_and_move_and_empty_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3()*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "Nf3", "(", ")", "*"])

    def test_086_move_and_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 2)
        ae(games[0].state, 3)
        ae(games[0]._text, ["Nf3", "(", "*"])

    def test_087_move_and_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["Nf3", " )", " *"])

    def test_088_move_and_empty_rav_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3()*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ["Nf3", "(", ")", "*"])

    def test_089_tag_and_move_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "Nf3", "(", "Nc3", ")", "*"])

    def test_090_move_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(Nc3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ["Nf3", "(", "Nc3", ")", "*"])

    def test_091_tag_and_move_and_sequential_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3)(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            ['[A"a"]', "Nf3", "(", "Nc3", ")", "(", "a3", ")", "*"],
        )

    def test_092_move_and_sequential_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(Nc3)(a3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ["Nf3", "(", "Nc3", ")", "(", "a3", ")", "*"])

    def test_093_tag_and_move_and_separated_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3)Nf6g3(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[A"a"]',
                "Nf3",
                "(",
                "Nc3",
                ")",
                "Nf6",
                "g3",
                "(",
                "a3",
                ")",
                "*",
            ],
        )

    def test_094_move_and_separated_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(Nc3)Nf6g3(a3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            ["Nf3", "(", "Nc3", ")", "Nf6", "g3", "(", "a3", ")", "*"],
        )

    def test_095_tag_and_move_and_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3(a3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            ['[A"a"]', "Nf3", "(", "Nc3", "(", "a3", ")", ")", "*"],
        )

    def test_096_move_and_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(Nc3(a3))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ["Nf3", "(", "Nc3", "(", "a3", ")", ")", "*"])

    def test_097_tag_and_move_and_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3((Nc3)a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            ['[A"a"]', "Nf3", "(", "(", "Nc3", ")", "a3", ")", "*"],
        )

    def test_098_move_and_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3((Nc3)a3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ["Nf3", "(", "(", "Nc3", ")", "a3", ")", "*"])

    def test_099_comment_tag_and_move_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3{a}({b}Nc3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            ['[A"a"]', "Nf3", "{a}", "(", "{b}", "Nc3", ")", "*"],
        )

    def test_100_comment_move_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3{a}({b}Nc3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ["Nf3", "{a}", "(", "{b}", "Nc3", ")", "*"])

    def test_101_comment_tag_and_move_and_sequential_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3{a}({b}Nc3){a}({b}a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[A"a"]',
                "Nf3",
                "{a}",
                "(",
                "{b}",
                "Nc3",
                ")",
                "{a}",
                "(",
                "{b}",
                "a3",
                ")",
                "*",
            ],
        )

    def test_102_comment_move_and_sequential_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3{a}({b}Nc3){a}({b}a3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "Nf3",
                "{a}",
                "(",
                "{b}",
                "Nc3",
                ")",
                "{a}",
                "(",
                "{b}",
                "a3",
                ")",
                "*",
            ],
        )

    def test_103_comment_tag_and_move_and_separated_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3{a}({b}Nc3)Nf6g3(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[A"a"]',
                "Nf3",
                "{a}",
                "(",
                "{b}",
                "Nc3",
                ")",
                "Nf6",
                "g3",
                "(",
                "a3",
                ")",
                "*",
            ],
        )

    def test_104_comment_move_and_separated_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3{a}({b}Nc3)Nf6g3(a3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "Nf3",
                "{a}",
                "(",
                "{b}",
                "Nc3",
                ")",
                "Nf6",
                "g3",
                "(",
                "a3",
                ")",
                "*",
            ],
        )

    def test_105_comment_tag_and_move_and_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3(a3{a}){b}{a}){b}*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[A"a"]',
                "Nf3",
                "(",
                "Nc3",
                "(",
                "a3",
                "{a}",
                ")",
                "{b}",
                "{a}",
                ")",
                "{b}",
                "*",
            ],
        )

    def test_106_comment_move_and_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(Nc3(a3{a}){b}{a}){b}*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "Nf3",
                "(",
                "Nc3",
                "(",
                "a3",
                "{a}",
                ")",
                "{b}",
                "{a}",
                ")",
                "{b}",
                "*",
            ],
        )

    def test_107_comment_tag_and_move_and_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3{a}({b}{a}({b}Nc3)a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[A"a"]',
                "Nf3",
                "{a}",
                "(",
                "{b}",
                "{a}",
                "(",
                "{b}",
                "Nc3",
                ")",
                "a3",
                ")",
                "*",
            ],
        )

    def test_108_comment_move_and_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3{a}({b}{a}({b}Nc3)a3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "Nf3",
                "{a}",
                "(",
                "{b}",
                "{a}",
                "(",
                "{b}",
                "Nc3",
                ")",
                "a3",
                ")",
                "*",
            ],
        )

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_109_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "{1/2-1/2}", "*"])

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_110_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{\n1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "{\n1/2-1/2}", "*"])

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_111_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "(", "d4", "{1/2-1/2}", ")", "*"])

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_112_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{\n1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            ['[A"a"]', "e4", "(", "d4", "{\n1/2-1/2}", ")", "*"],
        )

    # Added on seeing results when crash traced to game in crafty06_03.pgn.
    # Non-strict version accepts c4c5 as long algebraic notation for c5.
    def test_113_start_rav_after_moves_after_nags(self):
        ae = self.assertEqual
        games = self.get("$10$21$10$22c4e5c4c5(()")
        ae(len(games), 1)
        ae(games[0].state, 6)
        ae(
            games[0]._text,
            [
                "$10",
                "$21",
                "$10",
                "$22",
                "c4",
                "e5",
                " c4",
                " c5",
                " (",
                " (",
                " )",
            ],
        )

    # Added after changes to convertion of chess engine responses to PGN.
    def test_114_long_algebraic_pawn_move_wrong_direction(self):
        ae = self.assertEqual
        games = self.get("e4e5e4e3")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " e4", " e3"])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_115_long_algebraic_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e7e5")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " e7", " e5"])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_116_long_algebraic_pawn_move_game_terminated(self):
        ae = self.assertEqual
        games = self.get("e4e7e5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " e7", " e5", " *"])

    def test_117_01_bxc4(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"8/8/7k/8/2r5/1P6/8/4K3 w - - 0 1"]bxc4*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"8/8/7k/8/2r5/1P6/8/4K3 w - - 0 1"]',
                "bxc4",
                "*",
            ],
        )

    def test_117_02_dxc4(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"8/8/7k/8/2r5/3P4/8/4K3 w - - 0 1"]dxc4*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"8/8/7k/8/2r5/3P4/8/4K3 w - - 0 1"]',
                "dxc4",
                "*",
            ],
        )

    def test_118_01_BxC4_without_B_on_board(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/8/8/2p5/1P6/8/6K1 w - - 0 1"]BxC4*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"6k1/8/8/8/2p5/1P6/8/6K1 w - - 0 1"]',
                " BxC4*",
            ],
        )

    def test_118_02_BxC4_with_B_on_board(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/8/8/2p5/1P6/1B6/6K1 w - - 0 1"]BxC4*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"6k1/8/8/8/2p5/1P6/1B6/6K1 w - - 0 1"]',
                " BxC4*",
            ],
        )

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_01_b8_Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"8/1P5k/8/8/8/8/1p5K/8 w - - 0 1"]b8=Q*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"8/1P5k/8/8/8/8/1p5K/8 w - - 0 1"]',
                "b8=Q",
                "*",
            ],
        )

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_02_b1_Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"8/1P5k/8/8/8/8/1p5K/8 b - - 0 1"]b1=Q*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"8/1P5k/8/8/8/8/1p5K/8 b - - 0 1"]',
                "b1=Q",
                "*",
            ],
        )

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_03_bcd_Q(self):
        fen = ['[FEN"r1n1n2k/1PBP4/8/7B/7b/8/1pbp4/R1N1N2K ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("bxa8=Q*", ["bxa8=Q", "*"], None, "w"),
            ("b8=Q*", ["b8=Q", "*"], None, "w"),
            ("bxc8=Q*", ["bxc8=Q", "*"], None, "w"),
            ("dxc8=Q*", ["dxc8=Q", "*"], None, "w"),
            ("d8=Q*", ["d8=Q", "*"], None, "w"),
            ("dxe8=Q*", ["dxe8=Q", "*"], None, "w"),
            ("bxa1=Q*", ["bxa1=Q", "*"], None, "b"),
            ("b1=Q*", ["b1=Q", "*"], None, "b"),
            ("bxc1=Q*", ["bxc1=Q", "*"], None, "b"),
            ("dxc1=Q*", ["dxc1=Q", "*"], None, "b"),
            ("d1=Q*", ["d1=Q", "*"], None, "b"),
            ("dxe1=Q*", ["dxe1=Q", "*"], None, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_04_bcd_bishop(self):
        fen = ['[FEN"r1n1n2k/1BB5/8/7B/7b/8/1bb5/R1N1N2K ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("Bxa8*", ["Bxa8", "*"], None, "w"),
            ("Bb8*", ["Bb8", "*"], None, "w"),
            ("Bxc8*", ["Bxc8", "*"], None, "w"),
            ("Bd8*", ["Bd8", "*"], None, "w"),
            ("Bxe8*", ["Bxe8", "*"], None, "w"),
            ("Bxa1*", ["Bxa1", "*"], None, "b"),
            ("Bb1*", ["Bb1", "*"], None, "b"),
            ("Bxc1*", ["Bxc1", "*"], None, "b"),
            ("Bd1*", ["Bd1", "*"], None, "b"),
            ("Bxe1*", ["Bxe1", "*"], None, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_05_bcd_bishop(self):
        fen = ['[FEN"r1n1n2k/2B5/2B4b/8/8/2b4B/2b5/R1N1N2K ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("Bxa8*", ["Bxa8", "*"], None, "w"),
            ("Bb8*", ["Bb8", "*"], None, "w"),
            ("Bxc8*", ["Bxc8", "*"], None, "w"),
            ("Bd8*", ["Bd8", "*"], None, "w"),
            ("Bxe8*", ["Bxe8", "*"], None, "w"),
            ("Bxa1*", ["Bxa1", "*"], None, "b"),
            ("Bb1*", ["Bb1", "*"], None, "b"),
            ("Bxc1*", ["Bxc1", "*"], None, "b"),
            ("Bd1*", ["Bd1", "*"], None, "b"),
            ("Bxe1*", ["Bxe1", "*"], None, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_06_bcd_bishop(self):
        fen = ['[FEN"r1n1n2k/2B5/2B4b/8/8/2b4B/2b5/R1N1N2K ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("bxa8*", [" bxa8*"], 2, "w"),
            ("bb8*", [" bb8*"], 2, "w"),
            ("bxc8*", [" bxc8*"], 2, "w"),
            ("bd8*", [" bd8*"], 2, "w"),
            ("bxe8*", [" bxe8*"], 2, "w"),
            ("bxa1*", [" bxa1*"], 2, "b"),
            ("bb1*", [" bb1*"], 2, "b"),
            ("bxc1*", [" bxc1*"], 2, "b"),
            ("bd1*", [" bd1*"], 2, "b"),
            ("bxe1*", [" bxe1*"], 2, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_07_bcd_bishop(self):
        fen = ['[FEN"r1n1n2k/2B5/2B4b/8/8/2b4B/2b5/R1N1N2K ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("b6xa8*", [" b6", " xa8", " *"], 2, "w"),
            ("b7b8*", [" b7", " b8", " *"], 2, "w"),
            ("b3xc8*", [" b3", " xc8", " *"], 2, "w"),
            ("b7d8*", [" b7", " d8", " *"], 2, "w"),
            ("b6xe8*", [" b6", " xe8", " *"], 2, "w"),
            ("b3xa1*", [" b3", " xa1", " *"], 2, "b"),
            ("b2b1*", [" b2", " b1", " *"], 2, "b"),
            ("b6xc1*", [" b6", " xc1", " *"], 2, "b"),
            ("b2d1*", [" b2", " d1", " *"], 2, "b"),
            ("b3xe1*", [" b3", " xe1", " *"], 2, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_08_bcd_bishop(self):
        fen = ['[FEN"8/r1n1n2k/2B3b1/2B5/2b5/2b3B1/R1N1N2K/8 ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("bxa7*", [" bxa7", " *"], 2, "w"),
            ("bb7*", [" bb7*"], 2, "w"),
            ("bxc7*", [" bxc7", " *"], 2, "w"),
            ("bd7*", [" bd7*"], 2, "w"),
            ("bxe7*", [" bxe7", " *"], 2, "w"),
            ("bxa2*", [" bxa2", " *"], 2, "b"),
            ("bb2*", [" bb2*"], 2, "b"),
            ("bxc2*", [" bxc2", " *"], 2, "b"),
            ("bd2*", [" bd2*"], 2, "b"),
            ("bxe2*", [" bxe2", " *"], 2, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_09_bcd_bishop(self):
        fen = ['[FEN"8/r1n1n2k/2B3b1/2B5/2b5/2b3B1/R1N1N2K/8 ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("b5xa7*", [" b5", " xa7", " *"], 2, "w"),
            ("b6b7*", [" b6", " b7", " *"], 2, "w"),
            ("b4xc7*", [" b4", " xc7", " *"], 2, "w"),
            ("b6d7*", [" b6", " d7", " *"], 2, "w"),
            ("b5xe7*", [" b5", " xe7", " *"], 2, "w"),
            ("b4xa2*", [" b4", " xa2", " *"], 2, "b"),
            ("b3b2*", [" b3", " b2", " *"], 2, "b"),
            ("b5xc2*", [" b5", " xc2", " *"], 2, "b"),
            ("b3d2*", [" b3", " d2", " *"], 2, "b"),
            ("b4xe2*", [" b4", " xe2", " *"], 2, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # Tests *_118_* through *_122_* renumbered making room for new *_119_*.
    def test_120_01_dxc8_Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/8/8/8/8/4K3 w - - 0 1"]dxc8=Q*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/3P4/7k/8/8/8/8/4K3 w - - 0 1"]',
                "dxc8=Q",
                "*",
            ],
        )

    def test_120_02_bxc8_Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/8/8/8/8/4K3 w - - 0 1"]bxc8=Q*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/8/8/8/8/4K3 w - - 0 1"]',
                "bxc8=Q",
                "*",
            ],
        )

    def test_120_03_bxc8_Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=Qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "bxc8=Q",
                " qg3*",
            ],
        )

    def test_120_04_bxc8Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8Qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8Qqg3*",
            ],
        )

    # Compare with test_163_bxc8q.
    def test_120_05_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8qqg3*",
            ],
        )

    def test_120_06_bxc8_q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8=qqg3*",
            ],
        )

    def test_120_07_bxc8_qx(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=q qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8=q ",
                " qg3*",
            ],
        )

    # '*_121_*' tests added for error in pgn_files test '055' for version 2.1.
    def test_121_01_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("((")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " ("])

    def test_121_02_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("(((")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " (", " ("])

    def test_121_03_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("(zz(")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " zz("])

    def test_121_04_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("(<>(")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " <>", " ("])

    def test_121_05_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("()(")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " )", " ("])

    def test_121_06_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("(2729)(")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " 2729", " )", " ("])

    def test_121_07_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("(2729) - Svidler,P (")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" (", " 2729", " )", " - ", " Svidler,P ", " ("])

    def test_121_08_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("(263,500 USD)! (2729) - Svidler,P (")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(
            games[0]._text,
            [
                " (",
                " 263",
                " ,500 ",
                " USD)! ",
                " (",
                " 2729",
                " )",
                " - ",
                " Svidler,P ",
                " (",
            ],
        )

    # The significant tokens from pgn_files test_055 which caused an exception
    # in the 'text' classes.
    def test_121_09_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("c4(263,500 USD)! (2729) - Svidler,P (")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                "c4",
                "(",
                " ,500 ",
                " USD)! ",
                " (",
                " 2729",
                " )",
                " - ",
                " Svidler,P ",
                " (",
            ],
        )

    # Changed while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_162_dxc8q.
    def test_123_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " dxc8qqg3*",
            ],
        )

    def test_124_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " dxc8=qqg3*",
            ],
        )

    def test_125_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8qg3*",
            ],
        )

    def test_126_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8 ",
                " qg3*",
            ],
        )

    def test_127_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
                " qg3*",
            ],
        )

    def test_128_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
                " qg3*",
            ],
        )

    def test_129_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8qg3*",
            ],
        )

    def test_130_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8 ",
                " qg3*",
            ],
        )

    def test_131_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{a1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "{a1/2-1/2}", "*"])

    def test_132_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{a\n1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "{a\n1/2-1/2}", "*"])

    def test_133_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{a1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "(", "d4", "{a1/2-1/2}", ")", "*"])

    def test_134_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{a\n1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            ['[A"a"]', "e4", "(", "d4", "{a\n1/2-1/2}", ")", "*"],
        )

    def test_135_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{a\t1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            ['[A"a"]', "e4", "(", "d4", "{a\t1/2-1/2}", ")", "*"],
        )

    def test_136_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{a 1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            ['[A"a"]', "e4", "(", "d4", "{a 1/2-1/2}", ")", "*"],
        )

    def test_140_partial_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A"a')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' [A"a'])

    def test_141_bad_value_in_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A:"a" ]')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['{::Bad Tag::[A:"a" ]::Bad Tag::}'])

    def test_141_bad_value_in_tag_02(self):
        ae = self.assertEqual
        games = self.get('[A:"\na" ]')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['{::Bad Tag::[A:"\na" ]::Bad Tag::}'])

    def test_142_bad_value_in_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A""a" ]')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['{::Bad Tag::[A""a" ]::Bad Tag::}'])

    def test_143_bad_value_in_tag_02(self):
        ae = self.assertEqual
        games = self.get('[A""a"][B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['{::Bad Tag::[A""a"]::Bad Tag::}', ' [B"b"]'])

    def test_144_bad_value_in_tag_03(self):
        ae = self.assertEqual
        games = self.get(r'[A"\a" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"\\a"]'])

    def test_145_bad_value_in_tag_04(self):
        ae = self.assertEqual
        games = self.get(r'[A"\"a" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"\\"a"]'])

    # Added while fixing problem.
    def test_146_castles_O_O_g1_occupied(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/RN2K1NR w KQ - 0 1"]O-OKe7*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"4k3/8/8/8/8/8/8/RN2K1NR w KQ - 0 1"]',
                " O-O",
                " Ke7",
                " *",
            ],
        )

    # Added while fixing problem.
    def test_147_castles_O_O_O_b1_occupied(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/RN2K1NR w KQ - 0 1"]O-O-OKe7*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"4k3/8/8/8/8/8/8/RN2K1NR w KQ - 0 1"]',
                " O-O-O",
                " Ke7",
                " *",
            ],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_148_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3((Nc3)a3(e3))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            ["Nf3", "(", "(", "Nc3", ")", "a3", "(", "e3", ")", ")", "*"],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_149_move_and_double_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(((e3)Nc3)a3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            ["Nf3", "(", "(", "(", "e3", ")", "Nc3", ")", "a3", ")", "*"],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_150_move_and_triple_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3((((g3)e3)Nc3)a3)*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "Nf3",
                "(",
                "(",
                "(",
                "(",
                "g3",
                ")",
                "e3",
                ")",
                "Nc3",
                ")",
                "a3",
                ")",
                "*",
            ],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_151_move_and_double_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(Nc3(a3(g3)))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            ["Nf3", "(", "Nc3", "(", "a3", "(", "g3", ")", ")", ")", "*"],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_152_move_and_triple_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3(Nc3(a3(g3(e3))))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "Nf3",
                "(",
                "Nc3",
                "(",
                "a3",
                "(",
                "g3",
                "(",
                "e3",
                ")",
                ")",
                ")",
                ")",
                "*",
            ],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_153_move_and_left_nested_move_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("Nf3((Nc3)a3)e6(c6(d6))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "Nf3",
                "(",
                "(",
                "Nc3",
                ")",
                "a3",
                ")",
                "e6",
                "(",
                "c6",
                "(",
                "d6",
                ")",
                ")",
                "*",
            ],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    # See version for GameIgnoreCasePGN, and test_155_* and test_156_* below
    # which change b4 or b5 to h4 or h5.
    def test_154_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("b4b5Nf3((Nc3)a3(e3))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "b4",
                "b5",
                "Nf3",
                "(",
                "(",
                "Nc3",
                ")",
                "a3",
                "(",
                "e3",
                ")",
                ")",
                "*",
            ],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_155_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("h4b5Nf3((Nc3)a3(e3))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "h4",
                "b5",
                "Nf3",
                "(",
                "(",
                "Nc3",
                ")",
                "a3",
                "(",
                "e3",
                ")",
                ")",
                "*",
            ],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_156_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("b4h5Nf3((Nc3)a3(e3))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "b4",
                "h5",
                "Nf3",
                "(",
                "(",
                "Nc3",
                ")",
                "a3",
                "(",
                "e3",
                ")",
                ")",
                "*",
            ],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # The first 'b', in 'bb5', caused an error when lower case allowed.
    def test_157_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get("e4e5nf3nc6bb5a6*")
        ae(len(games), 1)
        ae(games[0]._state, 2)
        ae(games[0]._text, ["e4", "e5", " nf3nc6bb5a6*"])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # The first 'b', in 'bb4', caused an error when lower case allowed.
    def test_158_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get("e4c5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6*")
        ae(len(games), 1)
        ae(games[0]._state, 4)
        ae(
            games[0]._text,
            ["e4", "c5", "d4", "e6", " nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6*"],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # The first 'b', in 'bb5', caused an error when lower case allowed.
    def test_159_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get("e4e5nf3nc6Bb5a6*")
        ae(len(games), 1)
        ae(games[0]._state, 2)
        ae(games[0]._text, ["e4", "e5", " nf3nc6Bb5a6*"])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # The first 'b', in 'bb4', caused an error when lower case allowed.
    def test_160_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get("e4c5d4e6nf3cxd4nxd4a6nc3qc7g3Bb4Bd2nf6*")
        ae(len(games), 1)
        ae(games[0]._state, 4)
        ae(
            games[0]._text,
            ["e4", "c5", "d4", "e6", " nf3cxd4nxd4a6nc3qc7g3Bb4Bd2nf6*"],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_129_bxc8.
    def test_161_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8=qg3*",
            ],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_123_dxc8q.
    def test_162_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " dxc8=qqg3*",
            ],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_120_05_bxc8q.
    def test_163_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8=qqg3*",
            ],
        )

    # Added while fixing Little.pgn upper case processing.
    def test_164_long_algebraic_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5d2d4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " d2", " d4", " *"])

    # Added while fixing Little.pgn upper case processing.
    def test_165_long_algebraic_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5d2-d4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " d2", " -d4", " *"])

    # Added while fixing Little.pgn upper case processing.
    def test_166_01_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5b2b4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " b2", " b4", " *"])

    # Accepted as 'b7' in non-strict PGN and text classes.
    def test_166_02_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]b6b7*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]',
                " b6",
                " b7",
                " *",
            ],
        )
        ae(games[0].state, 2)

    # Rejected like this in all cases except 'ignore case', where it is seen
    # as an attempted bishop move from rank 7 to b8, 'B7b8'.
    def test_166_03_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]b7b8=Q*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]',
                " b7",
                " b8=Q",
                " *",
            ],
        )
        ae(games[0].state, 2)

    # Always rejected as an attempt to move a pawn from f6 to f7.
    def test_166_04_long_algebraic_white_f_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]f7f8=Q*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]',
                " f7",
                " f8=Q",
                " *",
            ],
        )
        ae(games[0].state, 2)

    # Added while fixing Little.pgn upper case processing.
    def test_167_01_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5b2-b4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " b2", " -b4", " *"])

    def test_167_02_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]b6-b7*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]',
                " b6",
                " -b7",
                " *",
            ],
        )
        ae(games[0].state, 2)

    def test_167_03_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]b7-b8=Q*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]',
                " b7",
                " -b8",
                " =Q*",
            ],
        )
        ae(games[0].state, 2)

    def test_167_04_long_algebraic_white_f_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]f7-f8=Q*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]',
                " f7",
                " -f8",
                " =Q*",
            ],
        )
        ae(games[0].state, 2)

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_168_long_algebraic_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e7e5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " e7", " e5", " *"])

    # Added while fixing Little.pgn upper case processing.
    def test_169_long_algebraic_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e7-e5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " e7", " -e5", " *"])

    # Added while fixing Little.pgn upper case processing.
    def test_170_long_algebraic_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4b7b5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " b7", " b5", " *"])

    # Added while fixing Little.pgn upper case processing.
    def test_171_long_algebraic_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4b7-b5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " b7", " -b5", " *"])

    # Added while fixing Little.pgn upper case processing.
    def test_172_long_algebraic_uc_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5D2D4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " D2D4*"])

    # Added while fixing Little.pgn upper case processing.
    def test_173_long_algebraic_uc_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5D2-D4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " D2-D4*"])

    # Added while fixing Little.pgn upper case processing.
    def test_174_long_algebraic_uc_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5B2B4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " B2B4*"])

    # Added while fixing Little.pgn upper case processing.
    def test_175_long_algebraic_uc_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5B2-B4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " B2-B4*"])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_176_long_algebraic_uc_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4E7E5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " E7E5*"])

    # Added while fixing Little.pgn upper case processing.
    def test_177_long_algebraic_uc_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4E7-E5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " E7-E5*"])

    # Added while fixing Little.pgn upper case processing.
    def test_178_long_algebraic_uc_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4B7B5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " B7B5*"])

    # Added while fixing Little.pgn upper case processing.
    def test_179_long_algebraic_uc_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4B7-B5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " B7-B5*"])

    def test_180_01_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("N1f3*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" N1f3", " *"])

    def test_180_02_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("Ngf3*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" Ngf3", " *"])

    def test_180_03_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("Ng1f3*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" Ng1", " f3", " *"])

    def test_180_04_long_algebraic(self):
        ae = self.assertEqual
        games = self.get("Ng1-f3*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" Ng1", " -f3", " *"])

    def test_181_01_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5B1d3*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " B1d3", " *"])

    def test_181_02_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5B1D3*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " B1D3*"])

    def test_181_03_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5b1D3*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " b1", " D3*"])

    def test_181_04_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5b1d3*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " b1", " d3", " *"])

    def test_182_01_pawn_capture_bc4_or_too_much_precision(self):
        fen = '[FEN"8/8/8/8/2bk4/1P6/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B3xc4*", [" B3xc4", " *"], 2),
            ("B3xC4*", [" B3xC4*"], 2),
            ("b3xc4*", [" b3", " xc4", " *"], 2),
            ("b3xC4*", [" b3", " xC4*"], 2),
            ("Bxc4*", [" Bxc4", " *"], 2),
            ("BxC4*", [" BxC4*"], 2),
            ("bxc4*", ["bxc4", "*"], None),
            ("bxC4*", [" bxC4*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_182_02_pawn_capture_bc4_or_too_much_precision(self):
        fen = '[FEN"8/8/8/8/2bk4/1B6/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B3xc4*", [" B3xc4", " *"], 2),
            ("B3xC4*", [" B3xC4*"], 2),
            ("b3xc4*", [" b3", " xc4", " *"], 2),
            ("b3xC4*", [" b3", " xC4*"], 2),
            ("Bxc4*", ["Bxc4", "*"], None),
            ("BxC4*", [" BxC4*"], 2),
            ("bxc4*", [" bxc4", " *"], 2),
            ("bxC4*", [" bxC4*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_01_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1P6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" B7xc8", " =Q*"], 2),
            ("B7xc8=q*", [" B7xc8", " =q*"], 2),
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", [" b7", " xc8", " =q*"], 2),
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", [" B7xc8", " Q*"], 2),
            ("B7xc8q*", [" B7xc8", " q*"], 2),
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", [" Bxc8", " =Q*"], 2),
            ("Bxc8=q*", [" Bxc8", " =q*"], 2),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", ["bxc8=Q", "*"], None),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", [" Bxc8", " Q*"], 2),
            ("Bxc8q*", [" Bxc8", " q*"], 2),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_02_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" B7xc8", " =Q*"], 2),
            ("B7xc8=q*", [" B7xc8", " =q*"], 2),
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", [" b7", " xc8", " =q*"], 2),
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", [" B7xc8", " Q*"], 2),
            ("B7xc8q*", [" B7xc8", " q*"], 2),
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", ["Bxc8", " =Q*"], 3),
            ("Bxc8=q*", ["Bxc8", " =q*"], 3),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", [" bxc8=Q", " *"], 2),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", ["Bxc8", " Q*"], 3),
            ("Bxc8q*", ["Bxc8", " q*"], 3),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_03_pawn_capture_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8*", [" B7xc8", " *"], 2),
            ("B7xC8*", [" B7xC8*"], 2),
            ("b7xc8*", [" b7", " xc8", " *"], 2),
            ("b7xC8*", [" b7", " xC8*"], 2),
            ("Bxc8*", ["Bxc8", "*"], None),
            ("BxC8*", [" BxC8*"], 2),
            ("bxc8*", [" bxc8*"], 2),
            ("bxC8*", [" bxC8*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_01_pawn_promotion_b8_or_too_much_precision(self):
        fen = '[FEN"3k4/1Pb5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8=Q*", [" B7b8", " =Q*"], 2),
            ("B7b8=q*", [" B7b8", " =q*"], 2),
            ("B7B8=Q*", [" B7B8=Q*"], 2),
            ("B7B8=q*", [" B7B8=q*"], 2),
            ("b7b8=Q*", [" b7", " b8=Q", " *"], 2),
            ("b7b8=q*", [" b7", " b8", " =q*"], 2),
            ("b7B8=Q*", [" b7", " B8=Q*"], 2),
            ("b7B8=q*", [" b7", " B8=q*"], 2),
            ("B7b8Q*", [" B7b8", " Q*"], 2),
            ("B7b8q*", [" B7b8", " q*"], 2),
            ("B7B8Q*", [" B7B8Q*"], 2),
            ("B7B8q*", [" B7B8q*"], 2),
            ("b7b8Q*", [" b7", " b8", " Q*"], 2),
            ("b7b8q*", [" b7", " b8", " q*"], 2),
            ("b7B8Q*", [" b7", " B8Q*"], 2),
            ("b7B8q*", [" b7", " B8q*"], 2),
            ("B7-b8=Q*", [" B7-b8=Q*"], 2),
            ("B7-b8=q*", [" B7-b8=q*"], 2),
            ("B7-B8=Q*", [" B7-B8=Q*"], 2),
            ("B7-B8=q*", [" B7-B8=q*"], 2),
            ("b7-b8=Q*", [" b7", " -b8", " =Q*"], 2),
            ("b7-b8=q*", [" b7", " -b8", " =q*"], 2),
            ("b7-B8=Q*", [" b7", " -B8=Q*"], 2),
            ("b7-B8=q*", [" b7", " -B8=q*"], 2),
            ("B7-b8Q*", [" B7-b8Q*"], 2),
            ("B7-b8q*", [" B7-b8q*"], 2),
            ("B7-B8Q*", [" B7-B8Q*"], 2),
            ("B7-B8q*", [" B7-B8q*"], 2),
            ("b7-b8Q*", [" b7", " -b8", " Q*"], 2),
            ("b7-b8q*", [" b7", " -b8", " q*"], 2),
            ("b7-B8Q*", [" b7", " -B8Q*"], 2),
            ("b7-B8q*", [" b7", " -B8q*"], 2),
            ("Bb8=Q*", [" Bb8", " =Q*"], 2),
            ("Bb8=q*", [" Bb8", " =q*"], 2),
            ("BB8=Q*", [" BB8=Q*"], 2),
            ("BB8=q*", [" BB8=q*"], 2),
            ("bb8=Q*", [" bb8=Q*"], 2),
            ("bb8=q*", [" bb8=q*"], 2),
            ("bB8=Q*", [" bB8=Q*"], 2),
            ("bB8=q*", [" bB8=q*"], 2),
            ("Bb8Q*", [" Bb8", " Q*"], 2),
            ("Bb8q*", [" Bb8", " q*"], 2),
            ("BB8Q*", [" BB8Q*"], 2),
            ("BB8q*", [" BB8q*"], 2),
            ("bb8Q*", [" bb8Q*"], 2),
            ("bb8q*", [" bb8q*"], 2),
            ("bB8Q*", [" bB8Q*"], 2),
            ("bB8q*", [" bB8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_02_bishop_c7_to_b8(self):
        fen = '[FEN"4k3/2B5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8*", [" B7b8", " *"], 2),
            ("B7B8*", [" B7B8*"], 2),
            ("b7b8*", [" b7", " b8", " *"], 2),
            ("b7B8*", [" b7", " B8*"], 2),
            ("B7-b8*", [" B7-b8*"], 2),
            ("B7-B8*", [" B7-B8*"], 2),
            ("b7-b8*", [" b7", " -b8", " *"], 2),
            ("b7-B8*", [" b7", " -B8*"], 2),
            ("Bb8*", ["Bb8", "*"], None),
            ("BB8*", [" BB8*"], 2),
            ("bb8*", [" bb8*"], 2),
            ("bB8*", [" bB8*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_03_bishop_c6_to_b7(self):
        fen = '[FEN"3k4/8/2B5/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B6b7*", [" B6b7", " *"], 2),
            ("B6B7*", [" B6B7*"], 2),
            ("b6b7*", [" b6", " b7", " *"], 2),
            ("b6B7*", [" b6", " B7*"], 2),
            ("B6-b7*", [" B6-b7*"], 2),
            ("B6-B7*", [" B6-B7*"], 2),
            ("b6-b7*", [" b6", " -b7", " *"], 2),
            ("b6-B7*", [" b6", " -B7*"], 2),
            ("Bb7*", ["Bb7", "*"], None),
            ("BB7*", [" BB7*"], 2),
            ("bb7*", [" bb7*"], 2),
            ("bB7*", [" bB7*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_185_01_pawn_capture_bc5_or_too_much_precision(self):
        fen = '[FEN"4K3/8/1p6/2Bk4/8/8/8/8 b - - 0 1"]'
        for string, tokens, state in (
            ("B6xc5*", [" B6xc5", " *"], 2),
            ("B6xC5*", [" B6xC5*"], 2),
            ("b6xc5*", [" b6", " xc5", " *"], 2),
            ("b6xC5*", [" b6", " xC5*"], 2),
            ("Bxc5*", [" Bxc5", " *"], 2),
            ("BxC5*", [" BxC5*"], 2),
            ("bxc5*", ["bxc5", "*"], None),
            ("bxC5*", [" bxC5*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_185_02_pawn_capture_bc5_or_too_much_precision(self):
        fen = '[FEN"4K3/8/1b6/2Bk4/8/8/8/8 b - - 0 1"]'
        for string, tokens, state in (
            ("B6xc5*", [" B6xc5", " *"], 2),
            ("B6xC5*", [" B6xC5*"], 2),
            ("b6xc5*", [" b6", " xc5", " *"], 2),
            ("b6xC5*", [" b6", " xC5*"], 2),
            ("Bxc5*", ["Bxc5", "*"], None),
            ("BxC5*", [" BxC5*"], 2),
            ("bxc5*", [" bxc5", " *"], 2),
            ("bxC5*", [" bxC5*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_01_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1p6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", [" B2xc1", " =Q*"], 2),
            ("B2xc1=q*", [" B2xc1", " =q*"], 2),
            ("B2xC1=Q*", [" B2xC1=Q*"], 2),
            ("B2xC1=q*", [" B2xC1=q*"], 2),
            ("b2xc1=Q*", [" b2", " xc1", " =Q*"], 2),
            ("b2xc1=q*", [" b2", " xc1", " =q*"], 2),
            ("b2xC1=Q*", [" b2", " xC1=Q*"], 2),
            ("b2xC1=q*", [" b2", " xC1=q*"], 2),
            ("B2xc1Q*", [" B2xc1", " Q*"], 2),
            ("B2xc1q*", [" B2xc1", " q*"], 2),
            ("B2xC1Q*", [" B2xC1Q*"], 2),
            ("B2xC1q*", [" B2xC1q*"], 2),
            ("b2xc1Q*", [" b2", " xc1", " Q*"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1Q*"], 2),
            ("b2xC1q*", [" b2", " xC1q*"], 2),
            ("Bxc1=Q*", [" Bxc1", " =Q*"], 2),
            ("Bxc1=q*", [" Bxc1", " =q*"], 2),
            ("BxC1=Q*", [" BxC1=Q*"], 2),
            ("BxC1=q*", [" BxC1=q*"], 2),
            ("bxc1=Q*", ["bxc1=Q", "*"], None),
            ("bxc1=q*", [" bxc1=q*"], 2),
            ("bxC1=Q*", [" bxC1=Q*"], 2),
            ("bxC1=q*", [" bxC1=q*"], 2),
            ("Bxc1Q*", [" Bxc1", " Q*"], 2),
            ("Bxc1q*", [" Bxc1", " q*"], 2),
            ("BxC1Q*", [" BxC1Q*"], 2),
            ("BxC1q*", [" BxC1q*"], 2),
            ("bxc1Q*", [" bxc1Q*"], 2),
            ("bxc1q*", [" bxc1q*"], 2),
            ("bxC1Q*", [" bxC1Q*"], 2),
            ("bxC1q*", [" bxC1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_02_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1b6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", [" B2xc1", " =Q*"], 2),
            ("B2xc1=q*", [" B2xc1", " =q*"], 2),
            ("B2xC1=Q*", [" B2xC1=Q*"], 2),
            ("B2xC1=q*", [" B2xC1=q*"], 2),
            ("b2xc1=Q*", [" b2", " xc1", " =Q*"], 2),
            ("b2xc1=q*", [" b2", " xc1", " =q*"], 2),
            ("b2xC1=Q*", [" b2", " xC1=Q*"], 2),
            ("b2xC1=q*", [" b2", " xC1=q*"], 2),
            ("B2xc1Q*", [" B2xc1", " Q*"], 2),
            ("B2xc1q*", [" B2xc1", " q*"], 2),
            ("B2xC1Q*", [" B2xC1Q*"], 2),
            ("B2xC1q*", [" B2xC1q*"], 2),
            ("b2xc1Q*", [" b2", " xc1", " Q*"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1Q*"], 2),
            ("b2xC1q*", [" b2", " xC1q*"], 2),
            ("Bxc1=Q*", ["Bxc1", " =Q*"], 3),
            ("Bxc1=q*", ["Bxc1", " =q*"], 3),
            ("BxC1=Q*", [" BxC1=Q*"], 2),
            ("BxC1=q*", [" BxC1=q*"], 2),
            ("bxc1=Q*", [" bxc1=Q", " *"], 2),
            ("bxc1=q*", [" bxc1=q*"], 2),
            ("bxC1=Q*", [" bxC1=Q*"], 2),
            ("bxC1=q*", [" bxC1=q*"], 2),
            ("Bxc1Q*", ["Bxc1", " Q*"], 3),
            ("Bxc1q*", ["Bxc1", " q*"], 3),
            ("BxC1Q*", [" BxC1Q*"], 2),
            ("BxC1q*", [" BxC1q*"], 2),
            ("bxc1Q*", [" bxc1Q*"], 2),
            ("bxc1q*", [" bxc1q*"], 2),
            ("bxC1Q*", [" bxC1Q*"], 2),
            ("bxC1q*", [" bxC1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_03_pawn_capture_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1b6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1*", [" B2xc1", " *"], 2),
            ("B2xC1*", [" B2xC1*"], 2),
            ("b2xc1*", [" b2", " xc1", " *"], 2),
            ("b2xC1*", [" b2", " xC1*"], 2),
            ("Bxc1*", ["Bxc1", "*"], None),
            ("BxC1*", [" BxC1*"], 2),
            ("bxc1*", [" bxc1*"], 2),
            ("bxC1*", [" bxC1*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_01_pawn_promotion_b1_or_too_much_precision(self):
        fen = '[FEN"4K3/8/8/8/8/8/1pB5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1=Q*", [" B2b1", " =Q*"], 2),
            ("B2b1=q*", [" B2b1", " =q*"], 2),
            ("B2B1=Q*", [" B2B1=Q*"], 2),
            ("B2B1=q*", [" B2B1=q*"], 2),
            ("b2b1=Q*", [" b2", " b1=Q", " *"], 2),
            ("b2b1=q*", [" b2", " b1", " =q*"], 2),
            ("b2B1=Q*", [" b2", " B1=Q*"], 2),
            ("b2B1=q*", [" b2", " B1=q*"], 2),
            ("B2b1Q*", [" B2b1", " Q*"], 2),
            ("B2b1q*", [" B2b1", " q*"], 2),
            ("B2B1Q*", [" B2B1Q*"], 2),
            ("B2B1q*", [" B2B1q*"], 2),
            ("b2b1Q*", [" b2", " b1", " Q*"], 2),
            ("b2b1q*", [" b2", " b1", " q*"], 2),
            ("b2B1Q*", [" b2", " B1Q*"], 2),
            ("b2B1q*", [" b2", " B1q*"], 2),
            ("B2-b1=Q*", [" B2-b1=Q*"], 2),
            ("B2-b1=q*", [" B2-b1=q*"], 2),
            ("B2-B1=Q*", [" B2-B1=Q*"], 2),
            ("B2-B1=q*", [" B2-B1=q*"], 2),
            ("b2-b1=Q*", [" b2", " -b1", " =Q*"], 2),
            ("b2-b1=q*", [" b2", " -b1", " =q*"], 2),
            ("b2-B1=Q*", [" b2", " -B1=Q*"], 2),
            ("b2-B1=q*", [" b2", " -B1=q*"], 2),
            ("B2-b1Q*", [" B2-b1Q*"], 2),
            ("B2-b1q*", [" B2-b1q*"], 2),
            ("B2-B1Q*", [" B2-B1Q*"], 2),
            ("B2-B1q*", [" B2-B1q*"], 2),
            ("b2-b1Q*", [" b2", " -b1", " Q*"], 2),
            ("b2-b1q*", [" b2", " -b1", " q*"], 2),
            ("b2-B1Q*", [" b2", " -B1Q*"], 2),
            ("b2-B1q*", [" b2", " -B1q*"], 2),
            ("Bb1=Q*", [" Bb1", " =Q*"], 2),
            ("Bb1=q*", [" Bb1", " =q*"], 2),
            ("BB1=Q*", [" BB1=Q*"], 2),
            ("BB1=q*", [" BB1=q*"], 2),
            ("bb1=Q*", [" bb1=Q*"], 2),
            ("bb1=q*", [" bb1=q*"], 2),
            ("bB1=Q*", [" bB1=Q*"], 2),
            ("bB1=q*", [" bB1=q*"], 2),
            ("Bb1Q*", [" Bb1", " Q*"], 2),
            ("Bb1q*", [" Bb1", " q*"], 2),
            ("BB1Q*", [" BB1Q*"], 2),
            ("BB1q*", [" BB1q*"], 2),
            ("bb1Q*", [" bb1Q*"], 2),
            ("bb1q*", [" bb1q*"], 2),
            ("bB1Q*", [" bB1Q*"], 2),
            ("bB1q*", [" bB1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_02_bishop_c2_to_b1(self):
        fen = '[FEN"4K3/8/8/8/8/8/2b5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1*", [" B2b1", " *"], 2),
            ("B2B1*", [" B2B1*"], 2),
            ("b2b1*", [" b2", " b1", " *"], 2),
            ("b2B1*", [" b2", " B1*"], 2),
            ("B2-b1*", [" B2-b1*"], 2),
            ("B2-B1*", [" B2-B1*"], 2),
            ("b2-b1*", [" b2", " -b1", " *"], 2),
            ("b2-B1*", [" b2", " -B1*"], 2),
            ("Bb1*", ["Bb1", "*"], None),
            ("BB1*", [" BB1*"], 2),
            ("bb1*", [" bb1*"], 2),
            ("bB1*", [" bB1*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_03_bishop_c3_to_b2(self):
        fen = '[FEN"4K3/8/8/8/8/2b5/8/3k4 b - - 0 1"]'
        for string, tokens, state in (
            ("B3b2*", [" B3b2", " *"], 2),
            ("B3B2*", [" B3B2*"], 2),
            ("b3b2*", [" b3", " b2", " *"], 2),
            ("b3B2*", [" b3", " B2*"], 2),
            ("B3-b2*", [" B3-b2*"], 2),
            ("B3-B2*", [" B3-B2*"], 2),
            ("b3-b2*", [" b3", " -b2", " *"], 2),
            ("b3-B2*", [" b3", " -B2*"], 2),
            ("Bb2*", ["Bb2", "*"], None),
            ("BB2*", [" BB2*"], 2),
            ("bb2*", [" bb2*"], 2),
            ("bB2*", [" bB2*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Added for Github issue 3.
    def test_188_01_pass_double_minus(self):
        ae = self.assertEqual
        games = self.get("e4--d4*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " --", " d4", " *"])

    # Added for Github issue 3.
    def test_188_02_pass_Z0(self):
        ae = self.assertEqual
        games = self.get("e4Z0d4*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " Z0", " d4", " *"])

    # Added for Github issue 3.
    # Different outcome in GameTextPGN and GameIgnoreCasePGN tests.
    def test_188_03_bad_pass_Z1(self):
        ae = self.assertEqual
        games = self.get("e4Z1d4*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " Z1d4*"])

    # Added for Github issue 3.
    # Different outcome in GameTextPGN and GameIgnoreCasePGN tests.
    def test_188_04_bad_pass_Z1(self):
        ae = self.assertEqual
        games = self.get("e4 Z1 d4*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " Z1 ", " d4", " *"])

    def test_189_01_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4$1e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "$1", "e5", "*"])

    def test_189_02_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4$11e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "$11", "e5", "*"])

    def test_189_03_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4$111e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "$111", "e5", "*"])

    def test_189_04_nag_and_game_termination_marker(self):
        # Fourth '1' is treated as a move number indicator and ignored.
        ae = self.assertEqual
        games = self.get("e4$1111e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "$111", "e5", "*"])

    def test_189_05_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4e5$1*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "$1", "*"])

    def test_189_06_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4e5$11*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "$11", "*"])

    def test_189_07_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4e5$111*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "$111", "*"])

    def test_189_08_nag_and_game_termination_marker(self):
        # Fourth '1' is treated as a move number indicator and ignored.
        ae = self.assertEqual
        games = self.get("e4e5$1111*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "$111", "*"])

    def test_189_09_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4e5$11-0")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "$1", "1-0"])

    def test_189_10_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4e5$111-0")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "$11", "1-0"])

    def test_189_11_nag_and_game_termination_marker(self):
        ae = self.assertEqual
        games = self.get("e4e5$1111-0")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "$111", "1-0"])

    # Different outcome in GameTextPGN and GameIgnoreCasePGN tests.
    def test_189_12_nag_and_game_termination_marker(self):
        # Fourth and fifth '1's are treated as a move number indicator and
        # ignored.
        ae = self.assertEqual
        games = self.get("e4e5$11111-0")
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text, ["e4", "e5", "$111", " -0"])

    def test_189_13_nag_and_game_termination_marker(self):
        # Fourth '1' is treated as a move number indicator and ignored.
        ae = self.assertEqual
        games = self.get("e4e5$1111.1-0")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "$111", "1-0"])

    def test_190_01_attempt_move_with_pinned_piece(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/1b6/2N5/8/4K3 w - - 0 1"]Ne4*'
        )
        ae(games[0].state, 2)
        ae(games[0]._position_deltas, [None, None, None])

    def test_190_02_attempt_capture_with_pinned_piece(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/1b2p3/2N1P3/8/4K3 w - - 0 1"]Nxe4*'
        )
        ae(games[0].state, 2)
        ae(games[0]._position_deltas, [None, None, None])

    def test_191_01_lan_promote_and_capture(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"4n3/3P4/8/8/8/8/8/k6K w - - 0 1"]',
            "=QKa2*",
        ]
        move = ["d7", "e8"]
        for delimiter in ("x",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, 2)
                ae(games[0]._text[-3:], [" d7", " xe8", " =QKa2*"])

    def test_191_02_lan_promote_and_capture(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"4n1Q1/8/4Q1Q1/8/8/8/8/k6K w - - 0 1"]',
            "=QKb2*",
        ]
        move = ["Qe6", "e8"]
        for delimiter in ("x",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, 2)
                ae(games[0]._text[-3:], [" Qe6", " xe8", " =QKb2*"])

    def test_191_03_lan_promote_and_capture(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"6Q1/8/4Q3/8/8/8/8/k6K w - - 0 1"]',
            "=QKb2*",
        ]
        move = ["Qe6", "e8"]
        for delimiter in ("-",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(games[0].state, 2)
                ae(games[0]._text[-3:], [" Qe6", " -e8", " =QKb2*"])

    def test_192_01_lan_king_move(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, 2)
                ae(games[0]._text[-3:], [" Ke4", " d5", " *"])

    def test_192_02_lan_king_move_hyphen(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("-",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, 2)
                ae(games[0]._text[-3:], [" Ke4", " -d5", " *"])

    def test_192_03_lan_knight_move_hyphen(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/5N2/8/8/k6K w - - 0 1"]',
            "*",
        ]
        move = ["Nf4", "d5"]
        for delimiter in ("-",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, 2)
                ae(games[0]._text[-3:], [" Nf4", " -d5", " *"])

    def test_192_04_lan_knight_move_full_disambiguation(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/5N2/8/1N3N2/8/8/k6K w - - 0 1"]',
            "*",
        ]
        move = ["Nf4", "d5"]
        for delimiter in ("-", ""):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Nf4d5", "*"])


class StrictPGNOneCharacterAtATime(StrictPGN):
    """Repeat StrictPGN tests reading text one character at a time."""

    def get(self, s):
        """Return sequence of Game instances derived from s.

        Read characters one at a time from s.

        """
        return [g for g in self.pgn.read_games(io.StringIO(s), size=1)]

    def test_183_01_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1P6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" B7xc8", " =Q*"], 2),
            ("B7xc8=q*", [" B7xc8", " =q*"], 2),
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", [" b7", " xc8", " =q*"], 2),
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", [" B7xc8", " Q*"], 2),
            ("B7xc8q*", [" B7xc8", " q*"], 2),
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", [" Bxc8", " =Q*"], 2),
            ("Bxc8=q*", [" Bxc8", " =q*"], 2),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", ["bxc8=Q", "*"], None),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", [" Bxc8", " Q*"], 2),
            ("Bxc8q*", [" Bxc8", " q*"], 2),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)


class StrictPGNExtendByOneCharacter(StrictPGN):
    """Repeat StrictPGN tests reading text in two chunks, last is length 1."""

    def get(self, s):
        """Return sequence of Game instances derived from s.

        Where possible do two reads of source where the second read is one
        character, the last one in s.

        """
        t = io.StringIO(s)
        size = max(len(t.getvalue()) - 1, 1)
        return [g for g in self.pgn.read_games(t, size=size)]

    def test_183_01_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1P6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" B7xc8", " =Q*"], 2),
            ("B7xc8=q*", [" B7xc8", " =q*"], 2),
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", [" b7", " xc8", " =q*"], 2),
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", [" B7xc8", " Q*"], 2),
            ("B7xc8q*", [" B7xc8", " q*"], 2),
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", [" Bxc8", " =Q*"], 2),
            ("Bxc8=q*", [" Bxc8", " =q*"], 2),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", ["bxc8=Q", "*"], None),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", [" Bxc8", " Q*"], 2),
            ("Bxc8q*", [" Bxc8", " q*"], 2),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)


class StrictFEN(_BasePGN):
    """FEN and SetUp tag tests only.  StrictPGN tests are not done."""

    def test_401_null_fen_illegal_game(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN""]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN""]'])
        ae(g._pieces_on_board, {})

    def test_402_null_fen(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN""]*')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN""]', " *"])
        ae(len(g._pieces_on_board), 26)
        for p in "KQRBNkqrbn":
            ae(g._pieces_on_board[p], [])
        for p in (
            "aP",
            "ap",
            "bP",
            "bp",
            "cP",
            "cp",
            "dP",
            "dp",
            "eP",
            "ep",
            "fP",
            "fp",
            "gP",
            "gp",
            "hP",
            "hp",
        ):
            ae(g._pieces_on_board[p], [])

    def test_403_fen_all_unknown(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"? ? ? ? ? ?"]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN"? ? ? ? ? ?"]'])

    def test_404_fen_illegal_piece_placement(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"? w - - 0 1"]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN"? w - - 0 1"]'])

    def test_405_fen_empty_board(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"8/8/8/8/8/8/8/8 w - - 0 1"]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN"8/8/8/8/8/8/8/8 w - - 0 1"]'])

    def test_406_fen_two_kings(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]'])

    def test_407_fen_two_kings_and_move(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, None)
        ae(
            g._text,
            ['[SetUp"1"]', '[FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]', "Kh2", "*"],
        )
        ae(
            {k: str(v) for k, v in g._piece_placement_data.items()},
            {"a8": "ka8", "h2": "Kh2"},
        )

    def test_408_fen_too_many_kings(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"k7/8/8/8/7K/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_409_fen_too_many_pawns(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7p/8/8/7K w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_410_fen_maximum_black_pawns(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7P/8/8/7K w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_411_fen_black_pawn_on_rank_1(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/ppppppp1/8/8/7P/8/8/6pK w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_412_fen_black_pawn_on_rank_8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k6p/ppppppp1/8/8/7P/8/8/7K w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_413_fen_white_pawn_on_rank_1(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/ppppppp1/8/8/7P/8/8/6PK w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_414_fen_white_pawn_on_rank_8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k6P/ppppppp1/8/8/7P/8/8/7K w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_415_fen_too_few_squares_middle_rank(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7P/7/8/7K w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_416_fen_too_few_squares_first_rank(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/7P/8/8/8/6K w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_417_fen_ep_no_pawns_in_place(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/7P/8/8/8/7K w - c6 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_418_fen_ep_no_pawns_to_capture(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/1P5P/8/8/8/7K w - c6 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_419_fen_ep_allowed(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pp1ppppp/8/1Pp4P/8/8/8/7K w - c6 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_420_fen_ep_target_square_occupied(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pp2pppp/2p5/1Pp4P/8/8/8/7K w - c6 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_421_fen_too_many_black_pieces(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"rnbqkbnr/pppppppp/n7/1P5P/8/8/8/7K w - - 0 1"]Kh2*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_422_fen_too_many_white_pieces(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/',
                            "7Q/PPPPPPPP/RNBQKBNR",
                        )
                    ),
                    ' w - - 0 1"]Nf3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_423_fen_white_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/',
                            "PPPPPPPP/RNBQKBRN",
                        )
                    ),
                    ' w K - 0 1"]Nc3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_424_fen_white_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/',
                            "PPPPPPPP/RNBQKBRN",
                        )
                    ),
                    ' w Qkq - 0 1"]Nc3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_425_fen_white_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/',
                            "PPPPPPPP/NRBQKBNR",
                        )
                    ),
                    ' w Q - 0 1"]Nf3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_426_fen_white_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/',
                            "PPPPPPPP/NRBQKBNR",
                        )
                    ),
                    ' w Kkq - 0 1"]Nf3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_427_fen_black_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"rnbqkbrn/pppppppp/8/8/8/8/',
                            "PPPPPPPP/RNBQKBNR",
                        )
                    ),
                    ' w k - 0 1"]Nc3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_428_fen_black_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"rnbqkbrn/pppppppp/8/8/8/8/',
                            "PPPPPPPP/RNBQKBNR",
                        )
                    ),
                    ' w KQq - 0 1"]Nc3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_429_fen_black_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"nrbqkbnr/pppppppp/8/8/8/8/',
                            "PPPPPPPP/RNBQKBNR",
                        )
                    ),
                    ' w q - 0 1"]Nf3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_430_fen_black_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    "".join(
                        (
                            '[SetUp"1"][FEN"nrbqkbnr/pppppppp/8/8/8/8/',
                            "PPPPPPPP/RNBQKBNR",
                        )
                    ),
                    ' w KQk - 0 1"]Nf3*',
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_431_fen_inactive_color_not_in_check(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                ('[SetUp"1"][FEN"4k3/8/8/7b/8/8/8/4K3', ' w - - 0 1"]Kf1*')
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_432_fen_inactive_color_in_check(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                ('[SetUp"1"][FEN"4k3/8/8/7B/8/8/8/4K3', ' w - - 0 1"]Kf1*')
            )
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_433_fen_adjacent_kings_and_move(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"8/8/8/4kK2/8/8/8/ w - - 0 1"]Kg5*')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)


class StrictDisambiguate(_BasePGN):
    """Movetext disambiguation tests only.  StrictPGN tests are not done.

    The PGN specification states movetext should use exactly the precision
    needed to describe the move.  These tests verify, for example, Rcc7 is
    stated when two rooks on rank 7 can legally move to c7; and Rc7 is stated
    when only one rook can legally move to c7 (from rank 7 or file c).

    """

    def test_501_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"7q/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qbb8*'
        )
        self.assertEqual(games[0].state, None)

    def test_502_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"7q/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qhb8*'
        )
        self.assertEqual(games[0].state, None)

    def test_503_disambiguate_move_needed(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"5q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]',
            "Kh3*",
        ]
        move = ["Qf6", "d8"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(games[0].state, None)
                ae(games[0]._text[2], "".join(move))

    def test_504_disambiguate_move_needed(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"]'
                    '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6xd8Kh3*'
                )
            )
        )
        self.assertEqual(games[0].state, None)

    def test_505_disambiguate_move_needed(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"]'
                    '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6Xd8Kh3*'
                )
            )
        )
        self.assertEqual(games[0].state, 2)
        self.assertEqual(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]',
                " Qf6",
                " Xd8Kh3*",
            ],
        )

    def test_506_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_507_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_508_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, None)

    def test_509_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_510_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_511_disambiguate_move_needed(self):
        ae = self.assertEqual
        fen = ['[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(games[0].state, None)
                ae(games[0]._text[2], "".join(move))

    def test_512_disambiguate_move_needed(self):
        fen = ['[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_513_disambiguate_move_needed(self):
        fen = ['[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_514_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_515_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_516_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, None)

    def test_517_disambiguate_move_and_rank_pin_one(self):
        ae = self.assertEqual
        fen = ['[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(games[0].state, 2)
                ae(games[0]._position_deltas, [None, None, None])

    def test_518_disambiguate_move_and_rank_pin_one(self):
        fen = ['[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_519_disambiguate_move_and_rank_pin_one(self):
        fen = ['[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_520_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_521_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_522_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_523_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_524_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_525_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_526_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_527_disambiguate_move_and_rank_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_528_disambiguate_move_and_rank_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_529_disambiguate_move_and_rank_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_530_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_531_disambiguate_move_and_rank_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_532_disambiguate_move_and_rank_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_533_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_534_disambiguate_move_and_rank_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_535_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_536_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_537_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_538_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_539_disambiguate_move_and_file_pin_one(self):
        fen = ['[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_540_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, None)

    def test_541_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_542_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_543_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_544_disambiguate_move_and_file_pin_one(self):
        fen = ['[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_545_disambiguate_move_and_file_pin_one(self):
        fen = ['[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_546_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_547_disambiguate_move_and_file_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_548_disambiguate_move_and_file_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_549_disambiguate_move_and_file_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_550_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_551_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_552_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_553_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, None)

    def test_554_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_555_disambiguate_move_and_file_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_556_disambiguate_move_and_file_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_557_disambiguate_move_and_file_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_558_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_559_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_560_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_561_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_562_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_563_disambiguate_move_and_diagonal_pin_one(self):
        fen = ['[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_564_disambiguate_move_and_diagonal_pin_one(self):
        fen = ['[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_565_disambiguate_move_and_diagonal_pin_one(self):
        fen = ['[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_566_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_567_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_568_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_569_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_570_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_571_disambiguate_move_and_diagonal_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_572_disambiguate_move_and_diagonal_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_573_disambiguate_move_and_diagonal_pin_two(self):
        fen = ['[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_574_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_575_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, None)

    def test_576_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_577_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_578_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_579_disambiguate_move_and_diagonal_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]', "*"]
        move = ["Qb6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_580_disambiguate_move_and_diagonal_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]', "*"]
        move = ["Qe6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_581_disambiguate_move_and_diagonal_both_pins(self):
        fen = ['[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]', "*"]
        move = ["Qb3", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_582_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qbe3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_583_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qee3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_584_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q6e3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_585_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_608_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_609_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_610_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_611_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_612_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_613_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_614_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_615_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_616_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_617_disambiguate_capture_and_rank_pin_one(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*'
        )
        ae(games[0].state, 2)
        ae(games[0]._position_deltas, [None, None, None])

    def test_618_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_619_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_620_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_621_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_622_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_623_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_624_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_625_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_626_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_627_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_628_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_629_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_630_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_631_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_632_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_633_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_634_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_635_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_636_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_637_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_638_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_639_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_640_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_641_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_642_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_643_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_644_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_645_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_646_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_647_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_648_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_649_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_650_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_651_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_652_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_653_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_654_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_655_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_656_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_657_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_658_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_659_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_660_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_661_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_662_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_663_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_664_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_665_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_666_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_667_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_668_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_669_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_670_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_671_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_672_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_673_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_674_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_675_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_676_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_677_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_678_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qxe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_679_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_680_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_681_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_682_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qbxe3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_683_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qexe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_684_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q6xe3*'
        )
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_685_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_686_FIDE_longest_possible_game_move_1461_by_white(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"]',
                    '[FEN"2r3kq/Q1pnnpq1/3pp1pp/1q1bb3/3B4/',
                    "2Q1NNP1/2PPPPBP/R1QK4 ",
                    'w - - 24 1461"]',
                    "Q1a3*",
                )
            )
        )
        self.assertEqual(games[0].state, None)

    def test_706_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_707_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R3e3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_708_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Ree3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_709_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Rbe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_710_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_711_disambiguate_move_needed(self):
        fen = ['[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]', "*"]
        move = ["Re1", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_712_disambiguate_move_needed(self):
        fen = ['[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]', "*"]
        move = ["Re6", "e3"]
        for delimiter in ("", "-"):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                self.assertEqual(games[0].state, 2)

    def test_713_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_806_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rxe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_807_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R3xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_808_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rexe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_809_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rbxe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_810_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_811_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_812_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_813_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_816_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]RXe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_817_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R3Xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_818_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]ReXe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_819_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]RbXe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_820_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6Xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_821_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1Xe3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_822_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xE3*'
        )
        self.assertEqual(games[0].state, 2)

    def test_823_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6Xe3*'
        )
        self.assertEqual(games[0].state, 2)


class StrictRAV(_BasePGN):
    """Recursive annotation variation tests.  StrictPGN tests are not done."""

    def fen_position(self, g, fen):
        self.assertEqual(
            gamedata.generate_fen_for_position(
                g._piece_placement_data.values(),
                g._active_color,
                g._castling_availability,
                g._en_passant_target_square,
                g._halfmove_clock,
                g._fullmove_number,
            ),
            fen,
        )

    def test_451_rav_after_piece_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nf6(Ne5)*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/5N1p/8/7K/8/8/8 b - - 2 2")

    def test_451_01_rav_after_piece_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nf6(Ne5)Kg6*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/5Nkp/8/7K/8/8/8 w - - 3 3")

    def test_452_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7N/8/7K/8/8/8 b - - 0 2")

    def test_452_01_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)Kg6*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kN/8/7K/8/8/8 w - - 1 3")

    def test_452_02_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)Kxh6*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/7k/8/7K/8/8/8 w - - 0 3")

    def test_453_rav_after_pawn_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6PK/8/8/8 b - - 0 1"]Kh7g5(Kh5)*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7p/6P1/7K/8/8/8 b - - 0 2")

    def test_453_01_rav_after_pawn_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6PK/8/8/8 b - - 0 1"]Kh7g5(Kh5)Kg6*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kp/6P1/7K/8/8/8 w - - 1 3")

    def test_454_rav_after_pawn_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]Kh7gxh6(Kh5)*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7P/8/7K/8/8/8 b - - 0 2")

    def test_454_01_rav_after_pawn_capture(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]',
                    "Kh7gxh6(Kh5)Kg6*",
                )
            )
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kP/8/7K/8/8/8 w - - 1 3")

    def test_454_02_rav_after_pawn_capture(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]',
                    "Kh7gxh6(Kh5)Kxh6*",
                )
            )
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/7k/8/7K/8/8/8 w - - 0 3")

    def test_455_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6B1/7k/7p/8/7K/8/8/8 b - - 0 2")

    def test_455_01_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)Kg6*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6B1/8/6kp/8/7K/8/8/8 w - - 1 3")

    def test_455_02_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)Kxg8*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6k1/8/7p/8/7K/8/8/8 w - - 0 3")

    def test_456_rav_after_pawn_promote_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7gxh8=B(Kh5)*'
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7B/7k/7p/8/7K/8/8/8 b - - 0 2")

    def test_456_01_rav_after_pawn_promote_capture(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]',
                    "Kh7gxh8=B(Kh5)Kg6*",
                )
            )
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7B/8/6kp/8/7K/8/8/8 w - - 1 3")

    def test_456_02_rav_after_pawn_promote_capture(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]',
                    "Kh7gxh8=B(Kh5)Kxh8*",
                )
            )
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7k/8/7p/8/7K/8/8/8 w - - 0 3")

    def test_457_rav_extract_from_4ncl(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"][FEN"8/p7/6p1/2K3P1/2P2k2/8/8/8 w - - 0 70"]',
                    "Kc6(Kb5Ke4Kc6)(Kd4Kxg5)*",
                )
            )
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/p7/2K3p1/6P1/2P2k2/8/8/8 b - - 1 70")

    def test_458_rav_extract_from_calgames_02(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"]',
                    '[FEN"r2b1rk1/ppp2p1n/7Q/4pb2/2B1N3/5N2/PPP2PPP/2K5 ',
                    'w - - 2 17"]',
                    "Neg5e4(Bxg5)Nxh7exf3(Bxh7Ne5Be7Nxf7Rxf7Bxf7",
                    "Kxf7Qxh7Kf6Qxe4)*",
                )
            )
        )
        self.assertEqual(games[0].state, None)
        self.fen_position(
            games[0], "r2b1rk1/ppp2p1N/7Q/5b2/2B5/5p2/PPP2PPP/2K5 w - - 0 19"
        )


class _NonStrictPGN:
    """Override StrictPGN tests which have a different outcome, but same for
    all, in PGN, PGNOneCharacterAtATime, and PGNExtendByOneCharacter tests.

    Usage is 'class C(_NonStrictPGN, StrictPGN)'.

    For example, Game class allows Nge2 when a knight on c3 is pinned against
    the king on e1, while GameStrictPGN class does not allow Nge2.

    """

    # Added on seeing results when crash traced to game in crafty06_03.pgn.
    # c4c5 is redundant precision, not long algebraic notation.
    def test_113_start_rav_after_moves_after_nags(self):
        ae = self.assertEqual
        games = self.get("$10$21$10$22c4e5c4c5(()")
        ae(len(games), 1)
        ae(games[0].state, 10)
        ae(
            games[0]._text,
            ["$10", "$21", "$10", "$22", "c4", "e5", "c5", "(", "(", ")"],
        )

    # Added after changes to convertion of chess engine responses to PGN.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_115_long_algebraic_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e7e5")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5"])

    # Added after changes to convertion of chess engine responses to PGN.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_116_long_algebraic_pawn_move_game_terminated(self):
        ae = self.assertEqual
        games = self.get("e4e7e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "*"])

    def test_141_bad_value_in_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A:"a" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A:"a"]'])

    def test_141_bad_value_in_tag_02(self):
        ae = self.assertEqual
        games = self.get('[A:"\na" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A:"\na"]'])

    def test_142_bad_value_in_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A""a" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"\\"a"]'])

    def test_143_bad_value_in_tag_02(self):
        ae = self.assertEqual
        games = self.get('[A""a"][B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"\\"a"]', '[B"b"]'])

    # Added while fixing Little.pgn upper case processing.
    # d2d4 is redundant precision, not long algebraic notation.
    def test_164_long_algebraic_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5d2d4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "d4", "*"])

    # Added while fixing Little.pgn upper case processing.
    # Hyphen noticed but ignored for seeing token d2 and peek ahead -d4 as
    # over-precise d4, but is not expecting -d4 when deciding if next token
    # has already been used for disambiguation.
    def test_165_long_algebraic_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5d2-d4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " d2", " -d4", " *"])

    # Added while fixing Little.pgn upper case processing.
    # b2b4 is redundant precision, not long algebraic notation.
    def test_166_01_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5b2b4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "b4", "*"])

    def test_166_02_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]b6b7*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]',
                "b7",
                "*",
            ],
        )
        ae(games[0].state, None)

    # Added while fixing Little.pgn upper case processing.
    # Hyphen treated like test_165_long_algebraic_white_pawn_move_with_hyphen
    # but b-pawn used to test for 'bishop or pawn' interpretation confusion.
    def test_167_01_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5b2-b4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " b2", " -b4", " *"])

    def test_167_02_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]b6-b7*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]',
                " b6",
                " -b7",
                " *",
            ],
        )
        ae(games[0].state, 2)

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_168_long_algebraic_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e7e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "*"])

    # Added while fixing Little.pgn upper case processing.
    # Hyphen treated like test_165_long_algebraic_white_pawn_move_with_hyphen.
    def test_169_long_algebraic_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e7-e5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " e7", " -e5", " *"])

    # Added while fixing Little.pgn upper case processing.
    # b7b5 is redundant precision, not long algebraic notation.
    def test_170_long_algebraic_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4b7b5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "b5", "*"])

    # Added while fixing Little.pgn upper case processing.
    # Hyphen treated like test_165_long_algebraic_white_pawn_move_with_hyphen
    # but b-pawn used to test for 'bishop or pawn' interpretation confusion.
    def test_171_long_algebraic_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4b7-b5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " b7", " -b5", " *"])

    def test_180_01_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("N1f3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["Nf3", "*"])

    def test_180_02_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("Ngf3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["Nf3", "*"])

    def test_180_03_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("Ng1f3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["Nf3", "*"])

    def test_180_04_long_algebraic(self):
        ae = self.assertEqual
        games = self.get("Ng1-f3*")
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [" Ng1", " -f3", " *"])

    def test_181_01_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5B1d3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "Bd3", "*"])

    def test_182_01_pawn_capture_bc4_or_too_much_precision(self):
        fen = '[FEN"8/8/8/8/2bk4/1P6/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B3xc4*", [" B3xc4", " *"], 2),
            ("B3xC4*", [" B3xC4*"], 2),
            ("b3xc4*", ["bxc4", " xc4", " *"], 3),
            ("b3xC4*", [" b3", " xC4*"], 2),
            ("Bxc4*", [" Bxc4", " *"], 2),
            ("BxC4*", [" BxC4*"], 2),
            ("bxc4*", ["bxc4", "*"], None),
            ("bxC4*", [" bxC4*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_182_02_pawn_capture_bc4_or_too_much_precision(self):
        fen = '[FEN"8/8/8/8/2bk4/1B6/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B3xc4*", ["Bxc4", "*"], None),
            ("B3xC4*", [" B3xC4*"], 2),
            ("b3xc4*", [" b3", " xc4", " *"], 2),
            ("b3xC4*", [" b3", " xC4*"], 2),
            ("Bxc4*", ["Bxc4", "*"], None),
            ("BxC4*", [" BxC4*"], 2),
            ("bxc4*", [" bxc4", " *"], 2),
            ("bxC4*", [" bxC4*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_02_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", ["Bxc8", " =Q*"], 3),  #
            ("B7xc8=q*", ["Bxc8", " =q*"], 3),  #
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", [" b7", " xc8", " =q*"], 2),
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", ["Bxc8", " Q*"], 3),  #
            ("B7xc8q*", ["Bxc8", " q*"], 3),  #
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", ["Bxc8", " =Q*"], 3),
            ("Bxc8=q*", ["Bxc8", " =q*"], 3),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", [" bxc8=Q", " *"], 2),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", ["Bxc8", " Q*"], 3),
            ("Bxc8q*", ["Bxc8", " q*"], 3),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_03_pawn_capture_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8*", ["Bxc8", "*"], None),
            ("B7xC8*", [" B7xC8*"], 2),
            ("b7xc8*", [" b7", " xc8", " *"], 2),
            ("b7xC8*", [" b7", " xC8*"], 2),
            ("Bxc8*", ["Bxc8", "*"], None),
            ("BxC8*", [" BxC8*"], 2),
            ("bxc8*", [" bxc8*"], 2),
            ("bxC8*", [" bxC8*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_02_bishop_c7_to_b8(self):
        fen = '[FEN"4k3/2B5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8*", ["Bb8", "*"], None),
            ("B7B8*", [" B7B8*"], 2),
            ("b7b8*", [" b7", " b8", " *"], 2),
            ("b7B8*", [" b7", " B8*"], 2),
            ("B7-b8*", [" B7-b8*"], 2),
            ("B7-B8*", [" B7-B8*"], 2),
            ("b7-b8*", [" b7", " -b8", " *"], 2),
            ("b7-B8*", [" b7", " -B8*"], 2),
            ("Bb8*", ["Bb8", "*"], None),
            ("BB8*", [" BB8*"], 2),
            ("bb8*", [" bb8*"], 2),
            ("bB8*", [" bB8*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_03_bishop_c6_to_b7(self):
        fen = '[FEN"3k4/8/2B5/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B6b7*", ["Bb7", "*"], None),
            ("B6B7*", [" B6B7*"], 2),
            ("b6b7*", [" b6", " b7", " *"], 2),
            ("b6B7*", [" b6", " B7*"], 2),
            ("B6-b7*", [" B6-b7*"], 2),
            ("B6-B7*", [" B6-B7*"], 2),
            ("b6-b7*", [" b6", " -b7", " *"], 2),
            ("b6-B7*", [" b6", " -B7*"], 2),
            ("Bb7*", ["Bb7", "*"], None),
            ("BB7*", [" BB7*"], 2),
            ("bb7*", [" bb7*"], 2),
            ("bB7*", [" bB7*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_185_01_pawn_capture_bc5_or_too_much_precision(self):
        fen = '[FEN"4K3/8/1p6/2Bk4/8/8/8/8 b - - 0 1"]'
        for string, tokens, state in (
            ("B6xc5*", [" B6xc5", " *"], 2),
            ("B6xC5*", [" B6xC5*"], 2),
            ("b6xc5*", ["bxc5", " xc5", " *"], 3),
            ("b3xC5*", [" b3", " xC5*"], 2),
            ("Bxc5*", [" Bxc5", " *"], 2),
            ("BxC5*", [" BxC5*"], 2),
            ("bxc5*", ["bxc5", "*"], None),
            ("bxC5*", [" bxC5*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_185_02_pawn_capture_bc5_or_too_much_precision(self):
        fen = '[FEN"4K3/8/1b6/2Bk4/8/8/8/8 b - - 0 1"]'
        for string, tokens, state in (
            ("B6xc5*", ["Bxc5", "*"], None),
            ("B6xC5*", [" B6xC5*"], 2),
            ("b6xc5*", [" b6", " xc5", " *"], 2),
            ("b6xC5*", [" b6", " xC5*"], 2),
            ("Bxc5*", ["Bxc5", "*"], None),
            ("BxC5*", [" BxC5*"], 2),
            ("bxc5*", [" bxc5", " *"], 2),
            ("bxC5*", [" bxC5*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_02_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1b6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", ["Bxc1", " =Q*"], 3),  #
            ("B2xc1=q*", ["Bxc1", " =q*"], 3),  #
            ("B2xC1=Q*", [" B2xC1=Q*"], 2),
            ("B2xC1=q*", [" B2xC1=q*"], 2),
            ("b2xc1=Q*", [" b2", " xc1", " =Q*"], 2),
            ("b2xc1=q*", ["b2", " xc1", " =q*"], 3),  # tolerate "b2" and 3.
            ("b2xC1=Q*", [" b2", " xC1=Q*"], 2),
            ("b2xC1=q*", [" b2", " xC1=q*"], 2),
            ("B2xc1Q*", ["Bxc1", " Q*"], 3),  #
            ("B2xc1q*", ["Bxc1", " q*"], 3),  #
            ("B2xC1Q*", [" B2xC1Q*"], 2),
            ("B2xC1q*", [" B2xC1q*"], 2),
            ("b2xc1Q*", [" b2", " xc1", " Q*"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1Q*"], 2),
            ("b2xC1q*", [" b2", " xC1q*"], 2),
            ("Bxc1=Q*", ["Bxc1", " =Q*"], 3),
            ("Bxc1=q*", ["Bxc1", " =q*"], 3),
            ("BxC1=Q*", [" BxC1=Q*"], 2),
            ("BxC1=q*", [" BxC1=q*"], 2),
            ("bxc1=Q*", [" bxc1=Q", " *"], 2),
            ("bxc1=q*", [" bxc1=q*"], 2),
            ("bxC1=Q*", [" bxC1=Q*"], 2),
            ("bxC1=q*", [" bxC1=q*"], 2),
            ("Bxc1Q*", ["Bxc1", " Q*"], 3),
            ("Bxc1q*", ["Bxc1", " q*"], 3),
            ("BxC1Q*", [" BxC1Q*"], 2),
            ("BxC1q*", [" BxC1q*"], 2),
            ("bxc1Q*", [" bxc1Q*"], 2),
            ("bxc1q*", [" bxc1q*"], 2),
            ("bxC1Q*", [" bxC1Q*"], 2),
            ("bxC1q*", [" bxC1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_03_pawn_capture_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1b6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1*", ["Bxc1", "*"], None),
            ("B2xC1*", [" B2xC1*"], 2),
            ("b2xc1*", [" b2", " xc1", " *"], 2),
            ("b2xC1*", [" b2", " xC1*"], 2),
            ("Bxc1*", ["Bxc1", "*"], None),
            ("BxC1*", [" BxC1*"], 2),
            ("bxc1*", [" bxc1*"], 2),
            ("bxC1*", [" bxC1*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_02_bishop_c2_to_b1(self):
        fen = '[FEN"4K3/8/8/8/8/8/2b5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1*", ["Bb1", "*"], None),
            ("B2B1*", [" B2B1*"], 2),
            ("b2b1*", [" b2", " b1", " *"], 2),
            ("b2B1*", [" b2", " B1*"], 2),
            ("B2-b1*", [" B2-b1*"], 2),
            ("B2-B1*", [" B2-B1*"], 2),
            ("b2-b1*", [" b2", " -b1", " *"], 2),
            ("b2-B1*", [" b2", " -B1*"], 2),
            ("Bb1*", ["Bb1", "*"], None),
            ("BB1*", [" BB1*"], 2),
            ("bb1*", [" bb1*"], 2),
            ("bB1*", [" bB1*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_03_bishop_c3_to_b2(self):
        fen = '[FEN"4K3/8/8/8/8/2b5/8/3k4 b - - 0 1"]'
        for string, tokens, state in (
            ("B3b2*", ["Bb2", "*"], None),
            ("B3B2*", [" B3B2*"], 2),
            ("b3b2*", [" b3", " b2", " *"], 2),
            ("b3B2*", [" b3", " B2*"], 2),
            ("B3-b2*", [" B3-b2*"], 2),
            ("B3-B2*", [" B3-B2*"], 2),
            ("b3-b2*", [" b3", " -b2", " *"], 2),
            ("b3-B2*", [" b3", " -B2*"], 2),
            ("Bb2*", ["Bb2", "*"], None),
            ("BB2*", [" BB2*"], 2),
            ("bb2*", [" bb2*"], 2),
            ("bB2*", [" bB2*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)


class PGN(_NonStrictPGN, StrictPGN):
    """Provide tests for Game version of parser."""

    def setUp(self):
        self.pgn = parser.PGN()

    def test_183_01_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1P6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" B7xc8", " =Q*"], 2),
            ("B7xc8=q*", [" B7xc8", " =q*"], 2),
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", ["b7", " xc8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", [" B7xc8", " Q*"], 2),
            ("B7xc8q*", [" B7xc8", " q*"], 2),
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", [" Bxc8", " =Q*"], 2),
            ("Bxc8=q*", [" Bxc8", " =q*"], 2),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", ["bxc8=Q", "*"], None),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", [" Bxc8", " Q*"], 2),
            ("Bxc8q*", [" Bxc8", " q*"], 2),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_02_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", ["Bxc8", " =Q*"], 3),  #
            ("B7xc8=q*", ["Bxc8", " =q*"], 3),  #
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", ["b7", " xc8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", ["Bxc8", " Q*"], 3),  #
            ("B7xc8q*", ["Bxc8", " q*"], 3),  #
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", ["Bxc8", " =Q*"], 3),
            ("Bxc8=q*", ["Bxc8", " =q*"], 3),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", [" bxc8=Q", " *"], 2),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", ["Bxc8", " Q*"], 3),
            ("Bxc8q*", ["Bxc8", " q*"], 3),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_01_pawn_promotion_b8_or_too_much_precision(self):
        fen = '[FEN"3k4/1Pb5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8=Q*", [" B7b8", " =Q*"], 2),
            ("B7b8=q*", [" B7b8", " =q*"], 2),
            ("B7B8=Q*", [" B7B8=Q*"], 2),
            ("B7B8=q*", [" B7B8=q*"], 2),
            ("b7b8=Q*", [" b7", " b8=Q", " *"], 2),
            ("b7b8=q*", ["b7", " b8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7B8=Q*", [" b7", " B8=Q*"], 2),
            ("b7B8=q*", [" b7", " B8=q*"], 2),
            ("B7b8Q*", [" B7b8", " Q*"], 2),
            ("B7b8q*", [" B7b8", " q*"], 2),
            ("B7B8Q*", [" B7B8Q*"], 2),
            ("B7B8q*", [" B7B8q*"], 2),
            ("b7b8Q*", [" b7", " b8", " Q*"], 2),
            ("b7b8q*", [" b7", " b8", " q*"], 2),
            ("b7B8Q*", [" b7", " B8Q*"], 2),
            ("b7B8q*", [" b7", " B8q*"], 2),
            ("B7-b8=Q*", [" B7-b8=Q*"], 2),
            ("B7-b8=q*", [" B7-b8=q*"], 2),
            ("B7-B8=Q*", [" B7-B8=Q*"], 2),
            ("B7-B8=q*", [" B7-B8=q*"], 2),
            ("b7-b8=Q*", [" b7", " -b8", " =Q*"], 2),
            ("b7-b8=q*", [" b7", " -b8", " =q*"], 2),
            ("b7-B8=Q*", [" b7", " -B8=Q*"], 2),
            ("b7-B8=q*", [" b7", " -B8=q*"], 2),
            ("B7-b8Q*", [" B7-b8Q*"], 2),
            ("B7-b8q*", [" B7-b8q*"], 2),
            ("B7-B8Q*", [" B7-B8Q*"], 2),
            ("B7-B8q*", [" B7-B8q*"], 2),
            ("b7-b8Q*", [" b7", " -b8", " Q*"], 2),
            ("b7-b8q*", [" b7", " -b8", " q*"], 2),
            ("b7-B8Q*", [" b7", " -B8Q*"], 2),
            ("b7-B8q*", [" b7", " -B8q*"], 2),
            ("Bb8=Q*", [" Bb8", " =Q*"], 2),
            ("Bb8=q*", [" Bb8", " =q*"], 2),
            ("BB8=Q*", [" BB8=Q*"], 2),
            ("BB8=q*", [" BB8=q*"], 2),
            ("bb8=Q*", [" bb8=Q*"], 2),
            ("bb8=q*", [" bb8=q*"], 2),
            ("bB8=Q*", [" bB8=Q*"], 2),
            ("bB8=q*", [" bB8=q*"], 2),
            ("Bb8Q*", [" Bb8", " Q*"], 2),
            ("Bb8q*", [" Bb8", " q*"], 2),
            ("BB8Q*", [" BB8Q*"], 2),
            ("BB8q*", [" BB8q*"], 2),
            ("bb8Q*", [" bb8Q*"], 2),
            ("bb8q*", [" bb8q*"], 2),
            ("bB8Q*", [" bB8Q*"], 2),
            ("bB8q*", [" bB8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_01_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1p6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", [" B2xc1", " =Q*"], 2),
            ("B2xc1=q*", [" B2xc1", " =q*"], 2),
            ("B2xC1=Q*", [" B2xC1=Q*"], 2),
            ("B2xC1=q*", [" B2xC1=q*"], 2),
            ("b2xc1=Q*", [" b2", " xc1", " =Q*"], 2),
            ("b2xc1=q*", ["b2", " xc1", " =q*"], 3),  # tolerate "b2" and 3.
            ("b2xC1=Q*", [" b2", " xC1=Q*"], 2),
            ("b2xC1=q*", [" b2", " xC1=q*"], 2),
            ("B2xc1Q*", [" B2xc1", " Q*"], 2),
            ("B2xc1q*", [" B2xc1", " q*"], 2),
            ("B2xC1Q*", [" B2xC1Q*"], 2),
            ("B2xC1q*", [" B2xC1q*"], 2),
            ("b2xc1Q*", [" b2", " xc1", " Q*"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1Q*"], 2),
            ("b2xC1q*", [" b2", " xC1q*"], 2),
            ("Bxc1=Q*", [" Bxc1", " =Q*"], 2),
            ("Bxc1=q*", [" Bxc1", " =q*"], 2),
            ("BxC1=Q*", [" BxC1=Q*"], 2),
            ("BxC1=q*", [" BxC1=q*"], 2),
            ("bxc1=Q*", ["bxc1=Q", "*"], None),
            ("bxc1=q*", [" bxc1=q*"], 2),
            ("bxC1=Q*", [" bxC1=Q*"], 2),
            ("bxC1=q*", [" bxC1=q*"], 2),
            ("Bxc1Q*", [" Bxc1", " Q*"], 2),
            ("Bxc1q*", [" Bxc1", " q*"], 2),
            ("BxC1Q*", [" BxC1Q*"], 2),
            ("BxC1q*", [" BxC1q*"], 2),
            ("bxc1Q*", [" bxc1Q*"], 2),
            ("bxc1q*", [" bxc1q*"], 2),
            ("bxC1Q*", [" bxC1Q*"], 2),
            ("bxC1q*", [" bxC1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_01_pawn_promotion_b1_or_too_much_precision(self):
        fen = '[FEN"4K3/8/8/8/8/8/1pB5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1=Q*", [" B2b1", " =Q*"], 2),
            ("B2b1=q*", [" B2b1", " =q*"], 2),
            ("B2B1=Q*", [" B2B1=Q*"], 2),
            ("B2B1=q*", [" B2B1=q*"], 2),
            ("b2b1=Q*", [" b2", " b1=Q", " *"], 2),
            ("b2b1=q*", ["b2", " b1", " =q*"], 3),  # tolerate "b2" and 3.
            ("b2B1=Q*", [" b2", " B1=Q*"], 2),
            ("b2B1=q*", [" b2", " B1=q*"], 2),
            ("B2b1Q*", [" B2b1", " Q*"], 2),
            ("B2b1q*", [" B2b1", " q*"], 2),
            ("B2B1Q*", [" B2B1Q*"], 2),
            ("B2B1q*", [" B2B1q*"], 2),
            ("b2b1Q*", [" b2", " b1", " Q*"], 2),
            ("b2b1q*", [" b2", " b1", " q*"], 2),
            ("b2B1Q*", [" b2", " B1Q*"], 2),
            ("b2B1q*", [" b2", " B1q*"], 2),
            ("B2-b1=Q*", [" B2-b1=Q*"], 2),
            ("B2-b1=q*", [" B2-b1=q*"], 2),
            ("B2-B1=Q*", [" B2-B1=Q*"], 2),
            ("B2-B1=q*", [" B2-B1=q*"], 2),
            ("b2-b1=Q*", [" b2", " -b1", " =Q*"], 2),
            ("b2-b1=q*", [" b2", " -b1", " =q*"], 2),
            ("b2-B1=Q*", [" b2", " -B1=Q*"], 2),
            ("b2-B1=q*", [" b2", " -B1=q*"], 2),
            ("B2-b1Q*", [" B2-b1Q*"], 2),
            ("B2-b1q*", [" B2-b1q*"], 2),
            ("B2-B1Q*", [" B2-B1Q*"], 2),
            ("B2-B1q*", [" B2-B1q*"], 2),
            ("b2-b1Q*", [" b2", " -b1", " Q*"], 2),
            ("b2-b1q*", [" b2", " -b1", " q*"], 2),
            ("b2-B1Q*", [" b2", " -B1Q*"], 2),
            ("b2-B1q*", [" b2", " -B1q*"], 2),
            ("Bb1=Q*", [" Bb1", " =Q*"], 2),
            ("Bb1=q*", [" Bb1", " =q*"], 2),
            ("BB1=Q*", [" BB1=Q*"], 2),
            ("BB1=q*", [" BB1=q*"], 2),
            ("bb1=Q*", [" bb1=Q*"], 2),
            ("bb1=q*", [" bb1=q*"], 2),
            ("bB1=Q*", [" bB1=Q*"], 2),
            ("bB1=q*", [" bB1=q*"], 2),
            ("Bb1Q*", [" Bb1", " Q*"], 2),
            ("Bb1q*", [" Bb1", " q*"], 2),
            ("BB1Q*", [" BB1Q*"], 2),
            ("BB1q*", [" BB1q*"], 2),
            ("bb1Q*", [" bb1Q*"], 2),
            ("bb1q*", [" bb1q*"], 2),
            ("bB1Q*", [" bB1Q*"], 2),
            ("bB1q*", [" bB1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_192_01_lan_king_move(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Kd5", "*"])


class PGNOneCharacterAtATime(_NonStrictPGN, StrictPGNOneCharacterAtATime):
    """Repeat PGN tests reading text one character at a time."""

    def setUp(self):
        self.pgn = parser.PGN()

    def test_183_01_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1P6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" B7xc8", " =Q*"], 2),
            ("B7xc8=q*", [" B7xc8", " =q*"], 2),
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", ["b7", " xc8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", [" B7xc8", " Q*"], 2),
            ("B7xc8q*", [" B7xc8", " q*"], 2),
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", [" Bxc8", " =Q*"], 2),
            ("Bxc8=q*", [" Bxc8", " =q*"], 2),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", ["bxc8=Q", "*"], None),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", [" Bxc8", " Q*"], 2),
            ("Bxc8q*", [" Bxc8", " q*"], 2),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_02_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", ["Bxc8", " =Q*"], 3),  #
            ("B7xc8=q*", ["Bxc8", " =q*"], 3),  #
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", ["b7", " xc8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", ["Bxc8", " Q*"], 3),  #
            ("B7xc8q*", ["Bxc8", " q*"], 3),  #
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", ["Bxc8", " =Q*"], 3),
            ("Bxc8=q*", ["Bxc8", " =q*"], 3),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", [" bxc8=Q", " *"], 2),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", ["Bxc8", " Q*"], 3),
            ("Bxc8q*", ["Bxc8", " q*"], 3),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_01_pawn_promotion_b8_or_too_much_precision(self):
        fen = '[FEN"3k4/1Pb5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8=Q*", [" B7b8", " =Q*"], 2),
            ("B7b8=q*", [" B7b8", " =q*"], 2),
            ("B7B8=Q*", [" B7B8=Q*"], 2),
            ("B7B8=q*", [" B7B8=q*"], 2),
            ("b7b8=Q*", [" b7", " b8=Q", " *"], 2),
            ("b7b8=q*", ["b7", " b8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7B8=Q*", [" b7", " B8=Q*"], 2),
            ("b7B8=q*", [" b7", " B8=q*"], 2),
            ("B7b8Q*", [" B7b8", " Q*"], 2),
            ("B7b8q*", [" B7b8", " q*"], 2),
            ("B7B8Q*", [" B7B8Q*"], 2),
            ("B7B8q*", [" B7B8q*"], 2),
            ("b7b8Q*", [" b7", " b8", " Q*"], 2),
            ("b7b8q*", [" b7", " b8", " q*"], 2),
            ("b7B8Q*", [" b7", " B8Q*"], 2),
            ("b7B8q*", [" b7", " B8q*"], 2),
            ("B7-b8=Q*", [" B7-b8=Q*"], 2),
            ("B7-b8=q*", [" B7-b8=q*"], 2),
            ("B7-B8=Q*", [" B7-B8=Q*"], 2),
            ("B7-B8=q*", [" B7-B8=q*"], 2),
            ("b7-b8=Q*", [" b7", " -b8", " =Q*"], 2),
            ("b7-b8=q*", [" b7", " -b8", " =q*"], 2),
            ("b7-B8=Q*", [" b7", " -B8=Q*"], 2),
            ("b7-B8=q*", [" b7", " -B8=q*"], 2),
            ("B7-b8Q*", [" B7-b8Q*"], 2),
            ("B7-b8q*", [" B7-b8q*"], 2),
            ("B7-B8Q*", [" B7-B8Q*"], 2),
            ("B7-B8q*", [" B7-B8q*"], 2),
            ("b7-b8Q*", [" b7", " -b8", " Q*"], 2),
            ("b7-b8q*", [" b7", " -b8", " q*"], 2),
            ("b7-B8Q*", [" b7", " -B8Q*"], 2),
            ("b7-B8q*", [" b7", " -B8q*"], 2),
            ("Bb8=Q*", [" Bb8", " =Q*"], 2),
            ("Bb8=q*", [" Bb8", " =q*"], 2),
            ("BB8=Q*", [" BB8=Q*"], 2),
            ("BB8=q*", [" BB8=q*"], 2),
            ("bb8=Q*", [" bb8=Q*"], 2),
            ("bb8=q*", [" bb8=q*"], 2),
            ("bB8=Q*", [" bB8=Q*"], 2),
            ("bB8=q*", [" bB8=q*"], 2),
            ("Bb8Q*", [" Bb8", " Q*"], 2),
            ("Bb8q*", [" Bb8", " q*"], 2),
            ("BB8Q*", [" BB8Q*"], 2),
            ("BB8q*", [" BB8q*"], 2),
            ("bb8Q*", [" bb8Q*"], 2),
            ("bb8q*", [" bb8q*"], 2),
            ("bB8Q*", [" bB8Q*"], 2),
            ("bB8q*", [" bB8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_01_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1p6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", [" B2xc1", " =Q*"], 2),
            ("B2xc1=q*", [" B2xc1", " =q*"], 2),
            ("B2xC1=Q*", [" B2xC1=Q*"], 2),
            ("B2xC1=q*", [" B2xC1=q*"], 2),
            ("b2xc1=Q*", [" b2", " xc1", " =Q*"], 2),
            ("b2xc1=q*", ["b2", " xc1", " =q*"], 3),  # tolerate "b2" and 3.
            ("b2xC1=Q*", [" b2", " xC1=Q*"], 2),
            ("b2xC1=q*", [" b2", " xC1=q*"], 2),
            ("B2xc1Q*", [" B2xc1", " Q*"], 2),
            ("B2xc1q*", [" B2xc1", " q*"], 2),
            ("B2xC1Q*", [" B2xC1Q*"], 2),
            ("B2xC1q*", [" B2xC1q*"], 2),
            ("b2xc1Q*", [" b2", " xc1", " Q*"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1Q*"], 2),
            ("b2xC1q*", [" b2", " xC1q*"], 2),
            ("Bxc1=Q*", [" Bxc1", " =Q*"], 2),
            ("Bxc1=q*", [" Bxc1", " =q*"], 2),
            ("BxC1=Q*", [" BxC1=Q*"], 2),
            ("BxC1=q*", [" BxC1=q*"], 2),
            ("bxc1=Q*", ["bxc1=Q", "*"], None),
            ("bxc1=q*", [" bxc1=q*"], 2),
            ("bxC1=Q*", [" bxC1=Q*"], 2),
            ("bxC1=q*", [" bxC1=q*"], 2),
            ("Bxc1Q*", [" Bxc1", " Q*"], 2),
            ("Bxc1q*", [" Bxc1", " q*"], 2),
            ("BxC1Q*", [" BxC1Q*"], 2),
            ("BxC1q*", [" BxC1q*"], 2),
            ("bxc1Q*", [" bxc1Q*"], 2),
            ("bxc1q*", [" bxc1q*"], 2),
            ("bxC1Q*", [" bxC1Q*"], 2),
            ("bxC1q*", [" bxC1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_01_pawn_promotion_b1_or_too_much_precision(self):
        fen = '[FEN"4K3/8/8/8/8/8/1pB5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1=Q*", [" B2b1", " =Q*"], 2),
            ("B2b1=q*", [" B2b1", " =q*"], 2),
            ("B2B1=Q*", [" B2B1=Q*"], 2),
            ("B2B1=q*", [" B2B1=q*"], 2),
            ("b2b1=Q*", [" b2", " b1=Q", " *"], 2),
            ("b2b1=q*", ["b2", " b1", " =q*"], 3),  # tolerate "b2" and 3.
            ("b2B1=Q*", [" b2", " B1=Q*"], 2),
            ("b2B1=q*", [" b2", " B1=q*"], 2),
            ("B2b1Q*", [" B2b1", " Q*"], 2),
            ("B2b1q*", [" B2b1", " q*"], 2),
            ("B2B1Q*", [" B2B1Q*"], 2),
            ("B2B1q*", [" B2B1q*"], 2),
            ("b2b1Q*", [" b2", " b1", " Q*"], 2),
            ("b2b1q*", [" b2", " b1", " q*"], 2),
            ("b2B1Q*", [" b2", " B1Q*"], 2),
            ("b2B1q*", [" b2", " B1q*"], 2),
            ("B2-b1=Q*", [" B2-b1=Q*"], 2),
            ("B2-b1=q*", [" B2-b1=q*"], 2),
            ("B2-B1=Q*", [" B2-B1=Q*"], 2),
            ("B2-B1=q*", [" B2-B1=q*"], 2),
            ("b2-b1=Q*", [" b2", " -b1", " =Q*"], 2),
            ("b2-b1=q*", [" b2", " -b1", " =q*"], 2),
            ("b2-B1=Q*", [" b2", " -B1=Q*"], 2),
            ("b2-B1=q*", [" b2", " -B1=q*"], 2),
            ("B2-b1Q*", [" B2-b1Q*"], 2),
            ("B2-b1q*", [" B2-b1q*"], 2),
            ("B2-B1Q*", [" B2-B1Q*"], 2),
            ("B2-B1q*", [" B2-B1q*"], 2),
            ("b2-b1Q*", [" b2", " -b1", " Q*"], 2),
            ("b2-b1q*", [" b2", " -b1", " q*"], 2),
            ("b2-B1Q*", [" b2", " -B1Q*"], 2),
            ("b2-B1q*", [" b2", " -B1q*"], 2),
            ("Bb1=Q*", [" Bb1", " =Q*"], 2),
            ("Bb1=q*", [" Bb1", " =q*"], 2),
            ("BB1=Q*", [" BB1=Q*"], 2),
            ("BB1=q*", [" BB1=q*"], 2),
            ("bb1=Q*", [" bb1=Q*"], 2),
            ("bb1=q*", [" bb1=q*"], 2),
            ("bB1=Q*", [" bB1=Q*"], 2),
            ("bB1=q*", [" bB1=q*"], 2),
            ("Bb1Q*", [" Bb1", " Q*"], 2),
            ("Bb1q*", [" Bb1", " q*"], 2),
            ("BB1Q*", [" BB1Q*"], 2),
            ("BB1q*", [" BB1q*"], 2),
            ("bb1Q*", [" bb1Q*"], 2),
            ("bb1q*", [" bb1q*"], 2),
            ("bB1Q*", [" bB1Q*"], 2),
            ("bB1q*", [" bB1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_192_01_lan_king_move(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Kd5", "*"])


class PGNExtendByOneCharacter(_NonStrictPGN, StrictPGNExtendByOneCharacter):
    """Repeat PGN tests reading text in two chunks, last is length 1."""

    def setUp(self):
        self.pgn = parser.PGN()

    def test_183_01_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1P6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" B7xc8", " =Q*"], 2),
            ("B7xc8=q*", [" B7xc8", " =q*"], 2),
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", ["b7", " xc8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", [" B7xc8", " Q*"], 2),
            ("B7xc8q*", [" B7xc8", " q*"], 2),
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", [" Bxc8", " =Q*"], 2),
            ("Bxc8=q*", [" Bxc8", " =q*"], 2),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", ["bxc8=Q", "*"], None),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", [" Bxc8", " Q*"], 2),
            ("Bxc8q*", [" Bxc8", " q*"], 2),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_02_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", ["Bxc8", " =Q*"], 3),  #
            ("B7xc8=q*", ["Bxc8", " =q*"], 3),  #
            ("B7xC8=Q*", [" B7xC8=Q*"], 2),
            ("B7xC8=q*", [" B7xC8=q*"], 2),
            ("b7xc8=Q*", [" b7", " xc8", " =Q*"], 2),
            ("b7xc8=q*", ["b7", " xc8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7xC8=Q*", [" b7", " xC8=Q*"], 2),
            ("b7xC8=q*", [" b7", " xC8=q*"], 2),
            ("B7xc8Q*", ["Bxc8", " Q*"], 3),  #
            ("B7xc8q*", ["Bxc8", " q*"], 3),  #
            ("B7xC8Q*", [" B7xC8Q*"], 2),
            ("B7xC8q*", [" B7xC8q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", ["Bxc8", " =Q*"], 3),
            ("Bxc8=q*", ["Bxc8", " =q*"], 3),
            ("BxC8=Q*", [" BxC8=Q*"], 2),
            ("BxC8=q*", [" BxC8=q*"], 2),
            ("bxc8=Q*", [" bxc8=Q", " *"], 2),
            ("bxc8=q*", [" bxc8=q*"], 2),
            ("bxC8=Q*", [" bxC8=Q*"], 2),
            ("bxC8=q*", [" bxC8=q*"], 2),
            ("Bxc8Q*", ["Bxc8", " Q*"], 3),
            ("Bxc8q*", ["Bxc8", " q*"], 3),
            ("BxC8Q*", [" BxC8Q*"], 2),
            ("BxC8q*", [" BxC8q*"], 2),
            ("bxc8Q*", [" bxc8Q*"], 2),
            ("bxc8q*", [" bxc8q*"], 2),
            ("bxC8Q*", [" bxC8Q*"], 2),
            ("bxC8q*", [" bxC8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_01_pawn_promotion_b8_or_too_much_precision(self):
        fen = '[FEN"3k4/1Pb5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8=Q*", [" B7b8", " =Q*"], 2),
            ("B7b8=q*", [" B7b8", " =q*"], 2),
            ("B7B8=Q*", [" B7B8=Q*"], 2),
            ("B7B8=q*", [" B7B8=q*"], 2),
            ("b7b8=Q*", [" b7", " b8=Q", " *"], 2),
            ("b7b8=q*", ["b7", " b8", " =q*"], 3),  # tolerate "b7" and 3.
            ("b7B8=Q*", [" b7", " B8=Q*"], 2),
            ("b7B8=q*", [" b7", " B8=q*"], 2),
            ("B7b8Q*", [" B7b8", " Q*"], 2),
            ("B7b8q*", [" B7b8", " q*"], 2),
            ("B7B8Q*", [" B7B8Q*"], 2),
            ("B7B8q*", [" B7B8q*"], 2),
            ("b7b8Q*", [" b7", " b8", " Q*"], 2),
            ("b7b8q*", [" b7", " b8", " q*"], 2),
            ("b7B8Q*", [" b7", " B8Q*"], 2),
            ("b7B8q*", [" b7", " B8q*"], 2),
            ("B7-b8=Q*", [" B7-b8=Q*"], 2),
            ("B7-b8=q*", [" B7-b8=q*"], 2),
            ("B7-B8=Q*", [" B7-B8=Q*"], 2),
            ("B7-B8=q*", [" B7-B8=q*"], 2),
            ("b7-b8=Q*", [" b7", " -b8", " =Q*"], 2),
            ("b7-b8=q*", [" b7", " -b8", " =q*"], 2),
            ("b7-B8=Q*", [" b7", " -B8=Q*"], 2),
            ("b7-B8=q*", [" b7", " -B8=q*"], 2),
            ("B7-b8Q*", [" B7-b8Q*"], 2),
            ("B7-b8q*", [" B7-b8q*"], 2),
            ("B7-B8Q*", [" B7-B8Q*"], 2),
            ("B7-B8q*", [" B7-B8q*"], 2),
            ("b7-b8Q*", [" b7", " -b8", " Q*"], 2),
            ("b7-b8q*", [" b7", " -b8", " q*"], 2),
            ("b7-B8Q*", [" b7", " -B8Q*"], 2),
            ("b7-B8q*", [" b7", " -B8q*"], 2),
            ("Bb8=Q*", [" Bb8", " =Q*"], 2),
            ("Bb8=q*", [" Bb8", " =q*"], 2),
            ("BB8=Q*", [" BB8=Q*"], 2),
            ("BB8=q*", [" BB8=q*"], 2),
            ("bb8=Q*", [" bb8=Q*"], 2),
            ("bb8=q*", [" bb8=q*"], 2),
            ("bB8=Q*", [" bB8=Q*"], 2),
            ("bB8=q*", [" bB8=q*"], 2),
            ("Bb8Q*", [" Bb8", " Q*"], 2),
            ("Bb8q*", [" Bb8", " q*"], 2),
            ("BB8Q*", [" BB8Q*"], 2),
            ("BB8q*", [" BB8q*"], 2),
            ("bb8Q*", [" bb8Q*"], 2),
            ("bb8q*", [" bb8q*"], 2),
            ("bB8Q*", [" bB8Q*"], 2),
            ("bB8q*", [" bB8q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_01_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1p6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", [" B2xc1", " =Q*"], 2),
            ("B2xc1=q*", [" B2xc1", " =q*"], 2),
            ("B2xC1=Q*", [" B2xC1=Q*"], 2),
            ("B2xC1=q*", [" B2xC1=q*"], 2),
            ("b2xc1=Q*", [" b2", " xc1", " =Q*"], 2),
            ("b2xc1=q*", ["b2", " xc1", " =q*"], 3),  # tolerate "b2" and 3.
            ("b2xC1=Q*", [" b2", " xC1=Q*"], 2),
            ("b2xC1=q*", [" b2", " xC1=q*"], 2),
            ("B2xc1Q*", [" B2xc1", " Q*"], 2),
            ("B2xc1q*", [" B2xc1", " q*"], 2),
            ("B2xC1Q*", [" B2xC1Q*"], 2),
            ("B2xC1q*", [" B2xC1q*"], 2),
            ("b2xc1Q*", [" b2", " xc1", " Q*"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1Q*"], 2),
            ("b2xC1q*", [" b2", " xC1q*"], 2),
            ("Bxc1=Q*", [" Bxc1", " =Q*"], 2),
            ("Bxc1=q*", [" Bxc1", " =q*"], 2),
            ("BxC1=Q*", [" BxC1=Q*"], 2),
            ("BxC1=q*", [" BxC1=q*"], 2),
            ("bxc1=Q*", ["bxc1=Q", "*"], None),
            ("bxc1=q*", [" bxc1=q*"], 2),
            ("bxC1=Q*", [" bxC1=Q*"], 2),
            ("bxC1=q*", [" bxC1=q*"], 2),
            ("Bxc1Q*", [" Bxc1", " Q*"], 2),
            ("Bxc1q*", [" Bxc1", " q*"], 2),
            ("BxC1Q*", [" BxC1Q*"], 2),
            ("BxC1q*", [" BxC1q*"], 2),
            ("bxc1Q*", [" bxc1Q*"], 2),
            ("bxc1q*", [" bxc1q*"], 2),
            ("bxC1Q*", [" bxC1Q*"], 2),
            ("bxC1q*", [" bxC1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_01_pawn_promotion_b1_or_too_much_precision(self):
        fen = '[FEN"4K3/8/8/8/8/8/1pB5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1=Q*", [" B2b1", " =Q*"], 2),
            ("B2b1=q*", [" B2b1", " =q*"], 2),
            ("B2B1=Q*", [" B2B1=Q*"], 2),
            ("B2B1=q*", [" B2B1=q*"], 2),
            ("b2b1=Q*", [" b2", " b1=Q", " *"], 2),
            ("b2b1=q*", ["b2", " b1", " =q*"], 3),  # tolerate "b2" and 3.
            ("b2B1=Q*", [" b2", " B1=Q*"], 2),
            ("b2B1=q*", [" b2", " B1=q*"], 2),
            ("B2b1Q*", [" B2b1", " Q*"], 2),
            ("B2b1q*", [" B2b1", " q*"], 2),
            ("B2B1Q*", [" B2B1Q*"], 2),
            ("B2B1q*", [" B2B1q*"], 2),
            ("b2b1Q*", [" b2", " b1", " Q*"], 2),
            ("b2b1q*", [" b2", " b1", " q*"], 2),
            ("b2B1Q*", [" b2", " B1Q*"], 2),
            ("b2B1q*", [" b2", " B1q*"], 2),
            ("B2-b1=Q*", [" B2-b1=Q*"], 2),
            ("B2-b1=q*", [" B2-b1=q*"], 2),
            ("B2-B1=Q*", [" B2-B1=Q*"], 2),
            ("B2-B1=q*", [" B2-B1=q*"], 2),
            ("b2-b1=Q*", [" b2", " -b1", " =Q*"], 2),
            ("b2-b1=q*", [" b2", " -b1", " =q*"], 2),
            ("b2-B1=Q*", [" b2", " -B1=Q*"], 2),
            ("b2-B1=q*", [" b2", " -B1=q*"], 2),
            ("B2-b1Q*", [" B2-b1Q*"], 2),
            ("B2-b1q*", [" B2-b1q*"], 2),
            ("B2-B1Q*", [" B2-B1Q*"], 2),
            ("B2-B1q*", [" B2-B1q*"], 2),
            ("b2-b1Q*", [" b2", " -b1", " Q*"], 2),
            ("b2-b1q*", [" b2", " -b1", " q*"], 2),
            ("b2-B1Q*", [" b2", " -B1Q*"], 2),
            ("b2-B1q*", [" b2", " -B1q*"], 2),
            ("Bb1=Q*", [" Bb1", " =Q*"], 2),
            ("Bb1=q*", [" Bb1", " =q*"], 2),
            ("BB1=Q*", [" BB1=Q*"], 2),
            ("BB1=q*", [" BB1=q*"], 2),
            ("bb1=Q*", [" bb1=Q*"], 2),
            ("bb1=q*", [" bb1=q*"], 2),
            ("bB1=Q*", [" bB1=Q*"], 2),
            ("bB1=q*", [" bB1=q*"], 2),
            ("Bb1Q*", [" Bb1", " Q*"], 2),
            ("Bb1q*", [" Bb1", " q*"], 2),
            ("BB1Q*", [" BB1Q*"], 2),
            ("BB1q*", [" BB1q*"], 2),
            ("bb1Q*", [" bb1Q*"], 2),
            ("bb1q*", [" bb1q*"], 2),
            ("bB1Q*", [" bB1Q*"], 2),
            ("bB1q*", [" bB1q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_192_01_lan_king_move(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Kd5", "*"])


class FEN(StrictFEN):
    """Provide FEN and SetUp tag tests only for Game version of parser."""

    def setUp(self):
        self.pgn = parser.PGN()


class Disambiguate(StrictDisambiguate):
    """Movetext disambiguation tests only.  StrictPGN tests are not done.

    The strictness rules on movetext precision are relaxed.

    The PGN specification states movetext should use exactly the precision
    needed to describe the move.  These tests verify, for example, Rcc7 is
    stated when two rooks on rank 7 can legally move to c7; and is allowed
    when only one rook can legally move to c7 (from rank 7 or file c).

    """

    def setUp(self):
        self.pgn = parser.PGN()

    def test_512_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_513_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_518_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_519_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_527_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_529_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_534_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_544_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qe6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_545_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qb3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_547_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_548_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_556_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_563_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_565_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb3e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_571_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_572_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_579_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_612_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_613_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_618_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_619_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_627_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_629_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_634_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_644_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_645_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_647_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_648_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_656_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_663_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_665_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_671_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_672_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_679_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_711_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re1e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_712_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re6e3*'
        )
        self.assertEqual(games[0].state, None)

    def test_811_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_812_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xe3*'
        )
        self.assertEqual(games[0].state, None)


class DisambiguateTextPGN(Disambiguate):
    """Movetext disambiguation tests only.  StrictPGN tests are not done.

    The strictness rules on movetext precision are relaxed.

    The PGN specification states movetext should use exactly the precision
    needed to describe the move.  These tests verify, for example, Rcc7 is
    stated when two rooks on rank 7 can legally move to c7; and is allowed
    when only one rook can legally move to c7 (from rank 7 or file c).

    """

    def setUp(self):
        self.pgn = parser.PGN(game_class=game_text_pgn.GameTextPGN)

    def test_505_disambiguate_move_needed(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"]'
                    '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6Xd8Kh3*'
                )
            )
        )
        self.assertEqual(games[0].state, 3)
        self.assertEqual(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]',
                "Qf6xd8",
            ],
        )

    # Redundant precision removed but GameTextPGN does not allow 'X' for 'x'.
    # Compare with test_811_disambiguate_move_needed.
    def test_821_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1Xe3*'
        )
        self.assertEqual(games[0].state, 3)
        self.assertEqual(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]',
                "R1xe3",
            ],
        )

    # Redundant precision removed but GameTextPGN does not allow 'E3' for 'e3'.
    # Compare with test_812_disambiguate_move_needed.
    def test_822_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xE3*'
        )
        self.assertEqual(games[0].state, 3)
        self.assertEqual(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]',
                "R6xe3",
            ],
        )


class DisambiguateIgnoreCasePGN(DisambiguateTextPGN):
    """Movetext disambiguation tests only.  StrictPGN tests are not done.

    The strictness rules on movetext precision are relaxed.

    The PGN specification states movetext should use exactly the precision
    needed to describe the move.  These tests verify, for example, Rcc7 is
    stated when two rooks on rank 7 can legally move to c7; and is allowed
    when only one rook can legally move to c7 (from rank 7 or file c).

    """

    def setUp(self):
        self.pgn = parser.PGN(
            game_class=game_ignore_case_pgn.GameIgnoreCasePGN
        )

    def test_505_disambiguate_move_needed(self):
        games = self.get(
            "".join(
                (
                    '[SetUp"1"]'
                    '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6Xd8Kh3*'
                )
            )
        )
        self.assertEqual(games[0].state, None)
        self.assertEqual(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]',
                "Qf6xd8",
                "Kh3",
                "*",
            ],
        )

    def test_819_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]RbXe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_820_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6Xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_821_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1Xe3*'
        )
        self.assertEqual(games[0].state, None)

    def test_822_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xE3*'
        )
        self.assertEqual(games[0].state, None)

    def test_823_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6Xe3*'
        )
        self.assertEqual(games[0].state, None)


class RAV(StrictRAV):
    """Provide tests for Game version of parser."""

    def setUp(self):
        self.pgn = parser.PGN()


class _NonStrictText:
    """Override StrictPGN tests which have a different outcome, but same for
    both, in GameTextPGN and GameIgnoreCasePGN tests.

    Usage is 'class C(_NonStrictText, StrictPGN)'.

    For example, Game class allows Nge2 when a knight on c3 is pinned against
    the king on e1, while GameStrictPGN class does not allow Nge2.

    """

    # StrictPGN version gives one game with state False and one tokens.
    def test_002_a_character(self):
        ae = self.assertEqual
        games = self.get("A")
        ae(len(games), 0)

    # StrictPGN version gives one game with state False and one tokens.
    def test_003_a_word(self):
        ae = self.assertEqual
        games = self.get("abcdef123")
        ae(len(games), 0)

    # StrictPGN version gives one game with state False and six tokens.
    def test_004_a_sentence(self):
        ae = self.assertEqual
        games = self.get("The cat sat on the mat")
        ae(len(games), 0)

    # StrictPGN version includes semicolon and text after.
    def test_008_05_tag_and_semicolon_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"];*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]'])

    # StrictPGN version includes percent and text after.
    def test_008_06_tag_and_percent_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]'])

    # StrictPGN version gives two games.
    # games[1].state is False and 'ff[B"b"]' token is kept.
    def test_021_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"]d41-0')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])

    # StrictPGN version gives two games.
    # games[1].state is False and 'ff[B"b"]' token is kept.
    def test_022_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1]._state, None)
        ae(games[1]._text, ["d4", "1-0"])

    # StrictPGN version gives two games.
    # games[1].state is False and 'ff[B"b"]' token is kept.
    def test_023_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] 1. d4 1-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1]._state, None)
        ae(games[1]._text, ["d4", "1-0"])

    # StrictPGN version gives three games.
    # games[0] is same and games[1] becomes games[2] with games[1] for 'ff'
    # token as an error.
    def test_024_legal_game_gash_space_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff [B"b"]d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', "d4", "1-0"])

    # StrictPGN version gives three games.
    # games[0] is same and games[1] becomes games[2] with games[1] for 'ff'
    # token as an error.
    def test_025_legal_game_gash_newline_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff\n[B"b"]d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', "d4", "1-0"])

    # StrictPGN version gives three games.
    # games[0] is same and games[1] becomes games[2] with games[1] for 'ff'
    # token as an error.
    def test_026_legal_game_gash_space_newline_legal_game_both_with_moves(
        self,
    ):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff \n[B"b"]d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "*"])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', "d4", "1-0"])

    # StrictPGN version gives three games.
    # games[0] is same and games[1] becomes games[2] with games[1] for 'ff'
    # token as an error.
    # This one, with realistic tags and movetext, occurs in a TWIC file.
    def test_028_legal_game_and_gash_and_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]1. e4 1-0 ff [B"b"] 1. d4 1-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "e4", "1-0"])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', "d4", "1-0"])

    # StrictPGN version gives error too.
    def test_051_1_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' {C;c\n<r>e4(d4)[B"b"'])

    # StrictPGN version gives error too.
    def test_051_2_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' {C;c\n<r>e4(d4)[B"b"]'])

    # StrictPGN version gives error too.
    def test_063_1_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' <r;c\n{C}e4(d4)[B"b"'])

    # StrictPGN version gives error too.
    def test_063_2_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' <r;c\n{C}e4(d4)[B"b"]'])

    # StrictPGN version gives error with captured text.
    def test_065_bare_escaped(self):
        ae = self.assertEqual
        games = self.get("%Run for your life!")
        ae(len(games), 0)

    # StrictPGN version gives error with captured text.
    def test_065_01_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get("%Run for your life!*")
        ae(len(games), 0)

    # StrictPGN version gives error too, but '%!' token is kept.
    def test_066_tag_and_escaped(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]'])

    # StrictPGN version gives error too, but '%!*' token is kept.
    def test_067_tag_and_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]'])

    # StrictPGN version gives error, having kept the '%!\n' token.
    def test_068_tag_and_terminated_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!\n*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "*"])

    # StrictPGN version gives error, having kept the
    # '%!{C}<r>e4(d4)[B"b"]%e' token.
    def test_069_tag_and_terminated_escaped_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!{C}<r>e4(d4)[B"b"]%e\n*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', "*"])

    # StrictPGN version gives error too, but '-' token is kept.
    def test_072_castles_O_O_incomplete_0(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-O-'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]', "O-O"],
        )

    # Added on seeing results when crash traced to game in crafty06_03.pgn.
    # Strict version gives an error: c4c5 is long algebraic notation.
    def test_113_start_rav_after_moves_after_nags(self):
        ae = self.assertEqual
        games = self.get("$10$21$10$22c4e5c4c5(()")
        ae(len(games), 1)
        ae(games[0].state, 10)
        ae(
            games[0]._text,
            ["$10", "$21", "$10", "$22", "c4", "e5", "c5", "(", "(", ")"],
        )

    # Added after changes to convertion of chess engine responses to PGN.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_115_long_algebraic_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e7e5")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5"])

    # Added after changes to convertion of chess engine responses to PGN.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_116_long_algebraic_pawn_move_game_terminated(self):
        ae = self.assertEqual
        games = self.get("e4e7e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "*"])

    # Changed while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_163_bxc8q.
    def test_120_05_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    # The significant tokens from pgn_files test_055 which caused an exception
    # in the 'text' classes.
    def test_121_09_rav_sequences(self):
        ae = self.assertEqual
        games = self.get("c4(263,500 USD)! (2729) - Svidler,P (")
        ae(len(games), 1)
        ae(games[0].state, 4)
        ae(games[0]._text, ["c4", "(", "(", ")", " ("])

    # Changed while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_162_dxc8q.
    def test_123_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    # Changed while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_128_bxc8 (and test_129_bxc8).
    def test_125_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    # Compare with test_161_bxc8.
    def test_129_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    def test_140_partial_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A"a')
        ae(len(games), 0)

    def test_141_bad_value_in_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A:"a" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A:"a"]'])

    def test_142_bad_value_in_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A""a" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"\\"a"]'])

    def test_143_bad_value_in_tag_02(self):
        ae = self.assertEqual
        games = self.get('[A""a"][B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"\\"a"]', '[B"b"]'])

    # Added while fixing Little.pgn upper case processing.
    def test_164_long_algebraic_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5d2d4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "d4", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_165_long_algebraic_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5d2-d4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "d4", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_167_01_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5b2-b4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "b4", "*"])

    def test_167_02_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]b6-b7*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]',
                "b7",
                "*",
            ],
        )

    def test_167_03_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]b7-b8=Q*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]',
                "b8=Q",
                "*",
            ],
        )
        ae(games[0].state, None)

    def test_167_04_long_algebraic_white_f_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]f7-f8=Q*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]',
                "f8=Q",
                "*",
            ],
        )
        ae(games[0].state, None)

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_168_long_algebraic_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e7e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_169_long_algebraic_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e7-e5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_171_long_algebraic_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4b7-b5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "b5", "*"])

    def test_180_01_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("N1f3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["Nf3", "*"])

    def test_180_02_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("Ngf3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["Nf3", "*"])

    def test_180_03_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("Ng1f3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["Nf3", "*"])

    def test_180_04_long_algebraic(self):
        ae = self.assertEqual
        games = self.get("Ng1-f3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["Nf3", "*"])

    def test_181_01_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5B1d3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "Bd3", "*"])

    def test_182_01_pawn_capture_bc4_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    [
                        '[SetUp"1"]',
                        '[FEN"5k2/8/8/8/2n5/1B6/8/5K2 w - - 0 1"]',
                        "B3xc4*",
                    ]
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"5k2/8/8/8/2n5/1B6/8/5K2 w - - 0 1"]',
                "Bxc4",
                "*",
            ],
        )

    def test_191_01_lan_promote_and_capture(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"4n3/3P4/8/8/8/8/8/k6K w - - 0 1"]',
            "=QKa2*",
        ]
        move = ["d7", "e8"]
        for delimiter in ("x",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(games[0].state, None)
                ae(games[0]._text[-3:], ["dxe8=Q", "Ka2", "*"])

    def test_191_02_lan_promote_and_capture(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"4n3/3P4/8/8/8/8/8/k6K w - - 0 1"]',
            "=QKa2*",
        ]
        move = ["d7", "e8"]
        for delimiter in ("x",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(games[0].state, None)
                ae(games[0]._text[-3:], ["dxe8=Q", "Ka2", "*"])


class GameTextPGN(_NonStrictText, StrictPGN):
    """Provide tests for GameTextPGN version of parser."""

    def setUp(self):
        self.pgn = parser.PGN(game_class=game_text_pgn.GameTextPGN)

    def test_118_01_BxC4_without_B_on_board(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/8/8/2p5/1P6/8/6K1 w - - 0 1"]BxC4*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"6k1/8/8/8/2p5/1P6/8/6K1 w - - 0 1"]'],
        )

    def test_118_02_BxC4_with_B_on_board(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/8/8/2p5/1P6/1B6/6K1 w - - 0 1"]BxC4*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"6k1/8/8/8/2p5/1P6/1B6/6K1 w - - 0 1"]'],
        )

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_06_bcd_bishop(self):
        fen = ['[FEN"r1n1n2k/2B5/2B4b/8/8/2b4B/2b5/R1N1N2K ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("bxa8*", [], 2, "w"),
            ("bb8*", [], 2, "w"),
            ("bxc8*", [], 2, "w"),
            ("bd8*", [], 2, "w"),
            ("bxe8*", [], 2, "w"),
            ("bxa1*", [], 2, "b"),
            ("bb1*", [], 2, "b"),
            ("bxc1*", [], 2, "b"),
            ("bd1*", [], 2, "b"),
            ("bxe1*", [], 2, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_08_bcd_bishop(self):
        fen = ['[FEN"8/r1n1n2k/2B3b1/2B5/2b5/2b3B1/R1N1N2K/8 ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("bxa7*", [" bxa7", " *"], 2, "w"),
            ("bb7*", [], 2, "w"),
            ("bxc7*", [" bxc7", " *"], 2, "w"),
            ("bd7*", [], 2, "w"),
            ("bxe7*", [" bxe7", " *"], 2, "w"),
            ("bxa2*", [" bxa2", " *"], 2, "b"),
            ("bb2*", [], 2, "b"),
            ("bxc2*", [" bxc2", " *"], 2, "b"),
            ("bd2*", [], 2, "b"),
            ("bxe2*", [" bxe2", " *"], 2, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_09_bcd_bishop(self):
        fen = ['[FEN"8/r1n1n2k/2B3b1/2B5/2b5/2b3B1/R1N1N2K/8 ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("b5xa7*", [" bxa7", " *"], 2, "w"),
            ("b6b7*", [" b6", " b7", " *"], 2, "w"),
            ("b4xc7*", [" bxc7", " *"], 2, "w"),
            ("b6d7*", [" b6", " d7", " *"], 2, "w"),
            ("b5xe7*", [" bxe7", " *"], 2, "w"),
            ("b4xa2*", [" bxa2", " *"], 2, "b"),
            ("b3b2*", [" b3", " b2", " *"], 2, "b"),
            ("b5xc2*", [" bxc2", " *"], 2, "b"),
            ("b3d2*", [" b3", " d2", " *"], 2, "b"),
            ("b4xe2*", [" bxe2", " *"], 2, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    def test_120_03_bxc8_Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=Qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "bxc8=Q",
            ],
        )

    def test_120_04_bxc8Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8Qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8Q",
                " qg3*",
            ],
        )

    def test_120_06_bxc8_q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    def test_120_07_bxc8_qx(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=q qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    def test_124_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    def test_126_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    def test_127_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
            ],
        )

    def test_128_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]', "Bxc8"],
        )

    def test_130_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    # Added to test '\n' in tag value.
    def test_141_bad_value_in_tag_02(self):
        ae = self.assertEqual
        games = self.get('[A:"\na" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A:"\na"]'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # The first 'b', in 'bb5', caused an error when lower case allowed.
    def test_157_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get("e4e5nf3nc6bb5a6*")
        ae(len(games), 1)
        ae(games[0]._state, 2)
        ae(games[0]._text, ["e4", "e5"])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # The first 'b', in 'bb4', caused an error when lower case allowed.
    def test_158_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get("e4c5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6*")
        ae(len(games), 1)
        ae(games[0]._state, 4)
        ae(games[0]._text, ["e4", "c5", "d4", "e6"])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # The first 'b', in 'bb5', caused an error when lower case allowed.
    def test_159_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get("e4e5nf3nc6Bb5a6*")
        ae(len(games), 1)
        ae(games[0]._state, 2)
        ae(games[0]._text, ["e4", "e5"])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # The first 'b', in 'bb4', caused an error when lower case allowed.
    def test_160_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get("e4c5d4e6nf3cxd4nxd4a6nc3qc7g3Bb4Bd2nf6*")
        ae(len(games), 1)
        ae(games[0]._state, 4)
        ae(games[0]._text, ["e4", "c5", "d4", "e6"])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_129_bxc8.
    def test_161_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_123_dxc8q.
    def test_162_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_120_05_bxc8q.
    def test_163_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            ['[SetUp"1"]', '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'],
        )

    # Added while fixing Little.pgn upper case processing.
    # b2b4 is redundant precision, not long algebraic notation.
    def test_166_01_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5b2b4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "b4", "*"])

    # b6b7 is redundant precision, not long algebraic notation.
    def test_166_02_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]b6b7*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]',
                "b7",
                "*",
            ],
        )

    # Rejected like this in all cases except 'ignore case', where it is seen
    # as an attempted bishop move from rank 7 to b8, 'B7b8'.
    def test_166_03_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]b7b8=Q*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]',
                "b7",
                " b8=Q",
                " *",
            ],
        )
        ae(games[0].state, 3)

    # Always rejected as an attempt to move a pawn from f6 to f7.
    def test_166_04_long_algebraic_white_f_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]f7f8=Q*'
        )
        ae(len(games), 1)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]',
                "f7",
                " f8=Q",
                " *",
            ],
        )
        ae(games[0].state, 3)

    # Added while fixing Little.pgn upper case processing.
    # b7b5 is redundant precision, not long algebraic notation.
    def test_170_long_algebraic_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4b7b5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "b5", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_172_long_algebraic_uc_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5D2D4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5"])

    # Added while fixing Little.pgn upper case processing.
    def test_173_long_algebraic_uc_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5D2-D4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5"])

    # Added while fixing Little.pgn upper case processing.
    def test_174_long_algebraic_uc_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5B2B4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5"])

    # Added while fixing Little.pgn upper case processing.
    def test_175_long_algebraic_uc_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5B2-B4*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5"])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_176_long_algebraic_uc_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4E7E5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4"])

    # Added while fixing Little.pgn upper case processing.
    def test_177_long_algebraic_uc_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4E7-E5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4"])

    # Added while fixing Little.pgn upper case processing.
    def test_178_long_algebraic_uc_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4B7B5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4"])

    # Added while fixing Little.pgn upper case processing.
    def test_179_long_algebraic_uc_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4B7-B5*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4"])

    def test_181_02_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5B1D3*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5"])

    def test_181_03_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5b1D3*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5"])

    def test_181_04_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5b1d3*")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " b1", " *"])

    def test_182_01_pawn_capture_bc4_or_too_much_precision(self):
        fen = '[FEN"8/8/8/8/2bk4/1P6/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B3xc4*", [" B3xc4", " *"], 2),
            ("B3xC4*", [], 2),
            ("b3xc4*", ["bxc4", "*"], None),
            ("b3xC4*", ["bxc4"], 3),
            ("Bxc4*", [" Bxc4", " *"], 2),
            ("BxC4*", [], 2),
            ("bxc4*", ["bxc4", "*"], None),
            ("bxC4*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_182_02_pawn_capture_bc4_or_too_much_precision(self):
        fen = '[FEN"8/8/8/8/2bk4/1B6/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B3xc4*", ["Bxc4", "*"], None),
            ("B3xC4*", [], 2),
            ("b3xc4*", [" bxc4", " *"], 2),
            ("b3xC4*", [" b3", " xC4*"], 2),
            ("Bxc4*", ["Bxc4", "*"], None),
            ("BxC4*", [], 2),
            ("bxc4*", [" bxc4", " *"], 2),
            ("bxC4*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Ignore unrecognized tokens is done in text mode when _state is not None,
    # but why some and not others in this test?
    def test_183_01_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1P6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" B7xc8", " =Q*"], 2),
            ("B7xc8=q*", [" B7xc8", " =q*"], 2),
            ("B7xC8=Q*", [], 2),
            ("B7xC8=q*", [], 2),
            ("b7xc8=Q*", ["bxc8=Q", "*"], None),
            ("b7xc8=q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("b7xC8=Q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("b7xC8=q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("B7xc8Q*", [" B7xc8", " Q*"], 2),
            ("B7xc8q*", [" B7xc8", " q*"], 2),
            ("B7xC8Q*", [], 2),
            ("B7xC8q*", [], 2),
            ("b7xc8Q*", [" bxc8Q", " *"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", [" Bxc8", " =Q*"], 2),
            ("Bxc8=q*", [" Bxc8", " =q*"], 2),
            ("BxC8=Q*", [], 2),
            ("BxC8=q*", [], 2),
            ("bxc8=Q*", ["bxc8=Q", "*"], None),
            ("bxc8=q*", [], 2),
            ("bxC8=Q*", [], 2),
            ("bxC8=q*", [], 2),
            ("Bxc8Q*", [" Bxc8", " Q*"], 2),
            ("Bxc8q*", [" Bxc8", " q*"], 2),
            ("BxC8Q*", [], 2),
            ("BxC8q*", [], 2),
            ("bxc8Q*", [" bxc8Q", " *"], 2),
            ("bxc8q*", [], 2),
            ("bxC8Q*", [], 2),
            ("bxC8q*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_02_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", ["Bxc8"], 3),
            ("B7xc8=q*", ["Bxc8"], 3),
            ("B7xC8=Q*", [], 2),
            ("B7xC8=q*", [], 2),
            ("b7xc8=Q*", [" bxc8=Q", " *"], 2),
            ("b7xc8=q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("b7xC8=Q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("b7xC8=q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("B7xc8Q*", ["Bxc8"], 3),
            ("B7xc8q*", ["Bxc8"], 3),
            ("B7xC8Q*", [], 2),
            ("B7xC8q*", [], 2),
            ("b7xc8Q*", [" bxc8Q", " *"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8Q*"], 2),
            ("b7xC8q*", [" b7", " xC8q*"], 2),
            ("Bxc8=Q*", ["Bxc8"], 3),
            ("Bxc8=q*", ["Bxc8"], 3),
            ("BxC8=Q*", [], 2),
            ("BxC8=q*", [], 2),
            ("bxc8=Q*", [" bxc8=Q", " *"], 2),
            ("bxc8=q*", [], 2),
            ("bxC8=Q*", [], 2),
            ("bxC8=q*", [], 2),
            ("Bxc8Q*", ["Bxc8"], 3),
            ("Bxc8q*", ["Bxc8"], 3),
            ("BxC8Q*", [], 2),
            ("BxC8q*", [], 2),
            ("bxc8Q*", [" bxc8Q", " *"], 2),
            ("bxc8q*", [], 2),
            ("bxC8Q*", [], 2),
            ("bxC8q*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_03_pawn_capture_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8*", ["Bxc8", "*"], None),
            ("B7xC8*", [], 2),
            ("b7xc8*", [" b7", " xc8", " *"], 2),
            ("b7xC8*", [" b7", " xC8*"], 2),
            ("Bxc8*", ["Bxc8", "*"], None),
            ("BxC8*", [], 2),
            ("bxc8*", [], 2),
            ("bxC8*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_01_pawn_promotion_b8_or_too_much_precision(self):
        fen = '[FEN"3k4/1Pb5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8=Q*", [" B7b8", " =Q*"], 2),
            ("B7b8=q*", [" B7b8", " =q*"], 2),
            ("B7B8=Q*", [], 2),
            ("B7B8=q*", [], 2),
            ("b7b8=Q*", ["b7", " b8=Q", " *"], 3),  # tolerate "b7" and 3.
            ("b7b8=q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("b7B8=Q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("b7B8=q*", ["b7"], 3),  # tolerate "b7" and 3.
            ("B7b8Q*", [" B7b8", " Q*"], 2),
            ("B7b8q*", [" B7b8", " q*"], 2),
            ("B7B8Q*", [], 2),
            ("B7B8q*", [], 2),
            ("b7b8Q*", [" b7", " b8Q", " *"], 2),
            ("b7b8q*", [" b7", " b8", " q*"], 2),
            ("b7B8Q*", [" b7", " B8Q*"], 2),
            ("b7B8q*", [" b7", " B8q*"], 2),
            ("B7-b8=Q*", [" B7b8", " =Q*"], 2),
            ("B7-b8=q*", [" B7b8", " =q*"], 2),
            ("B7-B8=Q*", [], 2),
            ("B7-B8=q*", [], 2),
            ("b7-b8=Q*", ["b8=Q", "*"], None),
            ("b7-b8=q*", [" b7", " -b8", " =q*"], 2),
            ("b7-B8=Q*", [" b7", " -B8=Q*"], 2),
            ("b7-B8=q*", [" b7", " -B8=q*"], 2),
            ("B7-b8Q*", [" B7b8", " Q*"], 2),
            ("B7-b8q*", [" B7b8", " q*"], 2),
            ("B7-B8Q*", [], 2),
            ("B7-B8q*", [], 2),
            ("b7-b8Q*", [" b8", " *"], 2),
            ("b7-b8q*", [" b7", " -b8", " q*"], 2),
            ("b7-B8Q*", [" b7", " -B8Q*"], 2),
            ("b7-B8q*", [" b7", " -B8q*"], 2),
            ("Bb8=Q*", [" Bb8", " =Q*"], 2),
            ("Bb8=q*", [" Bb8", " =q*"], 2),
            ("BB8=Q*", [], 2),
            ("BB8=q*", [], 2),
            ("bb8=Q*", [], 2),
            ("bb8=q*", [], 2),
            ("bB8=Q*", [], 2),
            ("bB8=q*", [], 2),
            ("Bb8Q*", [" Bb8", " Q*"], 2),
            ("Bb8q*", [" Bb8", " q*"], 2),
            ("BB8Q*", [], 2),
            ("BB8q*", [], 2),
            ("bb8Q*", [], 2),
            ("bb8q*", [], 2),
            ("bB8Q*", [], 2),
            ("bB8q*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_02_bishop_c7_to_b8(self):
        fen = '[FEN"4k3/2B5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8*", ["Bb8", "*"], None),
            ("B7B8*", [], 2),
            ("b7b8*", [" b7", " b8", " *"], 2),
            ("b7B8*", [" b7", " B8*"], 2),
            ("B7-b8*", ["Bb8", "*"], None),
            ("B7-B8*", [], 2),
            ("b7-b8*", [" b7", " -b8", " *"], 2),
            ("b7-B8*", [" b7", " -B8*"], 2),
            ("Bb8*", ["Bb8", "*"], None),
            ("BB8*", [], 2),
            ("bb8*", [], 2),
            ("bB8*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_03_bishop_c6_to_b7(self):
        fen = '[FEN"3k4/8/2B5/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B6b7*", ["Bb7", "*"], None),
            ("B6B7*", [], 2),
            ("b6b7*", [" b6", " b7", " *"], 2),
            ("b6B7*", [" b6", " B7*"], 2),
            ("B6-b7*", ["Bb7", "*"], None),
            ("B6-B7*", [], 2),
            ("b6-b7*", [" b7", " *"], 2),
            ("b6-B7*", [" b6", " -B7*"], 2),
            ("Bb7*", ["Bb7", "*"], None),
            ("BB7*", [], 2),
            ("bb7*", [], 2),
            ("bB7*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_185_01_pawn_capture_bc5_or_too_much_precision(self):
        fen = '[FEN"4K3/8/1p6/2Bk4/8/8/8/8 b - - 0 1"]'
        for string, tokens, state in (
            ("B6xc5*", [" B6xc5", " *"], 2),
            ("B6xC5*", [], 2),
            ("b6xc5*", ["bxc5", "*"], None),
            ("b6xC5*", ["bxc5"], 3),
            ("Bxc5*", [" Bxc5", " *"], 2),
            ("BxC5*", [], 2),
            ("bxc5*", ["bxc5", "*"], None),
            ("bxC5*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_185_02_pawn_capture_bc5_or_too_much_precision(self):
        fen = '[FEN"4K3/8/1b6/2Bk4/8/8/8/8 b - - 0 1"]'
        for string, tokens, state in (
            ("B6xc5*", ["Bxc5", "*"], None),
            ("B6xC5*", [], 2),
            ("b6xc5*", [" bxc5", " *"], 2),
            ("b6xC5*", [" b6", " xC5*"], 2),
            ("Bxc5*", ["Bxc5", "*"], None),
            ("BxC5*", [], 2),
            ("bxc5*", [" bxc5", " *"], 2),
            ("bxC5*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Ignore unrecognized tokens is done in text mode when _state is not None,
    # but why some and not others in this test?
    def test_186_01_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1p6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", [" B2xc1", " =Q*"], 2),
            ("B2xc1=q*", [" B2xc1", " =q*"], 2),
            ("B2xC1=Q*", [], 2),
            ("B2xC1=q*", [], 2),
            ("b2xc1=Q*", ["bxc1=Q", "*"], None),
            ("b2xc1=q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("b2xC1=Q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("b2xC1=q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("B2xc1Q*", [" B2xc1", " Q*"], 2),
            ("B2xc1q*", [" B2xc1", " q*"], 2),
            ("B2xC1Q*", [], 2),
            ("B2xC1q*", [], 2),
            ("b2xc1Q*", [" bxc1Q", " *"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1Q*"], 2),
            ("b2xC1q*", [" b2", " xC1q*"], 2),
            ("Bxc1=Q*", [" Bxc1", " =Q*"], 2),
            ("Bxc1=q*", [" Bxc1", " =q*"], 2),
            ("BxC1=Q*", [], 2),
            ("BxC1=q*", [], 2),
            ("bxc1=Q*", ["bxc1=Q", "*"], None),
            ("bxc1=q*", [], 2),
            ("bxC1=Q*", [], 2),
            ("bxC1=q*", [], 2),
            ("Bxc1Q*", [" Bxc1", " Q*"], 2),
            ("Bxc1q*", [" Bxc1", " q*"], 2),
            ("BxC1Q*", [], 2),
            ("BxC1q*", [], 2),
            ("bxc1Q*", [" bxc1Q", " *"], 2),
            ("bxc1q*", [], 2),
            ("bxC1Q*", [], 2),
            ("bxC1q*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_02_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1b6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", ["Bxc1"], 3),
            ("B2xc1=q*", ["Bxc1"], 3),
            ("B2xC1=Q*", [], 2),
            ("B2xC1=q*", [], 2),
            ("b2xc1=Q*", [" bxc1=Q", " *"], 2),
            ("b2xc1=q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("b2xC1=Q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("b2xC1=q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("B2xc1Q*", ["Bxc1"], 3),
            ("B2xc1q*", ["Bxc1"], 3),
            ("B2xC1Q*", [], 2),
            ("B2xC1q*", [], 2),
            ("b2xc1Q*", [" bxc1Q", " *"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1Q*"], 2),
            ("b2xC1q*", [" b2", " xC1q*"], 2),
            ("Bxc1=Q*", ["Bxc1"], 3),
            ("Bxc1=q*", ["Bxc1"], 3),
            ("BxC1=Q*", [], 2),
            ("BxC1=q*", [], 2),
            ("bxc1=Q*", [" bxc1=Q", " *"], 2),
            ("bxc1=q*", [], 2),
            ("bxC1=Q*", [], 2),
            ("bxC1=q*", [], 2),
            ("Bxc1Q*", ["Bxc1"], 3),
            ("Bxc1q*", ["Bxc1"], 3),
            ("BxC1Q*", [], 2),
            ("BxC1q*", [], 2),
            ("bxc1Q*", [" bxc1Q", " *"], 2),
            ("bxc1q*", [], 2),
            ("bxC1Q*", [], 2),
            ("bxC1q*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_03_pawn_capture_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1b6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1*", ["Bxc1", "*"], None),
            ("B2xC1*", [], 2),
            ("b2xc1*", [" b2", " xc1", " *"], 2),
            ("b2xC1*", [" b2", " xC1*"], 2),
            ("Bxc1*", ["Bxc1", "*"], None),
            ("BxC1*", [], 2),
            ("bxc1*", [], 2),
            ("bxC1*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_01_pawn_promotion_b1_or_too_much_precision(self):
        fen = '[FEN"4K3/8/8/8/8/8/1pB5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1=Q*", [" B2b1", " =Q*"], 2),
            ("B2b1=q*", [" B2b1", " =q*"], 2),
            ("B2B1=Q*", [], 2),
            ("B2B1=q*", [], 2),
            ("b2b1=Q*", ["b2", " b1=Q", " *"], 3),  # tolerate "b2" and 3.
            ("b2b1=q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("b2B1=Q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("b2B1=q*", ["b2"], 3),  # tolerate "b2" and 3.
            ("B2b1Q*", [" B2b1", " Q*"], 2),
            ("B2b1q*", [" B2b1", " q*"], 2),
            ("B2B1Q*", [], 2),
            ("B2B1q*", [], 2),
            ("b2b1Q*", [" b2", " b1Q", " *"], 2),
            ("b2b1q*", [" b2", " b1", " q*"], 2),
            ("b2B1Q*", [" b2", " B1Q*"], 2),
            ("b2B1q*", [" b2", " B1q*"], 2),
            ("B2-b1=Q*", [" B2b1", " =Q*"], 2),
            ("B2-b1=q*", [" B2b1", " =q*"], 2),
            ("B2-B1=Q*", [], 2),
            ("B2-B1=q*", [], 2),
            ("b2-b1=Q*", ["b1=Q", "*"], None),
            ("b2-b1=q*", [" b2", " -b1", " =q*"], 2),
            ("b2-B1=Q*", [" b2", " -B1=Q*"], 2),
            ("b2-B1=q*", [" b2", " -B1=q*"], 2),
            ("B2-b1Q*", [" B2b1", " Q*"], 2),
            ("B2-b1q*", [" B2b1", " q*"], 2),
            ("B2-B1Q*", [], 2),
            ("B2-B1q*", [], 2),
            ("b2-b1Q*", [" b1", " *"], 2),
            ("b2-b1q*", [" b2", " -b1", " q*"], 2),
            ("b2-B1Q*", [" b2", " -B1Q*"], 2),
            ("b2-B1q*", [" b2", " -B1q*"], 2),
            ("Bb1=Q*", [" Bb1", " =Q*"], 2),
            ("Bb1=q*", [" Bb1", " =q*"], 2),
            ("BB1=Q*", [], 2),
            ("BB1=q*", [], 2),
            ("bb1=Q*", [], 2),
            ("bb1=q*", [], 2),
            ("bB1=Q*", [], 2),
            ("bB1=q*", [], 2),
            ("Bb1Q*", [" Bb1", " Q*"], 2),
            ("Bb1q*", [" Bb1", " q*"], 2),
            ("BB1Q*", [], 2),
            ("BB1q*", [], 2),
            ("bb1Q*", [], 2),
            ("bb1q*", [], 2),
            ("bB1Q*", [], 2),
            ("bB1q*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_02_bishop_c2_to_b1(self):
        fen = '[FEN"4K3/8/8/8/8/8/2b5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1*", ["Bb1", "*"], None),
            ("B2B1*", [], 2),
            ("b2b1*", [" b2", " b1", " *"], 2),
            ("b2B1*", [" b2", " B1*"], 2),
            ("B2-b1*", ["Bb1", "*"], None),
            ("B2-B1*", [], 2),
            ("b2-b1*", [" b2", " -b1", " *"], 2),
            ("b2-B1*", [" b2", " -B1*"], 2),
            ("Bb1*", ["Bb1", "*"], None),
            ("BB1*", [], 2),
            ("bb1*", [], 2),
            ("bB1*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_03_bishop_c3_to_b2(self):
        fen = '[FEN"4K3/8/8/8/8/2b5/8/3k4 b - - 0 1"]'
        for string, tokens, state in (
            ("B3b2*", ["Bb2", "*"], None),
            ("B3B2*", [], 2),
            ("b3b2*", [" b3", " b2", " *"], 2),
            ("b3B2*", [" b3", " B2*"], 2),
            ("B3-b2*", ["Bb2", "*"], None),
            ("B3-B2*", [], 2),
            ("b3-b2*", [" b2", " *"], 2),
            ("b3-B2*", [" b3", " -B2*"], 2),
            ("Bb2*", ["Bb2", "*"], None),
            ("BB2*", [], 2),
            ("bb2*", [], 2),
            ("bB2*", [], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Added for Github issue 3.
    # Different outcome in GameStrictPGN tests.
    def test_188_03_bad_pass_Z1(self):
        ae = self.assertEqual
        games = self.get("e4Z1d4*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4"])

    # Added for Github issue 3.
    # Different outcome in GameStrictPGN tests.
    def test_188_04_bad_pass_Z1(self):
        ae = self.assertEqual
        games = self.get("e4 Z1 d4*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " d4", " *"])

    # Different outcome in GameStrictPGN tests.
    def test_189_12_nag_and_game_termination_marker(self):
        # Fourth and fifth '1's are treated as a move number indicator and
        # ignored.
        ae = self.assertEqual
        games = self.get("e4e5$11111-0")
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text, ["e4", "e5", "$111"])

    def test_192_01_lan_king_move(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Kd5", "*"])

    def test_192_02_lan_king_move_hyphen(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("-",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Kd5", "*"])

    def test_192_03_lan_knight_move_hyphen(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/5N2/8/8/k6K w - - 0 1"]',
            "*",
        ]
        move = ["Nf4", "d5"]
        for delimiter in ("-",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Nd5", "*"])


class GameIgnoreCasePGN(_NonStrictText, StrictPGN):
    """Provide tests for GameIgnoreCasePGN version of parser.

    GameIgnoreCasePGN provides a few simple tests of lower and upper case
    movetext, but runs the full set of tests for normal case PGN through the
    GameIgnoreCasePGN class.

    The PGNLower and PGNUpper classes in test_pgn_files run a number of full
    games through GameIgnoreCasePGN with all movetext converted to lower and
    upper case respectively.  None of the games include the FEN tag which is
    case sensitive.

    """

    def setUp(self):
        self.pgn = parser.PGN(
            game_class=game_ignore_case_pgn.GameIgnoreCasePGN
        )

    # Added after changes to convertion of chess engine responses to PGN.
    def test_114_long_algebraic_pawn_move_wrong_direction(self):
        ae = self.assertEqual
        games = self.get("e4e5e4e3")
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ["e4", "e5", " e4"])

    def test_118_01_BxC4_without_B_on_board(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/8/8/2p5/1P6/8/6K1 w - - 0 1"]BxC4*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"6k1/8/8/8/2p5/1P6/8/6K1 w - - 0 1"]',
                "bxc4",
                "*",
            ],
        )

    def test_118_02_BxC4_with_B_on_board(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/8/8/2p5/1P6/1B6/6K1 w - - 0 1"]BxC4*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"6k1/8/8/8/2p5/1P6/1B6/6K1 w - - 0 1"]',
                "bxc4",
                "*",
            ],
        )

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_06_bcd_bishop(self):
        fen = ['[FEN"r1n1n2k/2B5/2B4b/8/8/2b4B/2b5/R1N1N2K ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("bxa8*", ["Bxa8", "*"], None, "w"),
            ("bb8*", ["Bb8", "*"], None, "w"),
            ("bxc8*", ["Bxc8", "*"], None, "w"),
            ("bd8*", ["Bd8", "*"], None, "w"),
            ("bxe8*", ["Bxe8", "*"], None, "w"),
            ("bxa1*", ["Bxa1", "*"], None, "b"),
            ("bb1*", ["Bb1", "*"], None, "b"),
            ("bxc1*", ["Bxc1", "*"], None, "b"),
            ("bd1*", ["Bd1", "*"], None, "b"),
            ("bxe1*", ["Bxe1", "*"], None, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_07_bcd_bishop(self):
        fen = ['[FEN"r1n1n2k/2B5/2B4b/8/8/2b4B/2b5/R1N1N2K ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("b6xa8*", ["Bxa8", "*"], None, "w"),
            ("b7b8*", ["Bb8", "*"], None, "w"),
            ("b3xc8*", ["Bxc8", "*"], None, "w"),
            ("b7d8*", ["Bd8", "*"], None, "w"),
            ("b6xe8*", ["Bxe8", "*"], None, "w"),
            ("b3xa1*", ["Bxa1", "*"], None, "b"),
            ("b2b1*", ["Bb1", "*"], None, "b"),
            ("b6xc1*", ["Bxc1", "*"], None, "b"),
            ("b2d1*", ["Bd1", "*"], None, "b"),
            ("b3xe1*", ["Bxe1", "*"], None, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_08_bcd_bishop(self):
        fen = ['[FEN"8/r1n1n2k/2B3b1/2B5/2b5/2b3B1/R1N1N2K/8 ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("bxa7*", ["Bxa7", "*"], None, "w"),
            ("bb7*", ["Bb7", "*"], None, "w"),
            ("bxc7*", ["Bxc7", "*"], None, "w"),
            ("bd7*", ["Bd7", "*"], None, "w"),
            ("bxe7*", ["Bxe7", "*"], None, "w"),
            ("bxa2*", ["Bxa2", "*"], None, "b"),
            ("bb2*", ["Bb2", "*"], None, "b"),
            ("bxc2*", ["Bxc2", "*"], None, "b"),
            ("bd2*", ["Bd2", "*"], None, "b"),
            ("bxe2*", ["Bxe2", "*"], None, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    # b1=Q gave error in GameIgnoreCasePGN when working on version 2.1.
    def test_119_09_bcd_bishop(self):
        fen = ['[FEN"8/r1n1n2k/2B3b1/2B5/2b5/2b3B1/R1N1N2K/8 ', ' - - 0 1"]']
        for string, tokens, state, side in (
            ("b5xa7*", ["Bxa7", "*"], None, "w"),
            ("b6b7*", ["Bb7", "*"], None, "w"),
            ("b4xc7*", ["Bxc7", "*"], None, "w"),
            ("b6d7*", ["Bd7", "*"], None, "w"),
            ("b5xe7*", ["Bxe7", "*"], None, "w"),
            ("b4xa2*", ["Bxa2", "*"], None, "b"),
            ("b3b2*", ["Bb2", "*"], None, "b"),
            ("b5xc2*", ["Bxc2", "*"], None, "b"),
            ("b3d2*", ["Bd2", "*"], None, "b"),
            ("b4xe2*", ["Bxe2", "*"], None, "b"),
        ):
            self.b_is_bishop_or_b_pawn(side.join(fen), string, tokens, state)

    def test_120_03_bxc8_Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=Qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "bxc8=Q",
                "Qg3",
                "*",
            ],
        )

    # Detected tokens changed following test_119_06_bcd_bishop at version 2.1.
    def test_120_04_bxc8Q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8Qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " Bxc8",
                " Qqg3*",
            ],
        )

    # Compare with test_163_bxc8q.
    # Detected tokens changed following test_119_06_bcd_bishop at version 2.1.
    def test_120_05_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                " Bxc8",
                " qqg3*",
            ],
        )

    def test_120_06_bxc8_q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "bxc8=Q",
                "Qg3",
                "*",
            ],
        )

    def test_120_07_bxc8_qx(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=q qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "bxc8=Q",
                "Qg3",
                "*",
            ],
        )

    def test_124_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "dxc8=Q",
                "Qg3",
                "*",
            ],
        )

    # Detected tokens changed following test_119_06_bcd_bishop at version 2.1.
    def test_125_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
                "Qg3",
                "*",
            ],
        )

    # Detected tokens changed following test_119_06_bcd_bishop at version 2.1.
    def test_126_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
                "Qg3",
                "*",
            ],
        )

    def test_127_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
                "Qg3",
                "*",
            ],
        )

    def test_128_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
                "Qg3",
                "*",
            ],
        )

    # Detected tokens changed following test_119_06_bcd_bishop at version 2.1.
    def test_129_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
                "Qg3",
                "*",
            ],
        )

    # Detected tokens changed following test_119_06_bcd_bishop at version 2.1.
    def test_130_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
                "Bxc8",
                "Qg3",
                "*",
            ],
        )

    # Added to test '\n' in tag value.
    def test_141_bad_value_in_tag_02(self):
        ae = self.assertEqual
        games = self.get('[A:"\na" ]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A:"\na"]'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    # The first 'b', in 'b4', caused an error.
    def test_154_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("b4b5Nf3((Nc3)a3(e3))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "b4",
                "b5",
                "Nf3",
                "(",
                "(",
                "Nc3",
                ")",
                "a3",
                "(",
                "e3",
                ")",
                ")",
                "*",
            ],
        )

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    # The first 'b', in 'b4', caused an error.
    def test_156_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get("b4h5Nf3((Nc3)a3(e3))*")
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "b4",
                "h5",
                "Nf3",
                "(",
                "(",
                "Nc3",
                ")",
                "a3",
                "(",
                "e3",
                ")",
                ")",
                "*",
            ],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # 'bb5' is accepted.
    def test_157_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get("e4e5nf3nc6bb5a6*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "*"])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # 'bb4' and 'bd2' are accepted.
    def test_158_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get("e4c5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "e4",
                "c5",
                "d4",
                "e6",
                "Nf3",
                "cxd4",
                "Nxd4",
                "a6",
                "Nc3",
                "Qc7",
                "g3",
                "Bb4",
                "Bd2",
                "Nf6",
                "*",
            ],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # 'Bb5' is accepted.
    def test_159_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get("e4e5nf3nc6Bb5a6*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "*"])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # 'Bb4Bd2' is accepted.
    def test_160_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get("e4c5d4e6nf3cxd4nxd4a6nc3qc7g3Bb4Bd2nf6*")
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(
            games[0]._text,
            [
                "e4",
                "c5",
                "d4",
                "e6",
                "Nf3",
                "cxd4",
                "Nxd4",
                "a6",
                "Nc3",
                "Qc7",
                "g3",
                "Bb4",
                "Bd2",
                "Nf6",
                "*",
            ],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_129_bxc8.
    def test_161_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
                " bxc8=Q",
                " g3",
                " *",
            ],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_123_dxc8q.
    def test_162_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "dxc8=Q",
                "Qg3",
                "*",
            ],
        )

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_120_05_bxc8q.
    def test_163_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
                "bxc8=Q",
                "Qg3",
                "*",
            ],
        )

    # Added while fixing Little.pgn upper case processing.
    # b2b4 is redundant precision, not long algebraic notation.
    def test_166_01_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5b2b4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "b4", "*"])

    # b6b7 is redundant precision, not long algebraic notation.
    def test_166_02_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]b6b7*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/8/1P6/8/8/8/8/4K3 w - - 0 1"]',
                "b7",
                "*",
            ],
        )

    def test_166_03_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]b7b8=Q*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/1P6/8/8/8/8/8/4K3 w - - 0 1"]',
                "b8=Q",
                "*",
            ],
        )

    def test_166_04_long_algebraic_white_f_pawn_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]f7f8=Q*'
        )
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(
            games[0]._text,
            [
                '[SetUp"1"]',
                '[FEN"3k4/5P2/8/8/8/8/8/4K3 w - - 0 1"]',
                "f8=Q",
                "*",
            ],
        )

    # Added while fixing Little.pgn upper case processing.
    # b7b5 is redundant precision, not long algebraic notation.
    def test_170_long_algebraic_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4b7b5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "b5", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_172_long_algebraic_uc_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5D2D4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "d4", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_173_long_algebraic_uc_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5D2-D4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "d4", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_174_long_algebraic_uc_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4e5B2B4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "b4", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_175_long_algebraic_uc_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4e5B2-B4*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "b4", "*"])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_176_long_algebraic_uc_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4E7E5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_177_long_algebraic_uc_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4E7-E5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_178_long_algebraic_uc_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get("e4B7B5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "b5", "*"])

    # Added while fixing Little.pgn upper case processing.
    def test_179_long_algebraic_uc_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get("e4B7-B5*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "b5", "*"])

    def test_181_02_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5B1D3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "Bd3", "*"])

    def test_181_03_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5b1D3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "Bd3", "*"])

    def test_181_04_pawn_move_or_too_much_precision(self):
        ae = self.assertEqual
        games = self.get("e4e5b1d3*")
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ["e4", "e5", "Bd3", "*"])

    def test_182_01_pawn_capture_bc4_or_too_much_precision(self):
        fen = '[FEN"8/8/8/8/2bk4/1P6/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B3xc4*", ["bxc4", "*"], None),
            ("B3xC4*", ["bxc4", "*"], None),
            ("b3xc4*", ["bxc4", "*"], None),
            ("b3xC4*", ["bxc4", "*"], None),
            ("Bxc4*", ["bxc4", "*"], None),
            ("BxC4*", ["bxc4", "*"], None),
            ("bxc4*", ["bxc4", "*"], None),
            ("bxC4*", ["bxc4", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_182_02_pawn_capture_bc4_or_too_much_precision(self):
        fen = '[FEN"8/8/8/8/2bk4/1B6/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B3xc4*", ["Bxc4", "*"], None),
            ("B3xC4*", ["Bxc4", "*"], None),
            ("b3xc4*", ["Bxc4", "*"], None),
            ("b3xC4*", ["Bxc4", "*"], None),
            ("Bxc4*", ["Bxc4", "*"], None),
            ("BxC4*", ["Bxc4", "*"], None),
            ("bxc4*", ["Bxc4", "*"], None),
            ("bxC4*", ["Bxc4", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Like '183_02' but a 'P' is on 'b7'.
    def test_183_01_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1P6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", ["bxc8=Q", "*"], None),
            ("B7xc8=q*", ["bxc8=Q", "*"], None),
            ("B7xC8=Q*", ["bxc8=Q", "*"], None),
            ("B7xC8=q*", ["bxc8=Q", "*"], None),
            ("b7xc8=Q*", ["bxc8=Q", "*"], None),
            ("b7xc8=q*", ["bxc8=Q", "*"], None),
            ("b7xC8=Q*", ["bxc8=Q", "*"], None),
            ("b7xC8=q*", ["bxc8=Q", "*"], None),
            ("B7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("B7xc8q*", [" b7", " xc8", " q*"], 2),
            ("B7xC8Q*", [" b7", " xC8", " Q*"], 2),
            ("B7xC8q*", [" b7", " xC8", " q*"], 2),
            ("b7xc8Q*", [" b7", " xc8", " Q*"], 2),
            ("b7xc8q*", [" b7", " xc8", " q*"], 2),
            ("b7xC8Q*", [" b7", " xC8", " Q*"], 2),
            ("b7xC8q*", [" b7", " xC8", " q*"], 2),
            ("Bxc8=Q*", ["bxc8=Q", "*"], None),
            ("Bxc8=q*", ["bxc8=Q", "*"], None),
            ("BxC8=Q*", ["bxc8=Q", "*"], None),
            ("BxC8=q*", ["bxc8=Q", "*"], None),
            ("bxc8=Q*", ["bxc8=Q", "*"], None),
            ("bxc8=q*", ["bxc8=Q", "*"], None),
            ("bxC8=Q*", ["bxc8=Q", "*"], None),
            ("bxC8=q*", ["bxc8=Q", "*"], None),
            ("Bxc8Q*", [" Bxc8", " Q*"], 2),
            ("Bxc8q*", [" Bxc8", " q*"], 2),
            ("BxC8Q*", [" BxC8", " Q*"], 2),
            ("BxC8q*", [" BxC8", " q*"], 2),
            ("bxc8Q*", [" Bxc8", " Q*"], 2),
            ("bxc8q*", [" Bxc8", " q*"], 2),
            ("bxC8Q*", [" Bxc8", " Q*"], 2),
            ("bxC8q*", [" Bxc8", " q*"], 2),
            ("BxC8ignored*", [" BxC8", " ignored*"], 2),
            ("bxC8ignored*", [" Bxc8", " ignored*"], 2),
            ("Bxc8ignored* *", [" Bxc8", " ignored* ", " *"], 2),
            ("bxc8ignored* *", [" Bxc8", " ignored* ", " *"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Like '183_01' but a 'B' is on 'b7'.
    # When compared the results for 'Bxc8' and 'bxc8' are inconsistent when
    # followed by '=Q' or '=q'.  In isolation the results are fine: see the
    # examples with 'ignored' rather than '=Q' or '=q'.
    def test_183_02_pawn_promotion_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8=Q*", [" bxc8=Q", " *"], 2),
            ("B7xc8=q*", [" bxc8=Q", " *"], 2),
            ("B7xC8=Q*", [" bxc8=Q", " *"], 2),
            ("B7xC8=q*", [" bxc8=Q", " *"], 2),
            ("b7xc8=Q*", [" bxc8=Q", " *"], 2),
            ("b7xc8=q*", [" bxc8=Q", " *"], 2),
            ("b7xC8=Q*", [" bxc8=Q", " *"], 2),
            ("b7xC8=q*", [" bxc8=Q", " *"], 2),
            ("B7xc8Q*", ["Bxc8"], 3),
            ("B7xc8q*", ["Bxc8"], 3),
            ("B7xC8Q*", ["Bxc8"], 3),
            ("B7xC8q*", ["Bxc8"], 3),
            ("b7xc8Q*", ["Bxc8"], 3),
            ("b7xc8q*", ["Bxc8"], 3),
            ("b7xC8Q*", ["Bxc8"], 3),
            ("b7xC8q*", ["Bxc8"], 3),
            ("Bxc8=Q*", ["Bxc8", "*"], None),
            ("Bxc8=q*", ["Bxc8", "*"], None),
            ("BxC8=Q*", ["Bxc8", "*"], None),
            ("BxC8=q*", ["Bxc8", "*"], None),
            ("bxc8=Q*", [" bxc8=Q", " *"], 2),
            ("bxc8=q*", [" bxc8=Q", " *"], 2),
            ("bxC8=Q*", [" bxc8=Q", " *"], 2),
            ("bxC8=q*", [" bxc8=Q", " *"], 2),
            ("Bxc8Q*", ["Bxc8"], 3),
            ("Bxc8q*", ["Bxc8"], 3),
            ("BxC8Q*", ["Bxc8"], 3),
            ("BxC8q*", ["Bxc8"], 3),
            ("bxc8Q*", ["Bxc8"], 3),
            ("bxc8q*", ["Bxc8"], 3),
            ("bxC8Q*", ["Bxc8"], 3),
            ("bxC8q*", ["Bxc8"], 3),
            ("BxC8ignored*", ["Bxc8"], 3),
            ("bxC8ignored*", ["Bxc8"], 3),
            ("Bxc8ignored* *", ["Bxc8", "*"], None),
            ("bxc8ignored* *", ["Bxc8", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_183_03_pawn_capture_bc8_or_too_much_precision(self):
        fen = '[FEN"2bk4/1B6/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7xc8*", ["Bxc8", "*"], None),
            ("B7xC8*", ["Bxc8", "*"], None),
            ("b7xc8*", ["Bxc8", "*"], None),
            ("b7xC8*", ["Bxc8", "*"], None),
            ("Bxc8*", ["Bxc8", "*"], None),
            ("BxC8*", ["Bxc8", "*"], None),
            ("bxc8*", ["Bxc8", "*"], None),
            ("bxC8*", ["Bxc8", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # All tests with '-' should be accepted, like tests _170_*, *_171_*,
    # *_174_*, and *_175_*.
    def test_184_01_pawn_promotion_b8_or_too_much_precision(self):
        fen = '[FEN"3k4/1Pb5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8=Q*", ["b8=Q", "*"], None),
            ("B7b8=q*", ["b8=Q", "*"], None),
            ("B7B8=Q*", ["b8=Q", "*"], None),
            ("B7B8=q*", ["b8=Q", "*"], None),
            ("b7b8=Q*", ["b8=Q", "*"], None),
            ("b7b8=q*", ["b8=Q", "*"], None),
            ("b7B8=Q*", ["b8=Q", "*"], None),
            ("b7B8=q*", ["b8=Q", "*"], None),
            ("B7b8Q*", [" b7", " b8", " Q*"], 2),
            ("B7b8q*", [" b7", " b8", " q*"], 2),
            ("B7B8Q*", [" b7", " B8", " Q*"], 2),
            ("B7B8q*", [" b7", " B8", " q*"], 2),
            ("b7b8Q*", [" b7", " b8", " Q*"], 2),
            ("b7b8q*", [" b7", " b8", " q*"], 2),
            ("b7B8Q*", [" b7", " B8", " Q*"], 2),
            ("b7B8q*", [" b7", " B8", " q*"], 2),
            ("B7-b8=Q*", ["b8=Q", "*"], None),
            ("B7-b8=q*", ["b8=Q", "*"], None),
            ("B7-B8=Q*", ["b8=Q", "*"], None),
            ("B7-B8=q*", ["b8=Q", "*"], None),
            ("b7-b8=Q*", ["b8=Q", "*"], None),
            ("b7-b8=q*", ["b8=Q", "*"], None),
            ("b7-B8=Q*", ["b8=Q", "*"], None),
            ("b7-B8=q*", ["b8=Q", "*"], None),
            ("B7-b8Q*", [" b7", " -b8", " Q*"], 2),
            ("B7-b8q*", [" b7", " -b8", " q*"], 2),
            ("B7-B8Q*", [" b7", " -B8", " Q*"], 2),
            ("B7-B8q*", [" b7", " -B8", " q*"], 2),
            ("b7-b8Q*", [" b7", " -b8", " Q*"], 2),
            ("b7-b8q*", [" b7", " -b8", " q*"], 2),
            ("b7-B8Q*", [" b7", " -B8", " Q*"], 2),
            ("b7-B8q*", [" b7", " -B8", " q*"], 2),
            ("Bb8=Q*", [" Bb8", " =Q", " *"], 2),
            ("Bb8=q*", [" Bb8", " =q", " *"], 2),
            ("BB8=Q*", [" BB8", " =Q", " *"], 2),
            ("BB8=q*", [" BB8", " =q", " *"], 2),
            ("bb8=Q*", [" bb8", " =Q", " *"], 2),
            ("bb8=q*", [" bb8", " =q", " *"], 2),
            ("bB8=Q*", [" bB8", " =Q", " *"], 2),
            ("bB8=q*", [" bB8", " =q", " *"], 2),
            ("Bb8Q*", [" Bb8", " Q*"], 2),
            ("Bb8q*", [" Bb8", " q*"], 2),
            ("BB8Q*", [" BB8", " Q*"], 2),
            ("BB8q*", [" BB8", " q*"], 2),
            ("bb8Q*", [" bb8", " Q*"], 2),
            ("bb8q*", [" bb8", " q*"], 2),
            ("bB8Q*", [" bB8", " Q*"], 2),
            ("bB8q*", [" bB8", " q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_02_bishop_c7_to_b8(self):
        fen = '[FEN"4k3/2B5/8/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B7b8*", ["Bb8", "*"], None),
            ("B7B8*", ["Bb8", "*"], None),
            ("b7b8*", ["Bb8", "*"], None),
            ("b7B8*", ["Bb8", "*"], None),
            ("B7-b8*", ["Bb8", "*"], None),
            ("B7-B8*", ["Bb8", "*"], None),
            ("b7-b8*", ["Bb8", "*"], None),
            ("b7-B8*", ["Bb8", "*"], None),
            ("Bb8*", ["Bb8", "*"], None),
            ("BB8*", ["Bb8", "*"], None),
            ("bb8*", ["Bb8", "*"], None),
            ("bB8*", ["Bb8", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_184_03_bishop_c6_to_b7(self):
        fen = '[FEN"3k4/8/2B5/8/8/8/8/4K3 w - - 0 1"]'
        for string, tokens, state in (
            ("B6b7*", ["Bb7", "*"], None),
            ("B6B7*", ["Bb7", "*"], None),
            ("b6b7*", ["Bb7", "*"], None),
            ("b6B7*", ["Bb7", "*"], None),
            ("B6-b7*", ["Bb7", "*"], None),
            ("B6-B7*", ["Bb7", "*"], None),
            ("b6-b7*", ["Bb7", "*"], None),
            ("b6-B7*", ["Bb7", "*"], None),
            ("Bb7*", ["Bb7", "*"], None),
            ("BB7*", ["Bb7", "*"], None),
            ("bb7*", ["Bb7", "*"], None),
            ("bB7*", ["Bb7", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_185_01_pawn_capture_bc5_or_too_much_precision(self):
        fen = '[FEN"4K3/8/1p6/2Bk4/8/8/8/8 b - - 0 1"]'
        for string, tokens, state in (
            ("B6xc5*", ["bxc5", "*"], None),
            ("B6xC5*", ["bxc5", "*"], None),
            ("b6xc5*", ["bxc5", "*"], None),
            ("b6xC5*", ["bxc5", "*"], None),
            ("Bxc5*", ["bxc5", "*"], None),
            ("BxC5*", ["bxc5", "*"], None),
            ("bxc5*", ["bxc5", "*"], None),
            ("bxC5*", ["bxc5", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_185_02_pawn_capture_bc5_or_too_much_precision(self):
        fen = '[FEN"4K3/8/1b6/2Bk4/8/8/8/8 b - - 0 1"]'
        for string, tokens, state in (
            ("B6xc5*", ["Bxc5", "*"], None),
            ("B6xC5*", ["Bxc5", "*"], None),
            ("b6xc5*", ["Bxc5", "*"], None),
            ("b6xC5*", ["Bxc5", "*"], None),
            ("Bxc5*", ["Bxc5", "*"], None),
            ("BxC5*", ["Bxc5", "*"], None),
            ("bxc5*", ["Bxc5", "*"], None),
            ("bxC5*", ["Bxc5", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Like '183_02' but a 'P' is on 'b7'.
    def test_186_01_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1p6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", ["bxc1=Q", "*"], None),
            ("B2xc1=q*", ["bxc1=Q", "*"], None),
            ("B2xC1=Q*", ["bxc1=Q", "*"], None),
            ("B2xC1=q*", ["bxc1=Q", "*"], None),
            ("b2xc1=Q*", ["bxc1=Q", "*"], None),
            ("b2xc1=q*", ["bxc1=Q", "*"], None),
            ("b2xC1=Q*", ["bxc1=Q", "*"], None),
            ("b2xC1=q*", ["bxc1=Q", "*"], None),
            ("B2xc1Q*", [" b2", " xc1", " Q*"], 2),
            ("B2xc1q*", [" b2", " xc1", " q*"], 2),
            ("B2xC1Q*", [" b2", " xC1", " Q*"], 2),
            ("B2xC1q*", [" b2", " xC1", " q*"], 2),
            ("b2xc1Q*", [" b2", " xc1", " Q*"], 2),
            ("b2xc1q*", [" b2", " xc1", " q*"], 2),
            ("b2xC1Q*", [" b2", " xC1", " Q*"], 2),
            ("b2xC1q*", [" b2", " xC1", " q*"], 2),
            ("Bxc1=Q*", ["bxc1=Q", "*"], None),
            ("Bxc1=q*", ["bxc1=Q", "*"], None),
            ("BxC1=Q*", ["bxc1=Q", "*"], None),
            ("BxC1=q*", ["bxc1=Q", "*"], None),
            ("bxc1=Q*", ["bxc1=Q", "*"], None),
            ("bxc1=q*", ["bxc1=Q", "*"], None),
            ("bxC1=Q*", ["bxc1=Q", "*"], None),
            ("bxC1=q*", ["bxc1=Q", "*"], None),
            ("Bxc1Q*", [" Bxc1", " Q*"], 2),
            ("Bxc1q*", [" Bxc1", " q*"], 2),
            ("BxC1Q*", [" BxC1", " Q*"], 2),
            ("BxC1q*", [" BxC1", " q*"], 2),
            ("bxc1Q*", [" Bxc1", " Q*"], 2),
            ("bxc1q*", [" Bxc1", " q*"], 2),
            ("bxC1Q*", [" Bxc1", " Q*"], 2),
            ("bxC1q*", [" Bxc1", " q*"], 2),
            ("BxC1ignored*", [" BxC1", " ignored*"], 2),
            ("bxC1ignored*", [" Bxc1", " ignored*"], 2),
            ("Bxc1ignored* *", [" Bxc1", " ignored* ", " *"], 2),
            ("bxc1ignored* *", [" Bxc1", " ignored* ", " *"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Like '183_01' but a 'B' is on 'b2'.
    # When compared the results for 'Bxc1' and 'bxc1' are inconsistent when
    # followed by '=Q' or '=q'.  In isolation the results are fine: see the
    # examples with 'ignored' rather than '=Q' or '=q'.
    def test_186_02_pawn_promotion_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1b6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1=Q*", [" bxc1=Q", " *"], 2),
            ("B2xc1=q*", [" bxc1=Q", " *"], 2),
            ("B2xC1=Q*", [" bxc1=Q", " *"], 2),
            ("B2xC1=q*", [" bxc1=Q", " *"], 2),
            ("b2xc1=Q*", [" bxc1=Q", " *"], 2),
            ("b2xc1=q*", [" bxc1=Q", " *"], 2),
            ("b2xC1=Q*", [" bxc1=Q", " *"], 2),
            ("b2xC1=q*", [" bxc1=Q", " *"], 2),
            ("B2xc1Q*", ["Bxc1"], 3),
            ("B2xc1q*", ["Bxc1"], 3),
            ("B2xC1Q*", ["Bxc1"], 3),
            ("B2xC1q*", ["Bxc1"], 3),
            ("b2xc1Q*", ["Bxc1"], 3),
            ("b2xc1q*", ["Bxc1"], 3),
            ("b2xC1Q*", ["Bxc1"], 3),
            ("b2xC1q*", ["Bxc1"], 3),
            ("Bxc1=Q*", ["Bxc1", "*"], None),
            ("Bxc1=q*", ["Bxc1", "*"], None),
            ("BxC1=Q*", ["Bxc1", "*"], None),
            ("BxC1=q*", ["Bxc1", "*"], None),
            ("bxc1=Q*", [" bxc1=Q", " *"], 2),
            ("bxc1=q*", [" bxc1=Q", " *"], 2),
            ("bxC1=Q*", [" bxc1=Q", " *"], 2),
            ("bxC1=q*", [" bxc1=Q", " *"], 2),
            ("Bxc1Q*", ["Bxc1"], 3),
            ("Bxc1q*", ["Bxc1"], 3),
            ("BxC1Q*", ["Bxc1"], 3),
            ("BxC1q*", ["Bxc1"], 3),
            ("bxc1Q*", ["Bxc1"], 3),
            ("bxc1q*", ["Bxc1"], 3),
            ("bxC1Q*", ["Bxc1"], 3),
            ("bxC1q*", ["Bxc1"], 3),
            ("BxC1ignored*", ["Bxc1"], 3),
            ("bxC1ignored*", ["Bxc1"], 3),
            ("Bxc1ignored* *", ["Bxc1", "*"], None),
            ("bxc1ignored* *", ["Bxc1", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_186_03_pawn_capture_bc1_or_too_much_precision(self):
        fen = '[FEN"8/4K3/8/8/8/8/1b6/2Bk4 b - - 0 1"]'
        for string, tokens, state in (
            ("B2xc1*", ["Bxc1", "*"], None),
            ("B2xC1*", ["Bxc1", "*"], None),
            ("b2xc1*", ["Bxc1", "*"], None),
            ("b2xC1*", ["Bxc1", "*"], None),
            ("Bxc1*", ["Bxc1", "*"], None),
            ("BxC1*", ["Bxc1", "*"], None),
            ("bxc1*", ["Bxc1", "*"], None),
            ("bxC1*", ["Bxc1", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # All tests with '-' should be accepted, like tests _170_*, *_171_*,
    # *_174_*, and *_175_*.
    def test_187_01_pawn_promotion_b1_or_too_much_precision(self):
        fen = '[FEN"4K3/8/8/8/8/8/1pB5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1=Q*", ["b1=Q", "*"], None),
            ("B2b1=q*", ["b1=Q", "*"], None),
            ("B2B1=Q*", ["b1=Q", "*"], None),
            ("B2B1=q*", ["b1=Q", "*"], None),
            ("b2b1=Q*", ["b1=Q", "*"], None),
            ("b2b1=q*", ["b1=Q", "*"], None),
            ("b2B1=Q*", ["b1=Q", "*"], None),
            ("b2B1=q*", ["b1=Q", "*"], None),
            ("B2b1Q*", [" b2", " b1", " Q*"], 2),
            ("B2b1q*", [" b2", " b1", " q*"], 2),
            ("B2B1Q*", [" b2", " B1", " Q*"], 2),
            ("B2B1q*", [" b2", " B1", " q*"], 2),
            ("b2b1Q*", [" b2", " b1", " Q*"], 2),
            ("b2b1q*", [" b2", " b1", " q*"], 2),
            ("b2B1Q*", [" b2", " B1", " Q*"], 2),
            ("b2B1q*", [" b2", " B1", " q*"], 2),
            ("B2-b1=Q*", ["b1=Q", "*"], None),
            ("B2-b1=q*", ["b1=Q", "*"], None),
            ("B2-B1=Q*", ["b1=Q", "*"], None),
            ("B2-B1=q*", ["b1=Q", "*"], None),
            ("b2-b1=Q*", ["b1=Q", "*"], None),
            ("b2-b1=q*", ["b1=Q", "*"], None),
            ("b2-B1=Q*", ["b1=Q", "*"], None),
            ("b2-B1=q*", ["b1=Q", "*"], None),
            ("B2-b1Q*", [" b2", " -b1", " Q*"], 2),
            ("B2-b1q*", [" b2", " -b1", " q*"], 2),
            ("B2-B1Q*", [" b2", " -B1", " Q*"], 2),
            ("B2-B1q*", [" b2", " -B1", " q*"], 2),
            ("b2-b1Q*", [" b2", " -b1", " Q*"], 2),
            ("b2-b1q*", [" b2", " -b1", " q*"], 2),
            ("b2-B1Q*", [" b2", " -B1", " Q*"], 2),
            ("b2-B1q*", [" b2", " -B1", " q*"], 2),
            ("Bb1=Q*", [" Bb1", " =Q", " *"], 2),
            ("Bb1=q*", [" Bb1", " =q", " *"], 2),
            ("BB1=Q*", [" BB1", " =Q", " *"], 2),
            ("BB1=q*", [" BB1", " =q", " *"], 2),
            ("bb1=Q*", [" bb1", " =Q", " *"], 2),
            ("bb1=q*", [" bb1", " =q", " *"], 2),
            ("bB1=Q*", [" bB1", " =Q", " *"], 2),
            ("bB1=q*", [" bB1", " =q", " *"], 2),
            ("Bb1Q*", [" Bb1", " Q*"], 2),
            ("Bb1q*", [" Bb1", " q*"], 2),
            ("BB1Q*", [" BB1", " Q*"], 2),
            ("BB1q*", [" BB1", " q*"], 2),
            ("bb1Q*", [" bb1", " Q*"], 2),
            ("bb1q*", [" bb1", " q*"], 2),
            ("bB1Q*", [" bB1", " Q*"], 2),
            ("bB1q*", [" bB1", " q*"], 2),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_02_bishop_c2_to_b1(self):
        fen = '[FEN"4K3/8/8/8/8/8/2b5/4k3 b - - 0 1"]'
        for string, tokens, state in (
            ("B2b1*", ["Bb1", "*"], None),
            ("B2B1*", ["Bb1", "*"], None),
            ("b2b1*", ["Bb1", "*"], None),
            ("b2B1*", ["Bb1", "*"], None),
            ("B2-b1*", ["Bb1", "*"], None),
            ("B2-B1*", ["Bb1", "*"], None),
            ("b2-b1*", ["Bb1", "*"], None),
            ("b2-B1*", ["Bb1", "*"], None),
            ("Bb1*", ["Bb1", "*"], None),
            ("BB1*", ["Bb1", "*"], None),
            ("bb1*", ["Bb1", "*"], None),
            ("bB1*", ["Bb1", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    def test_187_03_bishop_c3_to_b2(self):
        fen = '[FEN"4K3/8/8/8/8/2b5/8/3k4 b - - 0 1"]'
        for string, tokens, state in (
            ("B6b2*", ["Bb2", "*"], None),
            ("B6B2*", ["Bb2", "*"], None),
            ("b6b2*", ["Bb2", "*"], None),
            ("b6B2*", ["Bb2", "*"], None),
            ("B6-b2*", ["Bb2", "*"], None),
            ("B6-B2*", ["Bb2", "*"], None),
            ("b6-b2*", ["Bb2", "*"], None),
            ("b6-B2*", ["Bb2", "*"], None),
            ("Bb2*", ["Bb2", "*"], None),
            ("BB2*", ["Bb2", "*"], None),
            ("bb2*", ["Bb2", "*"], None),
            ("bB2*", ["Bb2", "*"], None),
        ):
            self.b_is_bishop_or_b_pawn(fen, string, tokens, state)

    # Added for Github issue 3.
    # Different outcome in GameStrictPGN tests.
    def test_188_03_bad_pass_Z1(self):
        ae = self.assertEqual
        games = self.get("e4Z1d4*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4"])

    # Added for Github issue 3.
    # Different outcome in GameStrictPGN tests.
    def test_188_04_bad_pass_Z1(self):
        ae = self.assertEqual
        games = self.get("e4 Z1 d4*")
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ["e4", " d4", " *"])

    # Different outcome in GameStrictPGN tests.
    def test_189_12_nag_and_game_termination_marker(self):
        # Fourth and fifth '1's are treated as a move number indicator and
        # ignored.
        ae = self.assertEqual
        games = self.get("e4e5$11111-0")
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text, ["e4", "e5", "$111"])

    def test_191_03_lan_promote_and_capture(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"6Q1/8/4Q3/8/8/8/8/k6K w - - 0 1"]',
            "=QKb2*",
        ]
        move = ["Qe6", "e8"]
        for delimiter in ("-",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, 2)
                ae(games[0]._text[-3:], [" -e8=Q", " Kb2", " *"])

    def test_192_01_lan_king_move(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Kd5", "*"])

    def test_192_02_lan_king_move_hyphen(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/4K3/8/8/k7 w - - 0 1"]',
            "*",
        ]
        move = ["Ke4", "d5"]
        for delimiter in ("-",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Kd5", "*"])

    def test_192_03_lan_knight_move_hyphen(self):
        ae = self.assertEqual
        fen = [
            '[SetUp"1"][FEN"8/8/8/8/5N2/8/8/k6K w - - 0 1"]',
            "*",
        ]
        move = ["Nf4", "d5"]
        for delimiter in ("-",):
            with self.subTest(fen=fen, move=move, delimiter=delimiter):
                games = self.get(delimiter.join(move).join(fen))
                ae(len(games), 1)
                ae(games[0].state, None)
                ae(games[0]._text[-2:], ["Nd5", "*"])


class GameLongAlgebraicNotationPawnMove(_BasePGN):
    """Provide PGN parser using Game and get() to read PGN text."""

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.Game)

    def test_01_01_pawn_e7_takes_f8_equals_queen(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    [
                        '[SetUp"1"]',
                        '[FEN"5r2/4P3/8/8/8/2K5/8/3k4 w - - 0 1"]',
                        "e7xf8=Q1-0",
                    ]
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_01_02_pawn_e_takes_f8_equals_queen(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    [
                        '[SetUp"1"]',
                        '[FEN"5r2/4P3/8/8/8/2K5/8/3k4 w - - 0 1"]',
                        "exf8=Q1-0",
                    ]
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)


class GameTextPGNLongAlgebraicNotationPawnMove(_BasePGN):
    """Provide PGN parser using GameTextPGN and get() to read PGN text."""

    def setUp(self):
        self.pgn = parser.PGN(game_class=game_text_pgn.GameTextPGN)

    def test_01_01_pawn_e7_takes_f8_equals_queen(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    [
                        '[SetUp"1"]',
                        '[FEN"5r2/4P3/8/8/8/2K5/8/3k4 w - - 0 1"]',
                        "e7xf8=Q1-0",
                    ]
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_01_02_pawn_e_takes_f8_equals_queen(self):
        ae = self.assertEqual
        games = self.get(
            "".join(
                (
                    [
                        '[SetUp"1"]',
                        '[FEN"5r2/4P3/8/8/8/2K5/8/3k4 w - - 0 1"]',
                        "exf8=Q1-0",
                    ]
                )
            )
        )
        ae(len(games), 1)
        ae(games[0].state, None)


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(StrictPGN))
    runner().run(loader(StrictPGNOneCharacterAtATime))
    runner().run(loader(StrictPGNExtendByOneCharacter))
    runner().run(loader(PGN))
    runner().run(loader(PGNOneCharacterAtATime))
    runner().run(loader(PGNExtendByOneCharacter))
    runner().run(loader(StrictFEN))
    runner().run(loader(StrictDisambiguate))
    runner().run(loader(StrictRAV))
    runner().run(loader(FEN))
    runner().run(loader(Disambiguate))
    runner().run(loader(DisambiguateTextPGN))
    runner().run(loader(DisambiguateIgnoreCasePGN))
    runner().run(loader(RAV))
    runner().run(loader(GameTextPGN))
    runner().run(loader(GameIgnoreCasePGN))
    runner().run(loader(GameLongAlgebraicNotationPawnMove))
    runner().run(loader(GameTextPGNLongAlgebraicNotationPawnMove))
