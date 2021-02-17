# test_game.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""game tests"""

import unittest
import re

from .. import game
from .. import constants
from .. import piece


class Game(unittest.TestCase):

    def setUp(self):
        self.match = re.match('(Ke4)', 'Ke4')

    def tearDown(self):
        del self.match

    def test_01___init__(self):
        self.assertRaisesRegex(
            TypeError,
            "__init__\(\) takes 1 positional argument but 2 were given",
            game.Game,
            *(None,),
            )

    def test_02___init__(self):
        ae = self.assertEqual
        g = game.Game()
        ae(isinstance(g, game.Game), True)
        ae(sorted(i for i in g.__dict__.items()),
           [('_error_list', []),
            ('_piece_placement_data', {}),
            ('_pieces_on_board', {}),
            ('_position_deltas', []),
            ('_ravstack', []),
            ('_state_stack', [None]),
            ('_tags', {}),
            ('_text', []),
            ])
        ae(game.Game._full_disambiguation_detected, False)
        ae(game.Game._active_color, None)
        ae(game.Game._castling_availability, None)
        ae(game.Game._en_passant_target_square, None)
        ae(game.Game._fullmove_number, None)
        ae(game.Game._halfmove_clock, None)
        ae(game.Game._movetext_offset, None)
        ae(game.Game._state, None)
        ae(g._full_disambiguation_detected, False)
        ae(g._active_color, None)
        ae(g._castling_availability, None)
        ae(g._en_passant_target_square, None)
        ae(g._fullmove_number, None)
        ae(g._halfmove_clock, None)
        ae(g._movetext_offset, None)
        ae(g._state, None)

    def test_03_set_game_error(self):
        ae = self.assertEqual
        g = game.Game()
        ae(g._state, None)
        g.set_game_error()
        ae(g._state, 0)
        ae(g.state, 0)

    def test_04_error_offset(self):
        ae = self.assertEqual
        g = game.Game()
        ae(g.state, None)

    def test_05_movetext_offset(self):
        ae = self.assertEqual
        g = game.Game()
        ae(g.movetext_offset, None)

    def test_06_append_token(self):
        ae = self.assertEqual
        g = game.Game()
        g._position_deltas.append('some position')
        ae(g._position_deltas, ['some position'])
        ae(g.append_token(self.match), None)
        ae(g._state, None)
        ae(g._text, ['Ke4'])
        ae(g._position_deltas, ['some position', 'some position'])

    def test_07__append_token_and_set_error(self):
        ae = self.assertEqual
        g = game.Game()
        ae(g.state, None)
        ae(g._append_token_and_set_error(self.match), None)
        ae(g.state, 0)
        ae(g._state, 0)
        ae(g._text, ['Ke4'])
        ae(g._position_deltas, [])
        ae(g._append_token_and_set_error(self.match), None)
        ae(g.state, 0)
        ae(g._state, 0)
        ae(g._text, ['Ke4', 'Ke4'])
        ae(g._position_deltas, [])

    def test_08__append_token_and_set_error(self):
        ae = self.assertEqual
        g = game.Game()
        g._position_deltas.append('some position')
        ae(g._position_deltas, ['some position'])
        ae(g.state, None)
        ae(g._append_token_and_set_error(self.match), None)
        ae(g.state, 0)
        ae(g._state, 0)
        ae(g._text, ['Ke4'])
        ae(g._position_deltas, ['some position', 'some position'])
        ae(g._append_token_and_set_error(self.match), None)
        ae(g.state, 0)
        ae(g._state, 0)
        ae(g._text, ['Ke4', 'Ke4'])
        ae(g._position_deltas,
           ['some position', 'some position', 'some position'])

    def test_09_append_token_and_set_error(self):
        ae = self.assertEqual
        g = game.Game()
        ae(g.state, None)

        ae(g.append_token_and_set_error(self.match), None)
        ae(g._state, 0)

        ae(g.state, 0)
        ae(g._state, 0)
        ae(g._text, ['Ke4'])
        ae(g._position_deltas, [])

    def test_10_append_other_or_disambiguation_pgn(self):
        ae = self.assertEqual
        g = game.Game()

        # Calls append_token_and_set_error.
        ae(g.append_other_or_disambiguation_pgn(self.match), None)
        ae(g._state, None)

    def test_11_append_other_or_disambiguation_pgn(self):
        ae = self.assertEqual
        g = game.Game()
        g._full_disambiguation_detected = True

        # Calls append_token_and_set_error.
        ae(g.append_other_or_disambiguation_pgn(self.match), None)
        ae(g._state, None)
        ae('_full_disambiguation_detected' in g.__dict__, False)
        ae(g._full_disambiguation_detected, False)

    def test_12_append_other_or_disambiguation_pgn(self):
        ae = self.assertEqual
        g = game.Game()
        g._full_disambiguation_detected = True
        ae(g.append_other_or_disambiguation_pgn(
            re.match(constants.DISAMBIGUATE_PGN, 'xc3')), None)
        ae(g._state, None)
        ae('_full_disambiguation_detected' in g.__dict__, False)
        ae(g._full_disambiguation_detected, False)

    def test_13_append_start_tag(self):
        ae = self.assertEqual
        g = game.Game()

        # Populate the referenced captured groups.
        match = re.match('(((Ke4)))', 'Ke4')

        ae(g.append_start_tag(match), None)
        ae(g._state, None)
        ae(g._position_deltas, [None])
        ae(g._tags, {'Ke4': 'Ke4'})

    def test_14_append_start_tag(self):
        ae = self.assertEqual
        g = game.Game()
        g._tags = {'Ke4': 'Ke4'}

        # Populate the referenced captured groups.
        match = re.match('(((Ke4)))', 'Ke4')

        ae(g.append_start_tag(match), None)
        ae(g._state, 0)
        ae(g._position_deltas, [None])
        ae(g._tags, {'Ke4': 'Ke4'})

    def test_15_append_start_tag(self):
        ae = self.assertEqual
        g = game.Game()

        # Populate the referenced captured groups.
        match = re.match('(((Ke4)))', 'Ke4')

        ae(g.append_start_tag(match), None)
        ae(g._state, None)
        ae(g._position_deltas, [None])
        ae(g._tags, {'Ke4': 'Ke4'})

    def test_16_ignore_escape(self):
        ae = self.assertEqual
        g = game.Game()
        ae(g.ignore_escape(self.match), None)
        ae(g._state, None)

    def test_17_ignore_move_number(self):
        ae = self.assertEqual
        g = game.Game()
        ae(g.ignore_move_number(self.match), None)
        ae(g._state, None)

    def test_18_ignore_dots(self):
        ae = self.assertEqual
        g = game.Game()
        ae(g.ignore_dots(self.match), None)
        ae(g._state, None)

    def test_19_remove_piece_on_square(self):
        ae = self.assertEqual
        g = game.Game()
        g._piece_placement_data['mmm'] = None
        ae(g.remove_piece_on_square(('mmm', None)), None)
        ae(g._piece_placement_data, {})

    def test_20_remove_piece_from_board(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('Q', 'c5')
        g._piece_placement_data['c5'] = p
        g._pieces_on_board['Q'] = []
        g._pieces_on_board['Q'].append(p)
        ae(g.remove_piece_from_board(('c5', None)), None)
        ae(g._piece_placement_data, {})
        ae(g._pieces_on_board['Q'], [])

    def test_21_remove_piece_from_board(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('P', 'c5')
        g._piece_placement_data['c5'] = p
        g._pieces_on_board['cP'] = []
        g._pieces_on_board['cP'].append(p)
        ae(g.remove_piece_from_board(('c5', None)), None)
        ae(g._piece_placement_data, {})
        ae(g._pieces_on_board['cP'], [])

    def test_22_remove_piece_from_board(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('p', 'c5')
        g._piece_placement_data['c5'] = p
        g._pieces_on_board['cp'] = []
        g._pieces_on_board['cp'].append(p)
        ae(g.remove_piece_from_board(('c5', None)), None)
        ae(g._piece_placement_data, {})
        ae(g._pieces_on_board['cp'], [])

    def test_23_remove_piece_from_board(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('r', 'c5')
        g._piece_placement_data['c5'] = p
        g._pieces_on_board['r'] = []
        self.assertRaisesRegex(
            game.GameError,
            "rc5 not in _pieces_on_board at square c5",
            g.remove_piece_from_board,
            *(('c5', None),),
            )
        ae(g._piece_placement_data, {'c5': p})
        ae(g._pieces_on_board['r'], [])

    def test_24_place_piece_on_square(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('p', 'c5')
        ae(g.place_piece_on_square(('c5', p)), None)
        ae(g._piece_placement_data, {'c5': p})

    def test_25_place_piece_on_board(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('Q', 'c5')
        g._pieces_on_board['Q'] = []
        ae(g.place_piece_on_board(('c5', p, 'Q')), None)
        ae(g._piece_placement_data, {'c5': p})
        ae(g._pieces_on_board['Q'], [p])

    def test_26_place_piece_on_board(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('P', 'c5')
        g._pieces_on_board['cP'] = []
        ae(g.place_piece_on_board(('c5', p, 'P')), None)
        ae(g._piece_placement_data, {'c5': p})
        ae(g._pieces_on_board['cP'], [p])

    def test_27_place_piece_on_board(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('p', 'c5')
        g._pieces_on_board['cp'] = []
        ae(g.place_piece_on_board(('c5', p, 'p')), None)
        ae(g._piece_placement_data, {'c5': p})
        ae(g._pieces_on_board['cp'], [p])

    def test_28_line_empty(self):
        ae = self.assertEqual
        g = game.Game()
        p = piece.Piece('p', 'c5')
        g._pieces_on_board['cp'] = []
        ae(g.place_piece_on_board(('c5', p, 'p')), None)
        ae(g.line_empty('a7', 'f5'), True)
        ae(g.line_empty('a7', 'a1'), True)
        ae(g.line_empty('a7', 'c5'), True)
        ae(g.line_empty('a7', 'e3'), False)

    def test_29_get_castling_options_after_move_applied(self):
        ae = self.assertEqual
        g = game.Game()
        g._castling_availability = constants.FEN_NULL
        ae(g.get_castling_options_after_move_applied('h1'), constants.FEN_NULL)
        ae(g.get_castling_options_after_move_applied('e1'), constants.FEN_NULL)
        ae(g.get_castling_options_after_move_applied('a1'), constants.FEN_NULL)
        ae(g.get_castling_options_after_move_applied('h8'), constants.FEN_NULL)
        ae(g.get_castling_options_after_move_applied('e8'), constants.FEN_NULL)
        ae(g.get_castling_options_after_move_applied('a8'), constants.FEN_NULL)
        ae(g.get_castling_options_after_move_applied('f4'), constants.FEN_NULL)

    def test_30_get_castling_options_after_move_applied(self):
        ae = self.assertEqual
        g = game.Game()
        g._castling_availability = 'Kk'
        ae(g.get_castling_options_after_move_applied((('h1',),)), 'k')
        ae(g.get_castling_options_after_move_applied((('e1',),)), 'k')
        ae(g.get_castling_options_after_move_applied((('a1',),)), 'Kk')
        ae(g.get_castling_options_after_move_applied((('h8',),)), 'K')
        ae(g.get_castling_options_after_move_applied((('e8',),)), 'K')
        ae(g.get_castling_options_after_move_applied((('a8',),)), 'Kk')
        ae(g.get_castling_options_after_move_applied((('f4',),)), 'Kk')

    def test_31_get_castling_options_after_move_applied(self):
        ae = self.assertEqual
        g = game.Game()
        g._castling_availability = 'KQ'
        ae(g.get_castling_options_after_move_applied((('h1',),)), 'Q')
        ae(g.get_castling_options_after_move_applied((('e1',),)), '-')
        ae(g.get_castling_options_after_move_applied((('a1',),)), 'K')
        ae(g.get_castling_options_after_move_applied((('h8',),)), 'KQ')
        ae(g.get_castling_options_after_move_applied((('e8',),)), 'KQ')
        ae(g.get_castling_options_after_move_applied((('a8',),)), 'KQ')
        ae(g.get_castling_options_after_move_applied((('f4',),)), 'KQ')

    def test_32_get_castling_options_after_move_applied(self):
        ae = self.assertEqual
        g = game.Game()
        g._castling_availability = 'KQkq'
        ae(g.get_castling_options_after_move_applied((('h1',),)), 'Qkq')
        ae(g.get_castling_options_after_move_applied((('e1',),)), 'kq')
        ae(g.get_castling_options_after_move_applied((('a1',),)), 'Kkq')
        ae(g.get_castling_options_after_move_applied((('h8',),)), 'KQq')
        ae(g.get_castling_options_after_move_applied((('e8',),)), 'KQ')
        ae(g.get_castling_options_after_move_applied((('a8',),)), 'KQk')
        ae(g.get_castling_options_after_move_applied((('f4',),)), 'KQkq')

    def test_33_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_34_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('P', 'g3')
        g._piece_placement_data['g3'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_35_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('P', 'g5')
        g._piece_placement_data['g5'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_36_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('Q', 'f7')
        g._piece_placement_data['f7'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_37_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('B', 'd6')
        g._piece_placement_data['d6'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_38_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('R', 'a4')
        g._piece_placement_data['a4'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_39_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('N', 'd3')
        g._piece_placement_data['d3'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_40_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('P', 'f3')
        g._piece_placement_data['f3'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_41_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('P', 'f2')
        g._piece_placement_data['f2'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_42_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('P', 'f5')
        g._piece_placement_data['f5'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_43_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_44_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('P', 'g3')
        g._piece_placement_data['g3'] = p
        ae(g.is_square_attacked_by_other_side('f4'), True)

    def test_45_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('P', 'g5')
        g._piece_placement_data['g5'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_46_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('Q', 'f7')
        g._piece_placement_data['f7'] = p
        ae(g.is_square_attacked_by_other_side('f4'), True)

    def test_47_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('B', 'd6')
        g._piece_placement_data['d6'] = p
        ae(g.is_square_attacked_by_other_side('f4'), True)

    def test_48_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('R', 'a4')
        g._piece_placement_data['a4'] = p
        ae(g.is_square_attacked_by_other_side('f4'), True)

    def test_49_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('N', 'd3')
        g._piece_placement_data['d3'] = p
        ae(g.is_square_attacked_by_other_side('f4'), True)

    def test_50_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('P', 'f3')
        g._piece_placement_data['f3'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_51_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('P', 'f2')
        g._piece_placement_data['f2'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_52_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('P', 'f5')
        g._piece_placement_data['f5'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_53_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'w'
        p = piece.Piece('Q', 'a7')
        g._piece_placement_data['a7'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)

    def test_54_is_square_attacked_by_other_side(self):
        ae = self.assertEqual
        g = game.Game()
        g._active_color = 'b'
        p = piece.Piece('Q', 'a7')
        g._piece_placement_data['a7'] = p
        ae(g.is_square_attacked_by_other_side('f4'), False)


class Ravstack(unittest.TestCase):

    def setUp(self):
        self.match = re.match('(Ke4)', 'Ke4')
        class RavstackGame(game.Game):
            def set_position_to_play_prior_right_nested_rav_at_move(self):
                pass
            def set_position_to_play_right_nested_rav_at_move(self):
                pass
            def set_position_to_play_main_line_at_move(self):
                pass
            def set_position_to_play_first_rav_at_move(self):
                pass
        self.rsgame = RavstackGame

    def tearDown(self):
        del self.match
        del self.rsgame

    def test_01_append_start_rav(self):
        ae = self.assertEqual
        g = self.rsgame()

        # Populate the referenced captured groups.
        match = re.match('(((((((((((((((Ke4)))))))))))))))', 'Ke4')

        ae(g.append_start_rav(match), None)
        ae(g._state, 0)

    def test_02_append_start_rav(self):
        ae = self.assertEqual
        g = self.rsgame()
        ae(g._movetext_offset, None)
        ae(g.append_start_rav(self.match), None)
        ae(g._state, 0)

    def test_03_append_end_rav(self):
        ae = self.assertEqual
        g = self.rsgame()

        # Populate the referenced captured groups.
        match = re.match('(((((((((((((((Ke4)))))))))))))))', 'Ke4')

        ae(g.append_end_rav(match), None)
        ae(g._state, 0)

    def test_04_append_end_rav(self):
        ae = self.assertEqual
        g = self.rsgame()
        ae(g._movetext_offset, None)
        ae(g.append_end_rav(self.match), None)
        ae(g._state, 0)

    def test_05_append_end_rav(self):
        ae = self.assertEqual
        g = self.rsgame()
        ae(g._ravstack, [])
        g._ravstack.append([0])
        g._movetext_offset = 1
        ae(g.append_end_rav(self.match), None)
        ae(g._state, 0)
        ae(g._ravstack, [[0]])

    def test_06_append_start_rav(self):
        ae = self.assertEqual
        g = self.rsgame()
        ae(g._ravstack, [])
        g._ravstack.append([0])
        g._position_deltas.append([None, ['a']])
        g._movetext_offset = 1
        ae(g.append_start_rav(self.match), None)
        ae(g._state, None)
        ae(g._ravstack, [[1], [0]])

    def test_07_append_start_end_rav_sequence(self):
        ae = self.assertEqual
        g = self.rsgame()
        g._ravstack.append([0])
        g._position_deltas.append([None, ['a']])
        g._movetext_offset = 1
        ae(g.append_start_rav(self.match), None)
        ae(g._state, None)
        g._ravstack[0] = [1, None, [None, 'w', None, None, None, 2],
                          [None, 'w', None, None, None, 2]]
        ae(g.append_end_rav(self.match), True)
        ae(g._state, None)

    def test_08_append_start_end_start_rav_sequence(self):
        ae = self.assertEqual
        g = self.rsgame()
        g._ravstack.append([0])
        g._position_deltas.append([None, ['a']])
        g._movetext_offset = 1
        ae(g.append_start_rav(self.match), None)
        ae(g._state, None)
        g._ravstack[0] = [1, None, [None, 'w', None, None, None, 2],
                          [None, 'w', None, None, None, 2]]
        ae(g.append_end_rav(self.match), True)
        ae(g._state, None)
        ae(g.append_start_rav(self.match), None)
        ae(g._state, None)
        ae(g._ravstack, [[2], [0]])


class Termination(unittest.TestCase):

    def setUp(self):
        self.match = re.match('(Ke4)', 'Ke4')
        class TerminationGameSIPTrue(game.Game):
            def set_initial_position(self):
                return True
        class TerminationGameSIPFalse(game.Game):
            def set_initial_position(self):
                return False
        self.tggametrue = TerminationGameSIPTrue
        self.tggamefalse = TerminationGameSIPFalse

    def test_01_append_game_termination(self):
        ae = self.assertEqual
        g = game.Game()
        g._movetext_offset = 1
        g._position_deltas.append(None)
        ae(g.append_game_termination(self.match), None)
        ae(g._state, None)
        ae(g._position_deltas, [None, None])
        ae(g._text, ['Ke4'])

    def test_02_append_game_termination(self):
        ae = self.assertEqual
        g = self.tggamefalse()
        ae(g.append_game_termination(self.match), None)
        ae(g._state, 0)
        ae(g._position_deltas, [])
        ae(g._text, ['Ke4'])

    def test_03_append_game_termination(self):
        ae = self.assertEqual
        g = self.tggametrue()
        g._position_deltas.append(None)
        ae(g.append_game_termination(self.match), None)
        ae(g._state, None)
        ae(g._position_deltas, [None, None])
        ae(g._text, ['Ke4'])
        ae(g._movetext_offset, 0)


class GenerateFENForPosition(unittest.TestCase):

    def test_01_generate_fen(self):
        ae = self.assertEqual
        ae(game.generate_fen_for_position(
            [piece.Piece(constants.FEN_WHITE_KING,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[6]),
             piece.Piece(constants.FEN_BLACK_KING,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[0]),
             piece.Piece(constants.FEN_WHITE_PAWN,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[5]),
             piece.Piece(constants.FEN_BLACK_PAWN,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[1]),
             ],
            'w',
            '-',
            '-',
            0,
            1),
           '4k3/4p3/8/8/8/4P3/4K3/8 w - - 0 1')

    def test_02_generate_fen(self):
        ae = self.assertEqual
        ae(game.generate_fen_for_position(
            [piece.Piece(constants.FEN_WHITE_KING,
                         constants.FILE_NAMES[7] + constants.RANK_NAMES[6]),
             piece.Piece(constants.FEN_BLACK_KING,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[0]),
             piece.Piece(constants.FEN_WHITE_PAWN,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[5]),
             piece.Piece(constants.FEN_BLACK_PAWN,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[1]),
             ],
            'w',
            '-',
            '-',
            0,
            1),
           '4k3/4p3/8/8/8/4P3/7K/8 w - - 0 1')

    def test_03_generate_fen(self):
        ae = self.assertEqual
        ae(game.generate_fen_for_position(
            [piece.Piece(constants.FEN_WHITE_KING,
                         constants.FILE_NAMES[7] + constants.RANK_NAMES[7]),
             piece.Piece(constants.FEN_BLACK_KING,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[0]),
             piece.Piece(constants.FEN_WHITE_PAWN,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[5]),
             piece.Piece(constants.FEN_BLACK_PAWN,
                         constants.FILE_NAMES[4] + constants.RANK_NAMES[1]),
             ],
            'w',
            '-',
            '-',
            0,
            1),
           '4k3/4p3/8/8/8/4P3/8/7K w - - 0 1')


if __name__ == '__main__':
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase

    runner().run(loader(Game))
    runner().run(loader(Ravstack))
    runner().run(loader(Termination))
    runner().run(loader(GenerateFENForPosition))
