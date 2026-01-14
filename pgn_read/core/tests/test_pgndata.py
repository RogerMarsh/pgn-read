# test_pgndata.py
# Copyright 2026 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""game tests"""

import unittest
import re

from .. import pgndata
from .. import constants


class PGNDataModule(unittest.TestCase):

    def test_01_suffix_annotations(self):
        ae = self.assertEqual
        ae(isinstance(pgndata.suffix_annotations, re.Pattern), True)
        ae(pgndata.suffix_annotations.pattern, r"(!!|!\?|!|\?\?|\?!|\?)$")

    def test_02_white_black_tag_value_format(self):
        ae = self.assertEqual
        ae(isinstance(pgndata.white_black_tag_value_format, re.Pattern), True)
        ae(pgndata.white_black_tag_value_format.pattern, r"\s*([^,.\s]+)")

    def test_03_structured_comment_re(self):
        ae = self.assertEqual
        ae(isinstance(pgndata.structured_comment_re, re.Pattern), True)
        ae(pgndata.structured_comment_re.pattern, r"^{(?:\s*\[\s*%.*\])+\s*")

    def test_04_constants(self):
        ae = self.assertEqual
        ae(pgndata.NULL_PGN_COMMENT, "{}")
        ae(
            pgndata.COLLATION_ORDER,
            (
                "Date",
                "Event",
                "Site",
                "Round",
                "White",
                "Black",
                "Result",
            ),
        )

    def test_05_pgndata___class___attributes(self):
        ae = self.assertEqual
        ae(pgndata.PGNData._state, None)
        ae(pgndata.PGNData._movetext_offset, None)
        ae(pgndata.PGNData.game_offset, 0)


