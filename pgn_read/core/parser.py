# parser.py
# Copyright 2003, 2010, 2016, 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)
# Much of 2016 version code is transferred to, and modified in, game.py.

"""Portable Game Notation (PGN) parser.

The PGN class provides the read_games method which splits text into tokens and
by default passes them to an instance of the game.Game class to build a data
structure representing a game.

The add_token_to_game function searches for the next token in the text
argument and adds it to the instance of game.Game class, or susubclass, in the
game argument.

"""
import os
import re

from .game import (
    Game, GameStrictPGN, GameTextPGN, GameIgnoreCasePGN,
    import_format, text_format,
    )

from .constants import (
    IGNORE_CASE_FORMAT,
    UNTERMINATED,
    IFG_END_TAG,
    IFG_PIECE_MOVE,
    IFG_PIECE_DESTINATION,
    IFG_PAWN_TO_RANK,
    IFG_PAWN_PROMOTE_TO_RANK,
    IFG_PAWN_PROMOTE_PIECE,
    IFG_CASTLES,
    IFG_GAME_TERMINATION,
    IFG_MOVE_NUMBER,
    IFG_DOTS,
    IFG_COMMENT_TO_EOL,
    IFG_COMMENT,
    IFG_START_RAV,
    IFG_END_RAV,
    IFG_NUMERIC_ANNOTATION_GLYPH,
    IFG_RESERVED,
    IFG_ESCAPE,
    IFG_PASS,
    IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE,
    )

ignore_case_format = re.compile(IGNORE_CASE_FORMAT)


class PGNError(Exception):
    pass


