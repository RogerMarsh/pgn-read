# test_tagpair_parser.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""GameCount, TagPairGane, and PGNTagPair tests."""

import unittest
import io

from .. import tagpair_parser
from .. import constants


class GameCount_method_args(unittest.TestCase):
    def setUp(self):
        self.gc1 = tagpair_parser.GameCount()

    def test_01___init___01(self):
        self.assertRaisesRegex(
            TypeError,
            r"__init__\(\) takes 1 positional argument but 2 were given$",
            tagpair_parser.GameCount,
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
                    r"GameCount.append_comment_to_eol\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_comment_to_eol,
        )

    def test_04_append_token_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_token\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_token,
        )

    def test_05_append_token_and_set_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_token_and_set_error\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_token_and_set_error,
        )

    def test_06_append_token_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_token_after_error\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_token_after_error,
        )

    def test_07_append_token_after_error_without_separator_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_token_after_error_without_separator",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_token_after_error_without_separator,
        )

    def test_08_append_comment_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_comment_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_comment_after_error,
        )

    def test_09_append_bad_tag_and_set_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_bad_tag_and_set_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_bad_tag_and_set_error,
        )

    def test_10_append_bad_tag_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_bad_tag_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_bad_tag_after_error,
        )

    def test_11_append_game_termination_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_game_termination_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_game_termination_after_error,
        )

    def test_12_append_comment_to_eol_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_comment_to_eol_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_comment_to_eol_after_error,
        )

    def test_13_append_escape_after_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_escape_after_error",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_escape_after_error,
        )

    def test_14_append_other_or_disambiguation_pgn_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_other_or_disambiguation_pgn",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_other_or_disambiguation_pgn,
        )

    def test_15_append_start_tag_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_start_tag",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_start_tag,
        )

    def test_16_append_game_termination_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.append_game_termination",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.append_game_termination,
        )

    def test_17_ignore_escape_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.ignore_escape",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.ignore_escape,
        )

    def test_18_ignore_end_of_file_marker_prefix_to_tag_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"GameCount.ignore_end_of_file_marker_prefix_to_tag",
                    r"\(\) missing 1 required positional argument: 'match'$",
                )
            ),
            self.gc1.ignore_end_of_file_marker_prefix_to_tag,
        )