class PGNData(unittest.TestCase):

    def setUp(self):
        self.data = pgndata.PGNData()

    def test_01___init___01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            r"__init__\(\) takes 1 positional argument but 2 were given$",
            pgndata.PGNData,
            *(None,),
        )

    def test_01___init___02___dict__(self):
        ae = self.assertEqual
        ae(set(self.data.__dict__.keys()), set(["_tags", "_text"]))
        ae(self.data._tags, {})
        ae(self.data._text, [])

    def test_02_set_game_error_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"set_game_error\(\) takes 1 positional argument ",
                    r"but 2 were given$",
                )
            ),
            self.data.set_game_error,
            *(None,),
        )

    def test_02_set_game_error_02(self):
        ae = self.assertEqual
        ae("_state" in self.data.__dict__, False)
        self.data.set_game_error()
        ae("_state" in self.data.__dict__, True)
        ae(self.data._state, 0)

    def test_02_set_game_error_03(self):
        ae = self.assertEqual
        self.data._text.extend([1, 2, 3])
        ae(len(self.data._text), 3)
        self.data.set_game_error()
        ae(self.data._state, 3)
        self.data._text.append("a")
        self.data.set_game_error()
        ae(self.data._state, 3)

    def test_03_properties_01(self):
        ae = self.assertEqual
        ae(self.data.pgn_tags is self.data._tags, True)
        ae(self.data.pgn_text is self.data._text, True)
        ae(self.data.state is self.data._state, True)
        ae(self.data.movetext_offset is self.data._movetext_offset, True)

    def test_03_properties_02(self):
        ae = self.assertEqual
        ae(self.data.game_has_errors, False)
        self.data._text.append("a")
        self.data.set_game_error()
        ae(self.data.game_has_errors, True)

    def test_04_is_movetext_valid_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"is_movetext_valid\(\) takes 1 positional argument ",
                    r"but 2 were given$",
                )
            ),
            self.data.is_movetext_valid,
            *(None,),
        )

    def test_04_is_movetext_valid_02(self):
        ae = self.assertEqual
        ae(self.data.is_movetext_valid(), True)
        self.data._text.append("a")
        self.data.set_game_error()
        ae(self.data.is_movetext_valid(), False)

    def test_05_is_tag_roster_valid_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"is_tag_roster_valid\(\) takes 1 positional argument ",
                    r"but 2 were given$",
                )
            ),
            self.data.is_tag_roster_valid,
            *(None,),
        )

    def test_05_is_tag_roster_valid_02_no_tags(self):
        ae = self.assertEqual
        ae(self.data.is_tag_roster_valid(), False)

    def test_05_is_tag_roster_valid_03_empty_seven_tag_roster(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = ""
        ae(self.data.is_tag_roster_valid(), False)

    def test_05_is_tag_roster_valid_04_seven_tag_roster(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = "a"
        ae(self.data.is_tag_roster_valid(), True)

    def test_05_is_tag_roster_valid_05_empty_supplemental_tag(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = "a"
        self.data._tags[constants.TAG_BLACKELO] = ""
        ae(constants.TAG_BLACKELO in constants.SUPPLEMENTAL_TAG_ROSTER, True)
        ae(self.data.is_tag_roster_valid(), False)

    def test_05_is_tag_roster_valid_06_supplemental_tag(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = "a"
        self.data._tags[constants.TAG_WHITEELO] = "a"
        ae(constants.TAG_WHITEELO in constants.SUPPLEMENTAL_TAG_ROSTER, True)
        ae(self.data.is_tag_roster_valid(), True)

    def test_05_is_tag_roster_valid_07_other_tag(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = "a"
        self.data._tags[constants.TAG_BLACKTITLE] = "a"
        self.data._tags["other tag 1"] = ""
        self.data._tags["other tag 2"] = "a"
        ae("other tag 1" in constants.SUPPLEMENTAL_TAG_ROSTER, False)
        ae("other tag 2" in constants.SUPPLEMENTAL_TAG_ROSTER, False)
        ae(self.data.is_tag_roster_valid(), True)

    def test_06_is_pgn_valid_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"is_pgn_valid\(\) takes 1 positional argument ",
                    r"but 2 were given$",
                )
            ),
            self.data.is_pgn_valid,
            *(None,),
        )

    def test_06_is_pgn_valid_02_bad_tags_good_movetext(self):
        ae = self.assertEqual
        ae(self.data.is_pgn_valid(), False)

    def test_06_is_pgn_valid_03_good_tags_good_movetext(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = "a"
        ae(self.data.is_pgn_valid(), True)

    def test_06_is_pgn_valid_04_bad_tags_bad_movetext(self):
        ae = self.assertEqual
        self.data._text.append("a")
        self.data.set_game_error()
        ae(self.data.is_pgn_valid(), False)

    def test_06_is_pgn_valid_05_good_tags_bad_movetext(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = "a"
        self.data._text.append("a")
        self.data.set_game_error()
        ae(self.data.is_pgn_valid(), False)

    def test_07_is_pgn_valid_export_format_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"is_pgn_valid_export_format\(\) takes 1 positional ",
                    r"argument but 2 were given$",
                )
            ),
            self.data.is_pgn_valid_export_format,
            *(None,),
        )

    def test_07_is_pgn_valid_export_format_02_is_pgn_valid_false(self):
        ae = self.assertEqual
        ae(self.data.is_pgn_valid_export_format(), False)

    def test_07_is_pgn_valid_export_format_03_is_pgn_valid_bad_result(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = "a"
        self.data._text.append("b")
        ae(self.data.is_pgn_valid_export_format(), False)

    def test_07_is_pgn_valid_export_format_04_is_pgn_valid_good_result(self):
        ae = self.assertEqual
        for tag in constants.SEVEN_TAG_ROSTER:
            self.data._tags[tag] = "a"
        self.data._text.append("a")
        ae(self.data.is_pgn_valid_export_format(), True)

    def test_08_get_tags_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_tags\(\) takes from 1 to 2 positional ",
                    r"arguments but 3 were given$",
                )
            ),
            self.data.get_tags,
            *(None, None),
        )

    def test_08_get_tags_02_default_separator(self):
        ae = self.assertEqual
        self.data._tags = {"key2": "value2", "key1": "value1"}
        ae(
            sorted(self.data.get_tags()),
            ['[key1 "value1"]', '[key2 "value2"]'],
        )

    def test_08_get_tags_03_null_separator(self):
        ae = self.assertEqual
        self.data._tags = {"key2": "value2", "key1": "value1"}
        ae(
            sorted(self.data.get_tags(name_value_separator="")),
            ['[key1"value1"]', '[key2"value2"]'],
        )

    def test_09_get_tags_in_text_order_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_tags_in_text_order\(\) takes 1 positional ",
                    r"argument but 2 were given$",
                )
            ),
            self.data.get_tags_in_text_order,
            *(None,),
        )

    def test_09_get_tags_in_text_order_02_no_movetext(self):
        ae = self.assertEqual
        self.data._text.extend([1, 2, 3])
        ae(self.data.get_tags_in_text_order(), [])

    def test_09_get_tags_in_text_order_03_movetext(self):
        ae = self.assertEqual
        self.data._text.extend(["a", "b", "c"])
        self.data._movetext_offset = 2
        ae(self.data.get_tags_in_text_order(), ["a", "b"])

    def test_10_get_non_seven_tag_roster_tags_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_non_seven_tag_roster_tags\(\) takes 1 positional ",
                    r"argument but 2 were given$",
                )
            ),
            self.data.get_non_seven_tag_roster_tags,
            *(None,),
        )

    def test_10_get_non_seven_tag_roster_tags_02_three_tags(self):
        ae = self.assertEqual
        self.data._tags = {"key2": "value2", "Event": "test", "key1": "value1"}
        ae(
            self.data.get_non_seven_tag_roster_tags(),
            '[key1 "value1"]\n[key2 "value2"]',
        )

    def test_11_get_seven_tag_roster_tags_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_seven_tag_roster_tags\(\) takes 1 positional ",
                    r"argument but 2 were given$",
                )
            ),
            self.data.get_seven_tag_roster_tags,
            *(None,),
        )

    def test_11_get_seven_tag_roster_tags_02_name_formats(self):
        ae = self.assertEqual
        non_name_tags = {
            "Result": "1-0",
            "Round": "2",
            "Site": "Hall",
            "Date": "2026.01.09",
            "Event": "Match",
        }
        tag_text = [
            "\n".join(
                (
                    " ".join(("[Event", '"Match"]')),
                    " ".join(("[Site", '"Hall"]')),
                    " ".join(("[Date", '"2026.01.09"]')),
                    " ".join(("[Round", '"2"]')),
                )
            ),
            " ".join(("[Result", '"1-0"]')),
        ]
        name_tags = (
            {"Black": "Tal", "White": "Smyslov Vassily V"},
            {"Black": "Tal", "White": "Smyslov, Vassily V"},
            {"Black": "Tal", "White": "Smyslov Vassily V."},
            {"Black": "Tal", "White": "Smyslov, Vassily V."},
            {"Black": "Tal", "White": "Smyslov Vassily"},
            {"Black": "Tal", "White": "Smyslov, Vassily"},
            {"Black": "Tal", "White": "Smyslov V."},
            {"Black": "Tal", "White": "Smyslov, V."},
            {"Black": "Tal", "White": "Smyslov V"},
            {"Black": "Tal", "White": "Smyslov, V"},
            {"Black": "Tal", "White": "Smyslov V. Vassily"},
            {"Black": "Tal", "White": "Smyslov, V. Vassily"},
            {"Black": "Tal", "White": "Smyslov V Vassily"},
            {"Black": "Tal", "White": "Smyslov, V Vassily"},
            {"Black": "Smyslov V Vassily", "White": "Tal"},
            {"Black": "Smyslov, V Vassily", "White": "Tal"},
            {"Black": "Smyslov V. Vassily", "White": "Tal"},
            {"Black": "Smyslov, V. Vassily", "White": "Tal"},
            {"Black": "Smyslov Vassily", "White": "Tal"},
            {"Black": "Smyslov, Vassily", "White": "Tal"},
            {"Black": "Smyslov V.", "White": "Tal"},
            {"Black": "Smyslov, V.", "White": "Tal"},
            {"Black": "Smyslov V", "White": "Tal"},
            {"Black": "Smyslov, V", "White": "Tal"},
            {"Black": "Smyslov V. Vassily", "White": "Tal"},
            {"Black": "Smyslov, V. Vassily", "White": "Tal"},
            {"Black": "Smyslov V Vassily", "White": "Tal"},
            {"Black": "Smyslov, V Vassily", "White": "Tal"},
            {"Black": "Tal", "White": "Smith Jones, J"},
            {"Black": "Smith Jones, John", "White": "Tal"},
            {"Black": "Tal", "White": "Smith-Jones, J"},
            {"Black": "Smith-Jones, John", "White": "Tal"},
        )
        name_text = [
            "\n".join(('[White "Smyslov, Vassily V."]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, Vassily V."]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, Vassily V."]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, Vassily V."]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, Vassily"]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, Vassily"]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, V."]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, V."]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, V."]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, V."]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, V. Vassily"]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, V. Vassily"]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, V. Vassily"]', '[Black "Tal"]')),
            "\n".join(('[White "Smyslov, V. Vassily"]', '[Black "Tal"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V. Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V. Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V. Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V. Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V."]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V."]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V."]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V."]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V. Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V. Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V. Vassily"]')),
            "\n".join(('[White "Tal"]', '[Black "Smyslov, V. Vassily"]')),
            "\n".join(('[White "Smith, Jones J."]', '[Black "Tal"]')),
            "\n".join(('[White "Tal"]', '[Black "Smith, Jones John"]')),
            "\n".join(('[White "Smith-Jones, J."]', '[Black "Tal"]')),
            "\n".join(('[White "Tal"]', '[Black "Smith-Jones, John"]')),
        ]
        for tags, text in zip(name_tags, name_text):
            with self.subTest(tags=tags, text=text):
                tags.update(non_name_tags)
                self.data._tags = tags
                ae(
                    self.data.get_seven_tag_roster_tags(),
                    "\n".join((tag_text[0], text, tag_text[1])),
                )

    def test_12__set_movetext_indicators_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"_set_movetext_indicators\(\) takes 1 positional ",
                    r"argument but 2 were given$",
                )
            ),
            self.data._set_movetext_indicators,
            *(None,),
        )

    def test_12__set_movetext_indicators_02_fen_tag(self):
        ae = self.assertEqual
        fen_tag = (
            {},
            {"FEN": "t w t t t 12"},
            {"FEN": "t b t t t 13"},
        )
        movetext_indicators = (
            (1, "w"),
            (12, "w"),
            (13, "b"),
        )
        for fen, indicator in zip(fen_tag, movetext_indicators):
            with self.subTest(fen=fen, indicator=indicator):
                self.data._tags = fen
                ae(self.data._set_movetext_indicators(), indicator)

    def test_13_get_movetext_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_movetext\(\) takes 1 positional ",
                    r"argument but 2 were given$",
                )
            ),
            self.data.get_movetext,
            *(None,),
        )

    def test_13_get_movetext_02_no_movetext(self):
        ae = self.assertEqual
        self.data._text.extend([1, 2, 3])
        ae(self.data.get_movetext(), [])

    def test_13_get_movetext_03_movetext(self):
        ae = self.assertEqual
        self.data._text.extend(["a", "b", "c"])
        self.data._movetext_offset = 2
        ae(self.data.get_movetext(), ["c"])

    def test_14_get_text_of_game_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_text_of_game\(\) takes 1 positional ",
                    r"argument but 2 were given$",
                )
            ),
            self.data.get_text_of_game,
            *(None,),
        )

    def test_14_get_text_of_game_02_text(self):
        ae = self.assertEqual
        self.data._text.extend(["a", "b", "c"])
        ae(self.data.get_text_of_game(), "abc")

    def test_15__add_token_to_movetext_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"_add_token_to_movetext\(\) takes 3 positional ",
                    r"arguments but 4 were given$",
                )
            ),
            self.data._add_token_to_movetext,
            *(None, None, None, None),
        )

    def test_15__add_token_to_movetext_01_add(self):
        ae = self.assertEqual
        add = self.data._add_token_to_movetext
        length = 0
        token = "abcdefghijklmnopqrstuvwxyz"
        movetext = []
        length = add(token, movetext, length)
        ae(len(movetext), 1)
        ae(movetext[-1], token)
        length = add(token, movetext, length)
        ae(len(movetext), 3)
        ae(movetext[-2], " ")
        ae(movetext[-1], token)
        length = add(token, movetext, length)
        ae(len(movetext), 5)
        ae(movetext[-2], "\n")
        ae(movetext[-1], token)
        length = add(token, movetext, length)
        ae(len(movetext), 7)
        ae(movetext[-1], token)