class PGN:
    """Extract tokens from text using definitions in PGN specification.

    The tokens are passed to an instance of the game.Game class which decides
    whether the token is allowed in the current context.

    Input is assumed to be Import Format PGN, with Export Format PGN treated as
    a valid Import Format.

    The following are examples of minimal text accepted as valid Import Format:
    '*'
    '[TagName"Tag Value"]*'
    'e4*'
    '[TagName"Tag Value"]e4*'
    '[TagName"Tag Value"]e4e5Nf3Nc6Bb5*'
    
    The last of the examples would be '[TagName"Tag Value"]e4 e5 Nf3 Nc6 Bb5*'
    in text valid according to the PGN Import Format specification: the spaces
    inserted between the moves.

    Fully disambiguated moves, such as Qc3e3, are not detected in one step
    because the interpretation of Qc3e3 depends on the game state.  Normally
    'Qc3' means 'move the queen which can move to c3' and 'e3' means 'move the
    pawn which can move to e3'.  'Qc3e3' means 'move the queen on c3 to e3'.
    Tokens 'Qc3' and 'e3' are passed one-by-one to a Game instance which
    decides which, if any, interpretation is valid.

    """
    def __init__(self, game_class=Game):
        super().__init__()
        if issubclass(game_class, GameIgnoreCasePGN):
            self._rules = ignore_case_format
        elif issubclass(game_class, GameTextPGN):
            self._rules = text_format
        else:
            self._rules = import_format
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
            game_class.append_piece_move,
            game_class.append_token_and_set_error,
            game_class.append_token_and_set_error,
            game_class.append_piece_move,
            game_class.append_token_and_set_error,
            game_class.append_token_and_set_error,
            game_class.append_pawn_move,
            game_class.append_pawn_move,
            game_class.append_pawn_promote_move,
            game_class.append_castles,
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
            game_class.append_other_or_disambiguation_pgn,
            )
        self.error_despatch_table = (
            None,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_game_termination_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_comment_to_eol_after_error,
            game_class.append_token_after_error,
            game_class.append_start_rav_after_error,
            game_class.append_end_rav_after_error,
            game_class.append_token_after_error,
            game_class.append_token_after_error,
            game_class.append_escape_after_error,
            game_class.append_pass_after_error,
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
        residue = ''
        for pgntext in self._read_pgn(source, size):

            # The previous chunk of pgntext may have ended with an incomplete
            # game, with or without errors.
            if residue:
                pgntext = residue + pgntext
                residue = ''
            residue_start_on_error_at_pgntext_end = None

            game = game_class()
            for match in self._rules.finditer(pgntext):
                if game.state is not None:
                    if match.lastindex == IFG_END_TAG:

                        # A PGN Tag in an error sequence starts a new game
                        # except when the sequence starts with a comment, '{',
                        # or reserved, '<', sequence for which a matching '}'
                        # or '>' has not been found.  Chunking the input is
                        # likely to make this happen, even in the absence of
                        # PGN errors, until sufficient text has been read to
                        # resolve the problem.  '{[A"a"]}' is allowed as a
                        # comment in PGN.
                        if game._text[game.state][0] in UNTERMINATED:
                            game.append_token_after_error(match)
                            continue

                        residue_start_on_error_at_pgntext_end = match.start()
                        yield game
                        game = game_class()
                        despatch_table[match.lastindex](game, match)
                    else:
                        error_despatch_table[match.lastindex](game, match)
                elif match.lastindex == IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE:
                    despatch_table[match.lastindex](game, match)
                elif match.lastindex == IFG_GAME_TERMINATION:
                    residue_start_on_error_at_pgntext_end = match.end()
                    despatch_table[match.lastindex](game, match)
                    if len(game._ravstack) > 1:
                        game.set_game_error()
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
                residue = pgntext[
                    residue_start_on_error_at_pgntext_end:]

        # The final game in the input has an error, or has no error but no game
        # termination marker either.
        if game._text:
            game.set_game_error()
            yield game


def add_token_to_game(text, game, pos=0):
    """Apply first match in text after pos to game and return match end point.
    """
    if isinstance(game, GameIgnoreCasePGN):
        match = ignore_case_format.search(text, pos)
    elif isinstance(game, GameTextPGN):
        match = text_format.search(text, pos)
    else:
        match = import_format.search(text, pos)
    if not match:
        game.set_game_error()
        return None
    lastindex = match.lastindex
    if game.state is not None:
        if lastindex == IFG_GAME_TERMINATION:
            game.append_game_termination_after_error(match)
        elif lastindex == IFG_COMMENT_TO_EOL:
            game.append_comment_to_eol_after_error(match)
        elif lastindex == IFG_START_RAV:
            game.append_start_rav_after_error(match)
        elif lastindex == IFG_END_RAV:
            game.append_end_rav_after_error(match)
        elif lastindex == IFG_ESCAPE:
            game.append_escape_after_error(match)
        elif lastindex == IFG_PASS:
            game.append_pass_after_error(match)
        else:
            game.append_token_after_error(match)
        return match.end()
    if lastindex == IFG_END_TAG:
        game.append_start_tag(match)
    elif lastindex == IFG_PIECE_MOVE:
        game.append_piece_move(match)
    elif lastindex == IFG_PIECE_DESTINATION:
        game.append_piece_move(match)
    elif lastindex == IFG_PAWN_TO_RANK:
        game.append_pawn_move(match)
    elif lastindex == IFG_PAWN_PROMOTE_TO_RANK:
        game.append_pawn_move(match)
    elif lastindex == IFG_PAWN_PROMOTE_PIECE:
        game.append_pawn_promote_move(match)
    elif lastindex == IFG_CASTLES:
        game.append_castles(match)
    elif lastindex == IFG_GAME_TERMINATION:
        game.append_game_termination(match)
    elif lastindex == IFG_MOVE_NUMBER:
        game.ignore_move_number(match)
    elif lastindex == IFG_DOTS:
        game.ignore_dots(match)
    elif lastindex == IFG_COMMENT_TO_EOL:
        game.append_comment_to_eol(match)
    elif lastindex == IFG_COMMENT:
        game.append_token(match)
    elif lastindex == IFG_START_RAV:
        game.append_start_rav(match)
    elif lastindex == IFG_END_RAV:
        game.append_end_rav(match)
    elif lastindex == IFG_NUMERIC_ANNOTATION_GLYPH:
        game.append_token(match)
    elif lastindex == IFG_RESERVED:
        game.append_reserved(match)
    elif lastindex == IFG_ESCAPE:
        game.ignore_escape(match)
    elif lastindex == IFG_PASS:
        game.append_pass_and_set_error(match)
    elif lastindex == IFG_OTHER_WITH_NON_NEWLINE_WHITESPACE:
        game.append_other_or_disambiguation_pgn(match)
    else:
        game.append_token_and_set_error(match)
    return match.end()
