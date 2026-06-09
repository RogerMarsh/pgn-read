# pgndata.py
# Copyright 2026 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Portable Game Notation (PGN) data structures.

Tag pair and movetext tokens are identified, but the positions implied
by movetext are not tracked.

"""

import re

from .constants import (
    # The TAG_* list is long enough to cause a pylint duplicate-code report
    # citing pgn_read.core.constants module.
    TAG_EVENT,
    TAG_SITE,
    TAG_DATE,
    TAG_ROUND,
    TAG_WHITE,
    TAG_BLACK,
    TAG_RESULT,
    SEVEN_TAG_ROSTER,
    TAG_FEN,
    SUPPLEMENTAL_TAG_ROSTER,
    DEFAULT_TAG_VALUE,
    DEFAULT_SORT_TAG_VALUE,
    DEFAULT_SORT_TAG_RESULT_VALUE,
    SEVEN_TAG_ROSTER_DEFAULTS,
    DEFAULT_TAG_RESULT_VALUE,
    PGN_MAXIMUM_LINE_LENGTH,
    PGN_LINE_SEPARATOR,
    PGN_TOKEN_SEPARATOR,
    OTHER_SIDE,
    FEN_BLACK_ACTIVE,
    FEN_WHITE_ACTIVE,
    PGN_DOT,
    SUFFIX_ANNOTATION_TO_NAG,
    FEN_FULLMOVE_NUMBER_FIELD_INDEX,
    FEN_ACTIVE_COLOR_FIELD_INDEX,
)

suffix_annotations = re.compile(r"(!!|!\?|!|\?\?|\?!|\?)$")
white_black_tag_value_format = re.compile(r"\s*([^,.\s]+)")

# Remove multiple leading '[%.*]' and adjacent \s* in '{.*}'.
structured_comment_re = re.compile(r"^{(?:\s*\[\s*%.*\])+\s*")
NULL_PGN_COMMENT = "{}"

# The Seven Tag Roster names in PGN collation order.
COLLATION_ORDER = (
    TAG_DATE,
    TAG_EVENT,
    TAG_SITE,
    TAG_ROUND,
    TAG_WHITE,
    TAG_BLACK,
    TAG_RESULT,
)


class PGNDataError(Exception):
    """Exceptions raised manipulating PGNData state."""


class PGNData:
    """Data structure of tag pairs and movetext taken from a PGN game score.

    Comparison operators implement the PGN collating sequence, except in
    ascending str order rather than ascending ASCII order.
    """

    # Defaults for PGNData instance state.
    _state = None
    _movetext_offset = None

    # Locate position in PGN text file of latest game.
    game_offset = 0

    def __init__(self):
        """Create empty data structure for a game presented in PGN format."""
        self._text = []
        self._tags = {}

    def set_game_error(self):
        """Declare parsing of game text has failed.

        set_game_error() allows an instance of parser.PGN to declare the game
        invalid in cases where the Game class instance cannot do so: such as
        when input text ends without a game termination marker but is valid up
        to that point.

        set_game_error() does nothing if the current state is not None.

        Otherwise the state is set to the current length of the list of
        tokens found, and this value is appended to the state stack.

        set_game_error() should not be used within the Game class or any
        subclass.

        """
        if self._state is None:
            self._state = len(self._text)

    @property
    def pgn_tags(self):
        """Return _tags dict of PGN tag names and values."""
        return self._tags

    @property
    def pgn_text(self):
        """Return _text str of PGN text (the whole game score)."""
        return self._text

    @property
    def game_has_errors(self):
        """Return True if game has PGN errors: variations are ignored."""
        return bool(self._state is not None)

    @property
    def state(self):
        """Return the token offset where PGN error in game occured."""
        return self._state

    @property
    def movetext_offset(self):
        """Return the token offset where PGN movetext begins."""
        return self._movetext_offset

    # May be removed in future, or converted to property.
    # Property game_has_errors is equivalent but meaning of True and False is
    # reversed.
    def is_movetext_valid(self):
        """Return True if there are no error_tokens in the collected game."""
        return self._state is None

    # May be overridden in subclasses.
    def is_tag_roster_valid(self):
        """Return True if the game's tag roster is valid."""
        tags = self._tags
        for str_tag in SEVEN_TAG_ROSTER:
            if str_tag not in tags:
                # A mandatory tag is missing.
                return False
            if len(tags[str_tag]) == 0:
                # Mandatory tags must have a non-null value.
                return False
        for str_tag in SUPPLEMENTAL_TAG_ROSTER:
            if str_tag in tags:
                if len(tags[str_tag]) == 0:
                    return False
        return True

    def is_pgn_valid(self):
        """Return True if the tags and movetext in the game are valid.

        Movetext with no PGN errors in the main line but errors in one or more
        RAVs will cause this method to return True.

        """
        return self.is_movetext_valid() and self.is_tag_roster_valid()

    def is_pgn_valid_export_format(self):
        """Return True if the tags and movetext meet PGN export format rules.

        This method always returns False if is_pgn_valid returns False, but
        may return False if is_pgn_valid returns True.

        """
        if not self.is_pgn_valid():
            return False
        return self._tags.get(TAG_RESULT) == self._text[-1]

    def get_collation(self):
        """Return list for PGN collation sort.

        The PGN collation order is the Seven Tag Roster in collation order
        plus a representation of the movetext by elements of an actual FEN
        tag, or the implied starting position fen, and the movetext without
        move number indicators.

        A Query ('?') represents an unknown value in Event, Site, White, and
        Black, tags.

        A Query ('?') represents an unknown round and a hyphen ('-') means
        round not relevant.  Query is before hyphen in the collation order.

        A Query ('?') represents an unknown character in a date value.  It is
        treated as '0' for collation.

        1. e4 is before 1... e4 in collation order but self._text normally will
        not have the move number indications.  If sorting gets into movetext it
        is possible the ordering implemented in this method will differ from
        the ordering implied by the PGN specification when move sufficies are
        present.

        """
        collate = []
        tags = self._tags
        for tag in COLLATION_ORDER:
            value = tags.get(tag)
            if value is None:
                value = SEVEN_TAG_ROSTER_DEFAULTS.get(tag, DEFAULT_TAG_VALUE)
            collate.append(value)
        if DEFAULT_TAG_VALUE in collate[0]:  # Date.
            collate[0] = collate[0].replace(DEFAULT_TAG_VALUE, "0")
        if collate[3] == DEFAULT_TAG_VALUE:  # Round.
            collate[3] = DEFAULT_SORT_TAG_RESULT_VALUE
        if TAG_FEN in tags:
            fen = tags[TAG_FEN].split()
            fen = (
                int(fen[FEN_FULLMOVE_NUMBER_FIELD_INDEX]),
                OTHER_SIDE[fen[FEN_ACTIVE_COLOR_FIELD_INDEX]],
            )
            if fen != (1, FEN_BLACK_ACTIVE):
                collate.append(fen)
            else:
                collate.append((1, DEFAULT_SORT_TAG_VALUE))
        else:
            collate.append((1, DEFAULT_SORT_TAG_VALUE))
        collate.append(self._text[self._movetext_offset :])  # a[None:] -> [].
        return collate

    def __eq__(self, other):
        """Return True if self == other in PGN collation order."""
        return self.get_collation() == other.get_collation()

    def __ge__(self, other):
        """Return True if self >= other in PGN collation order."""
        return self.get_collation() >= other.get_collation()

    def __gt__(self, other):
        """Return True if self >= other in PGN collation order."""
        return self.get_collation() > other.get_collation()

    def __le__(self, other):
        """Return True if self >= other in PGN collation order."""
        return self.get_collation() <= other.get_collation()

    def __lt__(self, other):
        """Return True if self >= other in PGN collation order."""
        return self.get_collation() < other.get_collation()

    def __ne__(self, other):
        """Return True if self != other in PGN collation order."""
        return self.get_collation() != other.get_collation()

    def get_tags(self, name_value_separator=" "):
        """Return list of PGN tags in an undefined order.

        The default name_value_separator gives PGN tags in export format.

        """
        return [
            "".join(("[", k, name_value_separator, '"', v, '"]'))
            for k, v in self._tags.items()
        ]

    def get_tags_in_text_order(self):
        """Return list of tags in their order in game text in export format."""
        if self._movetext_offset is None:
            return []
        return self._text[: self._movetext_offset]

    def get_non_seven_tag_roster_tags(self):
        """Return string of sorted tags not in Seven Tag Roster."""
        return "\n".join(
            [
                "".join(("[", k, ' "', v, '"]'))
                for k, v in sorted(self._tags.items())
                if k not in SEVEN_TAG_ROSTER
            ]
        )

    def get_seven_tag_roster_tags(self):
        """Return Seven Tag Roster string in order given in PGN specification.

        The PGN specification says name format is <family name>,< ><first name>
        or when an initial is given it is immediately followed by a period.
        Thus 'Smyslov, Vassily V.' but nothing is said about multiple initials
        or cases where 'Smyslov, V. Vassily' is the correct form.  It seems
        consistent to do multiple initials like 'Smyslov, V. V.' with a single
        space following the dot too.

        Many PGN files do something very close to, but not exactly, this in
        the White and Black tags.

        """
        tags = self._tags
        str_tags = []
        for tag in SEVEN_TAG_ROSTER:
            if tag not in tags:
                value = SEVEN_TAG_ROSTER_DEFAULTS.get(tag, DEFAULT_TAG_VALUE)
            elif tag in (TAG_WHITE, TAG_BLACK):
                val = white_black_tag_value_format.findall(tags[tag])
                if len(val) == 1:
                    value = val[0]
                else:
                    value = [val.pop(0) + ","]
                    value.extend(
                        [(n + "." if len(n) == 1 else n) for n in val]
                    )
                    value = " ".join(value)
            else:
                value = tags[tag]
            str_tags.append("".join(("[", tag, ' "', value, '"]')))
        return "\n".join(str_tags)

    def _set_movetext_indicators(self):
        if TAG_FEN in self._tags:
            fen = self._tags[TAG_FEN].split()
            fullmove_number = int(fen[FEN_FULLMOVE_NUMBER_FIELD_INDEX])
            active_color = fen[FEN_ACTIVE_COLOR_FIELD_INDEX]
        else:
            fullmove_number = 1
            active_color = FEN_WHITE_ACTIVE
        return fullmove_number, active_color

    def get_movetext(self):
        """Return list of movetext.

        Moves have check and checkmate indicators, but not the black move
        indicators found in export format if a black move follows a comment
        or is first move in a RAV, nor move numbers.

        """
        if self._movetext_offset is None:
            return []
        return self._text[self._movetext_offset :]

    def get_all_movetext_in_pgn_export_format(self):
        """Return all movetext in pgn export format.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return "".join(movetext)
        length = 0
        insert_fullmove_number = True
        fnas = [[fullmove_number, active_color]]
        _attm = self._add_token_to_movetext
        termination = self._tags.get(TAG_RESULT, DEFAULT_TAG_RESULT_VALUE)
        for mvt in self._text[self._movetext_offset :]:
            if mvt.startswith("{"):
                for word in mvt.split():
                    length = _attm(word, movetext, length)
                insert_fullmove_number = True
            elif mvt.startswith("$"):
                length = _attm(mvt, movetext, length)
            elif mvt.startswith(";"):
                if len(mvt) + length >= PGN_MAXIMUM_LINE_LENGTH:
                    movetext.append(PGN_LINE_SEPARATOR)
                else:
                    movetext.append(PGN_TOKEN_SEPARATOR)
                movetext.append(mvt)
                length = 0
                insert_fullmove_number = True
            elif mvt == "(":
                length = _attm(mvt, movetext, length)
                fnas[-1] = [fullmove_number, active_color]
                active_color = OTHER_SIDE[active_color]
                if active_color == FEN_BLACK_ACTIVE:
                    fullmove_number -= 1
                fnas.append([fullmove_number, active_color])
                insert_fullmove_number = True
            elif mvt == ")":
                length = _attm(mvt, movetext, length)
                del fnas[-1]
                fullmove_number, active_color = fnas[-1]
                insert_fullmove_number = True
            elif mvt == termination:
                length = _attm(mvt, movetext, length)
            elif active_color == FEN_WHITE_ACTIVE:
                length = _attm(
                    str(fullmove_number) + PGN_DOT, movetext, length
                )
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                insert_fullmove_number = False
            else:
                if insert_fullmove_number:
                    length = _attm(
                        str(fullmove_number) + PGN_DOT * 3, movetext, length
                    )
                    insert_fullmove_number = False
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                fullmove_number += 1
        return "".join(movetext)

    def get_movetext_without_comments_in_pgn_export_format(self):
        """Return movetext without comments in pgn export format.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return "".join(movetext)
        length = 0
        insert_fullmove_number = True
        fnas = [[fullmove_number, active_color]]
        _attm = self._add_token_to_movetext
        termination = self._tags.get(TAG_RESULT, DEFAULT_TAG_RESULT_VALUE)
        for mvt in self._text[self._movetext_offset :]:
            if (
                mvt.startswith("{")
                or mvt.startswith("$")
                or mvt.startswith(";")
            ):
                pass
            elif mvt == "(":
                length = _attm(mvt, movetext, length)
                fnas[-1] = [fullmove_number, active_color]
                active_color = OTHER_SIDE[active_color]
                if active_color == FEN_BLACK_ACTIVE:
                    fullmove_number -= 1
                fnas.append([fullmove_number, active_color])
                insert_fullmove_number = True
            elif mvt == ")":
                length = _attm(mvt, movetext, length)
                del fnas[-1]
                fullmove_number, active_color = fnas[-1]
                insert_fullmove_number = True
            elif mvt == termination:
                length = _attm(mvt, movetext, length)
            elif active_color == FEN_WHITE_ACTIVE:
                length = _attm(
                    str(fullmove_number) + PGN_DOT, movetext, length
                )
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                insert_fullmove_number = False
            else:
                if insert_fullmove_number:
                    length = _attm(
                        str(fullmove_number) + PGN_DOT * 3, movetext, length
                    )
                    insert_fullmove_number = False
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                fullmove_number += 1
        return "".join(movetext)

    def get_export_movetext_without_structured_comments(self):
        """Return movetext without structured comments in pgn export format.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return "".join(movetext)
        length = 0
        insert_fullmove_number = True
        fnas = [[fullmove_number, active_color]]
        _attm = self._add_token_to_movetext
        termination = self._tags.get(TAG_RESULT, DEFAULT_TAG_RESULT_VALUE)
        for mvt in self._text[self._movetext_offset :]:
            if mvt.startswith("{"):
                if mvt != NULL_PGN_COMMENT:
                    mvt = structured_comment_re.sub("{", mvt)
                    if mvt == NULL_PGN_COMMENT:
                        continue
                for word in mvt.split():
                    length = _attm(word, movetext, length)
                insert_fullmove_number = True
            elif mvt.startswith("$"):
                length = _attm(mvt, movetext, length)
            elif mvt.startswith(";"):
                if len(mvt) + length >= PGN_MAXIMUM_LINE_LENGTH:
                    movetext.append(PGN_LINE_SEPARATOR)
                else:
                    movetext.append(PGN_TOKEN_SEPARATOR)
                movetext.append(mvt)
                length = 0
                insert_fullmove_number = True
            elif mvt == "(":
                length = _attm(mvt, movetext, length)
                fnas[-1] = [fullmove_number, active_color]
                active_color = OTHER_SIDE[active_color]
                if active_color == FEN_BLACK_ACTIVE:
                    fullmove_number -= 1
                fnas.append([fullmove_number, active_color])
                insert_fullmove_number = True
            elif mvt == ")":
                length = _attm(mvt, movetext, length)
                del fnas[-1]
                fullmove_number, active_color = fnas[-1]
                insert_fullmove_number = True
            elif mvt == termination:
                length = _attm(mvt, movetext, length)
            elif active_color == FEN_WHITE_ACTIVE:
                length = _attm(
                    str(fullmove_number) + PGN_DOT, movetext, length
                )
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                insert_fullmove_number = False
            else:
                if insert_fullmove_number:
                    length = _attm(
                        str(fullmove_number) + PGN_DOT * 3, movetext, length
                    )
                    insert_fullmove_number = False
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                fullmove_number += 1
        return "".join(movetext)

    def get_archive_movetext(self):
        """Return Reduced Export format PGN movetext.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return "".join(movetext)
        length = 0
        insert_fullmove_number = True
        rav_depth = 0
        _attm = self._add_token_to_movetext
        termination = self._tags.get(TAG_RESULT, DEFAULT_TAG_RESULT_VALUE)
        for mvt in self._text[self._movetext_offset :]:
            if (
                mvt.startswith("{")
                or mvt.startswith("$")
                or mvt.startswith(";")
            ):
                pass
            elif mvt == "(":
                rav_depth += 1
            elif mvt == ")":
                rav_depth -= 1
            elif rav_depth:
                pass
            elif mvt == termination:
                length = _attm(mvt, movetext, length)
            elif active_color == FEN_WHITE_ACTIVE:
                length = _attm(
                    str(fullmove_number) + PGN_DOT, movetext, length
                )
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                insert_fullmove_number = False
            else:
                if insert_fullmove_number:
                    length = _attm(
                        str(fullmove_number) + PGN_DOT * 3, movetext, length
                    )
                    insert_fullmove_number = False
                srchm = suffix_annotations.search(mvt)
                if srchm:
                    mvt = mvt[: srchm.start()]
                length = _attm(mvt, movetext, length)
                if srchm:
                    length = _attm(
                        SUFFIX_ANNOTATION_TO_NAG[srchm.group()],
                        movetext,
                        length,
                    )
                active_color = OTHER_SIDE[active_color]
                fullmove_number += 1
        return "".join(movetext)

    def get_export_pgn_elements(self):
        """Return Export format PGN version of game.

        This method will be removed without notice in future.  It seems more
        convenient and clearer to use the called methods directly.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        return (
            self.get_seven_tag_roster_tags(),
            self.get_all_movetext_in_pgn_export_format(),
            self.get_non_seven_tag_roster_tags(),
        )

    def get_archive_pgn_elements(self):
        """Return Archive format PGN version of game. (Reduced Export Format).

        This method will be removed without notice in future.  It seems more
        convenient and clearer to use the called methods directly.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        return self.get_seven_tag_roster_tags(), self.get_archive_movetext()

    def get_export_pgn_rav_elements(self):
        """Return Export format PGN version of game with RAVs but no comments.

        This method will be removed without notice in future.  It seems more
        convenient and clearer to use the called methods directly.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        return (
            self.get_seven_tag_roster_tags(),
            self.get_movetext_without_comments_in_pgn_export_format(),
            self.get_non_seven_tag_roster_tags(),
        )

    def get_text_of_game(self):
        """Return current text version of game."""
        return "".join(self._text)

    @staticmethod
    def _add_token_to_movetext(token, movetext, length):
        # Not modified to do what everyone else seems to do with '(...)':
        # '16. e4 Qd8 (16... dxe4) 17. fxe4' rather than
        # '16. e4 Qd8 ( 16... dxe4 ) 17. fxe4'.
        # I think both are allowed by the PGN specification along with,
        # strictly speaking, '16. e4 Qd8(16... dxe4)17. fxe4' since '(' and ')'
        # are self-terminating and nothing is said about separation from
        # adjacent tokens.
        if not length:
            movetext.append(token)
            return len(token)
        if len(token) + length >= PGN_MAXIMUM_LINE_LENGTH:
            movetext.append(PGN_LINE_SEPARATOR)
            movetext.append(token)
            return len(token)
        # if token == ')':
        #    movetext.append(token)
        #    return len(token) + length
        # if movetext[-1] == '(':
        #    movetext.append(token)
        #    return len(token) + length
        # else:
        movetext.append(PGN_TOKEN_SEPARATOR)
        movetext.append(token)
        return len(token) + length + 1
