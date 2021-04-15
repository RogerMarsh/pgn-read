# test_parser.py
# Copyright 2012, 2016, 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""parser tests"""

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

    def get(self, s):
        """Return sequence of Game instances derived from s."""
        return [g for g in self.pgn.read_games(io.StringIO(s))]


class StrictPGN(_BasePGN):
    """Provide tests for GameStrictPGN version of parser.

    Subclasses overrride specific tests where the outcome is different.

    If a subclass defines an extra test it should be added here too if the
    outcome is different, or defined here instead if the outcome is the same.

    """
    def test_001_null_string(self):
        ae = self.assertEqual
        games = self.get('')
        ae(len(games), 0)

    # _NonStrictTests version gives no games.
    def test_002_a_character(self):
        ae = self.assertEqual
        games = self.get('A')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' A'])

    # _NonStrictTests version gives no games.
    def test_003_a_word(self):
        ae = self.assertEqual
        games = self.get('abcdef123')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' abcdef123'])

    # _NonStrictTests version gives no games.
    def test_004_a_sentence(self):
        ae = self.assertEqual
        games = self.get('The cat sat on the mat')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text,
           [' The ', ' cat ', ' sat ', ' on ', ' the ', ' mat'])

    def test_005_bare_star(self):
        ae = self.assertEqual
        games = self.get('*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ['*'])

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
        ae(games[0]._text, ['[A"a"]', '*'])

    def test_008_01_tag_escaped_quotes_and_star(self):
        ae = self.assertEqual
        games = self.get(r'[A"a\""]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, [r'[A"a\""]', '*'])
        ae(games[0]._tags, {'A': r'a\"'})

    def test_008_02_tag_escaped_backslash_and_star(self):
        ae = self.assertEqual
        games = self.get(r'[A"a\\"]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, [r'[A"a\\"]', '*'])
        ae(games[0]._tags, {'A': r'a\\'})

    def test_008_03_tag_right_bracket_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a]"]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a]"]', '*'])
        ae(games[0]._tags, {'A': 'a]'})

    def test_008_04_tag_left_bracket_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a["]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a["]', '*'])
        ae(games[0]._tags, {'A': 'a['})

    def test_009_tag_and_star(self):
        ae = self.assertEqual
        games = self.get('[A "a"]*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '*'])

    # Added len(pgntext) test in parser.PGN.read_games to pass this test.
    def test_010_bare_legal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('e3')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['e3'])

    # Added to identify scope of len(pgntext) test in parser.PGN.read_games.
    def test_010_1_bare_legal_move_sequence_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('e3e6')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['e3', 'e6'])

    # Added to identify scope of len(pgntext) test in parser.PGN.read_games.
    def test_010_2_bare_legal_move_and_tag_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('e3[A "a"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['e3', ' [A "a"]'])

    def test_011_bare_illegal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('e6')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' e6'])

    def test_012_legal_move_in_default_initial_position_and_star(self):
        ae = self.assertEqual
        games = self.get('e3*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ['e3', '*'])

    def test_013_illegal_move_in_default_initial_position_and_star(self):
        ae = self.assertEqual
        games = self.get('e6*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' e6', ' *'])

    def test_014_tag_and_legal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e3')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', 'e3'])

    def test_015_tag_and_illegal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e6')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' e6'])

    def test_016_tag_and_legal_move_in_default_initial_position_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e3', '*'])

    def test_017_tag_and_illegal_move_in_default_initial_position_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e6*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' e6', ' *'])

    def test_018_legal_game_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]**')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '*'])
        ae(games[1]._state, None)
        ae(games[1]._text, ['*'])

    def test_019_legal_game_and_star_and_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]**[B"b"]1-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '*'])
        ae(games[1]._state, None)
        ae(games[1]._text, ['*'])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', '1-0'])

    def test_020_legal_game_and_star_and_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4**[B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1]._state, None)
        ae(games[1]._text, ['*'])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', 'd4', '1-0'])

    # _NonStrictTests version gives just games[0].
    def test_021_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"]d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff[B"b"]d41-0'])

    # _NonStrictTests version gives two games.
    # games[1].state is None and 'ff[B"b"]' token is lost.
    def test_022_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff[B"b"] ', ' d4', ' 1-0'])

    # _NonStrictTests version gives two games.
    # games[1].state is None and 'ff[B"b"]' token is lost.
    def test_023_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] 1. d4 1-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff[B"b"] ', ' 1', '.', ' d4', ' 1-0'])

    # _NonStrictTests version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    def test_024_legal_game_gash_space_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff [B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff '])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', 'd4', '1-0'])

    # _NonStrictTests version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    def test_025_legal_game_gash_newline_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff\n[B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff'])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', 'd4', '1-0'])

    # _NonStrictTests version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    def test_026_legal_game_gash_space_newline_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff \n[B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff '])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', 'd4', '1-0'])

    # This one, with realistic tags and movetext, occurs in a TWIC file.
    def test_027_legal_game_and_star_and_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"] 1. e4 * * [B"b"] 1. d4 1-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1]._state, None)
        ae(games[1]._text, ['*'])
        ae(games[2].state, None)
        ae(games[2]._text, ['[B"b"]', 'd4', '1-0'])

    # _NonStrictTests version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    # This one, with realistic tags and movetext, occurs in a TWIC file.
    def test_028_legal_game_and_gash_and_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]1. e4 1-0 ff [B"b"] 1. d4 1-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '1-0'])
        ae(games[1].state, 0)
        ae(games[1]._text, [' ff '])
        ae(games[0].state, None)
        ae(games[2]._text, ['[B"b"]', 'd4', '1-0'])

    def test_029_bare_move_number(self):
        ae = self.assertEqual
        games = self.get('12')
        ae(len(games), 0)

    def test_029_01_move_number_and_star(self):
        ae = self.assertEqual
        games = self.get('12*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ['*'])

    def test_030_bare_dot(self):
        ae = self.assertEqual
        games = self.get('.')
        ae(len(games), 0)

    def test_030_01_dot_and_star(self):
        ae = self.assertEqual
        games = self.get('.*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ['*'])

    def test_031_bare_move_numbers_and_dots(self):
        ae = self.assertEqual
        games = self.get('12. ... 13. 14 11. ... 50. 51. 3.')
        ae(len(games), 0)

    def test_032_legal_game_with_move_numbers_and_dots(self):
        ae = self.assertEqual
        games = self.get(
            '[A"a"] 1. e4 12. ... 13. d5 14 11. ... 50 . 51 3. 1-0')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', 'd5', '1-0'])

    def test_033_illegal_game_with_move_numbers_and_dots(self):
        ae = self.assertEqual
        games = self.get(
            '[A"a"] 1. e4 12. ... 13. d4 14 11. ... 50 . 51 3. 1-0')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', 'e4', ' d4', ' 14', ' 11', '.', '...',
                            ' 50', '.', ' 51', ' 3', '.', ' 1-0'])

    def test_034_legal_game_move_numbers_and_dots_newline_not_space(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(('[A"a"]\n1.\ne4\n12.\n...\n13.\nd5\n14',
                     '\n11.\n...\n50\n.\n51\n3.\n1-0')))
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', 'd5', '1-0'])

    def test_035_illegal_game_move_numbers_and_dots_newline_not_space(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(('[A"a"]\n1.\ne4\n12.\n...\n13.\nd4\n14',
                     '\n11.\n...\n50\n.\n51\n3.\n1-0')))
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', 'e4', ' d4', ' 14', ' 11', '.', '...',
                            ' 50', '.', ' 51', ' 3', '.', ' 1-0'])

    def test_036_illegal_game_and_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"] 1. e4 d4 2. e5 0-1 [B"b"] 1. d4 d5 1-0')
        ae(len(games), 2)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', 'e4', ' d4', ' 2', '.', ' e5', ' 0-1'])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', 'd4', 'd5', '1-0'])

    def test_037_illegal_game_and_legal_game_with_newline_not_space(self):
        ae = self.assertEqual
        games = self.get(
            '[A"a"]\n1.\ne4\nd4\n2.\ne5\n0-1\n[B"b"]\n1.\nd4\nd5\n1-0')
        ae(len(games), 2)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', 'e4', ' d4', ' 2', '.', ' e5', ' 0-1'])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', 'd4', 'd5', '1-0'])

    def test_038_bare_eol_comment(self):
        ae = self.assertEqual
        games = self.get(';c\n')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, [';c\n'])

    def test_039_tag_and_eol_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"];c\n')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', ';c\n'])

    def test_040_tag_and_eol_comment_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"];c\n*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', ';c\n', '*'])

    def test_041_tag_and_eol_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"];c{c}<r>e4(d4)[B"b"]%e\n*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', ';c{c}<r>e4(d4)[B"b"]%e\n', '*'])

    def test_042_bare_comment(self):
        ae = self.assertEqual
        games = self.get('{C}')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['{C}'])

    def test_043_tag_and_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C}')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', '{C}'])

    def test_044_tag_and_comment_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '{C}', '*'])

    def test_045_tag_and_comment_with_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{Cx\ny}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '{Cx\ny}', '*'])

    def test_046_tag_and_move_comment_with_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]c4{Cx\ny}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'c4', '{Cx\ny}', '*'])

    def test_047_tag_and_comment_wrapping_eol_comment_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{Cx;x\ny}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '{Cx;x\ny}', '*'])

    def test_048_tag_and_move_comment_wrapping_eol_comment_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]c4{Cx;x\ny}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'c4', '{Cx;x\ny}', '*'])

    def test_049_tag_and_comment_wrapping_escape_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{Cx\n%yy}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '{Cx\n%yy}', '*'])

    def test_050_tag_and_move_comment_wrapping_escape_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]c4{Cx\n%yy}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'c4', '{Cx\n%yy}', '*'])

    def test_051_tag_and_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"]%e\n}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '{C;c\n<r>e4(d4)[B"b"]%e\n}', '*'])

    # _NonStrictTests version gives error too.
    def test_051_1_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', ' {C;c\n<r>e4(d4)[B"b"'])

    # _NonStrictTests version gives error too.
    def test_051_2_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', ' {C;c\n<r>e4(d4)[B"b"]'])

    def test_052_tag_and_comment_wrapping_tokens_no_tag_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)%e\n}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '{C;c\n<r>e4(d4)%e\n}', '*'])

    def test_053_bare_numeric_annotation_glyph(self):
        ae = self.assertEqual
        games = self.get('$32')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['$32'])

    def test_054_tag_and_numeric_annotation_glyph(self):
        ae = self.assertEqual
        games = self.get('[A"a"]$32')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', '$32'])

    def test_055_tag_and_numeric_annotation_glyph_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]$32*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '$32', '*'])

    def test_056_bare_reserved(self):
        ae = self.assertEqual
        games = self.get('<r>')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['<r>'])

    def test_057_tag_and_reserved(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r>')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', '<r>'])

    def test_058_tag_and_reserved_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '<r>', '*'])

    def test_059_tag_and_reserved_with_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<rd\ne>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '<rd\ne>', '*'])

    def test_060_tag_and_move_reserved_with_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3<rd\ne>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'Nf3', '<rd\ne>', '*'])

    def test_061_tag_and_reserved_wrapping_escape_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<rx\n%yy>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '<rx\n%yy>', '*'])

    def test_062_tag_and_move_reserved_wrapping_escape_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]c4<rx\n%yy>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'c4', '<rx\n%yy>', '*'])

    def test_063_tag_and_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"]%e\n>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '<r;c\n{C}e4(d4)[B"b"]%e\n>', '*'])

    # _NonStrictTests version gives error too.
    def test_063_1_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', ' <r;c\n{C}e4(d4)[B"b"'])

    # _NonStrictTests version gives error too.
    def test_063_2_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', ' <r;c\n{C}e4(d4)[B"b"]'])

    def test_064_tag_and_reserved_wrapping_tokens_no_tag_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)%e\n>*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '<r;c\n{C}e4(d4)%e\n>', '*'])

    def test_065_bare_escaped(self):
        ae = self.assertEqual
        games = self.get('%Run for your life!')
        ae(len(games), 0)

    def test_065_01_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('%Run for your life!*')
        ae(len(games), 0)

    def test_065_02_escaped_and_newline(self):
        ae = self.assertEqual
        games = self.get('%Run for your life!\n')
        ae(len(games), 0)

    def test_065_03_escaped_and_newline_and_star(self):
        ae = self.assertEqual
        games = self.get('%Run for your life!\n*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text, ['*'])

    # _NonStrictTests version gives error too, but '%!' token is lost.
    def test_066_tag_and_escaped(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' %!'])

    # _NonStrictTests version gives error too, but '%!*' token is lost.
    def test_067_tag_and_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' %!*'])

    # _NonStrictTests version gives one game, having lost the '%!\n' token.
    def test_068_tag_and_terminated_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!\n*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' %!', ' *'])

    # _NonStrictTests version gives one game, having lost the
    # '%!{C}<r>e4(d4)[B"b"]%e' token.
    def test_069_tag_and_terminated_escaped_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!{C}<r>e4(d4)[B"b"]%e\n*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' %!{C}<r>e4(d4)[B"b"]%e', ' *'])

    def test_070_castles_O_O_and_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-OKe7*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]',
            'O-O', 'Ke7', '*'])

    def test_071_castles_O_O_O_and_move(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-O-OKe7*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]',
            'O-O-O', 'Ke7', '*'])

    # _NonStrictTests version gives error too, but '-' token is lost.
    def test_072_castles_O_O_incomplete_0(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-O-')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]',
            'O-O', ' -'])

    def test_073_castles_O_O_O(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-O-O')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]',
            'O-O-O'])

    def test_074_bare_rav_start(self):
        ae = self.assertEqual
        games = self.get('(')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' ('])

    def test_075_bare_rav_end(self):
        ae = self.assertEqual
        games = self.get(')')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' )'])

    def test_076_bare_rav(self):
        ae = self.assertEqual
        games = self.get('()')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' (', ' )'])

    def test_077_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get('(*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' (', ' *'])

    def test_078_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get(')*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' )', ' *'])

    def test_079_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('()*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' (', ' )', ' *'])

    def test_080_tag_and_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"](*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' (', ' *'])

    def test_081_tag_and_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"])*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' )', ' *'])

    def test_082_tag_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]()*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ' (', ' )', ' *'])

    def test_083_tag_and_move_and_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 2)
        ae(games[0].state, 4)
        ae(games[0]._text, ['[A"a"]', 'Nf3', '(', '*'])

    def test_084_tag_and_move_and_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', 'Nf3', ' )', ' *'])

    def test_085_tag_and_move_and_empty_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3()*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'Nf3', '(', ')', '*'])

    def test_086_move_and_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 2)
        ae(games[0].state, 3)
        ae(games[0]._text, ['Nf3', '(', '*'])

    def test_087_move_and_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['Nf3', ' )', ' *'])

    def test_088_move_and_empty_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3()*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ['Nf3', '(', ')', '*'])

    def test_089_tag_and_move_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'Nf3', '(', 'Nc3', ')', '*'])

    def test_090_move_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(Nc3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ['Nf3', '(', 'Nc3', ')', '*'])

    def test_091_tag_and_move_and_sequential_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3)(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'Nf3', '(', 'Nc3', ')', '(', 'a3', ')', '*'])

    def test_092_move_and_sequential_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(Nc3)(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', 'Nc3', ')', '(', 'a3', ')', '*'])

    def test_093_tag_and_move_and_separated_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3)Nf6g3(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'Nf3', '(', 'Nc3', ')', 'Nf6', 'g3',
            '(', 'a3', ')', '*'])

    def test_094_move_and_separated_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(Nc3)Nf6g3(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', 'Nc3', ')', 'Nf6', 'g3',
            '(', 'a3', ')', '*'])

    def test_095_tag_and_move_and_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3(a3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'Nf3', '(', 'Nc3', '(', 'a3', ')', ')', '*'])

    def test_096_move_and_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(Nc3(a3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', 'Nc3', '(', 'a3', ')', ')', '*'])

    def test_097_tag_and_move_and_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3((Nc3)a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'Nf3', '(', '(', 'Nc3', ')', 'a3', ')', '*'])

    def test_098_move_and_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3((Nc3)a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', '(', 'Nc3', ')', 'a3', ')', '*'])

    def test_099_comment_tag_and_move_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3{a}({b}Nc3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'Nf3', '{a}', '(', '{b}', 'Nc3', ')', '*'])

    def test_100_comment_move_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3{a}({b}Nc3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text, ['Nf3', '{a}', '(', '{b}', 'Nc3', ')', '*'])

    def test_101_comment_tag_and_move_and_sequential_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3{a}({b}Nc3){a}({b}a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'Nf3', '{a}', '(', '{b}', 'Nc3', ')', '{a}', '(', '{b}',
            'a3', ')', '*'])

    def test_102_comment_move_and_sequential_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3{a}({b}Nc3){a}({b}a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '{a}', '(', '{b}', 'Nc3', ')', '{a}', '(', '{b}',
            'a3', ')', '*'])

    def test_103_comment_tag_and_move_and_separated_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3{a}({b}Nc3)Nf6g3(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'Nf3', '{a}', '(', '{b}', 'Nc3', ')', 'Nf6', 'g3',
            '(', 'a3', ')', '*'])

    def test_104_comment_move_and_separated_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3{a}({b}Nc3)Nf6g3(a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '{a}', '(', '{b}', 'Nc3', ')', 'Nf6', 'g3',
            '(', 'a3', ')', '*'])

    def test_105_comment_tag_and_move_and_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3(Nc3(a3{a}){b}{a}){b}*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'Nf3', '(', 'Nc3', '(', 'a3', '{a}', ')', '{b}',
            '{a}', ')', '{b}', '*'])

    def test_106_comment_move_and_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(Nc3(a3{a}){b}{a}){b}*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', 'Nc3', '(', 'a3', '{a}', ')', '{b}',
            '{a}', ')', '{b}', '*'])

    def test_107_comment_tag_and_move_and_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]Nf3{a}({b}{a}({b}Nc3)a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'Nf3', '{a}', '(', '{b}', '{a}', '(', '{b}', 'Nc3', ')',
            'a3', ')', '*'])

    def test_108_comment_move_and_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3{a}({b}{a}({b}Nc3)a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '{a}', '(', '{b}', '{a}', '(', '{b}', 'Nc3', ')',
            'a3', ')', '*'])

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_109_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '{1/2-1/2}', '*'])

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_110_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{\n1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '{\n1/2-1/2}', '*'])

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_111_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'e4', '(', 'd4', '{1/2-1/2}', ')', '*'])

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_112_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{\n1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'e4', '(', 'd4', '{\n1/2-1/2}', ')', '*'])

    # Added on seeing results when crash traced to game in crafty06_03.pgn.
    # Non-strict version accepts c4c5 as long algebraic notation for c5.
    def test_113_start_rav_after_moves_after_nags(self):
        ae = self.assertEqual
        games = self.get('$10$21$10$22c4e5c4c5(()')
        ae(len(games), 1)
        ae(games[0].state, 6)
        ae(games[0]._text,
           ['$10', '$21', '$10', '$22', 'c4', 'e5',
            ' c4', ' c5', ' (', ' (', ' )'])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_114_long_algebraic_pawn_move_wrong_direction(self):
        ae = self.assertEqual
        games = self.get('e4e5e4e3')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' e4', ' e3'])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_115_long_algebraic_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e7e5')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' e7', ' e5'])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_116_long_algebraic_pawn_move_game_terminated(self):
        ae = self.assertEqual
        games = self.get('e4e7e5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' e7', ' e5', ' *'])

    # Compare with test_163_bxc8q.
    def test_120_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8qqg3*'])

    def test_121_bxc8_q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8=qqg3*'])

    def test_122_bxc8_qx(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=q qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8=q ',
            ' qg3*'])

    # Changed while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_162_dxc8q.
    def test_123_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' dxc8qqg3*'])

    def test_124_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' dxc8=qqg3*'])

    def test_125_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8qg3*'])

    def test_126_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8 ',
            ' qg3*'])

    def test_127_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'Bxc8',
            ' qg3*'])

    def test_128_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            'Bxc8',
            ' qg3*'])

    def test_129_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8qg3*'])

    def test_130_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8 ',
            ' qg3*'])

    def test_131_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{a1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '{a1/2-1/2}', '*'])

    def test_132_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{a\n1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '{a\n1/2-1/2}', '*'])

    def test_133_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{a1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'e4', '(', 'd4', '{a1/2-1/2}', ')', '*'])

    def test_134_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{a\n1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'e4', '(', 'd4', '{a\n1/2-1/2}', ')', '*'])

    def test_135_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{a\t1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'e4', '(', 'd4', '{a\t1/2-1/2}', ')', '*'])

    def test_136_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{a 1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[A"a"]', 'e4', '(', 'd4', '{a 1/2-1/2}', ')', '*'])

    def test_140_partial_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A"a')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [' [A"a'])

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
        ae(games[0]._text, ['[A"\\\"a"]'])

    # Added while fixing problem.
    def test_146_castles_O_O_g1_occupied(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/RN2K1NR w KQ - 0 1"]O-OKe7*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"4k3/8/8/8/8/8/8/RN2K1NR w KQ - 0 1"]',
            ' O-O', ' Ke7', ' *'])

    # Added while fixing problem.
    def test_147_castles_O_O_O_b1_occupied(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/RN2K1NR w KQ - 0 1"]O-O-OKe7*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"4k3/8/8/8/8/8/8/RN2K1NR w KQ - 0 1"]',
            ' O-O-O', ' Ke7', ' *'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_148_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3((Nc3)a3(e3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', '(', 'Nc3', ')', 'a3', '(', 'e3', ')', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_149_move_and_double_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(((e3)Nc3)a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', '(', '(', 'e3', ')', 'Nc3', ')', 'a3', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_150_move_and_triple_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3((((g3)e3)Nc3)a3)*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', '(', '(', '(', 'g3', ')', 'e3', ')', 'Nc3', ')',
            'a3', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_151_move_and_double_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(Nc3(a3(g3)))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', 'Nc3', '(', 'a3', '(', 'g3', ')', ')', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_152_move_and_triple_left_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3(Nc3(a3(g3(e3))))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', 'Nc3', '(', 'a3', '(', 'g3', '(', 'e3', ')',
            ')', ')', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_153_move_and_left_nested_move_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('Nf3((Nc3)a3)e6(c6(d6))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['Nf3', '(', '(', 'Nc3', ')', 'a3', ')',
            'e6', '(', 'c6', '(', 'd6', ')', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    # See version for GameIgnoreCasePGN, and test_155_* and test_156_* below
    # which change b4 or b5 to h4 or h5.
    def test_154_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('b4b5Nf3((Nc3)a3(e3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['b4', 'b5', 'Nf3', '(', '(', 'Nc3', ')', 'a3',
            '(', 'e3', ')', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_155_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('h4b5Nf3((Nc3)a3(e3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['h4', 'b5', 'Nf3', '(', '(', 'Nc3', ')', 'a3',
            '(', 'e3', ')', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    def test_156_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('b4h5Nf3((Nc3)a3(e3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['b4', 'h5', 'Nf3', '(', '(', 'Nc3', ')', 'a3',
            '(', 'e3', ')', ')', '*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # The first 'b', in 'bb5', caused an error when lower case allowed.
    def test_157_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get('e4e5nf3nc6bb5a6*')
        ae(len(games), 1)
        ae(games[0]._state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' nf3nc6bb5a6*'])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # The first 'b', in 'bb4', caused an error when lower case allowed.
    def test_158_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get('e4c5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6*')
        ae(len(games), 1)
        ae(games[0]._state, 4)
        ae(games[0]._text,
           ['e4', 'c5', 'd4', 'e6', ' nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # The first 'b', in 'bb5', caused an error when lower case allowed.
    def test_159_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get('e4e5nf3nc6Bb5a6*')
        ae(len(games), 1)
        ae(games[0]._state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' nf3nc6Bb5a6*'])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # The first 'b', in 'bb4', caused an error when lower case allowed.
    def test_160_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get('e4c5d4e6nf3cxd4nxd4a6nc3qc7g3Bb4Bd2nf6*')
        ae(len(games), 1)
        ae(games[0]._state, 4)
        ae(games[0]._text,
           ['e4', 'c5', 'd4', 'e6', ' nf3cxd4nxd4a6nc3qc7g3Bb4Bd2nf6*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_129_bxc8.
    def test_161_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8=qg3*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_123_dxc8q.
    def test_162_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' dxc8=qqg3*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_120_bxc8q.
    def test_163_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8=qqg3*'])

    # Added while fixing Little.pgn upper case processing.
    def test_164_long_algebraic_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5d2d4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' d2', ' d4', ' *'])

    # Added while fixing Little.pgn upper case processing.
    def test_165_long_algebraic_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5d2-d4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' d2', ' -d4*'])

    # Added while fixing Little.pgn upper case processing.
    def test_166_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5b2b4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' b2', ' b4', ' *'])

    # Added while fixing Little.pgn upper case processing.
    def test_167_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5b2-b4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' b2', ' -b4*'])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_168_long_algebraic_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e7e5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' e7', ' e5', ' *'])

    # Added while fixing Little.pgn upper case processing.
    def test_169_long_algebraic_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e7-e5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' e7', ' -e5*'])

    # Added while fixing Little.pgn upper case processing.
    def test_170_long_algebraic_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4b7b5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' b7', ' b5', ' *'])

    # Added while fixing Little.pgn upper case processing.
    def test_171_long_algebraic_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4b7-b5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' b7', ' -b5*'])

    # Added while fixing Little.pgn upper case processing.
    def test_172_long_algebraic_uc_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5D2D4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' D2D4*'])

    # Added while fixing Little.pgn upper case processing.
    def test_173_long_algebraic_uc_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5D2-D4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' D2-D4*'])

    # Added while fixing Little.pgn upper case processing.
    def test_174_long_algebraic_uc_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5B2B4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' B2B4*'])

    # Added while fixing Little.pgn upper case processing.
    def test_175_long_algebraic_uc_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5B2-B4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' B2-B4*'])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_176_long_algebraic_uc_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4E7E5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' E7E5*'])

    # Added while fixing Little.pgn upper case processing.
    def test_177_long_algebraic_uc_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4E7-E5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' E7-E5*'])

    # Added while fixing Little.pgn upper case processing.
    def test_178_long_algebraic_uc_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4B7B5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' B7B5*'])

    # Added while fixing Little.pgn upper case processing.
    def test_179_long_algebraic_uc_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4B7-B5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', ' B7-B5*'])

    def test_180_01_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('N1f3*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text,
           [' N1f3', ' *'])

    def test_180_02_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('Ngf3*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text,
           [' Ngf3', ' *'])

    def test_180_03_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('Ng1f3*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text,
           [' Ng1', ' f3', ' *'])


