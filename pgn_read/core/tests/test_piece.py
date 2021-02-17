# test_piece.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""piece tests"""

import unittest

from .. import piece
from .. import squares


class Piece(unittest.TestCase):

    def test_01___init__(self):
        self.assertRaisesRegex(
            TypeError,
            "".join((
                "__init__\(\) missing 1 required positional argument: ",
                "'name'",
                )),
            piece.Piece,
            )

    def test_02___init__(self):
        self.assertRaisesRegex(
            TypeError,
            "".join((
                "set_square\(\) missing 1 required positional argument: ",
                "'a'",
                )),
            piece.Piece,
            *('x',),
            )

    def test_03___init__(self):
        self.assertRaisesRegex(
            KeyError,
            "'a'",
            piece.Piece,
            *('x', 'a'),
            )

    def test_04___init__(self):
        ae = self.assertEqual
        p = piece.Piece('x', 'a3')
        ae(isinstance(p, piece.Piece), True)
        ae(sorted(k for k in p.__dict__),
           ['color', 'identity', 'name', 'square']) 

    def test_05___init__(self):
        ae = self.assertEqual
        p = piece.Piece('K', 'a3')
        ae(p.name, 'K')
        ae(p.color, 'w')
        ae(p.identity, '40')
        ae(p.square.file, 'a')
        ae(p.square.rank, '3')
        ae(isinstance(p.square, squares._Square), True)

    def test_06___init__(self):
        ae = self.assertEqual
        p = piece.Piece('k', 'a3')
        ae(p.name, 'k')
        ae(p.color, 'b')
        ae(p.identity, '40')
        ae(isinstance(p.square, squares._Square), True)

    def test_07_promoted_pawn(self):
        ae = self.assertEqual
        p = piece.Piece('p', 'a2')
        pp = p.promoted_pawn('q', 'a1')
        ae(p.name, 'p')
        ae(p.color, 'b')
        ae(p.square.name, 'a2')
        ae(pp.name, 'q')
        ae(pp.color, 'b')
        ae(pp.square.name, 'a1')
        ae(p.identity, pp.identity)

    def test_08_set_square(self):
        ae = self.assertEqual
        p = piece.Piece('K', 'a3')
        sq1 = p.square
        p.set_square('e5')
        ae(p.square is not sq1, True)

    def test_09__str__(self):
        ae = self.assertEqual
        p = piece.Piece('K', 'a3')
        ae(str(p), 'Ka3')

    def test_10__eq__(self):
        ae = self.assertEqual
        p1 = piece.Piece('K', 'a3')
        p2 = piece.Piece('k', 'a3')
        p3 = piece.Piece('k', 'a4')
        p4 = piece.Piece('k', 'b3')
        p5 = piece.Piece('k', 'b4')
        ae(p1 == p2, True)
        ae(p1 == p3, False)
        ae(p1 == p4, False)
        ae(p1 == p5, False)

    def test_11__ge__(self):
        ae = self.assertEqual
        p1 = piece.Piece('K', 'a3')
        p2 = piece.Piece('k', 'a3')
        p3 = piece.Piece('k', 'a4')
        p4 = piece.Piece('k', 'b3')
        p5 = piece.Piece('k', 'b4')
        ae(p1 >= p2, True)
        ae(p1 >= p3, True)
        ae(p1 >= p4, False)
        ae(p1 >= p5, True)

    def test_12__gt__(self):
        ae = self.assertEqual
        p1 = piece.Piece('K', 'a3')
        p2 = piece.Piece('k', 'a3')
        p3 = piece.Piece('k', 'a4')
        p4 = piece.Piece('k', 'b3')
        p5 = piece.Piece('k', 'b4')
        ae(p1 > p2, False)
        ae(p1 > p3, True)
        ae(p1 > p4, False)
        ae(p1 > p5, True)

    def test_13__le__(self):
        ae = self.assertEqual
        p1 = piece.Piece('K', 'a3')
        p2 = piece.Piece('k', 'a3')
        p3 = piece.Piece('k', 'a4')
        p4 = piece.Piece('k', 'b3')
        p5 = piece.Piece('k', 'b4')
        ae(p1 <= p2, True)
        ae(p1 <= p3, False)
        ae(p1 <= p4, True)
        ae(p1 <= p5, False)

    def test_14__lt__(self):
        ae = self.assertEqual
        p1 = piece.Piece('K', 'a3')
        p2 = piece.Piece('k', 'a3')
        p3 = piece.Piece('k', 'a4')
        p4 = piece.Piece('k', 'b3')
        p5 = piece.Piece('k', 'b4')
        ae(p1 < p2, False)
        ae(p1 < p3, False)
        ae(p1 < p4, True)
        ae(p1 < p5, False)

    def test_18_key_str(self):
        ae = self.assertEqual
        p = piece.Piece('K', 'a3')
        ae(p.key_str, 'Ka3')

    def test_19_key_str(self):
        ae = self.assertEqual
        p = piece.Piece('k', 'a3')
        ae(p.key_str, 'ka3')

    def test_20_key_str(self):
        ae = self.assertEqual
        p = piece.Piece('P', 'a3')
        ae(p.key_str, 'A3')

    def test_21_key_str(self):
        ae = self.assertEqual
        p = piece.Piece('p', 'a3')
        ae(p.key_str, 'a3')


if __name__ == '__main__':
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase

    runner().run(loader(Piece))