class PGNDataExport(unittest.TestCase):

    def setUp(self):
        self.data = pgndata.PGNData()
        self.data._tags = {
            "WhiteELO": "1921",
            "Black": "Smith",
            "Result": "1-0",
            "Round": "2",
            "ECO": "E12",
            "Site": "Hall",
            "Date": "2026.01.09",
            "Event": "Match",
            "White": "Jones",
            "BlackELO": "1901",
            "Source": "Controller",
            "PlyCount": "34",
        }
        self.data._text = [
            '[PlyCount "34"]',
            '[Source ""]',
            '[BlackELO ""]',
            '[White ""]',
            '[Event ""]',
            '[Date ""]',
            '[Site ""]',
            '[ECO ""]',
            '[Round ""]',
            '[Result ""]',
            '[Black ""]',
            '[WhiteELO ""]',
            "e4",
            "(",
            "d4",
            ")",
            "e5",
            "(",
            "e6",
            ")",
            "Nf3",
            "{Comment One}",
            "Nc6",
            "{Comment Two}",
            "Bb5",
            "{[%eval 0]}",
            "$5",
            "a6",
            "{[%eval 0] Comment Three}",
            "Ba4",
            ";Comment to EOL\n",
            "b5",
            "Bb3",
            "Be7",
            "1-0",
        ]

    def test_01_get_all_movetext_in_pgn_export_format_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_all_movetext_in_pgn_export_format\(\) takes 1 ",
                    r"positional argument but 2 were given$",
                )
            ),
            self.data.get_all_movetext_in_pgn_export_format,
            *(None,),
        )

    def test_01_get_all_movetext_in_pgn_export_format_02_no_movetext(self):
        ae = self.assertEqual
        ae(self.data.get_all_movetext_in_pgn_export_format(), "\n")

    def test_01_get_all_movetext_in_pgn_export_format_03_movetext(self):
        ae = self.assertEqual
        self.data._movetext_offset = 12
        ae(
            self.data.get_all_movetext_in_pgn_export_format(),
            "".join(
                (
                    "\n1. e4 ( 1. d4 ) 1... e5 ( 1... e6 ) 2. Nf3 ",
                    "{Comment One} 2... Nc6 {Comment Two}\n",
                    "3. Bb5 {[%eval 0]} $5 3... a6 {[%eval 0] Comment Three} ",
                    "4. Ba4 ;Comment to EOL\n",
                    "4... b5 5. Bb3 Be7 1-0",
                )
            ),
        )

    def test_02_get_movetext_no_comments_export_format_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_movetext_without_comments_in_pgn_export_format\(\) ",
                    r"takes 1 positional argument but 2 were given$",
                )
            ),
            self.data.get_movetext_without_comments_in_pgn_export_format,
            *(None,),
        )

    def test_02_get_movetext_no_comments_export_format_02_no_movetext(self):
        ae = self.assertEqual
        ae(
            self.data.get_movetext_without_comments_in_pgn_export_format(),
            "\n",
        )

    def test_02_get_movetext_no_comments_export_format_03_movetext(self):
        ae = self.assertEqual
        self.data._movetext_offset = 12
        ae(
            self.data.get_movetext_without_comments_in_pgn_export_format(),
            "".join(
                (
                    "\n1. e4 ( 1. d4 ) 1... e5 ( 1... e6 ) 2. Nf3 ",
                    "Nc6 ",
                    "3. Bb5 a6 ",
                    "4. Ba4 ",
                    "b5 5. Bb3 Be7\n1-0",
                )
            ),
        )

    def test_03_get_export_movetext_no_structured_comments_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_export_movetext_without_structured_comments\(\) ",
                    r"takes 1 positional argument but 2 were given$",
                )
            ),
            self.data.get_export_movetext_without_structured_comments,
            *(None,),
        )

    def test_03_get_export_movetext_no_structured_comments_02_no_mvtext(self):
        ae = self.assertEqual
        ae(self.data.get_export_movetext_without_structured_comments(), "\n")

    def test_03_get_export_movetext_no_structured_comments_03_movetext(self):
        ae = self.assertEqual
        self.data._movetext_offset = 12
        ae(
            self.data.get_export_movetext_without_structured_comments(),
            "".join(
                (
                    "\n1. e4 ( 1. d4 ) 1... e5 ( 1... e6 ) 2. Nf3 ",
                    "{Comment One} 2... Nc6 {Comment Two}\n",
                    "3. Bb5 $5 a6 {Comment Three} ",
                    "4. Ba4 ;Comment to EOL\n",
                    "4... b5 5. Bb3 Be7 1-0",
                )
            ),
        )

    def test_04_get_archive_movetext_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_archive_movetext\(\) takes 1 ",
                    r"positional argument but 2 were given$",
                )
            ),
            self.data.get_archive_movetext,
            *(None,),
        )

    def test_04_get_archive_movetext_02_no_movetext(self):
        ae = self.assertEqual
        ae(self.data.get_archive_movetext(), "\n")

    def test_04_get_archive_movetext_03_movetext(self):
        ae = self.assertEqual
        self.data._movetext_offset = 12
        ae(
            self.data.get_archive_movetext(),
            "".join(
                (
                    "\n1. e4 e5 2. Nf3 ",
                    "Nc6 ",
                    "3. Bb5 a6 ",
                    "4. Ba4 ",
                    "b5 5. Bb3 Be7 1-0",
                )
            ),
        )

    def test_05_get_seven_tag_roster_tags(self):
        ae = self.assertEqual
        ae(
            self.data.get_seven_tag_roster_tags(),
            "\n".join(
                (
                    '[Event "Match"]',
                    '[Site "Hall"]',
                    '[Date "2026.01.09"]',
                    '[Round "2"]',
                    '[White "Jones"]',
                    '[Black "Smith"]',
                    '[Result "1-0"]',
                )
            ),
        )

    def test_06_get_non_seven_tag_roster_tags(self):
        ae = self.assertEqual
        ae(
            self.data.get_non_seven_tag_roster_tags(),
            "\n".join(
                (
                    '[BlackELO "1901"]',
                    '[ECO "E12"]',
                    '[PlyCount "34"]',
                    '[Source "Controller"]',
                    '[WhiteELO "1921"]',
                )
            ),
        )


