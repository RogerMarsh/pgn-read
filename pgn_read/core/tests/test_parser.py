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
        ae(games[0]._text, ['A'])

    # _NonStrictTests version gives no games.
    def test_003_a_word(self):
        ae = self.assertEqual
        games = self.get('abcdef123')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['abcdef123'])

    # _NonStrictTests version gives no games.
    def test_004_a_sentence(self):
        ae = self.assertEqual
        games = self.get('The cat sat on the mat')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['The ', 'cat ', 'sat ', 'on ', 'the ', 'mat'])

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
        ae(games[0]._text, ['[A "a"]'])

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
        ae(games[0]._text, ['[A "a"]', '*'])

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
        ae(games[0]._text, ['e3', '[A "a"]'])

    def test_011_bare_illegal_move_in_default_initial_position(self):
        ae = self.assertEqual
        games = self.get('e6')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['e6'])

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
        ae(games[0]._text, ['e6', '*'])

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
        ae(games[0]._text, ['[A"a"]', 'e6'])

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
        ae(games[0]._text, ['[A"a"]', 'e6', '*'])

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
        ae(games[1]._text, ['ff[B"b"]d41-0'])

    # _NonStrictTests version gives two games.
    # games[1].state is None and 'ff[B"b"]' token is lost.
    def test_022_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] d41-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, ['ff[B"b"] ', 'd4', '1-0'])

    # _NonStrictTests version gives two games.
    # games[1].state is None and 'ff[B"b"]' token is lost.
    def test_023_legal_game_and_gash_consuming_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff[B"b"] 1. d4 1-0')
        ae(len(games), 2)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, ['ff[B"b"] ', '1', '.', 'd4', '1-0'])

    # _NonStrictTests version gives two games.
    # games[0] and games[2] are same and games[1] is lost.
    def test_024_legal_game_gash_space_legal_game_both_with_moves(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4*ff [B"b"]d41-0')
        ae(len(games), 3)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '*'])
        ae(games[1].state, 0)
        ae(games[1]._text, ['ff '])
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
        ae(games[1]._text, ['ff'])
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
        ae(games[1]._text, ['ff '])
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
        ae(games[1]._text, ['ff '])
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
        ae(games[0]._text, ['[A"a"]', 'e4', 'd4', '14', '11', '.', '...',
                            '50', '.', '51', '3', '.', '1-0'])

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
        ae(games[0]._text, ['[A"a"]', 'e4', 'd4', '14', '11', '.', '...',
                            '50', '.', '51', '3', '.', '1-0'])

    def test_036_illegal_game_and_legal_game(self):
        ae = self.assertEqual
        games = self.get('[A"a"] 1. e4 d4 2. e5 0-1 [B"b"] 1. d4 d5 1-0')
        ae(len(games), 2)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', 'e4', 'd4', '2', '.', 'e5', '0-1'])
        ae(games[1].state, None)
        ae(games[1]._text, ['[B"b"]', 'd4', 'd5', '1-0'])

    def test_037_illegal_game_and_legal_game_with_newline_not_space(self):
        ae = self.assertEqual
        games = self.get(
            '[A"a"]\n1.\ne4\nd4\n2.\ne5\n0-1\n[B"b"]\n1.\nd4\nd5\n1-0')
        ae(len(games), 2)
        ae(games[0].state, 2)
        ae(games[0]._text, ['[A"a"]', 'e4', 'd4', '2', '.', 'e5', '0-1'])
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

    # _NonStrictTests version gives error too, but '{C;c' and '[B"b"' tokens
    # are lost.
    def test_051_1_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', '{C;c', '<r>', 'e4', '(', 'd4', ')', '[B"b"'])

    # _NonStrictTests version gives error too, but '{C;c' and '[B"b"' tokens
    # are lost.
    def test_051_2_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', '{C;c', '<r>', 'e4', '(', 'd4', ')', '[B"b"]'])

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

    # _NonStrictTests version gives error too, but '<r;c' and '[B"b"' tokens
    # are lost.
    def test_063_1_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', '<r;c', '{C}', 'e4', '(', 'd4', ')', '[B"b"'])

    # _NonStrictTests version gives error too, but '<r;c' token is lost.
    def test_063_2_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['[A"a"]', '<r;c', '{C}', 'e4', '(', 'd4', ')', '[B"b"]'])

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
        ae(games[0]._text, ['[A"a"]', '%!'])

    # _NonStrictTests version gives error too, but '%!*' token is lost.
    def test_067_tag_and_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', '%!*'])

    # _NonStrictTests version gives one game, having lost the '%!\n' token.
    def test_068_tag_and_terminated_escaped_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!\n*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', '%!', '*'])

    # _NonStrictTests version gives one game, having lost the
    # '%!{C}<r>e4(d4)[B"b"]%e' token.
    def test_069_tag_and_terminated_escaped_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]%!{C}<r>e4(d4)[B"b"]%e\n*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', '%!{C}<r>e4(d4)[B"b"]%e', '*'])

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
            'O-O', '-'])

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
        ae(games[0]._text, ['('])

    def test_075_bare_rav_end(self):
        ae = self.assertEqual
        games = self.get(')')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [')'])

    def test_076_bare_rav(self):
        ae = self.assertEqual
        games = self.get('()')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['(', ')'])

    def test_077_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get('(*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['(', '*'])

    def test_078_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get(')*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, [')', '*'])

    def test_079_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('()*')
        ae(len(games), 1)
        ae(games[0].state, 0)
        ae(games[0]._text, ['(', ')', '*'])

    def test_080_tag_and_rav_start_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"](*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', '(', '*'])

    def test_081_tag_and_rav_end_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"])*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', ')', '*'])

    def test_082_tag_and_rav_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]()*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text, ['[A"a"]', '(', ')', '*'])

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
        ae(games[0]._text, ['[A"a"]', 'Nf3', ')', '*'])

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
        ae(games[0]._text, ['Nf3', ')', '*'])

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
           ['$10', '$21', '$10', '$22', 'c4', 'e5', 'c4', 'c5', '(', '(', ')'])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_114_long_algebraic_pawn_move_wrong_direction(self):
        ae = self.assertEqual
        games = self.get('e4e5e4e3')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['e4', 'e5', 'e4', 'e3'])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_115_long_algebraic_pawn_move(self):
        ae = self.assertEqual
        games = self.get('e4e7e5')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', 'e7', 'e5'])

    # Added after changes to convertion of chess engine responses to PGN.
    def test_116_long_algebraic_pawn_move_game_terminated(self):
        ae = self.assertEqual
        games = self.get('e4e7e5*')
        ae(len(games), 1)
        ae(games[0].state, 1)
        ae(games[0]._text,
           ['e4', 'e7', 'e5', '*'])

    def test_120_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8qqg3*'])

    def test_121_bxc8_q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8=qqg3*'])

    def test_122_bxc8_qx(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=q qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8=q ',
            'qg3*'])

    def test_123_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'dxc8qqg3*'])

    def test_124_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'dxc8=qqg3*'])

    def test_125_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8qg3*'])

    def test_126_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8 ',
            'qg3*'])

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
            'qg3*'])

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
            'qg3*'])

    def test_129_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8qg3*'])

    def test_130_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8 ',
            'qg3*'])


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

    def test_001_null_fen_illegal_game(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN""]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN""]'])
        ae(g._pieces_on_board, {})

    def test_002_null_fen(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN""]*')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN""]', '*'])
        ae(len(g._pieces_on_board), 26)
        for p in 'KQRBNkqrbn':
            ae(g._pieces_on_board[p], [])
        for p in ('aP', 'ap', 'bP', 'bp', 'cP', 'cp', 'dP', 'dp',
                  'eP', 'ep', 'fP', 'fp', 'gP', 'gp', 'hP', 'hp'):
            ae(g._pieces_on_board[p], [])

    def test_003_fen_all_unknown(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"? ? ? ? ? ?"]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN"? ? ? ? ? ?"]'])

    def test_004_fen_illegal_piece_placement(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"? w - - 0 1"]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN"? w - - 0 1"]'])

    def test_005_fen_empty_board(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"8/8/8/8/8/8/8/8 w - - 0 1"]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN"8/8/8/8/8/8/8/8 w - - 0 1"]'])

    def test_006_fen_two_kings(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, 2)
        ae(g._text, ['[SetUp"1"]', '[FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]'])

    def test_007_fen_two_kings_and_move(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        g = games[0]
        ae(g.state, None)
        ae(g._text, ['[SetUp"1"]', '[FEN"k7/8/8/8/8/8/8/7K w - - 0 1"]',
                     'Kh2', '*'])
        ae({k: str(v) for k, v in g._piece_placement_data.items()},
           {'a8': 'ka8', 'h2': 'Kh2'})

    def test_008_fen_too_many_kings(self):
        ae = self.assertEqual
        games = self.get('[SetUp"1"][FEN"k7/8/8/8/7K/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_009_fen_too_many_pawns(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7p/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_010_fen_maximum_black_pawns(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7P/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_011_fen_black_pawn_on_rank_1(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/ppppppp1/8/8/7P/8/8/6pK w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_012_fen_black_pawn_on_rank_8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k6p/ppppppp1/8/8/7P/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_013_fen_white_pawn_on_rank_1(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/ppppppp1/8/8/7P/8/8/6PK w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_014_fen_white_pawn_on_rank_8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k6P/ppppppp1/8/8/7P/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_015_fen_too_few_squares_middle_rank(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/8/7P/7/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_016_fen_too_few_squares_first_rank(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/7P/8/8/8/6K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_017_fen_ep_no_pawns_in_place(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/7P/8/8/8/7K w - c6 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_018_fen_ep_no_pawns_to_capture(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pppppppp/8/1P5P/8/8/8/7K w - c6 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_019_fen_ep_allowed(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pp1ppppp/8/1Pp4P/8/8/8/7K w - c6 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_020_fen_ep_target_square_occupied(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"k7/pp2pppp/2p5/1Pp4P/8/8/8/7K w - c6 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_021_fen_too_many_black_pieces(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"rnbqkbnr/pppppppp/n7/1P5P/8/8/8/7K w - - 0 1"]Kh2*')
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_022_fen_too_many_white_pieces(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/7Q/PPPPPPPP/RNBQKBNR',
                 ' w - - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_023_fen_white_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBRN',
                 ' w K - 0 1"]Nc3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_024_fen_white_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBRN',
                 ' w Qkq - 0 1"]Nc3*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_025_fen_white_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/NRBQKBNR',
                 ' w Q - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_026_fen_white_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/NRBQKBNR',
                 ' w Kkq - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_027_fen_black_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbrn/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 ' w k - 0 1"]Nc3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_028_fen_black_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"rnbqkbrn/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 ' w KQq - 0 1"]Nc3*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_029_fen_black_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"nrbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 ' w q - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_030_fen_black_O_O_O_option(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"nrbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 ' w KQk - 0 1"]Nf3*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_031_fen_inactive_color_not_in_check(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"4k3/8/8/7b/8/8/8/4K3',
                 ' w - - 0 1"]Kf1*')))
        ae(len(games), 1)
        ae(games[0].state, None)

    def test_032_fen_inactive_color_in_check(self):
        ae = self.assertEqual
        games = self.get(
            ''.join(
                ('[SetUp"1"][FEN"4k3/8/8/7B/8/8/8/4K3',
                 ' w - - 0 1"]Kf1*')))
        ae(len(games), 1)
        ae(games[0].state, 2)

    def test_033_fen_adjacent_kings_and_move(self):
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
    def test_001_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"7q/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qbb8*')
        self.assertEqual(games[0].state, None)

    def test_002_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"7q/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qhb8*')
        self.assertEqual(games[0].state, None)

    def test_003_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"5q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6d8Kh3*')
        self.assertEqual(games[0].state, None)

    def test_004_disambiguate_move_needed(self):
        games = self.get(
            ''.join(
                ('[SetUp"1"]'
                 '[FEN"3B1q2/8/1q1q1q2/8/8/8/6K1/2k5 b - - 0 1"]Qf6xd8Kh3*')))
        self.assertEqual(games[0].state, None)

    def test_006_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_007_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, None)

    def test_008_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_009_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2)

    def test_010_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_011_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_012_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_013_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_014_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_015_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, None)

    def test_016_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_017_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_018_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_019_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_020_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_021_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_022_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_023_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2)

    def test_024_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2)

    def test_025_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, None)

    def test_026_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, None)

    def test_027_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_028_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_029_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_030_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, None)

    def test_031_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_032_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_033_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2)

    def test_034_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_035_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_036_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_037_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_038_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_039_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_040_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_041_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, None)

    def test_042_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_043_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_044_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_045_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_046_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_047_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_048_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_049_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_050_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_051_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_052_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, None)

    def test_053_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_054_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, None)

    def test_055_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_056_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_057_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_058_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2)

    def test_059_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_060_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_061_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_062_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_063_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_064_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_065_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_066_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2)

    def test_067_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2)

    def test_068_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, None)

    def test_069_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, None)

    def test_070_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, 2)

    def test_071_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_072_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_073_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_074_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, None)

    def test_075_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, None)

    def test_076_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2)

    def test_077_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_078_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe3*')
        self.assertEqual(games[0].state, None)

    def test_079_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, 2)

    def test_080_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, 2)

    def test_081_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, 2)

    def test_082_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qbe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_083_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qee3*')
        self.assertEqual(games[0].state, 2)

    def test_084_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Q6e3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_085_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3e3*')
        self.assertEqual(games[0].state, 2)

    def test_108_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_109_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2)

    def test_110_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_111_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_112_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_113_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_114_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_115_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, None)

    def test_116_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, None)

    def test_117_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_118_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_119_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_120_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_121_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_122_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_123_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2)

    def test_124_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2)

    def test_125_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, None)

    def test_126_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, None)

    def test_127_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_128_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_129_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_130_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, None)

    def test_131_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_132_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_133_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2)

    def test_134_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_135_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_136_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_137_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_138_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_139_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_140_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, None)

    def test_141_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, None)

    def test_142_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_143_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_144_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_145_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_146_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_147_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_148_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_149_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_150_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_151_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_152_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, None)

    def test_153_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, None)

    def test_154_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, None)

    def test_155_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_156_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_157_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_158_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2)

    def test_159_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_160_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_161_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_162_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_163_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_164_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_165_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_166_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2)

    def test_167_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2)

    def test_168_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, None)

    def test_169_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, None)

    def test_170_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, 2)

    def test_171_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_172_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_173_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_174_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, None)

    def test_175_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, None)

    def test_176_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_177_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_178_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qxe3*')
        self.assertEqual(games[0].state, None)

    def test_179_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_180_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_181_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_182_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qbxe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_183_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qexe3*')
        self.assertEqual(games[0].state, 2)

    def test_184_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q6xe3*')
        self.assertEqual(games[0].state, 2 if games[0]._strict_pgn else None)

    def test_185_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Q3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_186_FIDE_longest_possible_game_move_1461_by_white(self):
        games = self.get(''.join(
            ('[SetUp"1"]',
             '[FEN"2r3kq/Q1pnnpq1/3pp1pp/1q1bb3/3B4/2Q1NNP1/2PPPPBP/R1QK4 ',
             'w - - 24 1461"]',
             'Q1a3*')))
        self.assertEqual(games[0].state, None)

    def test_206_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re3*')
        self.assertEqual(games[0].state, 2)

    def test_207_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R3e3*')
        self.assertEqual(games[0].state, 2)

    def test_208_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Ree3*')
        self.assertEqual(games[0].state, 2)

    def test_209_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Rbe3*')
        self.assertEqual(games[0].state, None)

    def test_210_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R6e3*')
        self.assertEqual(games[0].state, None)

    def test_211_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re1e3*')
        self.assertEqual(games[0].state, 2)

    def test_212_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re6e3*')
        self.assertEqual(games[0].state, 2)

    def test_213_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]R6e3*')
        self.assertEqual(games[0].state, None)

    def test_306_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rxe3*')
        self.assertEqual(games[0].state, 2)

    def test_307_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R3xe3*')
        self.assertEqual(games[0].state, 2)

    def test_308_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rexe3*')
        self.assertEqual(games[0].state, 2)

    def test_309_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Rbxe3*')
        self.assertEqual(games[0].state, None)

    def test_310_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6xe3*')
        self.assertEqual(games[0].state, None)

    def test_311_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1xe3*')
        self.assertEqual(games[0].state, 2)

    def test_312_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xe3*')
        self.assertEqual(games[0].state, 2)

    def test_313_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]R6xe3*')
        self.assertEqual(games[0].state, None)


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

    def test_001_rav_after_piece_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nf6(Ne5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/5N1p/8/7K/8/8/8 b - - 2 2")

    def test_001_01_rav_after_piece_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nf6(Ne5)Kg6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/5Nkp/8/7K/8/8/8 w - - 3 3")

    def test_002_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7N/8/7K/8/8/8 b - - 0 2")

    def test_002_01_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)Kg6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kN/8/7K/8/8/8 w - - 1 3")

    def test_002_02_rav_after_piece_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6NK/8/8/8 b - - 0 1"]Kh7Nxh6(Ne5)Kxh6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/7k/8/7K/8/8/8 w - - 0 3")

    def test_003_rav_after_pawn_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6PK/8/8/8 b - - 0 1"]Kh7g5(Kh5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7p/6P1/7K/8/8/8 b - - 0 2")

    def test_003_01_rav_after_pawn_move(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/8/6PK/8/8/8 b - - 0 1"]Kh7g5(Kh5)Kg6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kp/6P1/7K/8/8/8 w - - 1 3")

    def test_004_rav_after_pawn_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]Kh7gxh6(Kh5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/7k/7P/8/7K/8/8/8 b - - 0 2")

    def test_004_01_rav_after_pawn_capture(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]',
            'Kh7gxh6(Kh5)Kg6*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/6kP/8/7K/8/8/8 w - - 1 3")

    def test_004_02_rav_after_pawn_capture(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"6k1/8/7p/6P1/7K/8/8/8 b - - 0 1"]',
            'Kh7gxh6(Kh5)Kxh6*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/8/7k/8/7K/8/8/8 w - - 0 3")

    def test_005_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6B1/7k/7p/8/7K/8/8/8 b - - 0 2")

    def test_005_01_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)Kg6*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6B1/8/6kp/8/7K/8/8/8 w - - 1 3")

    def test_005_02_rav_after_pawn_promote(self):
        games = self.get(
            '[SetUp"1"][FEN"6k1/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7g8=B(Kh5)Kxg8*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "6k1/8/7p/8/7K/8/8/8 w - - 0 3")

    def test_006_rav_after_pawn_promote_capture(self):
        games = self.get(
            '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]Kh7gxh8=B(Kh5)*')
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7B/7k/7p/8/7K/8/8/8 b - - 0 2")

    def test_006_01_rav_after_pawn_promote_capture(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]',
            'Kh7gxh8=B(Kh5)Kg6*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7B/8/6kp/8/7K/8/8/8 w - - 1 3")

    def test_006_02_rav_after_pawn_promote_capture(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"6kn/6P1/7p/8/7K/8/8/8 b - - 0 1"]',
            'Kh7gxh8=B(Kh5)Kxh8*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "7k/8/7p/8/7K/8/8/8 w - - 0 3")

    def test_007_rav_extract_from_4ncl(self):
        games = self.get(''.join((
            '[SetUp"1"][FEN"8/p7/6p1/2K3P1/2P2k2/8/8/8 w - - 0 70"]',
            'Kc6(Kb5Ke4Kc6)(Kd4Kxg5)*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(games[0], "8/p7/2K3p1/6P1/2P2k2/8/8/8 b - - 1 70")

    def test_008_rav_extract_from_calgames_02(self):
        games = self.get(''.join((
            '[SetUp"1"]',
            '[FEN"r2b1rk1/ppp2p1n/7Q/4pb2/2B1N3/5N2/PPP2PPP/2K5 w - - 2 17"]',
            'Neg5e4(Bxg5)Nxh7exf3(Bxh7Ne5Be7Nxf7Rxf7Bxf7Kxf7Qxh7Kf6Qxe4)*')))
        self.assertEqual(games[0].state, None)
        self.fen_position(
            games[0],
            "r2b1rk1/ppp2p1N/7Q/5b2/2B5/5p2/PPP2PPP/2K5 w - - 0 19")


class _NonStrictTests:
    """Override StrictPGN tests which have different outcome when alternatives
    to GameStrictPGN are used.

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

    # StrictPGN version gives error too, but '{C;c' and '[B"b"' tokens are kept.
    def test_051_1_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 6)
        ae(games[0]._text,
           ['[A"a"]', '<r>', 'e4', '(', 'd4', ')'])

    # StrictPGN version gives error too, but '{C;c' and '[B"b"' tokens are kept.
    def test_051_2_tag_and_incomplete_comment_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]{C;c\n<r>e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 6)
        ae(games[0]._text,
           ['[A"a"]', '<r>', 'e4', '(', 'd4', ')', '[B"b"]'])

    # StrictPGN version gives error too, but '<r;c' and '[B"b"' tokens are kept.
    def test_063_1_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"')
        ae(len(games), 1)
        ae(games[0].state, 6)
        ae(games[0]._text,
           ['[A"a"]', '{C}', 'e4', '(', 'd4', ')'])

    # StrictPGN version gives error too, but '<r;c' token is kept.
    def test_063_2_tag_and_incomplete_reserved_wrapping_tokens_and_star(self):
        ae = self.assertEqual
        games = self.get('[A"a"]<r;c\n{C}e4(d4)[B"b"]')
        ae(len(games), 1)
        ae(games[0].state, 6)
        ae(games[0]._text,
           ['[A"a"]', '{C}', 'e4', '(', 'd4', ')', '[B"b"]'])

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

    def test_120_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

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

    def test_123_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    def test_124_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

    def test_125_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]'])

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

    def test_129_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]'])

    def test_130_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8 qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]'])


class PGN(_NonStrictTests, StrictPGN):
    """Provide tests for Game version of parser."""

    def setUp(self):
        self.pgn = parser.PGN()


class PGNOneCharacterAtATime(_NonStrictTests, StrictPGNOneCharacterAtATime):
    """Repeat PGN tests reading text one character at a time.

    The two tests overridden in this class may indicate a design flaw, or
    may just imply relaxing strictness is incompatible with detecting the
    PGN error instantiated in the tests when reading PGN text one character
    at a time.

    """
    def setUp(self):
        self.pgn = parser.PGN()

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_110_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4{\n1/2-1/2}*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text, ['[A"a"]', 'e4', '1/2-1/2'])

    # Added on seeing results when test_025_calgames_05 run with _strict_pgn
    # set False.
    def test_112_game_termination_marker_inside_comment(self):
        ae = self.assertEqual
        games = self.get('[A"a"]e4(d4{\n1/2-1/2})*')
        ae(len(games), 1)
        ae(games[0].state, 5)
        ae(games[0]._text,
           ['[A"a"]', 'e4', '(', 'd4', '1/2-1/2'])


class PGNExtendByOneCharacter(_NonStrictTests, StrictPGNExtendByOneCharacter):
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

    def test_012_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_013_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_018_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_019_disambiguate_move_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_027_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_029_disambiguate_move_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_034_disambiguate_move_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_044_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_045_disambiguate_move_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_047_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_048_disambiguate_move_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_056_disambiguate_move_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q6/1R4K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_063_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_065_disambiguate_move_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/6K1/8 b - - 0 1"]Qb3e3*')
        self.assertEqual(games[0].state, None)

    def test_071_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_072_disambiguate_move_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qe6e3*')
        self.assertEqual(games[0].state, None)

    def test_079_disambiguate_move_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q6/B5K1/8 b - - 0 1"]Qb6e3*')
        self.assertEqual(games[0].state, None)

    def test_112_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_113_disambiguate_capture_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_118_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_119_disambiguate_capture_and_rank_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kq3/8/8/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_127_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_129_disambiguate_capture_and_rank_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_134_disambiguate_capture_and_rank_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/Rq1kqR2/8/8/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_144_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_145_disambiguate_capture_and_file_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_147_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_148_disambiguate_capture_and_file_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_156_disambiguate_capture_and_file_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/1R6/1q2q3/8/1k6/1q2N3/1R4K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_163_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_165_disambiguate_capture_and_diagonal_pin_one(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/6K1/8 b - - 0 1"]Qb3xe3*')
        self.assertEqual(games[0].state, None)

    def test_171_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_172_disambiguate_capture_and_diagonal_pin_two(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qe6xe3*')
        self.assertEqual(games[0].state, None)

    def test_179_disambiguate_capture_and_diagonal_both_pins(self):
        games = self.get(
            '[SetUp"1"][FEN"8/5B2/1q2q3/8/2k5/1q2N3/B5K1/8 b - - 0 1"]Qb6xe3*')
        self.assertEqual(games[0].state, None)

    def test_211_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re1e3*')
        self.assertEqual(games[0].state, None)

    def test_212_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r6/6K1/4r3 b - - 0 1"]Re6e3*')
        self.assertEqual(games[0].state, None)

    def test_311_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re1xe3*')
        self.assertEqual(games[0].state, None)

    def test_312_disambiguate_move_needed(self):
        games = self.get(
            '[SetUp"1"][FEN"8/8/3kr3/8/8/1r2N3/6K1/4r3 b - - 0 1"]Re6xe3*')
        self.assertEqual(games[0].state, None)


class RAV(StrictRAV):
    """Provide tests for Game version of parser."""

    def setUp(self):
        self.pgn = parser.PGN()


class GameTextPGN(_NonStrictTests, StrictPGN):
    """Provide tests for GameTextPGN version of parser."""

    def setUp(self):
        self.pgn = parser.PGN(game_class=game.GameTextPGN)


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

    def test_120_bxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8',
            'qqg3*'])

    def test_121_bxc8_q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8=qqg3*')
        ae(len(games), 1)
        ae(games[0].state, 3)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1P6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8=Q'])

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

    def test_123_dxc8q(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]dxc8qqg3*')
        ae(len(games), 1)
        ae(games[0].state, None)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/3P4/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'dxc8Q',
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

    def test_125_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/1B6/7k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8',
            'qg3',
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
            'bxc8',
            'qg3',
            '*'])

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

    def test_129_bxc8(self):
        ae = self.assertEqual
        games = self.get(
            '[SetUp"1"][FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]bxc8qg3*')
        ae(len(games), 1)
        ae(games[0].state, 2)
        ae(games[0]._text,
           ['[SetUp"1"]',
            '[FEN"2r5/8/B6k/6q1/8/8/8/4K3 w - - 0 1"]',
            'bxc8',
            'qg3',
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
            'bxc8',
            'qg3',
            '*'])


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
    runner().run(loader(RAV))
    runner().run(loader(GameTextPGN))
    runner().run(loader(GameIgnoreCasePGN))
