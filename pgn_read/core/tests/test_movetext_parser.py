# test_movetext_parser.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""MoveText, and PGNMoveText tests."""

import unittest
import io

from .. import movetext_parser
from .. import constants


class MoveText_method_args(unittest.TestCase):
    def setUp(self):
        self.gc1 = movetext_parser.MoveText()

    def test_01___init___01(self):
        self.assertRaisesRegex(
            TypeError,
            r"__init__\(\) takes 1 positional argument but 2 were given$",
            movetext_parser.MoveText,
            *(None,),
        )

    def test_02_set_game_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"set_game_error\(\) takes 1 positional argument ",
                    r"but 2 were given$",
                )
            ),
            self.gc1.set_game_error,
            *(None,),
        )

    def test_03_append_comment_to_eol_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_comment_to_eol\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_comment_to_eol,
        )

    def test_04_append_pass_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_pass_after_error\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_pass_after_error,
        )

    def test_05_append_token_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_token\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_token,
        )

    def test_06_append_pass_and_set_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_pass_and_set_error\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_pass_and_set_error,
        )

    def test_07_append_token_and_set_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_token_and_set_error\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_token_and_set_error,
        )

    def test_08_append_token_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_token_after_error\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_token_after_error,
        )

    def test_09_append_token_after_error_without_separator_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_token_after_error_without_separator",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_token_after_error_without_separator,
        )

    def test_10_append_comment_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_comment_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_comment_after_error,
        )

    def test_11_append_bad_tag_and_set_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_bad_tag_and_set_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_bad_tag_and_set_error,
        )

    def test_12_append_bad_tag_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_bad_tag_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_bad_tag_after_error,
        )

    def test_13_append_game_termination_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_game_termination_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_game_termination_after_error,
        )

    def test_14_append_comment_to_eol_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_comment_to_eol_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_comment_to_eol_after_error,
        )

    def test_15_append_start_rav_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_start_rav_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_start_rav_after_error,
        )

    def test_16_append_end_rav_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_end_rav_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_end_rav_after_error,
        )

    def test_17_append_escape_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_escape_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_escape_after_error,
        )

    def test_18_append_other_or_disambiguation_pgn_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_other_or_disambiguation_pgn",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_other_or_disambiguation_pgn,
        )

    def test_19_append_start_tag_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_start_tag",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_start_tag,
        )

    def test_20_append_move_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_move",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_move,
        )

    def test_21_append_start_rav_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_start_rav",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_start_rav,
        )

    def test_22_append_end_rav_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_end_rav",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_end_rav,
        )

    def test_23_append_game_termination_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_game_termination",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_game_termination,
        )

    def test_24_append_glyph_for_traditional_annotation_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.append_glyph_for_traditional_annotation",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_glyph_for_traditional_annotation,
        )

    def test_25_ignore_escape_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.ignore_escape",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.ignore_escape,
        )

    def test_26_ignore_end_of_file_marker_prefix_to_tag_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.ignore_end_of_file_marker_prefix_to_tag",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.ignore_end_of_file_marker_prefix_to_tag,
        )

    def test_27_ignore_move_number_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.ignore_move_number",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.ignore_move_number,
        )

    def test_28_ignore_dots_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.ignore_dots",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.ignore_dots,
        )

    def test_29_ignore_check_indicator_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"MoveText.ignore_check_indicator",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.ignore_check_indicator,
        )

    def test_30_is_tag_roster_valid_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"is_tag_roster_valid\(\) takes 1 positional argument ",
                    r"but 2 were given$",
                )
            ),
            self.gc1.is_tag_roster_valid,
            *(None,),
        )