class PGNDataCollation(unittest.TestCase):

    def setUp(self):
        self.data = pgndata.PGNData()

    def test_01_get_collation_01_bad_call(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"get_collation\(\) takes 1 ",
                    r"positional argument but 2 were given$",
                )
            ),
            self.data.get_collation,
            *(None,),
        )

    def test_02_get_collation_01_default(self):
        ae = self.assertEqual
        self.data._tags = {
            "Black": "?",
            "Result": "*",
            "Round": "?",
            "Site": "?",
            "Date": "????.??.??",
            "Event": "?",
            "White": "?",
        }
        ae(
            self.data.get_collation(),
            [
                "0000.00.00",
                "?",
                "?",
                " ",
                "?",
                "?",
                "*",
                (1, " "),
                [],
            ],
        )

    def test_02_get_collation_02_none_default(self):
        ae = self.assertEqual
        self.data._tags = {
            "Black": "a",
            "Result": "b",
            "Round": "c",
            "Site": "d",
            "Date": "e",
            "Event": "f",
            "White": "g",
        }
        ae(
            self.data.get_collation(),
            [
                "e",
                "f",
                "d",
                "c",
                "g",
                "a",
                "b",
                (1, " "),
                [],
            ],
        )

    def test_02_get_collation_03_non_default_date(self):
        ae = self.assertEqual
        self.data._tags = {
            "Black": "?",
            "Result": "*",
            "Round": "?",
            "Site": "?",
            "Date": "????.??.?3",
            "Event": "?",
            "White": "?",
        }
        ae(
            self.data.get_collation(),
            [
                "0000.00.03",
                "?",
                "?",
                " ",
                "?",
                "?",
                "*",
                (1, " "),
                [],
            ],
        )

    def test_02_get_collation_04_non_default_date(self):
        ae = self.assertEqual
        self.data._tags = {
            "Black": "?",
            "Result": "*",
            "Round": "?",
            "Site": "?",
            "Date": "2026.??.??",
            "Event": "?",
            "White": "?",
        }
        ae(
            self.data.get_collation(),
            [
                "2026.00.00",
                "?",
                "?",
                " ",
                "?",
                "?",
                "*",
                (1, " "),
                [],
            ],
        )