class GameCount_method_calls(unittest.TestCase):
    def setUp(self):
        self.gc1 = tagpair_parser.GameCount()

    def test_01___init___01(self):
        ae = self.assertEqual
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_02_set_game_error_01(self):
        ae = self.assertEqual
        self.gc1.set_game_error()
        ae(self.gc1._state, 0)
        ae(self.gc1.game_offset, 0)

    def test_03_append_comment_to_eol_01(self):
        ae = self.assertEqual
        self.gc1.append_comment_to_eol(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_04_append_token_01(self):
        ae = self.assertEqual
        self.gc1.append_token(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_05_append_token_and_set_error_01(self):
        ae = self.assertEqual
        self.assertRaisesRegex(
            AttributeError,
            "'NoneType' object has no attribute 'group'$",
            self.gc1.append_token_and_set_error,
            *(None,),
        )
        ae(self.gc1._state, 0)
        ae(self.gc1.game_offset, 0)

    def test_06_append_token_after_error_01(self):
        ae = self.assertEqual
        self.gc1.append_token_after_error(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_07_append_token_after_error_without_separator_01(self):
        ae = self.assertEqual
        self.gc1.append_token_after_error_without_separator(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_08_append_comment_after_error_01(self):
        ae = self.assertEqual
        self.gc1.append_comment_after_error(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_09_append_bad_tag_and_set_error_01(self):
        ae = self.assertEqual
        self.gc1.append_bad_tag_and_set_error(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_10_append_bad_tag_after_error_01(self):
        ae = self.assertEqual
        self.gc1.append_bad_tag_after_error(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_11_append_game_termination_after_error_01(self):
        ae = self.assertEqual
        self.gc1.append_game_termination_after_error(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_12_append_comment_to_eol_after_error_01(self):
        ae = self.assertEqual
        self.gc1.append_comment_to_eol_after_error(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_13_append_escape_after_error_01(self):
        ae = self.assertEqual
        self.gc1.append_escape_after_error(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_14_append_other_or_disambiguation_pgn_01(self):
        ae = self.assertEqual
        self.assertRaisesRegex(
            AttributeError,
            "'NoneType' object has no attribute 'group'$",
            self.gc1.append_other_or_disambiguation_pgn,
            *(None,),
        )
        ae(self.gc1._state, 0)
        ae(self.gc1.game_offset, 0)

    def test_15_append_start_tag_01(self):
        ae = self.assertEqual
        self.gc1.append_start_tag(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_16_append_game_termination_01(self):
        ae = self.assertEqual
        self.gc1.append_game_termination(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_17_ignore_escape_01(self):
        ae = self.assertEqual
        self.gc1.ignore_escape(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)

    def test_18_ignore_end_of_file_marker_prefix_to_tag_01(self):
        ae = self.assertEqual
        self.gc1.ignore_end_of_file_marker_prefix_to_tag(None)
        ae(self.gc1._state, None)
        ae(self.gc1.game_offset, 0)


class TagPairGame_method_args(unittest.TestCase):
    def setUp(self):
        self.gc1 = tagpair_parser.TagPairGame()

    def test_01___init___01(self):
        self.assertRaisesRegex(
            TypeError,
            r"__init__\(\) takes 1 positional argument but 2 were given$",
            tagpair_parser.TagPairGame,
            *(None,),
        )

    def test_02_append_bad_tag_and_set_error_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"TagPairGame.append_bad_tag_and_set_error\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_bad_tag_and_set_error,
        )

    def test_03_append_start_tag_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"TagPairGame.append_start_tag\(\) missing 1 ",
                    r"required positional argument: 'match'$",
                )
            ),
            self.gc1.append_start_tag,
        )


class TagPairGame_method_calls(unittest.TestCase):
    def setUp(self):
        self.tpg1 = tagpair_parser.TagPairGame()

    def test_01___init___01(self):
        ae = self.assertEqual
        ae(self.tpg1._state, None)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {})

    def test_02_append_bad_tag_and_set_error_01(self):
        self.assertRaisesRegex(
            AttributeError,
            "'NoneType' object has no attribute 'group'$",
            self.tpg1.append_bad_tag_and_set_error,
            *(None,),
        )

    def test_02_append_bad_tag_and_set_error_02(self):
        ae = self.assertEqual
        match = tagpair_parser.game_format.match("anything")
        ae(match.lastindex, 13)
        self.tpg1.append_bad_tag_and_set_error(match)
        ae(self.tpg1._state, None)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"anything": ""})
        self.tpg1.append_bad_tag_and_set_error(match)
        ae(self.tpg1._state, 0)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"anything": ""})

    def test_02_append_bad_tag_and_set_error_03(self):
        ae = self.assertEqual
        match = tagpair_parser.game_format.match(r'[Na@me"va\lue"]')
        ae(match.lastindex, 11)
        self.tpg1.append_bad_tag_and_set_error(match)
        ae(self.tpg1._state, None)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"Na@me": "va\\\\lue"})
        match = tagpair_parser.game_format.match(r'[Na@me"nextva\lue"]')
        self.tpg1.append_bad_tag_and_set_error(match)
        ae(self.tpg1._state, 0)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"Na@me": "va\\\\lue"})
        match = tagpair_parser.game_format.match(r'[Name"nextva\lue"]')
        ae(match.lastindex, 3)
        self.tpg1.append_bad_tag_and_set_error(match)
        ae(self.tpg1._state, 0)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"Na@me": "va\\\\lue", "Name": "nextva\\\\lue"})

    def test_03_append_start_tag_01(self):
        self.assertRaisesRegex(
            AttributeError,
            "'NoneType' object has no attribute 'group'$",
            self.tpg1.append_start_tag,
            *(None,),
        )

    def test_03_append_start_tag_02(self):
        ae = self.assertEqual
        match = tagpair_parser.game_format.match('[Na@me"value"]')
        ae(match.lastindex, 11)
        self.tpg1.append_start_tag(match)
        ae(self.tpg1._state, None)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {None: None})

    def test_03_append_start_tag_03(self):
        ae = self.assertEqual
        match = tagpair_parser.game_format.match('[Name"value"]')
        ae(match.lastindex, 3)
        self.tpg1.append_start_tag(match)
        ae(self.tpg1._state, None)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"Name": "value"})
        match = tagpair_parser.game_format.match('[Name"nextvalue"]')
        ae(match.lastindex, 3)
        self.tpg1.append_start_tag(match)
        ae(self.tpg1._state, True)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"Name": "value"})
        match = tagpair_parser.game_format.match('[NextName"nextvalue"]')
        ae(match.lastindex, 3)
        self.tpg1.append_start_tag(match)
        ae(self.tpg1._state, True)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"Name": "value"})

    def test_03_append_start_tag_04(self):
        ae = self.assertEqual
        match = tagpair_parser.game_format.match('[Name"value"]')
        ae(match.lastindex, 3)
        self.tpg1.append_start_tag(match)
        match = tagpair_parser.game_format.match('[NextName"nextvalue"]')
        ae(match.lastindex, 3)
        self.tpg1.append_start_tag(match)
        ae(self.tpg1._state, None)
        ae(self.tpg1.game_offset, 0)
        ae(self.tpg1._tags, {"Name": "value", "NextName": "nextvalue"})


