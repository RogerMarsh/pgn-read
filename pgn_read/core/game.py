# game.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)
# Code transferred from 2016 version of parser.py and modified.

"""Portable Game Notation (PGN) position and game navigation data structures.

Game expects Import Format PGN, which includes Export Format PGN, and allows
some transgressions which occur in real PGN files that do not stop extraction
of the moves played or given in variations (RAVs).

Game binds _strict_pgn to False.

"""
import re

from .constants import (
    IFG_TAG_NAME,
    IFG_TAG_VALUE,
    FILE_NAMES,
    RANK_NAMES,
    FEN_WHITE_ACTIVE,
    FEN_BLACK_ACTIVE,
    FEN_NULL,
    FEN_WHITE_PAWN,
    FEN_BLACK_PAWN,
    IFG_CASTLES,
    IFG_PIECE_MOVE,
    IFG_PIECE_MOVE_FROM_FILE_OR_RANK,
    IFG_PIECE_CAPTURE,
    IFG_PIECE_DESTINATION,
    IFG_PAWN_FROM_FILE,
    IFG_PAWN_CAPTURE_TO_FILE,
    IFG_PAWN_TO_RANK,
    IFG_PAWN_PROMOTE_TO_RANK,
    IFG_PAWN_PROMOTE_PIECE,
    PGN_CAPTURE_MOVE,
    FEN_TO_PGN,
    PGN_ROOK,
    CASTLING_MOVE_RIGHTS,
    FEN_PAWNS,
    PGN_O_O,
    OTHER_SIDE,
    PROMOTED_PIECE_NAME,
    DISAMBIGUATE_TEXT,
    DG_CAPTURE,
    DG_DESTINATION,
    DISAMBIGUATE_PGN,
    LAN_FORMAT,
    TAG_RESULT,
    DEFAULT_TAG_RESULT_VALUE,
    PGN_MAXIMUM_LINE_LENGTH,
    PGN_LINE_SEPARATOR,
    PGN_TOKEN_SEPARATOR,
    PGN_DOT,
    SUFFIX_ANNOTATION_TO_NAG,
)
from .gamedata import GameData, generate_fen_for_position, GameError
from .squares import fen_squares, source_squares, en_passant_target_squares

disambiguate_pgn_format = re.compile(DISAMBIGUATE_PGN)
disambiguate_text_format = re.compile(DISAMBIGUATE_TEXT)
lan_format = re.compile(LAN_FORMAT)
suffix_annotations = re.compile(r"(!!|!\?|!|\?\?|\?!|\?)$")


