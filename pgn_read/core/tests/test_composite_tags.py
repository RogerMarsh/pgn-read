# test_composite_tags.py
# Copyright 2024 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test PGN tokens which have values marked by '[]', '{}' , '""', and '<>'.

The test_constants module verifies values of regular expression components.

This module tests their interaction.

"""

import unittest
import re

from .. import constants

pgntag = re.compile(constants.PGN_TAG)
tagpair = re.compile(constants.TAG_PAIR)
comment = re.compile(constants.COMMENT)
reserved = re.compile(constants.RESERVED)
badcomment = re.compile(constants.BAD_COMMENT)
badreserved = re.compile(constants.BAD_RESERVED)
tagpairdataerror = re.compile(constants.TAG_PAIR_DATA_ERROR)
tagpairformat = re.compile(constants.TAG_PAIR_FORMAT)
gameformat = re.compile(constants.GAME_FORMAT)
pgnformat = re.compile(constants.PGN_FORMAT)
importformat = re.compile(constants.IMPORT_FORMAT)
textformat = re.compile(constants.TEXT_FORMAT)
ignorecaseformat = re.compile(constants.IGNORE_CASE_FORMAT)


class Comment(unittest.TestCase):
    def setUp(self):
        self.tag = "prefix{comment}suffix"
        self.tagbad = "prefix{commentsuffix"
        self.move = "a4{comment}a5"

    def test_01_all_tag_searches(self):
        ae = self.assertEqual
        ae(pgntag.search(self.tag) is None, True)
        ae(tagpair.search(self.tag) is None, True)
        ae(isinstance(comment.search(self.tag), re.Match), True)
        ae(reserved.search(self.tag) is None, True)
        ae(isinstance(badcomment.search(self.tag), re.Match), True)
        ae(badreserved.search(self.tag) is None, True)
        ae(tagpairdataerror.search(self.tag) is None, True)
        ae(isinstance(tagpairformat.search(self.tag), re.Match), True)
        ae(isinstance(gameformat.search(self.tag), re.Match), True)
        ae(isinstance(pgnformat.search(self.tag), re.Match), True)
        ae(isinstance(importformat.search(self.tag), re.Match), True)
        ae(isinstance(textformat.search(self.tag), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.tag), re.Match), True)

    def test_02_all_tagbad_searches(self):
        ae = self.assertEqual
        ae(pgntag.search(self.tagbad) is None, True)
        ae(tagpair.search(self.tagbad) is None, True)
        ae(comment.search(self.tagbad) is None, True)
        ae(reserved.search(self.tagbad) is None, True)
        ae(isinstance(badcomment.search(self.tagbad), re.Match), True)
        ae(badreserved.search(self.tagbad) is None, True)
        ae(tagpairdataerror.search(self.tagbad) is None, True)
        ae(isinstance(tagpairformat.search(self.tagbad), re.Match), True)
        ae(isinstance(gameformat.search(self.tagbad), re.Match), True)
        ae(isinstance(pgnformat.search(self.tagbad), re.Match), True)
        ae(isinstance(importformat.search(self.tagbad), re.Match), True)
        ae(isinstance(textformat.search(self.tagbad), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.tagbad), re.Match), True)

    def test_03_all_move_searches(self):
        ae = self.assertEqual
        ae(pgntag.search(self.move) is None, True)
        ae(tagpair.search(self.move) is None, True)
        ae(isinstance(comment.search(self.move), re.Match), True)
        ae(reserved.search(self.move) is None, True)
        ae(isinstance(badcomment.search(self.move), re.Match), True)
        ae(badreserved.search(self.move) is None, True)
        ae(tagpairdataerror.search(self.move) is None, True)
        ae(isinstance(tagpairformat.search(self.move), re.Match), True)
        ae(isinstance(gameformat.search(self.move), re.Match), True)
        ae(isinstance(pgnformat.search(self.move), re.Match), True)
        ae(isinstance(importformat.search(self.move), re.Match), True)
        ae(isinstance(textformat.search(self.move), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.move), re.Match), True)

    def test_04_comment_and_badcomment(self):
        ae = self.assertEqual
        tagmatch = comment.search(self.tag)
        ae(tagmatch.group(), "{comment}")
        tagmatch = badcomment.search(self.tag)
        ae(tagmatch.group(), "{comment")
        tagbadmatch = badcomment.search(self.tagbad)
        ae(tagbadmatch.group(), "{commentsuffix")
        movematch = comment.search(self.move)
        ae(movematch.group(), "{comment}")
        movematch = badcomment.search(self.move)
        ae(movematch.group(), "{comment")

    def test_05_tagpairformat(self):
        ae = self.assertEqual
        matches = tagpairformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix", "{comment}", "suffix"])
        matches = tagpairformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix", "{commentsuffix"])
        matches = tagpairformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "{comment}", "a5"])

    def test_06_gameformat(self):
        ae = self.assertEqual
        matches = gameformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix{comment}suffix"])
        matches = gameformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix{commentsuffix"])
        matches = gameformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "{comment}", "a5"])

    def test_07_pgnformat(self):
        ae = self.assertEqual
        matches = pgnformat.finditer(self.tag)
        ae([m.group() for m in matches], ["{comment}"])
        matches = pgnformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["{commentsuffix"])
        matches = pgnformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "{comment}", "a5"])

    def test_08_importformat(self):
        ae = self.assertEqual
        matches = importformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix{comment}suffix"])
        matches = importformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix{commentsuffix"])
        matches = importformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "{comment}", "a5"])

    def test_09_textformat(self):
        ae = self.assertEqual
        matches = textformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix{comment}suffix"])
        matches = textformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix{commentsuffix"])
        matches = textformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "{comment}", "a5"])

    def test_10_ignorecaseformat(self):
        ae = self.assertEqual
        matches = ignorecaseformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix{comment}suffix"])
        matches = ignorecaseformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix{commentsuffix"])
        matches = ignorecaseformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "{comment}", "a5"])


class Reserved(unittest.TestCase):
    def setUp(self):
        self.tag = "prefix<reserved>suffix"
        self.tagbad = "prefix<reservedsuffix"
        self.move = "a4<reserved>a5"

    def test_01_all_tag_searches(self):
        ae = self.assertEqual
        ae(pgntag.search(self.tag) is None, True)
        ae(tagpair.search(self.tag) is None, True)
        ae(comment.search(self.tag) is None, True)
        ae(isinstance(reserved.search(self.tag), re.Match), True)
        ae(badcomment.search(self.tag) is None, True)
        ae(isinstance(badreserved.search(self.tag), re.Match), True)
        ae(tagpairdataerror.search(self.tag) is None, True)
        ae(isinstance(tagpairformat.search(self.tag), re.Match), True)
        ae(isinstance(gameformat.search(self.tag), re.Match), True)
        ae(isinstance(pgnformat.search(self.tag), re.Match), True)
        ae(isinstance(importformat.search(self.tag), re.Match), True)
        ae(isinstance(textformat.search(self.tag), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.tag), re.Match), True)

    def test_02_all_tagbad_searches(self):
        ae = self.assertEqual
        ae(pgntag.search(self.tagbad) is None, True)
        ae(tagpair.search(self.tagbad) is None, True)
        ae(comment.search(self.tagbad) is None, True)
        ae(reserved.search(self.tagbad) is None, True)
        ae(badcomment.search(self.tagbad) is None, True)
        ae(isinstance(badreserved.search(self.tagbad), re.Match), True)
        ae(tagpairdataerror.search(self.tagbad) is None, True)
        ae(isinstance(tagpairformat.search(self.tagbad), re.Match), True)
        ae(isinstance(gameformat.search(self.tagbad), re.Match), True)
        ae(isinstance(pgnformat.search(self.tagbad), re.Match), True)
        ae(isinstance(importformat.search(self.tagbad), re.Match), True)
        ae(isinstance(textformat.search(self.tagbad), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.tagbad), re.Match), True)

    def test_03_all_move_searches(self):
        ae = self.assertEqual
        ae(pgntag.search(self.move) is None, True)
        ae(tagpair.search(self.move) is None, True)
        ae(comment.search(self.move) is None, True)
        ae(isinstance(reserved.search(self.move), re.Match), True)
        ae(badcomment.search(self.move) is None, True)
        ae(isinstance(badreserved.search(self.move), re.Match), True)
        ae(tagpairdataerror.search(self.move) is None, True)
        ae(isinstance(tagpairformat.search(self.move), re.Match), True)
        ae(isinstance(gameformat.search(self.move), re.Match), True)
        ae(isinstance(pgnformat.search(self.move), re.Match), True)
        ae(isinstance(importformat.search(self.move), re.Match), True)
        ae(isinstance(textformat.search(self.move), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.move), re.Match), True)

    def test_04_reserved_and_badreserved(self):
        ae = self.assertEqual
        tagmatch = reserved.search(self.tag)
        ae(tagmatch.group(), "<reserved>")
        tagmatch = badreserved.search(self.tag)
        ae(tagmatch.group(), "<reserved")
        tagbadmatch = badreserved.search(self.tagbad)
        ae(tagbadmatch.group(), "<reservedsuffix")
        movematch = reserved.search(self.move)
        ae(movematch.group(), "<reserved>")
        movematch = badreserved.search(self.move)
        ae(movematch.group(), "<reserved")

    def test_05_tagpairformat(self):
        ae = self.assertEqual
        matches = tagpairformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix", "<reserved>", "suffix"])
        matches = tagpairformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix", "<reservedsuffix"])
        matches = tagpairformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "<reserved>", "a5"])

    def test_06_gameformat(self):
        ae = self.assertEqual
        matches = gameformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix<reserved>suffix"])
        matches = gameformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix<reservedsuffix"])
        matches = gameformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "<reserved>", "a5"])

    def test_07_pgnformat(self):
        ae = self.assertEqual
        matches = pgnformat.finditer(self.tag)
        ae([m.group() for m in matches], ["<reserved>"])
        matches = pgnformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["<reservedsuffix"])
        matches = pgnformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "<reserved>", "a5"])

    def test_08_importformat(self):
        ae = self.assertEqual
        matches = importformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix<reserved>suffix"])
        matches = importformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix<reservedsuffix"])
        matches = importformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "<reserved>", "a5"])

    def test_09_textformat(self):
        ae = self.assertEqual
        matches = textformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix<reserved>suffix"])
        matches = textformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix<reservedsuffix"])
        matches = textformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "<reserved>", "a5"])

    def test_10_ignorecaseformat(self):
        ae = self.assertEqual
        matches = ignorecaseformat.finditer(self.tag)
        ae([m.group() for m in matches], ["prefix<reserved>suffix"])
        matches = ignorecaseformat.finditer(self.tagbad)
        ae([m.group() for m in matches], ["prefix<reservedsuffix"])
        matches = ignorecaseformat.finditer(self.move)
        ae([m.group() for m in matches], ["a4", "<reserved>", "a5"])


class Tag(unittest.TestCase):
    def setUp(self):
        self.tag = 'prefix[Name"Value"]suffix'
        self.tagbad = 'prefix[;ame"Value"]suffix'
        self.move = 'a4[Name"Value"]a5'

    def test_01_all_tag_searches(self):
        ae = self.assertEqual
        ae(isinstance(pgntag.search(self.tag), re.Match), True)
        ae(isinstance(tagpair.search(self.tag), re.Match), True)
        ae(comment.search(self.tag) is None, True)
        ae(reserved.search(self.tag) is None, True)
        ae(badcomment.search(self.tag) is None, True)
        ae(badreserved.search(self.tag) is None, True)
        ae(isinstance(tagpairdataerror.search(self.tag), re.Match), True)
        ae(isinstance(tagpairformat.search(self.tag), re.Match), True)
        ae(isinstance(gameformat.search(self.tag), re.Match), True)
        ae(isinstance(pgnformat.search(self.tag), re.Match), True)
        ae(isinstance(importformat.search(self.tag), re.Match), True)
        ae(isinstance(textformat.search(self.tag), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.tag), re.Match), True)

    def test_02_all_tagbad_searches(self):
        ae = self.assertEqual
        ae(isinstance(pgntag.search(self.tagbad), re.Match), True)
        ae(tagpair.search(self.tagbad) is None, True)
        ae(comment.search(self.tagbad) is None, True)
        ae(reserved.search(self.tagbad) is None, True)
        ae(badcomment.search(self.tagbad) is None, True)
        ae(badreserved.search(self.tagbad) is None, True)
        ae(isinstance(tagpairdataerror.search(self.tagbad), re.Match), True)
        ae(isinstance(tagpairformat.search(self.tagbad), re.Match), True)
        ae(isinstance(gameformat.search(self.tagbad), re.Match), True)
        ae(isinstance(pgnformat.search(self.tagbad), re.Match), True)
        ae(isinstance(importformat.search(self.tagbad), re.Match), True)
        ae(isinstance(textformat.search(self.tagbad), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.tagbad), re.Match), True)

    def test_03_all_move_searches(self):
        ae = self.assertEqual
        ae(isinstance(pgntag.search(self.move), re.Match), True)
        ae(isinstance(tagpair.search(self.move), re.Match), True)
        ae(comment.search(self.move) is None, True)
        ae(reserved.search(self.move) is None, True)
        ae(badcomment.search(self.move) is None, True)
        ae(badreserved.search(self.move) is None, True)
        ae(isinstance(tagpairdataerror.search(self.move), re.Match), True)
        ae(isinstance(tagpairformat.search(self.move), re.Match), True)
        ae(isinstance(gameformat.search(self.move), re.Match), True)
        ae(isinstance(pgnformat.search(self.move), re.Match), True)
        ae(isinstance(importformat.search(self.move), re.Match), True)
        ae(isinstance(textformat.search(self.move), re.Match), True)
        ae(isinstance(ignorecaseformat.search(self.move), re.Match), True)

    def test_04_tag_and_tagpair_and_badtag(self):
        ae = self.assertEqual
        tagmatch = pgntag.search(self.tag)
        ae(tagmatch.group(), '[Name"Value"]')
        tagmatch = tagpair.search(self.tag)
        ae(tagmatch.group(), '[Name"Value"]')
        tagmatch = tagpairdataerror.search(self.tag)
        ae(tagmatch.group(), '[Name"Value"]')
        tagbadmatch = pgntag.search(self.tagbad)
        ae(tagbadmatch.group(), '[;ame"Value"]')
        tagbadmatch = tagpair.search(self.tagbad)
        ae(tagbadmatch is None, True)
        tagbadmatch = tagpairdataerror.search(self.tagbad)
        ae(tagbadmatch.group(), '[;ame"Value"]')
        movematch = pgntag.search(self.move)
        ae(movematch.group(), '[Name"Value"]')
        movematch = tagpair.search(self.move)
        ae(movematch.group(), '[Name"Value"]')
        movematch = tagpairdataerror.search(self.move)
        ae(movematch.group(), '[Name"Value"]')


class EscapeAndNewline(unittest.TestCase):
    def test_01_apostrophe_in_value(self):
        tagstring = 'prefix[Name"Val\\"ue"]suffix'
        ae = self.assertEqual
        tagmatch = pgntag.search(tagstring)
        ae(tagmatch.group(), '[Name"Val\\"ue"]')
        tagmatch = tagpair.search(tagstring)
        ae(tagmatch.group(), '[Name"Val\\"ue"]')
        tagmatch = tagpairdataerror.search(tagstring)
        ae(tagmatch.group(), '[Name"Val\\"ue"]')

    def test_02_newline_in_value(self):
        tagstring = 'prefix[Name"Val\nue"]suffix'
        ae = self.assertEqual
        tagmatch = pgntag.search(tagstring)
        ae(tagmatch.group(), '[Name"Val\nue"]')
        tagmatch = tagpair.search(tagstring)
        ae(tagmatch is None, True)
        tagmatch = tagpairdataerror.search(tagstring)
        ae(tagmatch.group(), '[Name"Val\nue"]')

    def test_03_apostrophe_and_newline_in_value(self):
        tagstring = 'prefix[Name"V\\"al\nue"]suffix'
        ae = self.assertEqual
        tagmatch = pgntag.search(tagstring)
        ae(tagmatch.group(), '[Name"V\\"al\nue"]')
        tagmatch = tagpair.search(tagstring)
        ae(tagmatch is None, True)
        tagmatch = tagpairdataerror.search(tagstring)
        ae(tagmatch.group(), '[Name"V\\"al\nue"]')

    def test_04_newline_and_apostrophe_in_value(self):
        tagstring = 'prefix[Name"Val\nu\\"e"]suffix'
        ae = self.assertEqual
        tagmatch = pgntag.search(tagstring)
        ae(tagmatch.group(), '[Name"Val\nu\\"e"]')
        tagmatch = tagpair.search(tagstring)
        ae(tagmatch is None, True)
        tagmatch = tagpairdataerror.search(tagstring)
        ae(tagmatch.group(), '[Name"Val\nu\\"e"]')


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    runner().run(loader(Comment))
    runner().run(loader(Reserved))
    runner().run(loader(Tag))
    runner().run(loader(EscapeAndNewline))
