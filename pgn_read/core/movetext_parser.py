# movetext_parser.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Portable Game Notation (PGN) parser which validates movetext format.

The PGNMoveText class provides the read_games method which splits text into
tokens and by default passes them to an instance of the MoveText class to
build a data structure representing the Tag Pairs and syntactically
correct movetext in a game.

The add_token_to_game function searches for the next token in the text
argument and adds it to the instance of MoveText class, or subclass,
in the game argument.

The MoveText class allows the Tag Pairs and Movetext to be verified without
confirming the movetext represents a legal game.  Significant time should
be saved when the validity of moves played is not of interest.

"""
import re

from .constants import (
    GAME_FORMAT,
    FULL_DISAMBIGUATION_ALLOWED,
    UNTERMINATED,
    CGM_TAG_NAME,
    CGM_TAG_VALUE,
    CGM_END_TAG,
    CGM_MOVE_SYMBOLS,
    CGM_GAME_TERMINATION,
    CGM_MOVE_NUMBER,
    CGM_DOTS,
    CGM_COMMENT_TO_EOL,
    CGM_COMMENT,
    CGM_START_RAV,
    CGM_END_RAV,
    CGM_NUMERIC_ANNOTATION_GLYPH,
    CGM_RESERVED,
    CGM_ESCAPE,
    CGM_PASS,
    CGM_CHECK_INDICATOR,
    CGM_TRADITIONAL_ANNOTATION,
    CGM_BAD_COMMENT,
    CGM_BAD_RESERVED,
    CGM_BAD_TAG,
    CGM_END_OF_FILE_MARKER,
    CGM_OTHER_WITH_NON_NEWLINE_WHITESPACE,
    PGN_TOKEN_SEPARATOR,
    SEVEN_TAG_ROSTER,
    SUPPLEMENTAL_TAG_ROSTER,
)

game_format = re.compile(GAME_FORMAT)
full_disambiguation_allowed = re.compile(FULL_DISAMBIGUATION_ALLOWED)


class PGNMoveTextError(Exception):
    """Exception raised where PGNMoveText parsing cannot continue."""


class MoveText:
    """Data structure of game movetext symbols derived from a PGN game score.

    Movetext is ignored except for detecting comment, reserved, and
    escape, sequences because anything that looks like a tag pair or game
    termination marker within these is just text.

    Almost all games will be flagged as games with errors because they
    contain movetext, which is seen as invalid movetext by the parser
    in PGNMoveText.

    """

    # Defaults for MoveText instance state.
    _state = None

    # Locate position in PGN text file of latest game.
    game_offset = 0

    def __init__(self):
        """Create empty data structure for Tag Pairs and Movetext of game."""
        super().__init__()
        self._text = []
        self._tags = {}

    @property
    def pgn_tags(self):
        """Return _tags dict of PGN tag names and values."""
        return self._tags

    def is_pgn_valid(self):
        """Return True if the tags in the game are valid.

        Movetext is only relevant to this class for identifying presence
        of comments and the RAV structure so the end of a game can be
        found correctly.

        """
        return bool(self._tags)

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

    def is_full_disambiguation_allowed(self):
        """Return True if self._text could have fully disambiguated moves.

        A True response implies the movetext tokens in self._text are not
        reliable and the text should be reprocessed with a .parser.PGN
        instance using .game.Game as it's game_class argument.

        For example the fully disambiguated move 'Qb1c2' will be seen as
        [..., 'Qb1', 'c2', ...] in self._text, but the <PGN, Game> version
        will give [..., 'Qb1c2', ...].

        """
        return bool(full_disambiguation_allowed.search("".join(self._text)))

    def set_game_error(self):
        """Declare parsing of game text has failed.

        set_game_error() allows an instance of parser.PGN to declare the game
        invalid in cases where the Game class instance cannot do so: such as
        when input text ends without a game termination marker but is valid up
        to that point.

        set_game_error() does nothing if the current state is not None.

        Otherwise the state is set to True.

        set_game_error() should not be used within the Game class or any
        subclass.

        """
        if self._state is None:
            self._state = len(self._text)

    @property
    def pgn_text(self):
        """Return True if text has been found for game."""
        return self._text

    @property
    def state(self):
        """Return the token offset where PGN error in game occured."""
        return self._state

    def append_comment_to_eol(self, match):
        r"""Append ';...\n' token from gamescore.

        The '\n' termination for the comment is not captured because it may
        start an escaped line, '\n%...\n', and is explicitly added to the
        token.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(match.group().lstrip() + "\n")

    def append_pass_after_error(self, match):
        """Append '--' token found after detection of PGN error."""
        self.append_token_after_error(match)

    def append_token(self, match):
        """Append valid non-tag token from game score.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(match.group().lstrip())

    append_reserved = append_token

    def append_pass_and_set_error(self, match):
        """Append '--' token and set PGN error found."""
        self.append_token_and_set_error(match)

    def append_token_and_set_error(self, match):
        """Append first invalid token in main line or variation to game score.

        The game error state is adjusted so the error condition can be removed
        at the end of the variation in which it occured.

        """
        if self._state is None:
            self._state = len(self._text)
        self._text.append(PGN_TOKEN_SEPARATOR + match.group().lstrip())

    def append_token_after_error(self, match):
        """Append token to game score after an error has been found."""
        self._text.append(PGN_TOKEN_SEPARATOR + match.group().lstrip())

    def append_token_after_error_without_separator(self, match):
        """Append token without separator from game score after PGN error.

        Sequences of dots after an error are kept together, there is not a
        space before each dot.  When there is no error dots are ignored.

        Check indicators are not prefixed with a separator.

        """
        self._text.append(match.group().lstrip())

    def append_comment_after_error(self, match):
        """Append comment token to game score after an error has been found."""
        self._text.append(PGN_TOKEN_SEPARATOR + match.group().lstrip())

    def append_bad_tag_and_set_error(self, match):
        r"""Append incomplete or badly formed tag to game score and set error.

        The tag is formed like '[ Tagname "Tagvalue" ]' with extra, or
        less, whitespace allowed.  In particular there is at least one '\' or
        '"' without the '\' escape prefix.  If _state and _movetext_offset
        allow and the rules do not state _strict_pgn the escape prefix is
        added as needed, rather than declare an error and terminate the game.

        The tag is wrapped in a comment, '{}' and the game is terminated with
        the unknown result symbol '*'.

        """
        bad_tag = match.group().strip().split('"')
        val = (
            '"'.join(bad_tag[1:-1])
            .replace('"', '"')
            .replace("\\\\", "\\")
            .replace("\\", "\\\\")
            .replace('"', r"\"")
        )

        # Copy from append_start_tag() to apply correctly formatted PGN tag,
        # which must not be duplicated.
        tag_name = bad_tag[0].lstrip("[").strip()
        if tag_name in self._tags:
            if self._state is None:
                self._state = len(self._tags) - 1
            return
        self._tags[tag_name] = val
        self._text.append("".join(("[", tag_name, '"', val, '"]')))
        return

    def append_bad_tag_after_error(self, match):
        """Append token to game score after an error has been found."""
        self._text.append(match.group().lstrip())

    def append_game_termination_after_error(self, match):
        """Delegate action to append_token_after_error method.

        append_game_termination_after_error exists to provide explicit default
        action when a game termination token to found when in game error state.

        """
        self.append_token_after_error(match)

    def append_comment_to_eol_after_error(self, match):
        r"""Append ';...\n' token to game score after an error has been found.

        The '\n' termination for the comment is not captured because it may
        start an escaped line, '\n%...\n', and is explicitly added to the
        token.

        """
        self._text.append(match.group().lstrip() + "\n")

    def append_start_rav_after_error(self, match):
        """Append start RAV token from game score after PGN error found."""
        self.append_token_after_error(match)

    def append_end_rav_after_error(self, match):
        """Append end RAV token from game score after PGN error found."""
        self.append_token_after_error(match)

    def append_escape_after_error(self, match):
        r"""Append escape token to game score after an error has been found.

        The '\n' termination for the escaped line is not captured because it
        may start an escaped line.

        The '\n' is appended to the token.

        """
        self._text.append(match.group().lstrip() + "\n")

    def append_other_or_disambiguation_pgn(self, match):
        """Ignore token previously used for disambiguation, or set PGN error.

        'Qb3c2' can mean move the queen on b3 to c2 when all whitespace is
        removed from PGN movetext.  This method processes the 'c2' when it is
        consumed from the input: 'c2' is processed by peeking at the input when
        processing the 'Qb3'.

        """
        self.append_token_and_set_error(match)

    def append_start_tag(self, match):
        """Append tag token to game score and update game tags.

        Put game in error state if a duplicate tag name is found.

        """
        if self._state is not None:
            self.append_token_and_set_error(match)
            return
        group = match.group
        tag_name = group(CGM_TAG_NAME)
        tag_value = group(CGM_TAG_VALUE)
        self._text.append("".join(("[", tag_name, '"', tag_value, '"]')))

        # Tag names must not be duplicated.
        if tag_name in self._tags:
            if self._state is None:
                self._state = len(self._tags) - 1
            return

        self._tags[tag_name] = tag_value
        return

    def append_move(self, match):
        """Append piece move token to game score and update board state.

        Put game in error state if the token represents an illegal move.

        """
        self._text.append(match.group().lstrip())

    def append_start_rav(self, match):
        """Append start recursive annotation variation token to game score.

        Put game in error state if a variation cannot be put at current place
        in game score.

        """
        self._text.append(match.group().lstrip())

    def append_end_rav(self, match):
        """Append end recursive annotation variation token to game score.

        Put game in error state if a variation cannot be finished at current
        place in game score.

        """
        self._text.append(match.group().lstrip())

    def append_game_termination(self, match):
        """Append game termination token to game score and update game state.

        Put game in error state if no moves exists in game score and the
        initial position is not valid.  Validation includes piece counts and
        some piece placement: pawns on ranks 2 to 7 only and king of active
        color not in check for example.  Verification that the initial position
        declared in a PGN FEN tag is reachable from the standard starting
        position is not attempted.

        """
        self._text.append(match.group().lstrip())

    def append_glyph_for_traditional_annotation(self, match):
        """Append NAG for traditional annotation to game score.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(match.group().lstrip())

    def ignore_escape(self, match):
        r"""Ignore escape token and rest of line containing the token.

        The '\n' termination for the escaped line is not captured because it
        may start an escaped line.

        The '\n' must be appended to the token in subclasses which capture
        the escaped line.

        """

    def ignore_end_of_file_marker_prefix_to_tag(self, match):
        r"""Ignore end of file marker if it is prefix to a PGN tag.

        Concatenated PGN files may have an end of file marker, '\032' also
        called Ctrl-Z, followed immediately by the PGN Tag which was at start
        of next file.  This breaks the PGN specification because the PGN tag is
        not at the start of a line.

        Strictly Ctrl-Z is one of the ASCII control characters not permitted
        in PGN files, 4.1 in PGN specification, but according to Wikipedia,
        en.wikipedia.org/wiki/End-of-file, the end of file marker exists for
        two reasons.  One suggestion on the 'talk' page is Ctrl-Z was never
        necessary but in practice useful for a while in the 1980s.

        """

    def ignore_move_number(self, match):
        """Ignore move number indication token."""

    def ignore_dots(self, match):
        """Ignore dot sequence token.

        The PGN specification mentions dots as part of move number indication,
        '12.' and '12...' for example.  This class ignores any sequence of
        dots containing at least one dot in sequences of valid tokens.

        """

    def ignore_check_indicator(self, match):
        """Ignore check indicator indication token.

        Check indicators are required in PGN export format.  This PGN parser
        verifies a move does not leave the moving side's king in check, but
        takes no interest in whether a move gives check or checkmate except
        for output in PGN export format.  Game._append_check_indicator can
        be overridden to do this.

        """