class _ReadGames:
    """Provide get() method which reads games from an io.StringIO object.

    Subclasses must provide a self.pgn object with a read_games() method.

    """

    def get(self, s):
        """Return sequence of Game instances derived from s."""
        return [g for g in self.pgn.read_games(io.StringIO(s))]


class _GameCountPGN(unittest.TestCase, _ReadGames):
    """Provide PGNTagPair parser with GameCount class to process PGN text."""

    def setUp(self):
        self.pgn = tagpair_parser.PGNTagPair(
            game_class=tagpair_parser.GameCount
        )


class _TagPairGamePGN(unittest.TestCase, _ReadGames):
    """Provide PGNTagPair parser with TagPairGame class to process PGN text."""

    def setUp(self):
        self.pgn = tagpair_parser.PGNTagPair(
            game_class=tagpair_parser.TagPairGame
        )


class ReadGames(unittest.TestCase, _ReadGames):
    """Verify operation of _ReadGames.get() method."""

    def test_01_get_01(self):
        ae = self.assertEqual
        self.pgn = tagpair_parser.PGNTagPair(
            game_class=tagpair_parser.GameCount
        )
        games = self.get("Anything")
        ae(len(games), 1)
        for game in games:
            ae(isinstance(game, tagpair_parser.GameCount), True)

    def test_02_get_01(self):
        ae = self.assertEqual
        self.pgn = tagpair_parser.PGNTagPair(
            game_class=tagpair_parser.TagPairGame
        )
        games = self.get("Anything")
        ae(len(games), 1)
        for game in games:
            ae(isinstance(game, tagpair_parser.TagPairGame), True)


class GameCountPGN(_GameCountPGN):
    """Test PGNTagPair parser using GameCount class to process PGN text."""

    def test_01_get_01(self):
        ae = self.assertEqual
        games = self.get("Anything*else")
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, tagpair_parser.GameCount), True)

    def test_01_get_02(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*Anything')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, tagpair_parser.GameCount), True)

    def test_01_get_03(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*')
        ae(len(games), 1)
        for game in games:
            ae(isinstance(game, tagpair_parser.GameCount), True)

    def test_01_get_04(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*[Name1"value1"]*')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, tagpair_parser.GameCount), True)

    def test_01_get_05(self):
        ae = self.assertEqual
        games = self.get('Anything[Name"value"]*')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, tagpair_parser.GameCount), True)

    def test_01_get_06(self):
        ae = self.assertEqual
        games = self.get('Anything [Name"value"]*')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, tagpair_parser.GameCount), True)

    def test_01_get_07(self):
        ae = self.assertEqual
        games = self.get('Anything\n[Name"value"]*')
        ae(len(games), 2)
        for game in games:
            ae(isinstance(game, tagpair_parser.GameCount), True)