class MoveText_method_calls(unittest.TestCase):
    def setUp(self):
        self.gc1 = movetext_parser.MoveText()
        self.m = movetext_parser.game_format.match("Qe4")

    def confirm_no_change_base(self, position_count):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def confirm_no_change(self):
        self.confirm_no_change_base(0)
        ae = self.assertEqual

    def test_01___init___01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)
        ae(self.gc1._text, [])
        ae(self.gc1._tags, {})

    def test_02_is_pgn_valid_01(self):
        ae = self.assertEqual
        ae(self.gc1.is_pgn_valid(), False)

    def test_03_set_game_error_01(self):
        ae = self.assertEqual
        ae(self.gc1.set_game_error(), None)
        ae(self.gc1._state, 0)

    def test_04_append_comment_to_eol_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_comment_to_eol(self.m), None)
        ae(self.gc1._text[0], "Qe4\n")
        ae(self.gc1._state, None)

    def test_05_append_pass_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_pass_after_error(self.m), None)
        ae(self.gc1._text[0], " Qe4")
        ae(self.gc1._state, None)

    def test_06_append_token_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_token(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_07_append_reserved_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_reserved(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_08_append_token_and_set_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_token_and_set_error(self.m), None)
        ae(self.gc1._text[0], " Qe4")
        ae(self.gc1._state, 0)

    def test_09_append_token_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_token_after_error(self.m), None)
        ae(self.gc1._text[0], " Qe4")
        ae(self.gc1._state, None)

    def test_10_append_token_after_error_without_separator_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_token_after_error_without_separator(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_11_append_comment_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_comment_after_error(self.m), None)
        ae(self.gc1._text[0], " Qe4")
        ae(self.gc1._state, None)

    def test_12_append_bad_tag_and_set_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_bad_tag_and_set_error(self.m), None)
        ae(self.gc1._text, ['[Qe4""]'])
        ae(self.gc1._tags, {"Qe4": ""})
        ae(self.gc1._state, None)
        ae(self.gc1.append_bad_tag_and_set_error(self.m), None)
        ae(self.gc1._tags, {"Qe4": ""})
        ae(self.gc1._state, 0)

    def test_13_append_bad_tag_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_bad_tag_after_error(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_14_append_game_termination_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_game_termination_after_error(self.m), None)
        ae(self.gc1._text[0], " Qe4")
        ae(self.gc1._state, None)

    def test_15_append_comment_to_eol_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_comment_to_eol_after_error(self.m), None)
        ae(self.gc1._text[0], "Qe4\n")
        ae(self.gc1._state, None)

    def test_16_append_start_rav_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_start_rav_after_error(self.m), None)
        ae(self.gc1._text[0], " Qe4")
        ae(self.gc1._state, None)

    def test_17_append_end_rav_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_end_rav_after_error(self.m), None)
        ae(self.gc1._text[0], " Qe4")
        ae(self.gc1._state, None)

    def test_18_append_escape_after_error_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_escape_after_error(self.m), None)
        ae(self.gc1._text[0], "Qe4\n")
        ae(self.gc1._state, None)

    def test_19_append_other_or_disambiguation_pgn_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_other_or_disambiguation_pgn(self.m), None)
        ae(self.gc1._text[0], " Qe4")
        ae(self.gc1._state, 0)

    def test_20_append_start_tag_01(self):
        m = movetext_parser.game_format.match('[Qe4""]')
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_start_tag(m), None)
        ae(self.gc1._text, ['[Qe4""]'])
        ae(self.gc1._tags, {"Qe4": ""})
        ae(self.gc1._state, None)
        ae(self.gc1.append_start_tag(m), None)
        ae(self.gc1._text, ['[Qe4""]', '[Qe4""]'])
        ae(self.gc1._tags, {"Qe4": ""})
        ae(self.gc1._state, 0)
        ae(self.gc1.append_start_tag(m), None)
        ae(self.gc1._text, ['[Qe4""]', '[Qe4""]', ' [Qe4""]'])
        ae(self.gc1._tags, {"Qe4": ""})
        ae(self.gc1._state, 0)

    def test_21_append_move_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_move(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_22_append_start_rav_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_start_rav(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_23_append_end_rav_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_end_rav(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_24_append_game_termination_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_game_termination(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_25_append_glyph_for_traditional_annotation_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.append_glyph_for_traditional_annotation(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1._state, None)

    def test_26_ignore_escape_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.ignore_escape(self.m), None)
        ae(self.gc1._text, [])
        ae(self.gc1._state, None)

    def test_27_ignore_end_of_file_marker_prefix_to_tag_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.ignore_end_of_file_marker_prefix_to_tag(self.m), None)
        ae(self.gc1._text, [])
        ae(self.gc1._state, None)

    def test_28_ignore_move_number_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.ignore_move_number(self.m), None)
        ae(self.gc1._text, [])
        ae(self.gc1._state, None)

    def test_29_ignore_dots_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.ignore_dots(self.m), None)
        ae(self.gc1._text, [])
        ae(self.gc1._state, None)

    def test_30_ignore_check_indicator_01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.ignore_check_indicator(self.m), None)
        ae(self.gc1._text, [])
        ae(self.gc1._state, None)

    def test_31_is_tag_roster_valid_01(self):
        ae = self.assertEqual
        ae(self.gc1.is_tag_roster_valid(), False)

    def test_32_is_full_disambiguation_allowed_01(self):
        ae = self.assertEqual
        ae(self.gc1._text, [])
        ae(self.gc1.is_full_disambiguation_allowed(), False)

    def test_32_is_full_disambiguation_allowed_02(self):
        ae = self.assertEqual
        ae(self.gc1.append_token(self.m), None)
        ae(self.gc1._text[0], "Qe4")
        ae(self.gc1.is_full_disambiguation_allowed(), False)

    def test_32_is_full_disambiguation_allowed_03(self):
        ae = self.assertEqual
        self.m = movetext_parser.game_format.match("c8=B")
        ae(self.gc1.append_token(self.m), None)
        ae(self.gc1._text[0], "c8=B")
        ae(self.gc1.is_full_disambiguation_allowed(), False)
        ae(self.gc1.append_token(self.m), None)
        ae(self.gc1._text[1], "c8=B")
        ae(self.gc1.is_full_disambiguation_allowed(), True)

    def test_32_is_full_disambiguation_allowed_04(self):
        ae = self.assertEqual
        self.m = movetext_parser.game_format.match("c8=B")
        ae(self.gc1.append_token(self.m), None)
        ae(self.gc1._text[0], "c8=B")
        ae(self.gc1.is_full_disambiguation_allowed(), False)
        self.m = movetext_parser.game_format.match("c8=Q")
        ae(self.gc1.append_token(self.m), None)
        ae(self.gc1._text[1], "c8=Q")
        ae(self.gc1.is_full_disambiguation_allowed(), False)

    def test_32_is_full_disambiguation_allowed_05(self):
        ae = self.assertEqual
        self.m = movetext_parser.game_format.match("c8=N")
        ae(self.gc1.append_token(self.m), None)
        ae(self.gc1._text[0], "c8=N")
        ae(self.gc1.is_full_disambiguation_allowed(), True)


