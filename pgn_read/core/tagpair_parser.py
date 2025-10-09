# tagpair_parser.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Portable Game Notation (PGN) parser which ignores movetext.

The PGNTagPair class provides the read_games method which splits text into
tokens and by default passes them to an instance of the TagPairGame class
to build a data structure representing the tag pairs of a game.

The add_token_to_game function searches for the next token in the text
argument and adds it to the instance of TagPairGame class, or subclass,
in the game argument.

The GameCount class allows the games to be counted without verifying text
outside tags, comments, and termination markers, is SAN (Standard Algebraic
Notation) format.  This should save significant time when the moves played
are not of interest.

The TagPairGame class allows the Tag Pairs of games to be collected without
verifying the movetext represents a legal game or contains SAN format move
descriptions.  This should save significant time when the moves played are
not of interest.

"""
import re

from .constants import (
    PGN_TAG,
    BACK_STEP,
    TAG_PAIR_FORMAT,
    UNTERMINATED,
    TPF_TAG_NAME,
    TPF_TAG_VALUE,
    TPF_END_TAG,
    TPF_GAME_TERMINATION,
    TPF_COMMENT_TO_EOL,
    TPF_COMMENT,
    TPF_RESERVED,
    TPF_ESCAPE,
    TPF_BAD_COMMENT,
    TPF_BAD_RESERVED,
    TPF_BAD_TAG,
    TPF_END_OF_FILE_MARKER,
    TPF_OTHER_WITH_NON_NEWLINE_WHITESPACE,
)

game_format = re.compile(TAG_PAIR_FORMAT)
tagpair = re.compile(PGN_TAG)


class PGNTagPairError(Exception):
    """Exception raised where PGNTagPair parsing cannot continue."""


class GameCount:
    """Data structure of game tag pairs derived from a PGN game score.

    Movetext is ignored except for detecting comment, reserved, and
    escape, sequences because anything that looks like a tag pair or game
    termination marker within these is just text.

    Almost all games will be flagged as games with errors because they
    contain movetext, which is seen as invalid movetext by the parser
    in PGNTagPair.

    """

    # Defaults for Game instance state.
    _state = None

    # Locate position in PGN text file of latest game.
    game_offset = 0

    def __init__(self):
        """Create empty data structure for noting existence of game text."""
        self._text = []

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

    def append_token(self, match):
        """Append valid non-tag token from game score.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """

    append_reserved = append_token

    def append_token_and_set_error(self, match):
        """Append first invalid token in main line or variation to game score.

        The game error state is adjusted so the error condition can be removed
        at the end of the variation in which it occured.

        """
        del match
        if self._state is None:
            self._state = len(self._text)

    def append_token_after_error(self, match):
        """Append token to game score after an error has been found."""

    def append_token_after_error_without_separator(self, match):
        """Append token without separator from game score after PGN error.

        Sequences of dots after an error are kept together, there is not a
        space before each dot.  When there is no error dots are ignored.

        Check indicators are not prefixed with a separator.

        """

    def append_comment_after_error(self, match):
        """Append comment token to game score after an error has been found."""

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

    def append_bad_tag_after_error(self, match):
        """Append token to game score after an error has been found."""

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

    def append_escape_after_error(self, match):
        r"""Append escape token to game score after an error has been found.

        The '\n' termination for the escaped line is not captured because it
        may start an escaped line.

        The '\n' is appended to the token.

        """

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

    def append_game_termination(self, match):
        """Append game termination token to game score and update game state.

        Put game in error state if no moves exists in game score and the
        initial position is not valid.  Validation includes piece counts and
        some piece placement: pawns on ranks 2 to 7 only and king of active
        color not in check for example.  Verification that the initial position
        declared in a PGN FEN tag is reachable from the standard starting
        position is not attempted.

        """

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


class TagPairGame(GameCount):
    """Extend to capture PGN Tag Pairs."""

    def __init__(self):
        """Create empty data structure for the PGN Tag Pairs of a game."""
        super().__init__()
        self._tags = {}

    @property
    def pgn_tags(self):
        """Return _tags dict of PGN tag names and values."""
        return self._tags

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
        return

    def append_start_tag(self, match):
        """Append tag token to game score and update game tags.

        Put game in error state if a duplicate tag name is found.

        """
        if self._state is not None:
            self.append_token_and_set_error(match)
            return
        group = match.group
        tag_name = group(TPF_TAG_NAME)
        tag_value = group(TPF_TAG_VALUE)

        # Tag names must not be duplicated.
        if tag_name in self._tags:
            if self._state is None:
                self._state = True
            return

        self._tags[tag_name] = tag_value
        return


class PGNTagPair:
    """Extract tokens from text using definitions in PGN specification.

    The tokens are passed to an instance of the TagPairGame class which
    decides whether the token is allowed in the current context.

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

    def __init__(self, game_class=GameCount):
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
            game_class.append_game_termination,
            game_class.append_comment_to_eol,
            game_class.append_token,
            game_class.append_reserved,
            game_class.ignore_escape,
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
            game_class.append_game_termination_after_error,
            game_class.append_comment_to_eol_after_error,
            game_class.append_comment_after_error,
            game_class.append_token_after_error,
            game_class.append_escape_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_bad_tag_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
        )

    @staticmethod
    def _read_pgn(source, length):
        def _end_last_tag(buffer):
            step_match = None
            for step in (BACK_STEP, BACK_STEP + BACK_STEP):
                if step > len(buffer):
                    break
                for found in tagpair.finditer(buffer[-step:]):
                    step_match = found
                if step_match:
                    return len(buffer) - step + step_match.end()
            tag_match = None
            for found in tagpair.finditer(buffer):
                tag_match = found
            if tag_match:
                return tag_match.end()
            return None

        if isinstance(source, str):
            yield source
            return
        try:
            tail = ""
            while True:
                text = source.read(length)
                if not text:
                    yield tail
                    break
                end = _end_last_tag(text)
                if end is None:
                    tail += text
                    continue
                tail += text[:end]
                text = text[end:]
                yield tail
                tail = text
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
                    if match.lastindex == TPF_END_TAG:
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
                    elif match.lastindex == TPF_GAME_TERMINATION:
                        residue_start_on_error_at_pgntext_end = match.end()
                        error_despatch_table[match.lastindex](game, match)
                        game.game_offset = pgntext_offset + match.end()
                        yield game
                        game = game_class()

                    else:
                        error_despatch_table[match.lastindex](game, match)
                elif match.lastindex == TPF_OTHER_WITH_NON_NEWLINE_WHITESPACE:
                    despatch_table[match.lastindex](game, match)
                elif match.lastindex == TPF_GAME_TERMINATION:
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
        if lastindex == TPF_GAME_TERMINATION:
            game.append_game_termination_after_error(match)
        elif lastindex == TPF_COMMENT_TO_EOL:
            game.append_comment_to_eol_after_error(match)
        elif lastindex == TPF_ESCAPE:
            game.append_escape_after_error(match)
        elif lastindex == TPF_BAD_TAG:
            game.append_bad_tag_after_error(match)
        elif lastindex == TPF_COMMENT:
            game.append_comment_after_error(match)
        else:
            game.append_token_after_error(match)
        return match.end()
    if lastindex == TPF_END_TAG:
        game.append_start_tag(match)
    elif lastindex == TPF_GAME_TERMINATION:
        game.append_game_termination(match)
    elif lastindex == TPF_COMMENT_TO_EOL:
        game.append_comment_to_eol(match)
    elif lastindex == TPF_COMMENT:
        game.append_token(match)
    elif lastindex == TPF_RESERVED:
        game.append_reserved(match)
    elif lastindex == TPF_ESCAPE:
        game.ignore_escape(match)
    elif lastindex == TPF_BAD_COMMENT:
        game.append_token_and_set_error(match)
    elif lastindex == TPF_BAD_RESERVED:
        game.append_token_and_set_error(match)
    elif lastindex == TPF_BAD_TAG:
        game.append_bad_tag_and_set_error(match)
    elif lastindex == TPF_OTHER_WITH_NON_NEWLINE_WHITESPACE:
        game.append_other_or_disambiguation_pgn(match)
    elif lastindex == TPF_END_OF_FILE_MARKER:
        game.ignore_end_of_file_marker_prefix_to_tag(match)
    else:
        game.append_token_and_set_error(match)
    return match.end()