class PGNDataCompareDefault(unittest.TestCase):

    def setUp(self):
        self.data = pgndata.PGNData()
        self.data._tags = {
            "Date": "2026.??.??",
            "Event": "?",
            "Site": "?",
            "Round": "?",
            "White": "?",
            "Black": "?",
            "Result": "*",
        }
        self.comp = pgndata.PGNData()
        self.comp._tags = {
            "Date": "2026.??.??",
            "Event": "?",
            "Site": "?",
            "Round": "?",
            "White": "?",
            "Black": "?",
            "Result": "*",
        }

    def test_01_default_same(self):
        ae = self.assertEqual
        ae(self.data == self.comp, True)
        ae(self.data >= self.comp, True)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, False)
        ae(self.data != self.comp, False)

    def test_02_default_movetext_differ(self):
        ae = self.assertEqual
        self.comp._text = ["a"]
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_03_default_fen_differ_01_b1(self):
        ae = self.assertEqual
        self.comp._tags["FEN"] = "a b c d e 1"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_03_default_fen_differ_02_w1(self):
        ae = self.assertEqual
        self.comp._tags["FEN"] = "a w c d e 1"
        ae(self.data == self.comp, True)
        ae(self.data >= self.comp, True)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, False)
        ae(self.data != self.comp, False)

    def test_03_default_fen_differ_03_w2(self):
        ae = self.assertEqual
        self.comp._tags["FEN"] = "a w c d e 2"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_04_default_result_differ(self):
        ae = self.assertEqual
        self.comp._tags["Result"] = "1-0"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_05_default_black_differ(self):
        ae = self.assertEqual
        self.comp._tags["Black"] = "Smith"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_06_default_white_differ(self):
        ae = self.assertEqual
        self.comp._tags["White"] = "Smith"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_07_default_round_differ_01_dash(self):
        ae = self.assertEqual
        self.comp._tags["Round"] = "-"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_07_default_round_differ_02_1(self):
        ae = self.assertEqual
        self.comp._tags["Round"] = "1"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_08_default_site_differ(self):
        ae = self.assertEqual
        self.comp._tags["Site"] = "Hall"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_09_default_event_differ(self):
        ae = self.assertEqual
        self.comp._tags["Event"] = "Match"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_10_default_date_differ(self):
        ae = self.assertEqual
        self.comp._tags["Date"] = "2026.01.14"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)