class _ReadGames:
    """Provide get() method which reads games from an io.StringIO object.

    Subclasses must provide a self.pgn object with a read_games() method.

    """

    def get(self, s):
        """Return sequence of Game instances derived from s."""
        return [g for g in self.pgn.read_games(io.StringIO(s))]


class _MoveTextPGN(unittest.TestCase, _ReadGames):
    """Provide PGNMoveText parser with MoveText class to process PGN text."""

    def setUp(self):
        self.pgn = movetext_parser.PGNMoveText(
            game_class=movetext_parser.MoveText
        )


class ReadGames(unittest.TestCase, _ReadGames):
    """Verify operation of _ReadGames.get() method."""

    def test_01_get_01(self):
        ae = self.assertEqual
        self.pgn = movetext_parser.PGNMoveText(
            game_class=movetext_parser.MoveText
        )
        games = self.get("Anything")
        ae(len(games), 1)
        for game in games:
            ae(isinstance(game, movetext_parser.MoveText), True)


class MoveTextPGN(_MoveTextPGN):
    """Test PGNMoveText parser using MoveText class to process PGN text."""

    def test_01_get_01(self):
        ae = self.assertEqual
        games = self.get("Anything*else")
        ae(len(games), 1)
        for game in games:
            ae(isinstance(game, movetext_parser.MoveText), True)

    def test_01_get_02(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*Anything')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, movetext_parser.MoveText), True)

    def test_01_get_03(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*')
        ae(len(games), 1)
        for game in games:
            ae(isinstance(game, movetext_parser.MoveText), True)

    def test_01_get_04(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*[Name1"value1"]*')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, movetext_parser.MoveText), True)

    def test_01_get_05(self):
        ae = self.assertEqual
        games = self.get('Anything[Name"value"]*')
        ae(len(games), 1)
        for game in games:
            ae(isinstance(game, movetext_parser.MoveText), True)

    def test_01_get_06(self):
        ae = self.assertEqual
        games = self.get('Anything [Name"value"]*')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, movetext_parser.MoveText), True)

    def test_01_get_07(self):
        ae = self.assertEqual
        games = self.get('Anything\n[Name"value"]*')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, movetext_parser.MoveText), True)

    def test_02_get_01(self):
        ae = self.assertEqual
        games = self.get("c8=Qb1=Q")
        ae(len(games), 1)
        for game in games:
            ae(game.is_full_disambiguation_allowed(), False)

    def test_02_get_02(self):
        ae = self.assertEqual
        games = self.get("c8=Qb1=Qa8=Q")
        ae(len(games), 1)
        for game in games:
            ae(game.is_full_disambiguation_allowed(), True)

    def test_02_get_02(self):
        ae = self.assertEqual
        games = self.get('[FEN "k7/8/8/8/8/8/8/7k w - - 1 1" ]')
        ae(len(games), 1)
        for game in games:
            ae(game.is_full_disambiguation_allowed(), True)