class StrictPGNOneCharacterAtATime(StrictPGN):
    """Repeat StrictPGN tests reading text one character at a time."""

    def get(self, s):
        """Return sequence of Game instances derived from s.

        Read characters one at a time from s.

        """
        return [g for g in self.pgn.read_games(io.StringIO(s), size=1)]


class StrictPGNExtendByOneCharacter(StrictPGN):
    """Repeat StrictPGN tests reading text in two chunks, last is length 1."""

    def get(self, s):
        """Return sequence of Game instances derived from s.

        Where possible do two reads of source where the second read is one
        character, the last one in s.

        """
        t = io.StringIO(s)
        size = max(len(t.getvalue())-1, 1)
        return [g for g in self.pgn.read_games(t, size=size)]


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
        ae(g._text, ['[SetUp"1"]', '[FEN""]', ' *'])
        ae(len(g._pieces_on_board), 26)
        for p in 'KQRBNkqrbn':
            ae(g._pieces_on_board[p], [])
        for p in ('aP', 'ap', 'bP', 'bp', 'cP', 'cp', 'dP', 'dp',
                  'eP', 'ep', 'fP', 'fp', 'gP', 'gp', 'hP', 'hp'):
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
        ae(g._text, ['[SetUp"1"]', '[FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]',
                     'Kh2', '*'])
        ae({k: str(v) for k, v in g._piece_placement_data.items()},
           {'a8': 'ka8', 'h2': 'Kh2'})

    def test_408_fen_too_many_kings(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"k7/8/8/8/7K/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_409_fen_too_many_pawns(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7p/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_410_fen_maximum_black_pawns(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7P/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_411_fen_black_pawn_on_rank_1(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/ppppppp1/8/8/7P/8/8/6pK w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_412_fen_black_pawn_on_rank_8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k6p/ppppppp1/8/8/7P/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_413_fen_white_pawn_on_rank_1(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/ppppppp1/8/8/7P/8/8/6PK w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_414_fen_white_pawn_on_rank_8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k6P/ppppppp1/8/8/7P/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_415_fen_too_few_squares_middle_rank(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7P/7/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_416_fen_too_few_squares_first_rank(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/7P/8/8/8/6K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_417_fen_ep_no_pawns_in_place(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/7P/8/8/8/7K w - c6 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_418_fen_ep_no_pawns_to_capture(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/1P5P/8/8/8/7K w - c6 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_419_fen_ep_allowed(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pp1ppppp/8/1Pp4P/8/8/8/7K w - c6 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_420_fen_ep_target_square_occupied(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pp2pppp/2p5/1Pp4P/8/8/8/7K w - c6 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_421_fen_too_many_black_pieces(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"rnbqkbnr/pppppppp/n7/1P5P/8/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_422_fen_too_many_white_pieces(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/7Q/PPPPPPPP/RNBQKBNR',
                 ' w - - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_423_fen_white_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBRN',
                 ' w K - 0 1"]Nc3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_424_fen_white_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBRN',
                 ' w Qkq - 0 1"]Nc3*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_425_fen_white_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/NRBQKBNR',
                 ' w Q - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_426_fen_white_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/NRBQKBNR',
                 ' w Kkq - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_427_fen_black_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbrn/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 ' w k - 0 1"]Nc3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_428_fen_black_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbrn/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 ' w KQq - 0 1"]Nc3*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_429_fen_black_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"nrbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 ' w q - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_430_fen_black_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"nrbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 ' w KQk - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_431_fen_inactive_color_not_in_check(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"4k3/8/8/7b/8/8/8/4K3',
                 ' w - - 0 1"]Kf1*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_432_fen_inactive_color_in_check(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"4k3/8/8/7B/8/8/8/4K3',
                 ' w - - 0 1"]Kf1*')))
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
            '[SetUp"1"][FEN"7q/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qbb8*')
        self.assertEqual(games[0].state, None)

    def test_502_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"7q/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qhb8*')
        self.assertEqual(games[0].state, None)

    def test_503_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"5q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6d8Kh3*')
        self.assertEqual(games[0].state, None)

    def test_504_disambiguate_move_needed(self):
        games = self.get(
            ''.join(
                ('[SetUp"1"]'
                 '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6xd8Kh3*')))
        self.assertEqual(games[0].state, None)

    def test_505_disambiguate_move_needed(self):
        games = self.get(
            ''.join(
                ('[SetUp"1"]'
                 '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6Xd8Kh3*')))
        self.assertEqual(games[0].state, 2)
        self.assertEqual(
            games[0]._text,
            ['[SetUp"1"]',
             '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]',
             ' Qf6',
             ' Xd8Kh3*'])

    def test_506_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_507_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, None)

    def test_508_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_509_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2)

    def test_510_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_511_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_512_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_513_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_514_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_515_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, None)

    def test_516_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_517_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_518_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_519_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_520_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_521_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_522_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_523_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2)

    def test_524_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2)

    def test_525_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, None)

    def test_526_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, None)

    def test_527_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_528_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_529_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_530_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, None)

    def test_531_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_532_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_533_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2)

    def test_534_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_535_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_536_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_537_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_538_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_539_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_540_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_541_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, None)

    def test_542_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_543_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_544_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_545_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_546_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_547_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_548_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_549_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_550_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_551_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_552_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, None)

    def test_553_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_554_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, None)

    def test_555_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_556_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_557_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_558_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2)

    def test_559_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_560_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_561_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_562_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_563_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_564_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_565_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_566_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2)

    def test_567_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2)

    def test_568_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, None)

    def test_569_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, None)

    def test_570_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_571_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_572_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_573_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_574_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, None)

    def test_575_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_576_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_577_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_578_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, None)

    def test_579_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_580_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_581_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_582_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_583_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2)

    def test_584_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_585_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_608_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_609_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2)

    def test_610_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_611_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_612_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_613_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_614_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_615_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, None)

    def test_616_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, None)

    def test_617_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_618_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_619_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_620_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_621_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_622_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_623_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2)

    def test_624_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2)

    def test_625_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, None)

    def test_626_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, None)

    def test_627_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_628_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_629_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_630_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, None)

    def test_631_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_632_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_633_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2)

    def test_634_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_635_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_636_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_637_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_638_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_639_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_640_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, None)

    def test_641_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, None)

    def test_642_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_643_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_644_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_645_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_646_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_647_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_648_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_649_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_650_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_651_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_652_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, None)

    def test_653_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, None)

    def test_654_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, None)

    def test_655_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_656_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_657_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_658_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2)

    def test_659_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_660_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_661_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_662_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_663_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_664_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_665_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_666_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2)

    def test_667_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2)

    def test_668_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, None)

    def test_669_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, None)

    def test_670_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_671_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_672_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_673_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_674_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, None)

    def test_675_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, None)

    def test_676_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_677_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_678_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, None)

    def test_679_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_680_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_681_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_682_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_683_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2)

    def test_684_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_685_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_686_FIDE_longest_possible_game_move_1461_by_white(self):
        games = self.get(''.join(
            ('[SetUp"1"]',
             '[FEN"2r3kq/Q1pnnpq1/3pp1pp/1q1bb3/3B4/2Q1NNP1/2PPPPBP/R1QK4 ',
             'w - - 24 1461"]',
             'Q1a3*')))
        self.assertEqual(games[0].state, None)

    def test_706_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re3*')
        self.assertEqual(games[0].state, 2)

    def test_707_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R3e3*')
        self.assertEqual(games[0].state, 2)

    def test_708_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Ree3*')
        self.assertEqual(games[0].state, 2)

    def test_709_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Rbe3*')
        self.assertEqual(games[0].state, None)

    def test_710_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R6e3*')
        self.assertEqual(games[0].state, None)

    def test_711_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re1e3*')
        self.assertEqual(games[0].state, 2)

    def test_712_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re6e3*')
        self.assertEqual(games[0].state, 2)

    def test_713_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R6e3*')
        self.assertEqual(games[0].state, None)

    def test_806_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rxe3*')
        self.assertEqual(games[0].state, 2)

    def test_807_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_808_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rexe3*')
        self.assertEqual(games[0].state, 2)

    def test_809_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rbxe3*')
        self.assertEqual(games[0].state, None)

    def test_810_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6xe3*')
        self.assertEqual(games[0].state, None)

    def test_811_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1xe3*')
        self.assertEqual(games[0].state, 2)

    def test_812_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_813_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6xe3*')
        self.assertEqual(games[0].state, None)

    def test_816_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]RXe3*')
        self.assertEqual(games[0].state, 2)

    def test_817_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R3Xe3*')
        self.assertEqual(games[0].state, 2)

    def test_818_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]ReXe3*')
        self.assertEqual(games[0].state, 2)

    def test_819_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]RbXe3*')
        self.assertEqual(games[0].state, 2)

    def test_820_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6Xe3*')
        self.assertEqual(games[0].state, 2)

    def test_821_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1Xe3*')
        self.assertEqual(games[0].state, 2)

    def test_822_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xE3*')
        self.assertEqual(games[0].state, 2)

    def test_823_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6Xe3*')
        self.assertEqual(games[0].state, 2)