class Game(GameData):
    """Data structure of game positions derived from a PGN game score.

    Input is a token which is potentially a valid token, as defined in the PGN
    specification, in the current game state.

    Move number indications and dots are detected but completely ignored while
    the input is valid.  The PGN specification states move number indications
    are optional but must be correct if present.  Thus games with incorrect
    move number indications are accepted if the game is valid otherwise.

    Movetext like 'Nge2' is accepted when 'Ne2' is unambiguous: typically the
    'N' on 'c3' is pinned against the 'K' on 'e1'.

    Invalid tokens between the first valid movetext and the game termination
    marker are not allowed when _strict_pgn is False.  This may be changed in
    future to ignore these invalid tokens.

    The left and right angle bracket characters, and any characters between a
    ('<', '>') pair, are treated as an error because the two characters are
    reserved for future expansion in the PGN specification.  The sequence
    '<.*>' happens to match the markup sequences of HTML and XHTML.

    Comparison operators implement the PGN collating sequence, except in
    ascending str order rather than ascending ASCII order.
    """

    def append_comment_to_eol(self, match):
        r"""Append ';...\n' token from gamescore.

        The '\n' termination for the comment is not captured because it may
        start an escaped line, '\n%...\n', and is explicitly added to the
        token.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(match.group() + "\n")
        try:
            self.repeat_board_state()
        except IndexError:
            self.add_board_state_none()

    def append_token(self, match):
        """Append valid non-tag token from game score.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(match.group())
        try:
            self.repeat_board_state()
        except IndexError:
            self.add_board_state_none()

    append_reserved = append_token

    # '--' is a non-standard, and not rare, extension to PGN meaning side with
    # move does not make a move but the other side is now to move.
    # Some subclasses of Game ignore anything which is not PGN.  These two
    # methods ensure '--' is always captured because the associated moves will
    # not make sense, when eyeballed, if the '--' is missing.
    # '--' has been seen as the first or only move after the tags, where it
    # makes no sense, and is therefore treated as legal as the first movetext
    # token.  However it is not allowed as the first token of a game score, in
    # PGN files the first token after a game termination token, to minimise
    # the risk of swallowing valid games from it's use in PGN files: the
    # Craftynn.pgn series for example.
    def append_pass_and_set_error(self, match):
        """Append '--' token and set PGN error found."""
        if self._movetext_offset is None and self._text:
            if not self.set_initial_position():
                self._append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        self._append_token_and_set_error(match)

    def append_pass_after_error(self, match):
        """Append '--' token found after detection of PGN error."""
        self.append_token_after_error(match)

    # self left in place.  Pylint reports no-self-use.
    def pgn_mark_comment_in_error(self, comment):
        """Return comment.  Subclasses should override to fit requirements.

        When not overridden the game_ok or game_ok_with_variation_errors
        properties should be used to test for errors rather than the state
        or game_has_errors properties.  self._state can be None even if there
        are errors in recursive annotation variations.  The detail of the
        subclass will determine if this is still the case.

        One possibility is to wrap the error in a '{...}' comment.  The '}'
        token in any wrapped commment would end the comment wrapping the error
        prematurely, so some action may be needed.

        """
        return comment

    def append_token_and_set_error(self, match):
        """Append first invalid token in main line or variation to game score.

        The game error state is adjusted so the error condition can be removed
        at the end of the variation in which it occured.

        """
        self._append_token_and_set_error(match)

    def append_token_after_error(self, match):
        """Append token to game score after an error has been found."""
        self._text.append(PGN_TOKEN_SEPARATOR + match.group())

    def append_token_after_error_without_separator(self, match):
        """Append token without separator from game score after PGN error.

        Sequences of dots after an error are kept together, there is not a
        space before each dot.  When there is no error dots are ignored.

        Check indicators are not prefixed with a separator.

        """
        self._text.append(match.group())

    def append_comment_after_error(self, match):
        """Append comment token to game score after an error has been found."""
        self._text.append(
            PGN_TOKEN_SEPARATOR + self.pgn_mark_comment_in_error(match.group())
        )

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
        if (
            self._strict_pgn
            or self._state is not None
            or self._movetext_offset is not None
        ):
            if self._state is None:
                self._state = len(self._text)
                self._state_stack[-1] = self._state
                self._error_list.append(self._state)
            self._text.append(
                match.group().join(("{::Bad Tag::", "::Bad Tag::}"))
            )
            # self._text.append('*')
            try:
                self.repeat_board_state()
            except IndexError:
                if self._position_deltas:
                    raise
                self.add_board_state_none()
            return
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
        self.add_board_state_none()
        tag_name = bad_tag[0].lstrip("[").strip()
        self._text.append("".join(("[", tag_name, '"', val, '"]')))
        if tag_name in self._tags:
            if self._state is None:
                self._state = len(self._tags) - 1
                self._state_stack[-1] = self._state
            return
        self._tags[tag_name] = val
        return

    def append_bad_tag_after_error(self, match):
        """Append token to game score after an error has been found."""
        self._text.append(match.group())
        if self._state is not None or self._movetext_offset is not None:
            self.add_board_state_none()

    def append_game_termination_after_error(self, match):
        """Delegate action to append_token_after_error method.

        append_game_termination_after_error exists to provide explicit default
        action when a game termination token to found when in game error state.

        """
        self.pgn_error_recovery()
        self.append_token_after_error(match)

    def append_comment_to_eol_after_error(self, match):
        r"""Append ';...\n' token to game score after an error has been found.

        The '\n' termination for the comment is not captured because it may
        start an escaped line, '\n%...\n', and is explicitly added to the
        token.

        """
        self._text.append(match.group() + "\n")

    def append_start_rav_after_error(self, match):
        """Append start RAV token from game score after PGN error found."""
        self.append_token_after_error(match)
        self._state_stack.append(self._state)

    def append_end_rav_after_error(self, match):
        """Append end RAV token from game score after PGN error found."""
        if len(self._state_stack) > 1:
            if self._state_stack[-2] == self._state_stack[-1]:
                self.append_token_after_error(match)
                del self._state_stack[-1]
                self._state = self._state_stack[-1]
            else:
                # Cannot call append_end_rav() method because it tests some
                # conditions that should be true when errors are absent.
                if self._movetext_offset is None:
                    self._append_token_and_set_error(match)
                    return
                if len(self._ravstack) == 1:
                    self._append_token_and_set_error(match)
                    return
                del self._ravstack[-1]
                del self._state_stack[-1]
                self._state = self._state_stack[-1]
                if self._ravstack[-1][2] is None:
                    self.set_position_to_play_prior_right_nested_rav_at_move()
                else:
                    self.set_position_to_play_main_line_at_move()
                self.pgn_error_recovery()
                self._text.append(match.group())

        else:
            self.append_token_after_error(match)

    def append_escape_after_error(self, match):
        r"""Append escape token to game score after an error has been found.

        The '\n' termination for the escaped line is not captured because it
        may start an escaped line.

        The '\n' is appended to the token.

        """
        self._text.append(match.group() + "\n")

    def append_other_or_disambiguation_pgn(self, match):
        """Ignore token previously used for disambiguation, or set PGN error.

        'Qb3c2' can mean move the queen on b3 to c2 when all whitespace is
        removed from PGN movetext.  This method processes the 'c2' when it is
        consumed from the input: 'c2' is processed by peeking at the input when
        processing the 'Qb3'.

        """
        # The pawn-like capture destination has been processed as part of a
        # fully disambiguated piece move.
        # There is no need to do anything for long algebraic notation moves
        # because these are allowed only when unrecognized tokens are ignored.
        # In other words when 'if self._strict_pgn' evaluates False.
        if self._full_disambiguation_detected:
            del self._full_disambiguation_detected
            if disambiguate_pgn_format.match(match.group()):
                return

        if self._strict_pgn is not None:
            self._append_token_and_set_error(match)

    def append_start_tag(self, match):
        """Append tag token to game score and update game tags.

        Put game in error state if a duplicate tag name is found.

        """
        if self._state is not None or self._movetext_offset is not None:
            self._append_token_and_set_error(match)
            return
        group = match.group
        tag_name = group(IFG_TAG_NAME)
        tag_value = group(IFG_TAG_VALUE)
        self._text.append("".join(("[", tag_name, '"', tag_value, '"]')))
        self.add_board_state_none()

        # Iniitialized None and set True when first valid match is applied.
        # Parser detects when a tag is out-of-sequence and sets _game_ok False.
        # if self._state is None:
        #    self._state = 'True'
        #    self._state_stack[-1] = self._state

        # Tag names must not be duplicated.
        if tag_name in self._tags:
            # if self._state == 'True':
            if self._state is None:
                self._state = len(self._tags) - 1
                self._state_stack[-1] = self._state
            return

        self._tags[tag_name] = tag_value
        return

    def append_castles(self, match):
        """Append castling move token to game score and update board state.

        Put game in error state if the token represents an illegal move.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self._append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        piece_placement_data = self._piece_placement_data
        if self._active_color == FEN_WHITE_ACTIVE:
            king_square = FILE_NAMES[4] + RANK_NAMES[-1]
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            king_square = FILE_NAMES[4] + RANK_NAMES[0]
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        if king_square not in piece_placement_data:
            self._append_token_and_set_error(match)
            return
        castling_move = match.group(IFG_CASTLES)
        if (
            CASTLING_MOVE_RIGHTS[self._active_color, castling_move]
            not in self._castling_availability
        ):
            self._append_token_and_set_error(match)
            return
        if castling_move == PGN_O_O:
            if self._active_color == FEN_WHITE_ACTIVE:
                rook_square = FILE_NAMES[7] + RANK_NAMES[-1]
                king_destination = FILE_NAMES[6] + RANK_NAMES[-1]
                rook_destination = FILE_NAMES[5] + RANK_NAMES[-1]
            else:
                rook_square = FILE_NAMES[7] + RANK_NAMES[0]
                king_destination = FILE_NAMES[6] + RANK_NAMES[0]
                rook_destination = FILE_NAMES[5] + RANK_NAMES[0]
        elif self._active_color == FEN_WHITE_ACTIVE:
            rook_square = FILE_NAMES[0] + RANK_NAMES[-1]
            king_destination = FILE_NAMES[2] + RANK_NAMES[-1]
            rook_destination = FILE_NAMES[3] + RANK_NAMES[-1]
        else:
            rook_square = FILE_NAMES[0] + RANK_NAMES[0]
            king_destination = FILE_NAMES[2] + RANK_NAMES[0]
            rook_destination = FILE_NAMES[3] + RANK_NAMES[0]
        if rook_square not in piece_placement_data:
            self._append_token_and_set_error(match)
            return
        if not self.line_empty(king_square, rook_square):
            self._append_token_and_set_error(match)
            return

        # Cannot castle if king is in check, king would be in check if move
        # completed, or the square between the source and destination is
        # attacked by the other side.
        # No need to test if king is in check after applying remove and place
        # instructions to board.
        ptp = fen_squares[king_square].point_to_point[king_destination]
        for square in (
            king_square,
            king_destination,
            ptp[0],
        ):
            if self.is_square_attacked_by_other_side(
                square, self._active_color
            ):
                self._append_token_and_set_error(match)
                return

        king = piece_placement_data[king_square]
        rook = piece_placement_data[rook_square]
        self._modify_game_state_castles(
            ((king_square, king), (rook_square, rook)),
            ((king_destination, king), (rook_destination, rook)),
            fullmove_number_for_next_halfmove,
        )
        self._append_decorated_castles_text(match.group())

    def append_piece_move(self, match):
        """Append piece move token to game score and update board state.

        Put game in error state if the token represents an illegal move.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self._append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        group = match.group
        if self._active_color == FEN_WHITE_ACTIVE:
            piece_name = group(IFG_PIECE_MOVE)
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            piece_name = group(IFG_PIECE_MOVE).lower()
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        destination = group(IFG_PIECE_DESTINATION)
        try:
            src_squares = source_squares[group(IFG_PIECE_MOVE)][destination]
        except KeyError:
            self._append_token_and_set_error(match)
            return
        piece_placement_data = self._piece_placement_data

        # Piece move and capture.

        if group(IFG_PIECE_CAPTURE):
            if destination not in piece_placement_data:
                self._append_token_and_set_error(match)
                return
            candidates = []
            for piece in self._pieces_on_board[piece_name]:
                if piece.square.name in src_squares:
                    candidates.append(piece)
            if len(candidates) == 1:
                piece = candidates[0]
                if not self.line_empty(piece.square.name, destination):
                    self._append_token_and_set_error(match)
                    return

                # Allow acceptance of superfluous precision in movetext, even
                # though it may be too lenient as there is only one piece that
                # could make the move.
                # For example Ngxe2 when Nxe2 is unambiguous.
                # But Ng1xe2 is not accepted at this point.
                if group(IFG_PIECE_MOVE_FROM_FILE_OR_RANK):
                    if self._strict_pgn:
                        self._append_token_and_set_error(match)
                        return
                    movetext = group()[:1] + group()[2:]
                else:
                    movetext = group()

                self._modify_game_state_piece_capture(
                    (
                        (destination, piece_placement_data[destination]),
                        (piece.square.name, piece),
                    ),
                    ((destination, piece),),
                    fullmove_number_for_next_halfmove,
                )
                if self.is_side_off_move_in_check():
                    self.undo_board_state()
                    self._append_token_and_set_error(match)
                    return
                self._append_decorated_text(movetext)
                return
            from_file_or_rank = group(IFG_PIECE_MOVE_FROM_FILE_OR_RANK)
            if from_file_or_rank:
                can_move = []
            fit_count = 0
            chosen_move = None
            for piece in candidates:
                if not self.line_empty(piece.square.name, destination):
                    continue
                square_before_move = piece.square
                remove = (
                    (destination, piece_placement_data[destination]),
                    (square_before_move.name, piece),
                )
                self.remove_piece_from_board(remove[0])
                self.remove_piece_on_square(remove[1])
                place = destination, piece
                self.place_piece_on_square(place)
                if not self.is_piece_pinned_to_king(piece, square_before_move):
                    if from_file_or_rank:
                        if from_file_or_rank in remove[-1][0]:
                            chosen_move = remove, place
                            fit_count += 1
                        can_move.append(piece)
                    else:
                        chosen_move = remove, place
                        fit_count += 1
                self.remove_piece_on_square(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_square(remove[1])
            if chosen_move is None or fit_count != 1:
                self._append_token_and_set_error(match)
                return

            # Acceptance of superfluous precision in movetext is allowed.
            # For example Ngxe2 when Nxe2 is unambiguous.
            # But Ng1xe2 is not accepted at this point.
            if from_file_or_rank:
                if len(can_move) == 1:
                    if self._strict_pgn:
                        self._append_token_and_set_error(match)
                        return
                    movetext = group()[:1] + group()[2:]
                elif from_file_or_rank in RANK_NAMES:
                    pfile = chosen_move[0][1][0][0]
                    if (
                        len([p for p in can_move if p.square.file == pfile])
                        < 2
                    ):
                        self._append_token_and_set_error(match)
                        return
                    movetext = group()
                else:
                    movetext = group()
            else:
                movetext = group()

            self._modify_game_state_piece_capture(
                chosen_move[0],  # Two items because move is a capture.
                (chosen_move[1],),
                fullmove_number_for_next_halfmove,
            )
            if self.is_side_off_move_in_check():
                self.undo_board_state()
                self._append_token_and_set_error(match)
                return
            self._append_decorated_text(movetext)
            return

        # Piece move without capture.

        if destination in piece_placement_data:
            # IMPORT_FORMAT regular expression treats 'Qe3c6' as 'Qe3' and
            # 'c6', and 'Qe3xc6' as 'Qe3' and the unexpected 'xc6'.
            # The capture could be spotted, but not the move.
            # Allow all movetext like 'Qe3e6' or 'Qe3xe6' when _strict_pgn is
            # not enforced, and perhaps even 'Qe3-c6'.
            # Rooks never need full disambiguation, at most two pawns can
            # capture and land on a square, and there is only one king.
            # Full disambiguation is not needed when less than three pieces of
            # the type can move to the square.
            if piece_placement_data[destination].color != self._active_color:
                self._append_token_and_set_error(match)
                return
            if not self._strict_pgn:
                self._long_algebraic_notation_piece_move(match)
                return
            if FEN_TO_PGN[piece_placement_data[destination].name] == PGN_ROOK:
                self._append_token_and_set_error(match)
                return
            self._disambiguate_piece_move(match)
            return

        candidates = []
        for piece in self._pieces_on_board[piece_name]:
            if piece.square.name in src_squares:
                candidates.append(piece)
        if len(candidates) == 1:
            piece = candidates[0]
            if not self.line_empty(piece.square.name, destination):
                self._append_token_and_set_error(match)
                return

            # Allow acceptance of superfluous precision in movetext, even
            # though it may be too lenient as there is only one piece that
            # could make the move.
            # For example Nge2 when Ne2 is unambiguous.
            # But Ng1e2 is not accepted at this point.
            if group(IFG_PIECE_MOVE_FROM_FILE_OR_RANK):
                if self._strict_pgn:
                    self._append_token_and_set_error(match)
                    return
                movetext = group()[:1] + group()[2:]
            else:
                movetext = group()

            self._modify_game_state_piece_move(
                ((piece.square.name, piece),),
                ((destination, piece),),
                fullmove_number_for_next_halfmove,
            )
            if self.is_side_off_move_in_check():
                self.undo_board_state()
                self._append_token_and_set_error(match)
                return
            self._append_decorated_text(movetext)
            return
        from_file_or_rank = group(IFG_PIECE_MOVE_FROM_FILE_OR_RANK)
        if from_file_or_rank:
            can_move = []
        fit_count = 0
        chosen_move = None
        for piece in candidates:
            if not self.line_empty(piece.square.name, destination):
                continue
            square_before_move = piece.square
            remove = square_before_move.name, piece
            self.remove_piece_on_square(remove)
            place = destination, piece
            self.place_piece_on_square(place)
            if not self.is_piece_pinned_to_king(piece, square_before_move):
                if from_file_or_rank:
                    if from_file_or_rank in remove[0]:
                        chosen_move = remove, place
                        fit_count += 1
                    can_move.append(piece)
                else:
                    chosen_move = remove, place
                    fit_count += 1
            self.remove_piece_on_square(place)
            self.place_piece_on_square(remove)
        if chosen_move is None or fit_count != 1:
            self._append_token_and_set_error(match)
            return

        # Acceptance of superfluous precision in movetext is allowed.
        # For example Nge2 when Ne2 is unambiguous.
        # But Ng1e2 is not accepted at this point.
        if from_file_or_rank:
            if len(can_move) == 1:
                if self._strict_pgn:
                    self._append_token_and_set_error(match)
                    return
                movetext = group()[:1] + group()[2:]
            elif from_file_or_rank in RANK_NAMES:
                pfile = chosen_move[0][0][0][0]
                if len([p for p in can_move if p.square.file == pfile]) < 2:
                    self._append_token_and_set_error(match)
                    return
                movetext = group()
            else:
                movetext = group()
        else:
            movetext = group()

        self._modify_game_state_piece_move(
            (chosen_move[0],),  # One item because move is not a capture.
            (chosen_move[1],),
            fullmove_number_for_next_halfmove,
        )
        if self.is_side_off_move_in_check():
            self.undo_board_state()
            self._append_token_and_set_error(match)
            return
        self._append_decorated_text(movetext)

    def append_pawn_move(self, match):
        """Append pawn move token to game score and update board state.

        Pawn promotion moves are handled by append_pawn_promote_move.

        Put game in error state if the token represents an illegal move.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self._append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        group = match.group
        piece_placement_data = self._piece_placement_data

        # Pawn move and capture.

        if group(IFG_PAWN_CAPTURE_TO_FILE):
            destination = group(IFG_PAWN_CAPTURE_TO_FILE) + group(
                IFG_PAWN_TO_RANK
            )
            pawn_capture_from_file = group(IFG_PAWN_FROM_FILE)
            if self._active_color == FEN_WHITE_ACTIVE:
                fullmove_number_for_next_halfmove = self._fullmove_number
                source_squares_index = FEN_WHITE_PAWN + PGN_CAPTURE_MOVE
            else:
                fullmove_number_for_next_halfmove = self._fullmove_number + 1
                source_squares_index = FEN_BLACK_PAWN + PGN_CAPTURE_MOVE
            try:
                src_squares = source_squares[source_squares_index][destination]
            except KeyError:
                self._append_token_and_set_error(match)
                return
            # Pylint reports undefined-loop-variable for source later.
            # The loop looks safe at this time.
            for source in src_squares:
                if source.startswith(pawn_capture_from_file):
                    try:
                        if (
                            FEN_PAWNS.get(piece_placement_data[source].name)
                            == self._active_color
                        ):
                            piece = piece_placement_data[source]
                            break
                    except KeyError:
                        self._append_token_and_set_error(match)
                        return
            else:
                self._append_token_and_set_error(match)
                return
            if destination not in piece_placement_data:
                if self._en_passant_target_square == FEN_NULL:
                    self._append_token_and_set_error(match)
                    return
                capture_square = en_passant_target_squares.get(group()[:4])
                if not capture_square:
                    self._append_token_and_set_error(match)
                    return
                if capture_square not in piece_placement_data:
                    self._append_token_and_set_error(match)
                    return
                if (
                    FEN_PAWNS.get(piece_placement_data[capture_square].name)
                    == self._active_color
                ):
                    self._append_token_and_set_error(match)
                    return
            elif (
                piece_placement_data[source].color
                == piece_placement_data[destination].color
            ):
                self._append_token_and_set_error(match)
                return
            else:
                capture_square = destination
            self._modify_game_state_pawn_capture(
                (
                    (capture_square, piece_placement_data[capture_square]),
                    (piece.square.name, piece),
                ),
                ((destination, piece),),
                fullmove_number_for_next_halfmove,
            )
            if self.is_side_off_move_in_check():
                self.undo_board_state()
                self._append_token_and_set_error(match)
                return
            self._append_decorated_text(group())
            return

        # Pawn move without capture.

        destination = group(IFG_PAWN_FROM_FILE) + group(IFG_PAWN_TO_RANK)
        if destination in piece_placement_data:
            # The pawn-like move has been processed as part of a fully
            # disambiguated piece move.
            if self._full_disambiguation_detected:
                del self._full_disambiguation_detected
                return

            # Allow all movetext like 'e3e4' or 'e3xd4' when _strict_pgn
            # is not enforced, and perhaps even 'e3-e4'.  'exd4' is handled
            # in the 'Pawn move and capture' section, being within the PGN
            # specification.  Pawn promotions such as 'e7e8=Q' or 'e7xf8=Q'
            # are handled here, not by the append_pawn_promote_move method
            # which handles 'e8=Q' and 'exf8=Q'.
            # The pawn promotion comment seems to be wrong given outcome of
            # GameLongAlgebraicNotationPawnMove and
            # GameTextPGNLongAlgebraicNotationPawnMove
            # tests in .core.tests.test_parser module.
            if self._strict_pgn:
                self._append_token_and_set_error(match)
            else:
                self._long_algebraic_notation_pawn_move(match)
            return

        if self._active_color == FEN_WHITE_ACTIVE:
            fullmove_number_for_next_halfmove = self._fullmove_number
            source_squares_index = FEN_WHITE_PAWN
        else:
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
            source_squares_index = FEN_BLACK_PAWN
        try:
            src_squares = source_squares[source_squares_index][destination]
        except KeyError:
            self._append_token_and_set_error(match)
            return
        for source in src_squares:
            if source in piece_placement_data:
                piece = piece_placement_data[source]
                if FEN_PAWNS.get(piece.name) == self._active_color:
                    if self.line_empty(destination, source):
                        break
        else:
            self._append_token_and_set_error(match)
            return
        new_en_passant_target_square = en_passant_target_squares[
            OTHER_SIDE[self._active_color]
        ].get((destination, piece.square.name), FEN_NULL)
        self._modify_game_state_pawn_move(
            ((piece.square.name, piece),),
            ((destination, piece),),
            fullmove_number_for_next_halfmove,
            new_en_passant_target_square,
        )
        if self.is_side_off_move_in_check():
            self.undo_board_state()
            self._append_token_and_set_error(match)
            return
        self._append_decorated_text(group())

    def append_pawn_promote_move(self, match):
        """Append pawn promotion move token from game score.

        Put game in error state if the token represents an illegal move.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self._append_token_and_set_error(match)
                return
            self._ravstack.append([0])
            self._movetext_offset = len(self._text)
        group = match.group
        if group(IFG_PAWN_PROMOTE_TO_RANK) is None:
            self._append_token_and_set_error(match)
            return
        piece_placement_data = self._piece_placement_data

        # Promotion move and capture.

        if group(IFG_PAWN_CAPTURE_TO_FILE):
            destination = group(IFG_PAWN_CAPTURE_TO_FILE) + group(
                IFG_PAWN_PROMOTE_TO_RANK
            )
            pawn_capture_from_file = group(IFG_PAWN_FROM_FILE)
            if self._active_color == FEN_WHITE_ACTIVE:
                fullmove_number_for_next_halfmove = self._fullmove_number
                source_squares_index = FEN_WHITE_PAWN + PGN_CAPTURE_MOVE
            else:
                fullmove_number_for_next_halfmove = self._fullmove_number + 1
                source_squares_index = FEN_BLACK_PAWN + PGN_CAPTURE_MOVE
            try:
                src_squares = source_squares[source_squares_index][destination]
            except KeyError:
                self._append_token_and_set_error(match)
                return
            # Pylint reports undefined-loop-variable for source later.
            # The loop looks safe at this time.
            for source in src_squares:
                if source.startswith(pawn_capture_from_file):
                    try:
                        if (
                            FEN_PAWNS.get(piece_placement_data[source].name)
                            == self._active_color
                        ):
                            piece = piece_placement_data[source]
                            break
                    except KeyError:
                        self._append_token_and_set_error(match)
                        return
            else:
                self._append_token_and_set_error(match)
                return
            if destination not in piece_placement_data:
                if self._en_passant_target_square == FEN_NULL:
                    self._append_token_and_set_error(match)
                    return
                capture_square = en_passant_target_squares.get(group()[:4])
                if not capture_square:
                    self._append_token_and_set_error(match)
                    return
                if capture_square not in piece_placement_data:
                    self._append_token_and_set_error(match)
                    return
                if (
                    FEN_PAWNS.get(piece_placement_data[capture_square].name)
                    == self._active_color
                ):
                    self._append_token_and_set_error(match)
                    return
            elif (
                piece_placement_data[source].color
                == piece_placement_data[destination].color
            ):
                self._append_token_and_set_error(match)
                return
            else:
                capture_square = destination
            promoted_pawn = piece.promoted_pawn(
                PROMOTED_PIECE_NAME[self._active_color][
                    group(IFG_PAWN_PROMOTE_PIECE)
                ],
                destination,
            )
            self._modify_game_state_pawn_promote_capture(
                (
                    (capture_square, piece_placement_data[capture_square]),
                    (piece.square.name, piece),
                ),
                ((destination, promoted_pawn),),
                fullmove_number_for_next_halfmove,
            )
            if self.is_side_off_move_in_check():
                self.undo_board_state()
                self._append_token_and_set_error(match)
                return
            self._append_decorated_text(group())
            return

        # Promotion move without capture.

        destination = group(IFG_PAWN_FROM_FILE) + group(
            IFG_PAWN_PROMOTE_TO_RANK
        )
        if destination in piece_placement_data:
            self._append_token_and_set_error(match)
            return
        if self._active_color == FEN_WHITE_ACTIVE:
            fullmove_number_for_next_halfmove = self._fullmove_number
            source_squares_index = FEN_WHITE_PAWN
        else:
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
            source_squares_index = FEN_BLACK_PAWN
        try:
            src_squares = source_squares[source_squares_index][destination]
        except KeyError:
            self._append_token_and_set_error(match)
            return
        for source in src_squares:
            if source in piece_placement_data:
                piece = piece_placement_data[source]
                if FEN_PAWNS.get(piece.name) == self._active_color:
                    if self.line_empty(destination, source):
                        break
        else:
            self._append_token_and_set_error(match)
            return
        promoted_pawn = piece.promoted_pawn(
            PROMOTED_PIECE_NAME[self._active_color][
                group(IFG_PAWN_PROMOTE_PIECE)
            ],
            destination,
        )
        self._modify_game_state_pawn_promote(
            ((piece.square.name, piece),),
            ((destination, promoted_pawn),),
            fullmove_number_for_next_halfmove,
        )
        if self.is_side_off_move_in_check():
            self.undo_board_state()
            self._append_token_and_set_error(match)
            return
        self._append_decorated_text(group())

    def append_start_rav(self, match):
        """Append start recursive annotation variation token to game score."""
        if not self._reset_after_start_rav(match):
            return
        self._text.append(match.group())

    def append_end_rav(self, match):
        """Append end recursive annotation variation token to game score."""
        if not self._reset_after_end_rav(match):
            return
        self._reset_position_after_end_rav(match)
        self._text.append(match.group())

    def append_game_termination(self, match):
        """Append game termination token to game score and update game state.

        Put game in error state if no moves exists in game score and the
        initial position is not valid.  Validation includes piece counts and
        some piece placement: pawns on ranks 2 to 7 only and king of active
        color not in check for example.  Verification that the initial position
        declared in a PGN FEN tag is reachable from the standard starting
        position is not attempted.

        """
        if self._movetext_offset is None:
            if not self.set_initial_position():
                self._append_token_and_set_error(match)
                return
            self._movetext_offset = len(self._text)
        self._text.append(match.group())
        self.add_board_state_none()

    def append_glyph_for_traditional_annotation(self, match):
        """Append NAG for traditional annotation to game score.

        The game position for this token is the same as for the adjacent token,
        and the game state is adjusted to fit.

        """
        self._text.append(SUFFIX_ANNOTATION_TO_NAG[match.group()])
        try:
            self.repeat_board_state()
        except IndexError:
            self.add_board_state_none()

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

    def _disambiguate_piece_move(self, match):
        group = match.group
        if self._active_color == FEN_WHITE_ACTIVE:
            piece_name = group(IFG_PIECE_MOVE)
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            piece_name = group(IFG_PIECE_MOVE).lower()
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        peek_start = match.span(match.lastindex)[-1]
        dtfm = disambiguate_text_format.match(
            match.string[peek_start : peek_start + 10]
        )
        if not dtfm:
            self._append_token_and_set_error(match)
            return
        piece_placement_data = self._piece_placement_data
        piece = piece_placement_data[group(IFG_PIECE_DESTINATION)]
        destination = dtfm.group(DG_DESTINATION)
        src_squares = source_squares[group(IFG_PIECE_MOVE)][destination]

        # Piece move and capture.

        if dtfm.group(DG_CAPTURE) == "x":
            if destination not in piece_placement_data:
                self._append_token_and_set_error(match)
                return
            candidates = []
            for cpiece in self._pieces_on_board[piece_name]:
                if cpiece.square.name in src_squares:
                    candidates.append(cpiece)
            file_count = 0
            rank_count = 0
            sfile, srank = piece.square.name
            for cpiece in candidates:
                if not self.line_empty(cpiece.square.name, destination):
                    continue
                square_before_move = cpiece.square
                cpfile, cprank = square_before_move.name
                remove = (
                    (destination, piece_placement_data[destination]),
                    (square_before_move.name, cpiece),
                )
                self.remove_piece_from_board(remove[0])
                self.remove_piece_on_square(remove[1])
                place = destination, cpiece
                self.place_piece_on_square(place)
                if not self.is_piece_pinned_to_king(
                    cpiece, square_before_move
                ):
                    if cpfile == sfile:
                        file_count += 1
                    if cprank == srank:
                        rank_count += 1
                self.remove_piece_on_square(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_square(remove[1])
            if file_count < 2 or rank_count < 2:
                self._append_token_and_set_error(match)
                return
            self._modify_game_state_piece_capture(
                (
                    (destination, piece_placement_data[destination]),
                    (piece.square.name, piece),
                ),
                ((destination, piece),),  # Did have useless , piece.name),),
                fullmove_number_for_next_halfmove,
            )
            if self.is_side_off_move_in_check():
                self.undo_board_state()
                self._append_token_and_set_error(match)
                return
            self._append_decorated_text(group() + dtfm.group())
            self._full_disambiguation_detected = True
            return

        # Piece move without capture.
        candidates = []
        for cpiece in self._pieces_on_board[piece_name]:
            if cpiece.square.name in src_squares:
                candidates.append(cpiece)
        file_count = 0
        rank_count = 0
        sfile, srank = piece.square.name
        for cpiece in candidates:
            if not self.line_empty(cpiece.square.name, destination):
                continue
            square_before_move = cpiece.square
            cpfile, cprank = square_before_move.name
            remove = square_before_move.name, cpiece
            self.remove_piece_on_square(remove)
            place = destination, cpiece
            self.place_piece_on_square(place)
            if not self.is_piece_pinned_to_king(cpiece, square_before_move):
                if cpfile == sfile:
                    file_count += 1
                if cprank == srank:
                    rank_count += 1
            self.remove_piece_on_square(place)
            self.place_piece_on_square(remove)
        if file_count < 2 or rank_count < 2:
            self._append_token_and_set_error(match)
            return
        self._modify_game_state_piece_move(
            ((piece.square.name, piece),),
            ((destination, piece),),
            fullmove_number_for_next_halfmove,
        )
        if self.is_side_off_move_in_check():
            self.undo_board_state()
            self._append_token_and_set_error(match)
            return
        self._append_fully_disambiguated_piece_move(match, dtfm)
        self._full_disambiguation_detected = True

    def _append_fully_disambiguated_piece_move(self, match_, dtfm_match):
        """Append fully disambiguated piece move without hyphen."""
        self._append_decorated_text(
            match_.group() + dtfm_match.group(DG_DESTINATION)
        )

    def _long_algebraic_notation_destination(self, match):
        peek_start = match.span(match.lastindex)[-1]
        pms = match.string[peek_start : peek_start + 10]
        lfm = lan_format.match(pms.lower())
        return self._long_algebraic_notation_match(lfm, pms)

    def _long_algebraic_notation_match(self, long_match, peek_match):
        """Return the LAN match or None."""
        if long_match and peek_match.startswith(long_match.group()):
            return long_match
        return None

    def _long_algebraic_notation_piece_move(self, match):
        group = match.group
        if self._active_color == FEN_WHITE_ACTIVE:
            piece_name = group(IFG_PIECE_MOVE)
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            piece_name = group(IFG_PIECE_MOVE).lower()
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        landm = self._long_algebraic_notation_destination(match)

        # This token must be a match as second part of move, and must be
        # correct as a pawn or piece move in combination with first part.
        if not landm:
            self._append_token_and_set_error(match)
            return
        if landm.group(1) == "-" and self._strict_pgn is not None:
            counts = self._count_lan_piece_move_candidates(
                match,
                piece_name,
                source_squares[group(IFG_PIECE_MOVE)][landm.groups()[1]],
                landm.groups()[1],
                [],
            )
            if counts is None:
                self._append_token_and_set_error(match)
                return
            file_count, rank_count = counts
            if len(file_count) < 2 or len(rank_count) < 2:
                self._append_token_and_set_error(match)
                return

        piece_placement_data = self._piece_placement_data
        capture, destination, promotion_piece = landm.groups()
        if capture != PGN_CAPTURE_MOVE:
            if destination in piece_placement_data:
                self._append_token_and_set_error(match)
                return
        elif destination not in piece_placement_data:
            self._append_token_and_set_error(match)
            return
        if promotion_piece:
            self._append_token_and_set_error(match)
            return
        piece = piece_placement_data[group(IFG_PIECE_DESTINATION)]
        src_squares = source_squares[group(IFG_PIECE_MOVE)][destination]

        # Piece move and capture.
        if capture == PGN_CAPTURE_MOVE:
            from_square = piece.square
            counts = self._count_lan_piece_move_candidates(
                match,
                piece_name,
                src_squares,
                destination,
                [(destination, piece_placement_data[destination])],
            )
            if counts is None:
                return
            file_count, rank_count = counts
            if not self.line_empty(piece.square.name, destination):
                self._append_token_and_set_error(match)
                return
            # Does piece move without capture path need code from here:
            square_before_move = piece.square
            remove = (
                (destination, piece_placement_data[destination]),
                (square_before_move.name, piece),
            )
            self.remove_piece_from_board(remove[0])
            self.remove_piece_on_square(remove[1])
            place = destination, piece
            self.place_piece_on_square(place)
            if self.is_piece_pinned_to_king(piece, square_before_move):
                self.remove_piece_on_square(place)
                self.place_piece_on_board(remove[0])
                self.place_piece_on_square(remove[1])
                self.append_token_and_set_error(match)
                return
            # to here?
            # The only _long_algebraic_notation_piece_move() call at time
            # of writing is guarded by a test on self._strict_pgn.
            self._modify_game_state_piece_move(
                (
                    (destination, piece_placement_data[destination]),
                    (piece.square.name, piece),
                ),
                ((destination, piece),),
                fullmove_number_for_next_halfmove,
            )
            if self.is_side_off_move_in_check():
                self.undo_board_state()
                self._append_token_and_set_error(match)
                return
            if len(file_count) < 2 and len(rank_count) < 2:
                self._append_decorated_text(
                    PGN_CAPTURE_MOVE.join((group(IFG_PIECE_MOVE), destination))
                )
            elif file_count[from_square.file] == 1:
                self._append_decorated_text(
                    "".join(
                        (
                            group(IFG_PIECE_MOVE),
                            from_square.file,
                            PGN_CAPTURE_MOVE,
                            destination,
                        )
                    )
                )
            elif rank_count[from_square.rank] == 1:
                self._append_decorated_text(
                    "".join(
                        (
                            group(IFG_PIECE_MOVE),
                            from_square.rank,
                            PGN_CAPTURE_MOVE,
                            destination,
                        )
                    )
                )
            else:
                self._append_decorated_text(
                    "".join(
                        (
                            group(IFG_PIECE_MOVE),
                            from_square.name,
                            PGN_CAPTURE_MOVE,
                            destination,
                        )
                    )
                )
            self._full_disambiguation_detected = True
            return

        # Piece move without capture.
        from_square = piece.square
        counts = self._count_lan_piece_move_candidates(
            match, piece_name, src_squares, destination, []
        )
        if counts is None:
            return
        file_count, rank_count = counts
        if not self.line_empty(piece.square.name, destination):
            self._append_token_and_set_error(match)
            return
        # Should the block of code in the piece move with capture path
        # which tests if piece cannot be moved because it is pinned be
        # copied to here?
        # (Is there a test, not yet thought of, which breaks this code?)
        self._modify_game_state_piece_move(
            ((piece.square.name, piece),),
            ((destination, piece),),
            fullmove_number_for_next_halfmove,
        )
        if self.is_side_off_move_in_check():
            self.undo_board_state()
            self._append_token_and_set_error(match)
            return
        if len(file_count) < 2 and len(rank_count) < 2:
            self._append_decorated_text(group(IFG_PIECE_MOVE) + destination)
        elif file_count[from_square.file] == 1:
            self._append_decorated_text(
                "".join((group(IFG_PIECE_MOVE), from_square.file, destination))
            )
        elif rank_count[from_square.rank] == 1:
            self._append_decorated_text(
                "".join((group(IFG_PIECE_MOVE), from_square.rank, destination))
            )
        else:
            self._append_piece_move_with_from_square(
                group(IFG_PIECE_MOVE), from_square.name, destination
            )
        self._full_disambiguation_detected = True
        return

    def _append_piece_move_with_from_square(self, name, from_, destination):
        """Append fully disambiguated piece move without hyphen."""
        self._append_decorated_text("".join((name, from_, destination)))

    def _count_lan_piece_move_candidates(
        self, match, piece_name, src_squares, destination, remove_piece
    ):
        candidates = []
        for cpiece in self._pieces_on_board[piece_name]:
            if cpiece.square.name in src_squares:
                candidates.append(cpiece)
        if not candidates:
            self._append_token_and_set_error(match)
            return None
        file_count = {}
        rank_count = {}
        if len(candidates) > 1:
            for cpiece in candidates:
                if not self.line_empty(cpiece.square.name, destination):
                    continue
                square_before_move = cpiece.square
                cpfile, cprank = square_before_move.name
                remove_all = remove_piece + [(square_before_move.name, cpiece)]
                for remove in remove_all:
                    self.remove_piece_on_square(remove)
                place = destination, cpiece
                self.place_piece_on_square(place)
                if not self.is_piece_pinned_to_king(
                    cpiece, square_before_move
                ):
                    if cpfile not in file_count:
                        file_count[cpfile] = 1
                    else:
                        file_count[cpfile] += 1
                    if cprank not in rank_count:
                        rank_count[cprank] = 1
                    else:
                        rank_count[cprank] += 1
                self.remove_piece_on_square(place)
                for remove in remove_all:
                    self.place_piece_on_square(remove)
        return file_count, rank_count

    def _long_algebraic_notation_pawn_move(self, match):
        group = match.group
        if self._active_color == FEN_WHITE_ACTIVE:
            source_squares_index = FEN_WHITE_PAWN
            fullmove_number_for_next_halfmove = self._fullmove_number
        else:
            source_squares_index = FEN_BLACK_PAWN
            fullmove_number_for_next_halfmove = self._fullmove_number + 1
        square_name = group(IFG_PAWN_FROM_FILE) + group(IFG_PAWN_TO_RANK)
        landm = self._long_algebraic_notation_destination(match)

        # This token must be a match as second part of move, and must be
        # correct as a pawn or piece move in combination with first part.
        if not landm or landm.group().startswith("-"):
            self._append_token_and_set_error(match)
            return

        piece_placement_data = self._piece_placement_data
        capture, destination, promotion_piece = landm.groups()
        if capture != PGN_CAPTURE_MOVE:
            if destination in piece_placement_data:
                self._append_token_and_set_error(match)
                return
        elif self._en_passant_target_square == FEN_NULL:
            if destination not in piece_placement_data:
                self._append_token_and_set_error(match)
                return
        elif self._en_passant_target_square != destination:
            if destination not in piece_placement_data:
                self._append_token_and_set_error(match)
                return
        elif destination in piece_placement_data:
            try:
                raise GameError(
                    "".join(
                        (
                            "En-passant target square '",
                            self._en_passant_target_square,
                            "' is not consistent with position on board '",
                            generate_fen_for_position(
                                piece_placement_data.values(),
                                self._active_color,
                                self._castling_availability,
                                self._en_passant_target_square,
                                self._halfmove_clock,
                                self._fullmove_number,
                            ),
                        )
                    )
                )
            except Exception as error:
                raise GameError(
                    "En-passant target square does not fit position"
                ) from error

        if destination[1] in "18":
            if not promotion_piece:
                self._append_token_and_set_error(match)
                return
            promotion_piece = promotion_piece.upper()

            # Promotion move and capture.
            if capture == PGN_CAPTURE_MOVE:
                if (
                    square_name
                    not in source_squares[
                        source_squares_index + PGN_CAPTURE_MOVE
                    ][destination]
                ):
                    self._append_token_and_set_error(match)
                    return
                if destination not in piece_placement_data:
                    self._append_token_and_set_error(match)
                    return
                if (
                    piece_placement_data[square_name].color
                    == piece_placement_data[destination].color
                ):
                    self._append_token_and_set_error(match)
                    return
                # Binding for 'piece' deduced from cython compilation errors
                # and similar code in other paths.
                # No pylint complaint about following piece references,
                # perhaps 'from .piece import Piece' masked problem.
                # This code is probably unreachable given the outcome of
                # tests added to .tests.test_parser to verify correctness
                # of this change.  See classes in that module
                # GameLongAlgebraicNotationPawnMove and
                # GameTextPGNLongAlgebraicNotationPawnMove
                # which suggest the Game class does not see e7xf8=Q as a
                # movetext token while GameTextPGN does.
                piece = piece_placement_data[square_name]
                promoted_pawn = piece.promoted_pawn(
                    PROMOTED_PIECE_NAME[self._active_color][promotion_piece],
                    destination,
                )
                self._modify_game_state_pawn_promote_capture(
                    (
                        (destination, piece_placement_data[destination]),
                        (piece.square.name, piece),
                    ),
                    ((destination, promoted_pawn),),
                    fullmove_number_for_next_halfmove,
                )
                if self.is_side_off_move_in_check():
                    self.undo_board_state()
                    self._append_token_and_set_error(match)
                    return
                self._append_decorated_text(group())
                return

            # Promotion move without capture.
            piece = piece_placement_data[square_name]
            if (
                square_name
                not in source_squares[source_squares_index][destination]
            ):
                self._append_token_and_set_error(match)
                return
            promoted_pawn = piece.promoted_pawn(
                PROMOTED_PIECE_NAME[self._active_color][promotion_piece],
                destination,
            )
            self._modify_game_state_pawn_promote(
                ((piece.square.name, piece),),
                ((destination, promoted_pawn),),
                fullmove_number_for_next_halfmove,
            )
            if self.is_side_off_move_in_check():
                self.undo_board_state()
                self._append_token_and_set_error(match)
                return
            self._append_decorated_text(group())
            return

        # Pawn move and capture.
        if promotion_piece:
            self._append_token_and_set_error(match)
            return
        if capture == PGN_CAPTURE_MOVE:
            if (
                square_name
                not in source_squares[source_squares_index + PGN_CAPTURE_MOVE][
                    destination
                ]
            ):
                self._append_token_and_set_error(match)
                return
            piece = piece_placement_data[square_name]
            if FEN_PAWNS.get(piece.name) != self._active_color:
                self._append_token_and_set_error(match)
                return
            if not self.line_empty(destination, square_name):
                self._append_token_and_set_error(match)
                return
            if destination not in piece_placement_data:
                capture_square = en_passant_target_squares.get(
                    PGN_CAPTURE_MOVE.join(
                        (group(IFG_PAWN_FROM_FILE), destination)
                    )
                )
                if not capture_square:
                    self._append_token_and_set_error(match)
                    return
                if capture_square not in piece_placement_data:
                    self._append_token_and_set_error(match)
                    return
                if (
                    FEN_PAWNS.get(piece_placement_data[capture_square].name)
                    == self._active_color
                ):
                    self._append_token_and_set_error(match)
                    return
            elif (
                piece_placement_data[square_name].color
                == piece_placement_data[destination].color
            ):
                self._append_token_and_set_error(match)
                return
            else:
                capture_square = destination
            self._modify_game_state_pawn_capture(
                (
                    (capture_square, piece_placement_data[capture_square]),
                    (piece.square.name, piece),
                ),
                ((destination, piece),),
                fullmove_number_for_next_halfmove,
            )
            if self.is_side_off_move_in_check():
                self.undo_board_state()
                self._append_token_and_set_error(match)
                return
            self._append_decorated_text(
                PGN_CAPTURE_MOVE.join(
                    (group(IFG_PAWN_FROM_FILE), capture_square)
                )
            )
            return

        # Pawn move without capturing or promoting.
        if (
            square_name
            not in source_squares[source_squares_index][destination]
        ):
            self._append_token_and_set_error(match)
            return
        piece = piece_placement_data[square_name]
        if FEN_PAWNS.get(piece.name) != self._active_color:
            self._append_token_and_set_error(match)
            return
        if not self.line_empty(destination, square_name):
            self._append_token_and_set_error(match)
            return
        new_en_passant_target_square = en_passant_target_squares[
            OTHER_SIDE[self._active_color]
        ].get((destination, piece.square.name), FEN_NULL)
        self._modify_game_state_pawn_move(
            ((piece.square.name, piece),),
            ((destination, piece),),
            fullmove_number_for_next_halfmove,
            new_en_passant_target_square,
        )
        if self.is_side_off_move_in_check():
            self.undo_board_state()
            self._append_token_and_set_error(match)
            return
        self._append_decorated_text(destination)
        self._full_disambiguation_detected = True

    def line_empty(self, square1, square2):
        """Return True if the squares between square1 and square2 are empty."""
        piece_placement_data = self._piece_placement_data
        ptp = fen_squares[square1].point_to_point.get(square2)
        if ptp is None:
            return True
        for sqr in ptp:
            if sqr in piece_placement_data:
                return False
        return True

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

    def get_all_movetext_in_pgn_export_format(self):
        """Return all movetext in pgn export format.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return movetext
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

    def get_archive_movetext(self):
        """Return Reduced Export format PGN movetext.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return movetext
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

    def get_movetext_without_comments_in_pgn_export_format(self):
        """Return movetext without comments in pgn export format.

        Where check or checkmate moves are present the text is not in export
        format unless generated by the GameIndicateCheck class, because these
        indicators are not included in the text otherwise.

        """
        fullmove_number, active_color = self._set_movetext_indicators()
        movetext = ["\n"]
        if self._movetext_offset is None:
            return movetext
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