class PGNMoveText:
    """Extract tokens from text using definitions in PGN specification.

    The tokens are passed by default to an instance of the MoveText class
    which decides whether the token is allowed in the current context.

    Input is assumed to be Import Format PGN, with Export Format PGN
    treated as a valid Import Format.

    The following are examples of minimal text accepted as valid Import Format:
    '*'
    '[TagName"Tag Value"]*'
    'e4*'
    '[TagName"Tag Value"]e4*'
    '[TagName"Tag Value"]e4e5Nf3Nc6Bb5*'

    The last of the examples would be '[TagName"Tag Value"]e4 e5 Nf3 Nc6 Bb5*'
    in text valid according to the PGN Import Format specification: the spaces
    inserted between the moves.

    """

    def __init__(self, game_class=MoveText):
        """Initialise switches to call game_class methods."""
        super().__init__()
        self._rules = game_format
        self._game_class = game_class

        # Table is set for indexing by match.lastindex which is 1-based.
        # When using a match.groups() index which is 0-based, subtract 1 from
        # the group() index.
        # So despatch[0] is set to None so both sources can use the lookup
        # table.
        self.despatch_table = (
            None,
            game_class.append_token_and_set_error,
            game_class.append_token_and_set_error,
            game_class.append_start_tag,
            game_class.append_move,
            game_class.append_game_termination,
            game_class.ignore_move_number,
            game_class.ignore_dots,
            game_class.append_comment_to_eol,
            game_class.append_token,
            game_class.append_start_rav,
            game_class.append_end_rav,
            game_class.append_token,
            game_class.append_reserved,
            game_class.ignore_escape,
            game_class.append_pass_and_set_error,
            game_class.ignore_check_indicator,
            game_class.append_glyph_for_traditional_annotation,
            game_class.append_token_and_set_error,
            game_class.append_token_and_set_error,
            game_class.append_bad_tag_and_set_error,
            game_class.ignore_end_of_file_marker_prefix_to_tag,
            game_class.append_other_or_disambiguation_pgn,
        )
        self.error_despatch_table = (
            None,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_game_termination_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error_without_separator,
            game_class.append_comment_to_eol_after_error,
            game_class.append_comment_after_error,
            game_class.append_start_rav_after_error,
            game_class.append_end_rav_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_escape_after_error,
            game_class.append_pass_after_error,
            game_class.append_token_after_error_without_separator,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_bad_tag_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
        )

    @staticmethod
    def _read_pgn(source, length):
        if isinstance(source, str):
            yield source
            return
        try:
            while True:
                pgntext = source.read(length)
                yield pgntext
                if not pgntext:
                    break
        finally:
            source.close()

    def read_games(self, source, size=10000000):
        """Extract games from file-like source or string.

        Yield Game, or subclass, instance when match is game termination token.
        The final yield is the instance as it is when source exhausted.

        source - file-like object from which to read pgn text
        size - number of characters to read in each read() call

        """
        despatch_table = self.despatch_table
        error_despatch_table = self.error_despatch_table
        game_class = self._game_class
        residue = ""
        pgntext_length = 0
        for pgntext in self._read_pgn(source, size):
            pgntext_offset = pgntext_length - len(residue)
            pgntext_length += len(pgntext)

            # The previous chunk of pgntext may have ended with an incomplete
            # game, with or without errors.
            if residue:
                pgntext = residue + pgntext
                residue = ""
            residue_start_on_error_at_pgntext_end = None

            game = game_class()
            for match in self._rules.finditer(pgntext):
                if game.state is not None:
                    if match.lastindex == CGM_END_TAG:
                        # A PGN Tag in an error sequence starts a new game
                        # except when the sequence starts with a comment, '{',
                        # or reserved, '<', sequence for which a matching '}'
                        # or '>' has not been found.  Chunking the input is
                        # likely to make this happen, even in the absence of
                        # PGN errors, until sufficient text has been read to
                        # resolve the problem.  '{[A"a"]}' is allowed as a
                        # comment in PGN.
                        if (
                            game.pgn_text
                            and game.pgn_text[game.state][0] in UNTERMINATED
                        ):
                            game.append_token_after_error(match)
                            continue

                        residue_start_on_error_at_pgntext_end = match.start()
                        game.game_offset = pgntext_offset + match.start()
                        yield game
                        game = game_class()
                        despatch_table[match.lastindex](game, match)

                    # '--' moves in the main line cause rest of game moves to
                    # be wrapped in a {Error} comment.  The game termination
                    # is processed here.  It is an error sequence in the sense
                    # that the game is not valid, but the generated PGN is
                    # valid.
                    elif match.lastindex == CGM_GAME_TERMINATION:
                        residue_start_on_error_at_pgntext_end = match.end()
                        error_despatch_table[match.lastindex](game, match)
                        game.game_offset = pgntext_offset + match.end()
                        yield game
                        game = game_class()

                    else:
                        error_despatch_table[match.lastindex](game, match)
                elif match.lastindex == CGM_OTHER_WITH_NON_NEWLINE_WHITESPACE:
                    despatch_table[match.lastindex](game, match)
                elif match.lastindex == CGM_GAME_TERMINATION:
                    residue_start_on_error_at_pgntext_end = match.end()
                    despatch_table[match.lastindex](game, match)
                    game.game_offset = pgntext_offset + match.end()
                    yield game
                    game = game_class()
                else:
                    despatch_table[match.lastindex](game, match)

            # The final game in pgntext is likely incomplete when processing
            # large PGN files: retry the game after reading the next chunk of
            # the input file.
            # The test on len(pgntext) prevents a sequence of legal movetext
            # which is not preceded by any PGN Tags, in the final game in the
            # final pgntext, causing duplication of the movetext in self._text.
            if residue_start_on_error_at_pgntext_end is None:
                if len(pgntext):
                    game.set_game_error()
                residue = pgntext
            else:
                residue = pgntext[residue_start_on_error_at_pgntext_end:]

        # The final game in the input has an error, or has no error but no game
        # termination marker either.
        if game.pgn_text:
            game.set_game_error()
            game.game_offset = pgntext_offset + len(residue)
            yield game


