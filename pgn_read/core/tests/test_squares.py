# test_squares.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""squares tests"""

import unittest

from .. import squares


class _Square(unittest.TestCase):

    def test_01___init__(self):
        self.assertRaisesRegex(
            TypeError,
            "".join((
                "__init__\(\) missing 2 required positional arguments: ",
                "'file' and 'rank'",
                )),
            squares._Square,
            )

    def test_02___init__(self):
        self.assertRaisesRegex(
            ValueError,
            "substring not found",
            squares._Square,
            (*'k3'),
            )
        self.assertRaisesRegex(
            ValueError,
            "substring not found",
            squares._Square,
            (*'a0'),
            )

    def test_03___init__(self):
        ae = self.assertEqual
        sq = squares._Square('b', '3')
        ae(isinstance(sq, squares._Square), True)
        ae(sq.castling_rights_lost, '')
        ae(sorted(sq.__dict__.keys()),
           ['bit',
            'file',
            'left_to_right_down_diagonal',
            'name',
            'number',
            'rank',
            'right_to_left_down_diagonal',
            ])

    def test_04___init__(self):
        ae = self.assertEqual
        sq = squares._Square('a', '1')
        ae(isinstance(sq, squares._Square), True)
        ae(sq.castling_rights_lost, 'Q')
        ae(sorted(sq.__dict__.keys()),
           ['bit',
            'castling_rights_lost',
            'file',
            'left_to_right_down_diagonal',
            'name',
            'number',
            'rank',
            'right_to_left_down_diagonal',
            ])

    def test_05___eq__(self):
        ae = self.assertEqual
        sq1 = squares._Square('a', '1')
        sq2 = squares._Square('a', '1')
        ae(sq1 == sq1, False)
        ae(sq1 == sq2, True)

    def test_06___eq__(self):
        ae = self.assertEqual
        sq1 = squares._Square('a', '1')
        sq2 = squares._Square('a', '2')
        ae(sq1 == sq2, True)

    def test_07___eq__(self):
        ae = self.assertEqual
        sq1 = squares._Square('a', '1')
        sq2 = squares._Square('f', '1')
        ae(sq1 == sq2, True)

    def test_08___eq__(self):
        ae = self.assertEqual
        sq1 = squares._Square('a', '1')
        sq2 = squares._Square('h', '8')
        ae(sq1 == sq2, True)

    def test_09___eq__(self):
        ae = self.assertEqual
        sq1 = squares._Square('a', '8')
        sq2 = squares._Square('h', '1')
        ae(sq1 == sq2, True)

    def test_10___eq__(self):
        ae = self.assertEqual
        sq1 = squares._Square('b', '1')
        sq2 = squares._Square('h', '8')
        ae(sq1 == sq2, False)

    def test_11___eq__(self):
        ae = self.assertEqual
        sq1 = squares._Square('b', '8')
        sq2 = squares._Square('h', '1')
        ae(sq1 == sq2, False)

    def test_12_number(self):
        ae = self.assertEqual
        sq = squares._Square
        ae(sq(*'a8').number, 0)
        ae(sq(*'b8').number, 1)
        ae(sq(*'c8').number, 2)
        ae(sq(*'d8').number, 3)
        ae(sq(*'e8').number, 4)
        ae(sq(*'f8').number, 5)
        ae(sq(*'g8').number, 6)
        ae(sq(*'h8').number, 7)
        ae(sq(*'a7').number, 8)
        ae(sq(*'b7').number, 9)
        ae(sq(*'c7').number, 10)
        ae(sq(*'d7').number, 11)
        ae(sq(*'e7').number, 12)
        ae(sq(*'f7').number, 13)
        ae(sq(*'g7').number, 14)
        ae(sq(*'h7').number, 15)
        ae(sq(*'a6').number, 16)
        ae(sq(*'b6').number, 17)
        ae(sq(*'c6').number, 18)
        ae(sq(*'d6').number, 19)
        ae(sq(*'e6').number, 20)
        ae(sq(*'f6').number, 21)
        ae(sq(*'g6').number, 22)
        ae(sq(*'h6').number, 23)
        ae(sq(*'a5').number, 24)
        ae(sq(*'b5').number, 25)
        ae(sq(*'c5').number, 26)
        ae(sq(*'d5').number, 27)
        ae(sq(*'e5').number, 28)
        ae(sq(*'f5').number, 29)
        ae(sq(*'g5').number, 30)
        ae(sq(*'h5').number, 31)
        ae(sq(*'a4').number, 32)
        ae(sq(*'b4').number, 33)
        ae(sq(*'c4').number, 34)
        ae(sq(*'d4').number, 35)
        ae(sq(*'e4').number, 36)
        ae(sq(*'f4').number, 37)
        ae(sq(*'g4').number, 38)
        ae(sq(*'h4').number, 39)
        ae(sq(*'a3').number, 40)
        ae(sq(*'b3').number, 41)
        ae(sq(*'c3').number, 42)
        ae(sq(*'d3').number, 43)
        ae(sq(*'e3').number, 44)
        ae(sq(*'f3').number, 45)
        ae(sq(*'g3').number, 46)
        ae(sq(*'h3').number, 47)
        ae(sq(*'a2').number, 48)
        ae(sq(*'b2').number, 49)
        ae(sq(*'c2').number, 50)
        ae(sq(*'d2').number, 51)
        ae(sq(*'e2').number, 52)
        ae(sq(*'f2').number, 53)
        ae(sq(*'g2').number, 54)
        ae(sq(*'h2').number, 55)
        ae(sq(*'a1').number, 56)
        ae(sq(*'b1').number, 57)
        ae(sq(*'c1').number, 58)
        ae(sq(*'d1').number, 59)
        ae(sq(*'e1').number, 60)
        ae(sq(*'f1').number, 61)
        ae(sq(*'g1').number, 62)
        ae(sq(*'h1').number, 63)

    def test_13_bit(self):
        ae = self.assertEqual
        sq = squares._Square
        ae(sq(*'a8').bit, 1 << 0)
        ae(sq(*'b8').bit, 1 << 1)
        ae(sq(*'c8').bit, 1 << 2)
        ae(sq(*'d8').bit, 1 << 3)
        ae(sq(*'e8').bit, 1 << 4)
        ae(sq(*'f8').bit, 1 << 5)
        ae(sq(*'g8').bit, 1 << 6)
        ae(sq(*'h8').bit, 1 << 7)
        ae(sq(*'a7').bit, 1 << 8)
        ae(sq(*'b7').bit, 1 << 9)
        ae(sq(*'c7').bit, 1 << 10)
        ae(sq(*'d7').bit, 1 << 11)
        ae(sq(*'e7').bit, 1 << 12)
        ae(sq(*'f7').bit, 1 << 13)
        ae(sq(*'g7').bit, 1 << 14)
        ae(sq(*'h7').bit, 1 << 15)
        ae(sq(*'a6').bit, 1 << 16)
        ae(sq(*'b6').bit, 1 << 17)
        ae(sq(*'c6').bit, 1 << 18)
        ae(sq(*'d6').bit, 1 << 19)
        ae(sq(*'e6').bit, 1 << 20)
        ae(sq(*'f6').bit, 1 << 21)
        ae(sq(*'g6').bit, 1 << 22)
        ae(sq(*'h6').bit, 1 << 23)
        ae(sq(*'a5').bit, 1 << 24)
        ae(sq(*'b5').bit, 1 << 25)
        ae(sq(*'c5').bit, 1 << 26)
        ae(sq(*'d5').bit, 1 << 27)
        ae(sq(*'e5').bit, 1 << 28)
        ae(sq(*'f5').bit, 1 << 29)
        ae(sq(*'g5').bit, 1 << 30)
        ae(sq(*'h5').bit, 1 << 31)
        ae(sq(*'a4').bit, 1 << 32)
        ae(sq(*'b4').bit, 1 << 33)
        ae(sq(*'c4').bit, 1 << 34)
        ae(sq(*'d4').bit, 1 << 35)
        ae(sq(*'e4').bit, 1 << 36)
        ae(sq(*'f4').bit, 1 << 37)
        ae(sq(*'g4').bit, 1 << 38)
        ae(sq(*'h4').bit, 1 << 39)
        ae(sq(*'a3').bit, 1 << 40)
        ae(sq(*'b3').bit, 1 << 41)
        ae(sq(*'c3').bit, 1 << 42)
        ae(sq(*'d3').bit, 1 << 43)
        ae(sq(*'e3').bit, 1 << 44)
        ae(sq(*'f3').bit, 1 << 45)
        ae(sq(*'g3').bit, 1 << 46)
        ae(sq(*'h3').bit, 1 << 47)
        ae(sq(*'a2').bit, 1 << 48)
        ae(sq(*'b2').bit, 1 << 49)
        ae(sq(*'c2').bit, 1 << 50)
        ae(sq(*'d2').bit, 1 << 51)
        ae(sq(*'e2').bit, 1 << 52)
        ae(sq(*'f2').bit, 1 << 53)
        ae(sq(*'g2').bit, 1 << 54)
        ae(sq(*'h2').bit, 1 << 55)
        ae(sq(*'a1').bit, 1 << 56)
        ae(sq(*'b1').bit, 1 << 57)
        ae(sq(*'c1').bit, 1 << 58)
        ae(sq(*'d1').bit, 1 << 59)
        ae(sq(*'e1').bit, 1 << 60)
        ae(sq(*'f1').bit, 1 << 61)
        ae(sq(*'g1').bit, 1 << 62)
        ae(sq(*'h1').bit, 1 << 63)