class TagPairGamePGN(_TagPairGamePGN):
    """Test PGNTagPair parser using TagPairGame class to process PGN text."""

    def test_01_get_01(self):
        ae = self.assertEqual
        games = self.get("Anything*else")
        ae(len(games), 2)
        for game, tagcount in zip(games, [0]):
            ae(isinstance(game, tagpair_parser.TagPairGame), True)
            ae(len(game.pgn_tags), tagcount)

    def test_01_get_02(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*Anything')
        ae(len(games), 2)
        for game, tagcount in zip(games, [1, 0]):
            ae(isinstance(game, tagpair_parser.TagPairGame), True)
            ae(len(game.pgn_tags), tagcount)

    def test_01_get_03(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*')
        ae(len(games), 1)
        for game, tagcount in zip(games, [1]):
            ae(isinstance(game, tagpair_parser.TagPairGame), True)
            ae(len(game.pgn_tags), tagcount)

    def test_01_get_04(self):
        ae = self.assertEqual
        games = self.get('[Name"value"]*[Name1"value1"]*')
        ae(len(games), 2)
        for game, tagcount in zip(games, [1, 1]):
            ae(isinstance(game, tagpair_parser.TagPairGame), True)
            ae(len(game.pgn_tags), tagcount)

    def test_01_get_05(self):
        ae = self.assertEqual
        games = self.get('Anything[Name"value"]*')
        ae(len(games), 2)
        for game, tagcount in zip(games, [0]):
            ae(isinstance(game, tagpair_parser.TagPairGame), True)
            ae(len(game.pgn_tags), tagcount)

    def test_01_get_06(self):
        ae = self.assertEqual
        games = self.get('Anything [Name"value"]*')
        ae(len(games), 2)
        for game, tagcount in zip(games, [0, 1]):
            ae(isinstance(game, tagpair_parser.TagPairGame), True)
            ae(len(game.pgn_tags), tagcount)

    def test_01_get_07(self):
        ae = self.assertEqual
        games = self.get('Anything\n[Name"value"]*')
        ae(len(games), 2)
        for game, tagcount in zip(games, [0, 1]):
            ae(isinstance(game, tagpair_parser.TagPairGame), True)
            ae(len(game.pgn_tags), tagcount)


class AddTokenToGame(unittest.TestCase):
    """Verify operation of tagpair_parser.add_token_to_game() function."""

    def test_01_add_token_to_game_01(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"add_token_to_game\(\) missing 2 required ",
                    r"positional arguments: 'text' and 'game'$",
                )
            ),
            tagpair_parser.add_token_to_game,
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
            tagpair_parser.add_token_to_game,
            *(None, None, None, None),
        )

    def test_02_add_token_to_game_01(self):
        ae = self.assertEqual
        game = tagpair_parser.GameCount()
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
        pos = tagpair_parser.add_token_to_game(text, game, pos=0)
        ae(pos, 14)
        ae(game.state, None)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 16)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 24)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 34)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 44)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 53)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 76)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 77)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 91)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 106)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 121)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 122)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, None)
        ae(game.state, 0)

    def test_02_add_token_to_game_02(self):
        ae = self.assertEqual
        game = tagpair_parser.GameCount()
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
        pos = tagpair_parser.add_token_to_game(text, game, pos=0)
        ae(pos, 14)
        ae(game.state, None)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 22)
        ae(game.state, None)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 32)
        ae(game.state, None)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 42)
        ae(game.state, None)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 51)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 74)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 75)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 89)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 104)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 119)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, 120)
        ae(game.state, 0)
        pos = tagpair_parser.add_token_to_game(text, game, pos=pos)
        ae(pos, None)
        ae(game.state, 0)


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase

    runner().run(loader(GameCount_method_args))
    runner().run(loader(GameCount_method_calls))
    runner().run(loader(TagPairGame_method_args))
    runner().run(loader(TagPairGame_method_calls))
    runner().run(loader(ReadGames))
    runner().run(loader(GameCountPGN))
    runner().run(loader(TagPairGamePGN))
    runner().run(loader(AddTokenToGame))