class StrictRAV(_BasePGN):
    """Recursive annotation variation tests only.  StrictPGN tests are not done.
    """

    def fen_position(self, g, fen):
        self.assertEqual(
            game.generate_fen_for_position(
                g._piece_placement_data.values(),
                g._active_color,
                g._castling_availability,
                g._en_passant_target_square,
                g._halfmove_clock,
                g._fullmove_number),
            fen)

    def test_451_rav_after_piece_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nf6(Ne5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/5N1p/8/7K/8/8/8 b - - 2 2")

    def test_451_01_rav_after_piece_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nf6(Ne5)Kg6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/5Nkp/8/7K/8/8/8 w - - 3 3")

    def test_452_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7N/8/7K/8/8/8 b - - 0 2")

    def test_452_01_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)Kg6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kN/8/7K/8/8/8 w - - 1 3")

    def test_452_02_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)Kxh6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/7k/8/7K/8/8/8 w - - 0 3")

    def test_453_rav_after_pawn_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6PK/8/8/8 b - - 0 1"]Kh7g5(Kh5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7p/6P1/7K/8/8/8 b - - 0 2")

    def test_453_01_rav_after_pawn_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6PK/8/8/8 b - - 0 1"]Kh7g5(Kh5)Kg6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kp/6P1/7K/8/8/8 w - - 1 3")

    def test_454_rav_after_pawn_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]Kh7gxh6(Kh5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7P/8/7K/8/8/8 b - - 0 2")

    def test_454_01_rav_after_pawn_capture(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]',
            'Kh7gxh6(Kh5)Kg6*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kP/8/7K/8/8/8 w - - 1 3")

    def test_454_02_rav_after_pawn_capture(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]',
            'Kh7gxh6(Kh5)Kxh6*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/7k/8/7K/8/8/8 w - - 0 3")

    def test_455_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6B1/7k/7p/8/7K/8/8/8 b - - 0 2")

    def test_455_01_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)Kg6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6B1/8/6kp/8/7K/8/8/8 w - - 1 3")

    def test_455_02_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)Kxg8*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6k1/8/7p/8/7K/8/8/8 w - - 0 3")

    def test_456_rav_after_pawn_promote_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7gxh8=B(Kh5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7B/7k/7p/8/7K/8/8/8 b - - 0 2")

    def test_456_01_rav_after_pawn_promote_capture(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]',
            'Kh7gxh8=B(Kh5)Kg6*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7B/8/6kp/8/7K/8/8/8 w - - 1 3")

    def test_456_02_rav_after_pawn_promote_capture(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]',
            'Kh7gxh8=B(Kh5)Kxh8*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7k/8/7p/8/7K/8/8/8 w - - 0 3")

    def test_457_rav_extract_from_4ncl(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"8/p7/6p1/2K3P1/2P2k2/8/8/8 w - - 0 70"]',
            'Kc6(Kb5Ke4Kc6)(Kd4Kxg5)*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/p7/2K3p1/6P1/2P2k2/8/8/8 b - - 1 70")

    def test_458_rav_extract_from_calgames_02(self):
        games = self.get(''.join((
            '[SetUp"1"]',
            '[FEN"r2b1rk1/ppp2p1n/7Q/4pb2/2B1N3/5N2/PPP2PPP/2K5 w - - 2 17"]',
            'Neg5e4(Bxg5)Nxh7exf3(Bxh7Ne5Be7Nxf7Rxf7Bxf7Kxf7Qxh7Kf6Qxe4)*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(
            games[0],
            "r2b1rk1/ppp2p1N/7Q/5b2/2B5/5p2/PPP2PPP/2K5 w - - 0 19")


class _NonStrictTests:
    """Override StrictPGN tests which have a different outcome, but same for
    both, in GameTextPGN and GameIgnoreCasePGN tests.

    Usage is 'class C(_NonStrictTests, StrictPGN)'.

    For example, Game class allows Nge2 when a knight on c3 is pinned against
    the king on e1, while GameStrictPGN class does not allow Nge2.

    """

    # StrictPGN version gives one game with state False and one tokens.
    def test_002_a_character(self):
        ae = self.assertEqual
        games = self.get('A')
        ae(len(games), 0)

    # StrictPGN version gives one game with state False and one tokens.
    def test_003_a_word(self):
        ae = self.assertEqual
        games = self.get('abcdef123')
        ae(len(games), 0)

    # StrictPGN version gives one game with state False and six tokens.
    def test_004_a_sentence(self):
        ae = self.assertEqual
        games = self.get('The cat sat on the mat')
        ae(len(games), 0)

    # StrictPGN version gives two games.
    # games[1].state is False and 'ff[B"b"]' token is kept.
    def test_021_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"]d41-0')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])

    # StrictPGN version gives two games.
    # games[1].state is False and 'ff[B"b"]' token is kept.
    def test_022_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1]._state, None)
        ae(games[1]._text, ['d4', '1-0'])

    # StrictPGN version gives two games.
    # games[1].state is False and 'ff[B"b"]' token is kept.
    def test_023_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] 1. d4 1-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1]._state, None)
        ae(games[1]._text, ['d4', '1-0'])

    # StrictPGN version gives three games.
    # games[0] is same and games[1] becomes games[2] with games[1] for 'ff'
    # token as an error.
    def test_024_legal_game_gash_space_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff [B"b"]d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', 'd4', '1-0'])

    # StrictPGN version gives three games.
    # games[0] is same and games[1] becomes games[2] with games[1] for 'ff'
    # token as an error.
    def test_025_legal_game_gash_newline_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff\n[B"b"]d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', 'd4', '1-0'])

    # StrictPGN version gives three games.
    # games[0] is same and games[1] becomes games[2] with games[1] for 'ff'
    # token as an error.
    def test_026_legal_game_gash_space_newline_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff \n[B"b"]d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', 'd4', '1-0'])

    # StrictPGN version gives three games.
    # games[0] is same and games[1] becomes games[2] with games[1] for 'ff'
    # token as an error.
    # This one, with realistic tags and movetext, occurs in a TWIC file.
    def test_028_legal_game_and_gash_and_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]1. e4 1-0 ff [B"b"] 1. d4 1-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '1-0'])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', 'd4', '1-0'])

    # StrictPGN version gives error too.
    def test_051_1_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', ' {C;c\n<r>e4(d4)[B"b"'])

    # StrictPGN version gives error too.
    def test_051_2_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', ' {C;c\n<r>e4(d4)[B"b"]'])

    # StrictPGN version gives error too.
    def test_063_1_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', ' <r;c\n{C}e4(d4)[B"b"'])

    # StrictPGN version gives error too.
    def test_063_2_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', ' <r;c\n{C}e4(d4)[B"b"]'])

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
        ae(games[0]._text, ['[A"a"]', '*'])

    # StrictPGN version gives error, having kept the
    # '%!{C}<r>e4(d4)[B"b"]%e' token.
    def test_069_tag_and_terminated_escaped_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!{C}<r>e4(d4)[B"b"]%e\n*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', '*'])

    # StrictPGN version gives error too, but '-' token is kept.
    def test_072_castles_O_O_incomplete_0(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]O-O-')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1"]',
            'O-O'])

    # Added on seeing results when crash traced to game in crafty06_03.pgn.
    # Strict version gives an error: c4c5 is long algebraic notation.
    def test_113_start_rav_after_moves_after_nags(self):
        ae = self.assertEqual
        games = self.get('$10$21$10$22c4e5c4c5(()')
        ae(len(games), 1)
        ae(games[0].state, 10)
        ae(games[0]._text,
           ['$10', '$21', '$10', '$22', 'c4', 'e5', 'c5', '(', '(', ')'])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_115_long_algebraic_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e7e5')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5'])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_116_long_algebraic_pawn_move_game_terminated(self):
        ae = self.assertEqual
        games = self.get('e4e7e5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', '*'])

    # Changed while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_163_bxc8q.
    def test_120_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    # Changed while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_162_dxc8q.
    def test_123_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    # Changed while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_128_bxc8 (and test_129_bxc8).
    def test_125_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    # Compare with test_161_bxc8.
    def test_129_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]'])

    def test_140_partial_tag_01(self):
        ae = self.assertEqual
        games = self.get('[A"a')
        ae(len(games), 0)

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
        games = self.get('e4e5d2d4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'd4', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_165_long_algebraic_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5d2-d4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'd4', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_166_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5b2b4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'b4', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_167_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5b2-b4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'b4', '*'])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_168_long_algebraic_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e7e5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_169_long_algebraic_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e7-e5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_170_long_algebraic_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4b7b5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'b5', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_171_long_algebraic_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4b7-b5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'b5', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_172_long_algebraic_uc_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5D2D4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5'])

    # Added while fixing Little.pgn upper case processing.
    def test_173_long_algebraic_uc_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5D2-D4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5'])

    # Added while fixing Little.pgn upper case processing.
    def test_174_long_algebraic_uc_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5B2B4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5'])

    # Added while fixing Little.pgn upper case processing.
    def test_175_long_algebraic_uc_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5B2-B4*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5'])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_176_long_algebraic_uc_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4E7E5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4'])

    # Added while fixing Little.pgn upper case processing.
    def test_177_long_algebraic_uc_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4E7-E5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4'])

    # Added while fixing Little.pgn upper case processing.
    def test_178_long_algebraic_uc_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4B7B5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4'])

    # Added while fixing Little.pgn upper case processing.
    def test_179_long_algebraic_uc_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4B7-B5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4'])

    def test_180_01_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('N1f3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['Nf3', '*'])

    def test_180_02_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('Ngf3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['Nf3', '*'])

    def test_180_03_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('Ng1f3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['Nf3', '*'])


class _NonStrictPGNTests:
    """Override StrictPGN tests which have a different outcome, but same for
    all, in PGN, PGNOneCharacterAtATime, and PGNExtendByOneCharacter tests.

    Usage is 'class C(_NonStrictPGNTests, StrictPGN)'.

    For example, Game class allows Nge2 when a knight on c3 is pinned against
    the king on e1, while GameStrictPGN class does not allow Nge2.

    """

    # Added on seeing results when crash traced to game in crafty06_03.pgn.
    # c4c5 is redundant precision, not long algebraic notation.
    def test_113_start_rav_after_moves_after_nags(self):
        ae = self.assertEqual
        games = self.get('$10$21$10$22c4e5c4c5(()')
        ae(len(games), 1)
        ae(games[0].state, 10)
        ae(games[0]._text,
           ['$10', '$21', '$10', '$22', 'c4', 'e5', 'c5', '(', '(', ')'])

    # Added after changes to convertion of chess engine responses to PGN.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_115_long_algebraic_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e7e5')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5'])

    # Added after changes to convertion of chess engine responses to PGN.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_116_long_algebraic_pawn_move_game_terminated(self):
        ae = self.assertEqual
        games = self.get('e4e7e5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', '*'])

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
        games = self.get('e4e5d2d4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'd4', '*'])

    # Added while fixing Little.pgn upper case processing.
    # Hyphen noticed but ignored for seeing token d2 and peek ahead -d4 as
    # over-precise d4, but is not expecting -d4 when deciding if next token
    # has already been used for disambiguation.
    def test_165_long_algebraic_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5d2-d4*')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['e4', 'e5', 'd4', ' -d4*'])

    # Added while fixing Little.pgn upper case processing.
    # d2d4 is redundant precision, not long algebraic notation.
    def test_166_long_algebraic_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5b2b4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'b4', '*'])

    # Added while fixing Little.pgn upper case processing.
    # Hyphen treated like test_165_long_algebraic_white_pawn_move_with_hyphen
    # but b-pawn used to test for 'bishop or pawn' interpretation confusion.
    def test_167_long_algebraic_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5b2-b4*')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['e4', 'e5', 'b4', ' -b4*'])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    # e7e5 is redundant precision, not long algebraic notation.
    def test_168_long_algebraic_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e7e5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', '*'])

    # Added while fixing Little.pgn upper case processing.
    # Hyphen treated like test_165_long_algebraic_white_pawn_move_with_hyphen.
    def test_169_long_algebraic_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e7-e5*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', ' -e5*'])

    # Added while fixing Little.pgn upper case processing.
    # b7b5 is redundant precision, not long algebraic notation.
    def test_170_long_algebraic_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4b7b5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'b5', '*'])

    # Added while fixing Little.pgn upper case processing.
    # Hyphen treated like test_165_long_algebraic_white_pawn_move_with_hyphen
    # but b-pawn used to test for 'bishop or pawn' interpretation confusion.
    def test_171_long_algebraic_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4b7-b5*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'b5', ' -b5*'])

    def test_180_01_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('N1f3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['Nf3', '*'])

    def test_180_02_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('Ngf3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['Nf3', '*'])

    def test_180_03_too_much_precision(self):
        ae = self.assertEqual
        games = self.get('Ng1f3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['Nf3', '*'])


class PGN(_NonStrictPGNTests, StrictPGN):
    """Provide tests for Game version of parser."""

    def setUp(self):
        self.pgn = parser.PGN()


class PGNOneCharacterAtATime(_NonStrictPGNTests, StrictPGNOneCharacterAtATime):
    """Repeat PGN tests reading text one character at a time."""

    def setUp(self):
        self.pgn = parser.PGN()


class PGNExtendByOneCharacter(_NonStrictPGNTests,
                              StrictPGNExtendByOneCharacter):
    """Repeat PGN tests reading text in two chunks, last is length 1."""

    def setUp(self):
        self.pgn = parser.PGN()


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
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_513_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_518_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_519_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_527_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_529_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_534_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_544_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_545_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_547_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_548_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_556_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_563_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_565_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_571_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_572_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_579_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_612_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_613_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_618_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_619_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_627_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_629_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_634_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_644_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_645_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_647_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_648_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_656_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_663_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_665_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_671_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_672_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_679_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_711_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re1e3*')
        self.assertEqual(games[0].state, None)

    def test_712_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re6e3*')
        self.assertEqual(games[0].state, None)

    def test_811_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1xe3*')
        self.assertEqual(games[0].state, None)

    def test_812_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xe3*')
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
        self.pgn = parser.PGN(game_class=game.GameTextPGN)

    def test_505_disambiguate_move_needed(self):
        games = self.get(
            ''.join(
                ('[SetUp"1"]'
                 '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6Xd8Kh3*')))
        self.assertEqual(games[0].state, 3)
        self.assertEqual(
            games[0]._text,
            ['[SetUp"1"]',
             '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]',
             'Qf6xd8'])

    # Redundant precision removed but GameTextPGN does not allow 'X' for 'x'.
    # Compare with test_811_disambiguate_move_needed.
    def test_821_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1Xe3*')
        self.assertEqual(games[0].state, 3)
        self.assertEqual(
            games[0]._text,
            ['[SetUp"1"]',
             '[FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]',
             'R1xe3'])

    # Redundant precision removed but GameTextPGN does not allow 'E3' for 'e3'.
    # Compare with test_812_disambiguate_move_needed.
    def test_822_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xE3*')
        self.assertEqual(games[0].state, 3)
        self.assertEqual(
            games[0]._text,
            ['[SetUp"1"]',
             '[FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]',
             'R6xe3'])


class DisambiguateIgnoreCasePGN(DisambiguateTextPGN):
    """Movetext disambiguation tests only.  StrictPGN tests are not done.

    The strictness rules on movetext precision are relaxed.

    The PGN specification states movetext should use exactly the precision
    needed to describe the move.  These tests verify, for example, Rcc7 is
    stated when two rooks on rank 7 can legally move to c7; and is allowed
    when only one rook can legally move to c7 (from rank 7 or file c).

    """

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameIgnoreCasePGN)

    def test_505_disambiguate_move_needed(self):
        games = self.get(
            ''.join(
                ('[SetUp"1"]'
                 '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6Xd8Kh3*')))
        self.assertEqual(games[0].state, None)
        self.assertEqual(
            games[0]._text,
            ['[SetUp"1"]',
             '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]',
             'Qf6xd8',
             'Kh3',
             '*'])

    def test_819_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]RbXe3*')
        self.assertEqual(games[0].state, None)

    def test_820_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6Xe3*')
        self.assertEqual(games[0].state, None)

    def test_821_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1Xe3*')
        self.assertEqual(games[0].state, None)

    def test_822_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xE3*')
        self.assertEqual(games[0].state, None)

    def test_823_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6Xe3*')
        self.assertEqual(games[0].state, None)


class RAV(StrictRAV):
    """Provide tests for Game version of parser."""

    def setUp(self):
        self.pgn = parser.PGN()


class GameTextPGN(_NonStrictTests, StrictPGN):
    """Provide tests for GameTextPGN version of parser."""

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameTextPGN)

    def test_121_bxc8_q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    def test_122_bxc8_qx(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=q qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    def test_124_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    def test_126_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    def test_127_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'Bxc8'])

    def test_128_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            'Bxc8'])

    def test_130_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # The first 'b', in 'bb5', caused an error when lower case allowed.
    def test_157_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get('e4e5nf3nc6bb5a6*')
        ae(len(games), 1)
        ae(games[0]._state, 2)
        ae(games[0]._text,
           ['e4', 'e5'])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # The first 'b', in 'bb4', caused an error when lower case allowed.
    def test_158_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get('e4c5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6*')
        ae(len(games), 1)
        ae(games[0]._state, 4)
        ae(games[0]._text,
           ['e4', 'c5', 'd4', 'e6'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # The first 'b', in 'bb5', caused an error when lower case allowed.
    def test_159_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get('e4e5nf3nc6Bb5a6*')
        ae(len(games), 1)
        ae(games[0]._state, 2)
        ae(games[0]._text,
           ['e4', 'e5'])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # The first 'b', in 'bb4', caused an error when lower case allowed.
    def test_160_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get('e4c5d4e6nf3cxd4nxd4a6nc3qc7g3Bb4Bd2nf6*')
        ae(len(games), 1)
        ae(games[0]._state, 4)
        ae(games[0]._text,
           ['e4', 'c5', 'd4', 'e6'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_129_bxc8.
    def test_161_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_123_dxc8q.
    def test_162_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_120_bxc8q.
    def test_163_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'])


class GameIgnoreCasePGN(_NonStrictTests, StrictPGN):
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
        self.pgn = parser.PGN(game_class=game.GameIgnoreCasePGN)

    def test_121_bxc8_q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8=Q',
            'Qg3',
            '*'])

    def test_122_bxc8_qx(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=q qg3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8=Q',
            'Qg3',
            '*'])

    def test_124_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'dxc8=Q',
            'Qg3',
            '*'])

    def test_126_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' Qg3',
            ' *'])

    def test_127_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'Bxc8',
            'Qg3',
            '*'])

    def test_128_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]Bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            'Bxc8',
            'Qg3',
            '*'])

    def test_130_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' Qg3',
            ' *'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    # The first 'b', in 'b4', caused an error.
    def test_154_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('b4b5Nf3((Nc3)a3(e3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['b4', 'b5', 'Nf3', '(', '(', 'Nc3', ')', 'a3',
            '(', 'e3', ')', ')', '*'])

    # Added while fixing 'Nf3((Nc3)a3(e3))' problem.
    # The first 'b', in 'b4', caused an error.
    def test_156_move_and_left_right_nested_ravs_and_star(self):
        ae = self.assertEqual
        games = self.get('b4h5Nf3((Nc3)a3(e3))*')
        ae(len(games), 1)
        ae(len(games[0]._ravstack), 1)
        ae(len(games[0]._ravstack[-1]), 4)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['b4', 'h5', 'Nf3', '(', '(', 'Nc3', ')', 'a3',
            '(', 'e3', ')', ')', '*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # 'bb5' is accepted.
    def test_157_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get('e4e5nf3nc6bb5a6*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', '*'])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # 'bb4' and 'bd2' are accepted.
    def test_158_lower_case_movetext(self):
        ae = self.assertEqual
        games = self.get('e4c5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['e4', 'c5', 'd4', 'e6', 'Nf3', 'cxd4', 'Nxd4', 'a6', 'Nc3',
            'Qc7', 'g3', 'Bb4', 'Bd2', 'Nf6', '*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # 'Bb5' is accepted.
    def test_159_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get('e4e5nf3nc6Bb5a6*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', 'a6', '*'])

    # Added while fixing 'e4e5d4e6nf3cxd4nxd4a6nc3qc7g3bb4bd2nf6' problem.
    # 'Bb4Bd2' is accepted.
    def test_160_lower_case_movetext_except_bishops(self):
        ae = self.assertEqual
        games = self.get('e4c5d4e6nf3cxd4nxd4a6nc3qc7g3Bb4Bd2nf6*')
        ae(len(games), 1)
        ae(games[0]._state, None)
        ae(games[0]._text,
           ['e4', 'c5', 'd4', 'e6', 'Nf3', 'cxd4', 'Nxd4', 'a6', 'Nc3',
            'Qc7', 'g3', 'Bb4', 'Bd2', 'Nf6', '*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_129_bxc8.
    def test_161_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            ' bxc8=Q',
            ' g3',
            ' *'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_123_dxc8q.
    def test_162_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'dxc8=Q',
            'Qg3',
            '*'])

    # Added while fixing 'e4e5nf3nc6bb5a6' problem.
    # Compare with test_120_bxc8q.
    def test_163_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8=Q',
            'Qg3',
            '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_172_long_algebraic_uc_white_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5D2D4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'd4', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_173_long_algebraic_uc_white_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5D2-D4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'd4', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_174_long_algebraic_uc_white_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e5B2B4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'b4', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_175_long_algebraic_uc_white_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4e5B2-B4*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', 'b4', '*'])

    # Added while fixing Little.pgn upper case processing.
    # Adds the '*' compared with test_115_long_algebraic_pawn_move.
    def test_176_long_algebraic_uc_black_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4E7E5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_177_long_algebraic_uc_black_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4E7-E5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'e5', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_178_long_algebraic_uc_black_b_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4B7B5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'b5', '*'])

    # Added while fixing Little.pgn upper case processing.
    def test_179_long_algebraic_uc_black_b_pawn_move_with_hyphen(self):
        ae = self.assertEqual
        games = self.get('e4B7-B5*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['e4', 'b5', '*'])


if __name__ == '__main__':
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