def add_token_to_game(text, game, pos=0):
    """Apply first match in text after pos to game and return match.end().

    Return None if no match found.

    """
    match = game_format.search(text, pos)
    if not match:
        game.set_game_error()
        return None
    lastindex = match.lastindex
    if game.state is not None:
        if lastindex == CGM_GAME_TERMINATION:
            game.append_game_termination_after_error(match)
        elif lastindex == CGM_COMMENT_TO_EOL:
            game.append_comment_to_eol_after_error(match)
        elif lastindex == CGM_START_RAV:
            game.append_start_rav_after_error(match)
        elif lastindex == CGM_END_RAV:
            game.append_end_rav_after_error(match)
        elif lastindex == CGM_ESCAPE:
            game.append_escape_after_error(match)
        elif lastindex == CGM_PASS:
            game.append_pass_after_error(match)
        elif lastindex == CGM_BAD_TAG:
            game.append_bad_tag_after_error(match)
        elif lastindex == CGM_COMMENT:
            game.append_comment_after_error(match)
        elif lastindex == CGM_DOTS:
            game.append_token_after_error_without_separator(match)
        elif lastindex == CGM_CHECK_INDICATOR:
            game.append_token_after_error_without_separator(match)
        else:
            game.append_token_after_error(match)
        return match.end()
    if lastindex == CGM_END_TAG:
        game.append_start_tag(match)
    elif lastindex == CGM_MOVE_SYMBOLS:
        game.append_move(match)
    elif lastindex == CGM_GAME_TERMINATION:
        game.append_game_termination(match)
    elif lastindex == CGM_MOVE_NUMBER:
        game.ignore_move_number(match)
    elif lastindex == CGM_DOTS:
        game.ignore_dots(match)
    elif lastindex == CGM_COMMENT_TO_EOL:
        game.append_comment_to_eol(match)
    elif lastindex == CGM_COMMENT:
        game.append_token(match)
    elif lastindex == CGM_START_RAV:
        game.append_start_rav(match)
    elif lastindex == CGM_END_RAV:
        game.append_end_rav(match)
    elif lastindex == CGM_NUMERIC_ANNOTATION_GLYPH:
        game.append_token(match)
    elif lastindex == CGM_RESERVED:
        game.append_reserved(match)
    elif lastindex == CGM_ESCAPE:
        game.ignore_escape(match)
    elif lastindex == CGM_PASS:
        game.append_pass_and_set_error(match)
    elif lastindex == CGM_CHECK_INDICATOR:
        game.ignore_check_indicator(match)
    elif lastindex == CGM_TRADITIONAL_ANNOTATION:
        game.append_glyph_for_traditional_annotation(match)
    elif lastindex == CGM_BAD_COMMENT:
        game.append_token_and_set_error(match)
    elif lastindex == CGM_BAD_RESERVED:
        game.append_token_and_set_error(match)
    elif lastindex == CGM_BAD_TAG:
        game.append_bad_tag_and_set_error(match)
    elif lastindex == CGM_OTHER_WITH_NON_NEWLINE_WHITESPACE:
        game.append_other_or_disambiguation_pgn(match)
    elif lastindex == CGM_END_OF_FILE_MARKER:
        game.ignore_end_of_file_marker_prefix_to_tag(match)
    else:
        game.append_token_and_set_error(match)
    return match.end()