class AddTokenToGame(unittest.TestCase):
    """Verify operation of movetext_parser.add_token_to_game() function."""

    def test_01_add_token_to_game_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"add_token_to_game\(\) missing 2 required ",
                    r"positional arguments: 'text' and 'game'$",
                )
            ),
            movetext_parser.add_token_to_game,
        )

    def test_01_add_token_to_game_02(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"add_token_to_game\(\) takes from 2 to 3 ",
                    r"positional arguments but 4 were given$",
                )
            ),
            movetext_parser.add_token_to_game,
            *(None, None, None, None),
        )

    def test_02_add_token_to_game_01(self):
        ae = self.assertEqual
        game = movetext_parser.MoveText()
        text = "".join(
            (
                '[Name "value"]',
                "e4;comment\n",
                "{comment}",
                "<reserved>",
                "\n%escaped\n",
                '[Na@me "bad tag name"]',
                "*",
                '[Name "value"]',
                '[Name1 "value"]',
                '[Name2 "value"]',
                "*",
            )
        )
        pos = movetext_parser.add_token_to_game(text, game, pos=0)
        ae(pos, 14)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 16)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 24)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 34)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 44)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 53)
        ae(game.state, 5)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 76)
        ae(game.state, 5)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 77)
        ae(game.state, 5)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 91)
        ae(game.state, 5)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 106)
        ae(game.state, 5)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 121)
        ae(game.state, 5)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 122)
        ae(game.state, 5)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, None)
        ae(game.state, 5)

    def test_02_add_token_to_game_02(self):
        ae = self.assertEqual
        game = movetext_parser.MoveText()
        text = "".join(
            (
                '[Name "value"]',
                ";comment\n",
                "{comment}",
                "<reserved>",
                "\n%escaped\n",
                '[Na@me "bad tag name"]',
                "*",
                '[Name "value"]',
                '[Name1 "value"]',
                '[Name2 "value"]',
                "*",
            )
        )
        pos = movetext_parser.add_token_to_game(text, game, pos=0)
        ae(pos, 14)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 22)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 32)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 42)
        ae(game.state, None)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 51)
        ae(game.state, 4)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 74)
        ae(game.state, 4)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 75)
        ae(game.state, 4)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 89)
        ae(game.state, 4)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 104)
        ae(game.state, 4)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 119)
        ae(game.state, 4)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 120)
        ae(game.state, 4)
        pos = movetext_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, None)
        ae(game.state, 4)


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase

    runner().run(loader(MoveText_method_args))
    runner().run(loader(MoveText_method_calls))
    runner().run(loader(ReadGames))
    runner().run(loader(MoveTextPGN))
    runner().run(loader(AddTokenToGame))