class PGNDataCompareNonDefault(unittest.TestCase):

    def setUp(self):
        self.data = pgndata.PGNData()
        self.data._tags = {
            "Date": "2026.01.15",
            "Event": "Match",
            "Site": "Hall",
            "Round": "2",
            "White": "Gray",
            "Black": "Green",
            "Result": "0-1",
            "FEN": "a w c d e 4",
        }
        self.data._text = ["d4"]
        self.comp = pgndata.PGNData()
        self.comp._tags = {
            "Date": "2026.01.15",
            "Event": "Match",
            "Site": "Hall",
            "Round": "2",
            "White": "Gray",
            "Black": "Green",
            "Result": "0-1",
            "FEN": "a w c d e 4",
        }
        self.comp._text = ["d4"]

    def test_01_non_default_same(self):
        ae = self.assertEqual
        ae(self.data == self.comp, True)
        ae(self.data >= self.comp, True)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, False)
        ae(self.data != self.comp, False)

    def test_02_non_default_movetext_differ(self):
        ae = self.assertEqual
        self.comp._text = ["e4"]
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_03_non_default_fen_differ_01_b1(self):
        ae = self.assertEqual
        self.comp._tags["FEN"] = "a b c d e 5"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_03_non_default_fen_differ_02_w1(self):
        ae = self.assertEqual
        self.comp._tags["FEN"] = "a w c d e 4"
        ae(self.data == self.comp, True)
        ae(self.data >= self.comp, True)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, False)
        ae(self.data != self.comp, False)

    def test_03_non_default_fen_differ_03_w2(self):
        ae = self.assertEqual
        self.comp._tags["FEN"] = "a w c d e 5"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_04_non_default_result_differ(self):
        ae = self.assertEqual
        self.comp._tags["Result"] = "1-0"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_05_non_default_black_differ(self):
        ae = self.assertEqual
        self.comp._tags["Black"] = "Smith"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_06_non_default_white_differ(self):
        ae = self.assertEqual
        self.comp._tags["White"] = "Smith"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_07_non_default_round_differ_01_dash(self):
        ae = self.assertEqual
        self.comp._tags["Round"] = "-"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, True)
        ae(self.data > self.comp, True)
        ae(self.data <= self.comp, False)
        ae(self.data < self.comp, False)
        ae(self.data != self.comp, True)

    def test_07_non_default_round_differ_02_1(self):
        ae = self.assertEqual
        self.comp._tags["Round"] = "5"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_08_non_default_site_differ(self):
        ae = self.assertEqual
        self.comp._tags["Site"] = "Town"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_09_non_default_event_differ(self):
        ae = self.assertEqual
        self.comp._tags["Event"] = "Tourney"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)

    def test_10_non_default_date_differ(self):
        ae = self.assertEqual
        self.comp._tags["Date"] = "2026.02.14"
        ae(self.data == self.comp, False)
        ae(self.data >= self.comp, False)
        ae(self.data > self.comp, False)
        ae(self.data <= self.comp, True)
        ae(self.data < self.comp, True)
        ae(self.data != self.comp, True)


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase

    runner().run(loader(PGNDataModule))
    runner().run(loader(PGNData))
    runner().run(loader(PGNDataExport))
    runner().run(loader(PGNDataCollation))
    runner().run(loader(PGNDataCompareDefault))
    runner().run(loader(PGNDataCompareNonDefault))