class Squares(unittest.TestCase):

    def test_01_Squares(self):
        ae = self.assertEqual
        ae(sorted(squares.Squares.__dict__.keys()), ['squares'])
        ae(len(squares.Squares.squares), 64)
        ae(sorted(sq for sq in squares.Squares.squares),
           ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8',
            'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8',
            'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8',
            'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8',
            'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8',
            'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8',
            ])
        for k, sq in squares.Squares.squares.items():
            ae(isinstance(sq, squares._Square), True)
            ae(k, sq.name)
            ae(sq.name, sq.file + sq.rank)
            ae(sq.left_to_right_down_diagonal,
               ord(sq.file) + ord(sq.rank))
            ae(sq.right_to_left_down_diagonal,
               ord(sq.file) - ord(sq.rank))
            if sq.name == 'a1':
                ae(sq.castling_rights_lost, 'Q')
            elif sq.name == 'e1':
                ae(sq.castling_rights_lost, 'KQ')
            elif sq.name == 'h1':
                ae(sq.castling_rights_lost, 'K')
            elif sq.name == 'a8':
                ae(sq.castling_rights_lost, 'q')
            elif sq.name == 'e8':
                ae(sq.castling_rights_lost, 'kq')
            elif sq.name == 'h8':
                ae(sq.castling_rights_lost, 'k')
            else:
                ae(sq.castling_rights_lost, '')


if __name__ == '__main__':
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase

    runner().run(loader(_Square))
    runner().run(loader(Squares))
