# test_squares.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""squares tests"""

import unittest

from .. import squares
from .. import constants


class _Square(unittest.TestCase):
    def test_01___init__(self):
        self.assertRaisesRegex(
            TypeError,
            "".join(
                (
                    r"__init__\(\) missing 2 required positional arguments: ",
                    "'file' and 'rank'$",
                )
            ),
            squares._Square,
        )

    def test_02___init__(self):
        self.assertRaisesRegex(
            ValueError,
            "substring not found$",
            squares._Square,
            *"k3",
        )
        self.assertRaisesRegex(
            ValueError,
            "substring not found$",
            squares._Square,
            *"a0",
        )

    def test_03___init__(self):
        ae = self.assertEqual
        sq = squares._Square("b", "3")
        ae(isinstance(sq, squares._Square), True)
        ae(sq.castling_rights_lost, "")
        ae(
            sorted(sq.__dict__.keys()),
            [
                "bit",
                "file",
                "high_file_attacks",
                "high_lrd_attacks",
                "high_rank_attacks",
                "high_rld_attacks",
                "highlow",
                "left_to_right_down_diagonal",
                "low_file_attacks",
                "low_lrd_attacks",
                "low_rank_attacks",
                "low_rld_attacks",
                "name",
                "number",
                "point_to_point",
                "rank",
                "right_to_left_down_diagonal",
            ],
        )

    def test_04___init__(self):
        ae = self.assertEqual
        sq = squares._Square("a", "1")
        ae(isinstance(sq, squares._Square), True)
        ae(sq.castling_rights_lost, "Q")
        ae(
            sorted(sq.__dict__.keys()),
            [
                "bit",
                "castling_rights_lost",
                "file",
                "high_file_attacks",
                "high_lrd_attacks",
                "high_rank_attacks",
                "high_rld_attacks",
                "highlow",
                "left_to_right_down_diagonal",
                "low_file_attacks",
                "low_lrd_attacks",
                "low_rank_attacks",
                "low_rld_attacks",
                "name",
                "number",
                "point_to_point",
                "rank",
                "right_to_left_down_diagonal",
            ],
        )

    def test_05_is_in_same_line(self):
        ae = self.assertEqual
        sq1 = squares._Square("a", "1")
        sq2 = squares._Square("a", "1")
        ae(sq1.is_in_same_line(sq1), False)
        ae(sq1.is_in_same_line(sq2), True)

    def test_06_is_in_same_line(self):
        ae = self.assertEqual
        sq1 = squares._Square("a", "1")
        sq2 = squares._Square("a", "2")
        ae(sq1.is_in_same_line(sq2), True)

    def test_07_is_in_same_line(self):
        ae = self.assertEqual
        sq1 = squares._Square("a", "1")
        sq2 = squares._Square("f", "1")
        ae(sq1.is_in_same_line(sq2), True)

    def test_08_is_in_same_line(self):
        ae = self.assertEqual
        sq1 = squares._Square("a", "1")
        sq2 = squares._Square("h", "8")
        ae(sq1.is_in_same_line(sq2), True)

    def test_09_is_in_same_line(self):
        ae = self.assertEqual
        sq1 = squares._Square("a", "8")
        sq2 = squares._Square("h", "1")
        ae(sq1.is_in_same_line(sq2), True)

    def test_10_is_in_same_line(self):
        ae = self.assertEqual
        sq1 = squares._Square("b", "1")
        sq2 = squares._Square("h", "8")
        ae(sq1.is_in_same_line(sq2), False)

    def test_11_is_in_same_line(self):
        ae = self.assertEqual
        sq1 = squares._Square("b", "8")
        sq2 = squares._Square("h", "1")
        ae(sq1.is_in_same_line(sq2), False)

    def test_12_number(self):
        ae = self.assertEqual
        sq = squares._Square
        ae(sq(*"a8").number, 0)
        ae(sq(*"b8").number, 1)
        ae(sq(*"c8").number, 2)
        ae(sq(*"d8").number, 3)
        ae(sq(*"e8").number, 4)
        ae(sq(*"f8").number, 5)
        ae(sq(*"g8").number, 6)
        ae(sq(*"h8").number, 7)
        ae(sq(*"a7").number, 8)
        ae(sq(*"b7").number, 9)
        ae(sq(*"c7").number, 10)
        ae(sq(*"d7").number, 11)
        ae(sq(*"e7").number, 12)
        ae(sq(*"f7").number, 13)
        ae(sq(*"g7").number, 14)
        ae(sq(*"h7").number, 15)
        ae(sq(*"a6").number, 16)
        ae(sq(*"b6").number, 17)
        ae(sq(*"c6").number, 18)
        ae(sq(*"d6").number, 19)
        ae(sq(*"e6").number, 20)
        ae(sq(*"f6").number, 21)
        ae(sq(*"g6").number, 22)
        ae(sq(*"h6").number, 23)
        ae(sq(*"a5").number, 24)
        ae(sq(*"b5").number, 25)
        ae(sq(*"c5").number, 26)
        ae(sq(*"d5").number, 27)
        ae(sq(*"e5").number, 28)
        ae(sq(*"f5").number, 29)
        ae(sq(*"g5").number, 30)
        ae(sq(*"h5").number, 31)
        ae(sq(*"a4").number, 32)
        ae(sq(*"b4").number, 33)
        ae(sq(*"c4").number, 34)
        ae(sq(*"d4").number, 35)
        ae(sq(*"e4").number, 36)
        ae(sq(*"f4").number, 37)
        ae(sq(*"g4").number, 38)
        ae(sq(*"h4").number, 39)
        ae(sq(*"a3").number, 40)
        ae(sq(*"b3").number, 41)
        ae(sq(*"c3").number, 42)
        ae(sq(*"d3").number, 43)
        ae(sq(*"e3").number, 44)
        ae(sq(*"f3").number, 45)
        ae(sq(*"g3").number, 46)
        ae(sq(*"h3").number, 47)
        ae(sq(*"a2").number, 48)
        ae(sq(*"b2").number, 49)
        ae(sq(*"c2").number, 50)
        ae(sq(*"d2").number, 51)
        ae(sq(*"e2").number, 52)
        ae(sq(*"f2").number, 53)
        ae(sq(*"g2").number, 54)
        ae(sq(*"h2").number, 55)
        ae(sq(*"a1").number, 56)
        ae(sq(*"b1").number, 57)
        ae(sq(*"c1").number, 58)
        ae(sq(*"d1").number, 59)
        ae(sq(*"e1").number, 60)
        ae(sq(*"f1").number, 61)
        ae(sq(*"g1").number, 62)
        ae(sq(*"h1").number, 63)

    def test_13_bit(self):
        ae = self.assertEqual
        sq = squares._Square
        ae(sq(*"a8").bit, 1 << 0)
        ae(sq(*"b8").bit, 1 << 1)
        ae(sq(*"c8").bit, 1 << 2)
        ae(sq(*"d8").bit, 1 << 3)
        ae(sq(*"e8").bit, 1 << 4)
        ae(sq(*"f8").bit, 1 << 5)
        ae(sq(*"g8").bit, 1 << 6)
        ae(sq(*"h8").bit, 1 << 7)
        ae(sq(*"a7").bit, 1 << 8)
        ae(sq(*"b7").bit, 1 << 9)
        ae(sq(*"c7").bit, 1 << 10)
        ae(sq(*"d7").bit, 1 << 11)
        ae(sq(*"e7").bit, 1 << 12)
        ae(sq(*"f7").bit, 1 << 13)
        ae(sq(*"g7").bit, 1 << 14)
        ae(sq(*"h7").bit, 1 << 15)
        ae(sq(*"a6").bit, 1 << 16)
        ae(sq(*"b6").bit, 1 << 17)
        ae(sq(*"c6").bit, 1 << 18)
        ae(sq(*"d6").bit, 1 << 19)
        ae(sq(*"e6").bit, 1 << 20)
        ae(sq(*"f6").bit, 1 << 21)
        ae(sq(*"g6").bit, 1 << 22)
        ae(sq(*"h6").bit, 1 << 23)
        ae(sq(*"a5").bit, 1 << 24)
        ae(sq(*"b5").bit, 1 << 25)
        ae(sq(*"c5").bit, 1 << 26)
        ae(sq(*"d5").bit, 1 << 27)
        ae(sq(*"e5").bit, 1 << 28)
        ae(sq(*"f5").bit, 1 << 29)
        ae(sq(*"g5").bit, 1 << 30)
        ae(sq(*"h5").bit, 1 << 31)
        ae(sq(*"a4").bit, 1 << 32)
        ae(sq(*"b4").bit, 1 << 33)
        ae(sq(*"c4").bit, 1 << 34)
        ae(sq(*"d4").bit, 1 << 35)
        ae(sq(*"e4").bit, 1 << 36)
        ae(sq(*"f4").bit, 1 << 37)
        ae(sq(*"g4").bit, 1 << 38)
        ae(sq(*"h4").bit, 1 << 39)
        ae(sq(*"a3").bit, 1 << 40)
        ae(sq(*"b3").bit, 1 << 41)
        ae(sq(*"c3").bit, 1 << 42)
        ae(sq(*"d3").bit, 1 << 43)
        ae(sq(*"e3").bit, 1 << 44)
        ae(sq(*"f3").bit, 1 << 45)
        ae(sq(*"g3").bit, 1 << 46)
        ae(sq(*"h3").bit, 1 << 47)
        ae(sq(*"a2").bit, 1 << 48)
        ae(sq(*"b2").bit, 1 << 49)
        ae(sq(*"c2").bit, 1 << 50)
        ae(sq(*"d2").bit, 1 << 51)
        ae(sq(*"e2").bit, 1 << 52)
        ae(sq(*"f2").bit, 1 << 53)
        ae(sq(*"g2").bit, 1 << 54)
        ae(sq(*"h2").bit, 1 << 55)
        ae(sq(*"a1").bit, 1 << 56)
        ae(sq(*"b1").bit, 1 << 57)
        ae(sq(*"c1").bit, 1 << 58)
        ae(sq(*"d1").bit, 1 << 59)
        ae(sq(*"e1").bit, 1 << 60)
        ae(sq(*"f1").bit, 1 << 61)
        ae(sq(*"g1").bit, 1 << 62)
        ae(sq(*"h1").bit, 1 << 63)

    def test_14_highlow(self):
        ae = self.assertEqual
        sq = squares._Square
        ae(sq(*"a8").highlow, 56)
        ae(sq(*"b8").highlow, 57)
        ae(sq(*"c8").highlow, 58)
        ae(sq(*"d8").highlow, 59)
        ae(sq(*"e8").highlow, 60)
        ae(sq(*"f8").highlow, 61)
        ae(sq(*"g8").highlow, 62)
        ae(sq(*"h8").highlow, 63)
        ae(sq(*"a7").highlow, 48)
        ae(sq(*"b7").highlow, 49)
        ae(sq(*"c7").highlow, 50)
        ae(sq(*"d7").highlow, 51)
        ae(sq(*"e7").highlow, 52)
        ae(sq(*"f7").highlow, 53)
        ae(sq(*"g7").highlow, 54)
        ae(sq(*"h7").highlow, 55)
        ae(sq(*"a6").highlow, 40)
        ae(sq(*"b6").highlow, 41)
        ae(sq(*"c6").highlow, 42)
        ae(sq(*"d6").highlow, 43)
        ae(sq(*"e6").highlow, 44)
        ae(sq(*"f6").highlow, 45)
        ae(sq(*"g6").highlow, 46)
        ae(sq(*"h6").highlow, 47)
        ae(sq(*"a5").highlow, 32)
        ae(sq(*"b5").highlow, 33)
        ae(sq(*"c5").highlow, 34)
        ae(sq(*"d5").highlow, 35)
        ae(sq(*"e5").highlow, 36)
        ae(sq(*"f5").highlow, 37)
        ae(sq(*"g5").highlow, 38)
        ae(sq(*"h5").highlow, 39)
        ae(sq(*"a4").highlow, 24)
        ae(sq(*"b4").highlow, 25)
        ae(sq(*"c4").highlow, 26)
        ae(sq(*"d4").highlow, 27)
        ae(sq(*"e4").highlow, 28)
        ae(sq(*"f4").highlow, 29)
        ae(sq(*"g4").highlow, 30)
        ae(sq(*"h4").highlow, 31)
        ae(sq(*"a3").highlow, 16)
        ae(sq(*"b3").highlow, 17)
        ae(sq(*"c3").highlow, 18)
        ae(sq(*"d3").highlow, 19)
        ae(sq(*"e3").highlow, 20)
        ae(sq(*"f3").highlow, 21)
        ae(sq(*"g3").highlow, 22)
        ae(sq(*"h3").highlow, 23)
        ae(sq(*"a2").highlow, 8)
        ae(sq(*"b2").highlow, 9)
        ae(sq(*"c2").highlow, 10)
        ae(sq(*"d2").highlow, 11)
        ae(sq(*"e2").highlow, 12)
        ae(sq(*"f2").highlow, 13)
        ae(sq(*"g2").highlow, 14)
        ae(sq(*"h2").highlow, 15)
        ae(sq(*"a1").highlow, 0)
        ae(sq(*"b1").highlow, 1)
        ae(sq(*"c1").highlow, 2)
        ae(sq(*"d1").highlow, 3)
        ae(sq(*"e1").highlow, 4)
        ae(sq(*"f1").highlow, 5)
        ae(sq(*"g1").highlow, 6)
        ae(sq(*"h1").highlow, 7)


class Squares(unittest.TestCase):
    def test_01_Squares(self):
        ae = self.assertEqual
        ae(len(squares.fen_squares), 64)
        ae(
            sorted(sq for sq in squares.fen_squares),
            [
                "a1",
                "a2",
                "a3",
                "a4",
                "a5",
                "a6",
                "a7",
                "a8",
                "b1",
                "b2",
                "b3",
                "b4",
                "b5",
                "b6",
                "b7",
                "b8",
                "c1",
                "c2",
                "c3",
                "c4",
                "c5",
                "c6",
                "c7",
                "c8",
                "d1",
                "d2",
                "d3",
                "d4",
                "d5",
                "d6",
                "d7",
                "d8",
                "e1",
                "e2",
                "e3",
                "e4",
                "e5",
                "e6",
                "e7",
                "e8",
                "f1",
                "f2",
                "f3",
                "f4",
                "f5",
                "f6",
                "f7",
                "f8",
                "g1",
                "g2",
                "g3",
                "g4",
                "g5",
                "g6",
                "g7",
                "g8",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "h7",
                "h8",
            ],
        )
        for k, sq in squares.fen_squares.items():
            ae(isinstance(sq, squares._Square), True)
            ae(k, sq.name)
            ae(sq.name, sq.file + sq.rank)
            ae(sq.left_to_right_down_diagonal, ord(sq.file) + ord(sq.rank))
            ae(sq.right_to_left_down_diagonal, ord(sq.file) - ord(sq.rank))
            if sq.name == "a1":
                ae(sq.castling_rights_lost, "Q")
            elif sq.name == "e1":
                ae(sq.castling_rights_lost, "KQ")
            elif sq.name == "h1":
                ae(sq.castling_rights_lost, "K")
            elif sq.name == "a8":
                ae(sq.castling_rights_lost, "q")
            elif sq.name == "e8":
                ae(sq.castling_rights_lost, "kq")
            elif sq.name == "h8":
                ae(sq.castling_rights_lost, "k")
            else:
                ae(sq.castling_rights_lost, "")

    def test_02_Squares(self):
        ae = self.assertEqual
        ae(len(squares.fen_square_names), 64)
        ae(
            squares.fen_square_names,
            {
                0: "a8",
                1: "b8",
                2: "c8",
                3: "d8",
                4: "e8",
                5: "f8",
                6: "g8",
                7: "h8",
                8: "a7",
                9: "b7",
                10: "c7",
                11: "d7",
                12: "e7",
                13: "f7",
                14: "g7",
                15: "h7",
                16: "a6",
                17: "b6",
                18: "c6",
                19: "d6",
                20: "e6",
                21: "f6",
                22: "g6",
                23: "h6",
                24: "a5",
                25: "b5",
                26: "c5",
                27: "d5",
                28: "e5",
                29: "f5",
                30: "g5",
                31: "h5",
                32: "a4",
                33: "b4",
                34: "c4",
                35: "d4",
                36: "e4",
                37: "f4",
                38: "g4",
                39: "h4",
                40: "a3",
                41: "b3",
                42: "c3",
                43: "d3",
                44: "e3",
                45: "f3",
                46: "g3",
                47: "h3",
                48: "a2",
                49: "b2",
                50: "c2",
                51: "d2",
                52: "e2",
                53: "f2",
                54: "g2",
                55: "h2",
                56: "a1",
                57: "b1",
                58: "c1",
                59: "d1",
                60: "e1",
                61: "f1",
                62: "g1",
                63: "h1",
            },
        )

    def test_03_Squares(self):
        ae = self.assertEqual
        for sq in squares.fen_squares.values():
            ae(sq.attack_line(sq), None)

    def test_04_Squares(self):
        ae = self.assertEqual
        for sq1 in squares.fen_squares.values():
            for sq2 in squares.fen_squares.values():
                if sq1.rank == sq2.rank and sq1 is not sq2:
                    ae(sq1.attack_line(sq2) is not None, True)

    def test_05_Squares(self):
        ae = self.assertEqual
        for sq1 in squares.fen_squares.values():
            for sq2 in squares.fen_squares.values():
                if sq1.file == sq2.file and sq1 is not sq2:
                    ae(sq1.attack_line(sq2) is not None, True)

    def test_06_Squares(self):
        ae = self.assertEqual
        for sq1 in squares.fen_squares.values():
            for sq2 in squares.fen_squares.values():
                if (
                    sq1.left_to_right_down_diagonal
                    == sq2.left_to_right_down_diagonal
                ) and sq1 is not sq2:
                    ae(sq1.attack_line(sq2) is not None, True)

    def test_07_Squares(self):
        ae = self.assertEqual
        for sq1 in squares.fen_squares.values():
            for sq2 in squares.fen_squares.values():
                if (
                    sq1.right_to_left_down_diagonal
                    == sq2.right_to_left_down_diagonal
                ) and sq1 is not sq2:
                    ae(sq1.attack_line(sq2) is not None, True)

    def test_08_Squares(self):
        ae = self.assertEqual
        for sq1 in squares.fen_squares.values():
            for sq2 in squares.fen_squares.values():
                if not sq1.is_in_same_line(sq2):
                    ae(sq1.attack_line(sq2) is None, True)

    def test_09_Squares(self):
        ae = self.assertEqual
        sss = squares.fen_squares
        ae(
            sss["c4"].attack_line(sss["b4"]),
            (("b4", "a4"), ("d4", "e4", "f4", "g4", "h4")),
        )
        ae(
            sss["c4"].attack_line(sss["b5"]),
            (("d3", "e2", "f1"), ("b5", "a6")),
        )
        ae(
            sss["c4"].attack_line(sss["c5"]),
            (("c3", "c2", "c1"), ("c5", "c6", "c7", "c8")),
        )
        ae(
            sss["c4"].attack_line(sss["d5"]),
            (("b3", "a2"), ("d5", "e6", "f7", "g8")),
        )
        ae(
            sss["c4"].attack_line(sss["d4"]),
            (("b4", "a4"), ("d4", "e4", "f4", "g4", "h4")),
        )
        ae(
            sss["c4"].attack_line(sss["d3"]),
            (("d3", "e2", "f1"), ("b5", "a6")),
        )
        ae(
            sss["c4"].attack_line(sss["c3"]),
            (("c3", "c2", "c1"), ("c5", "c6", "c7", "c8")),
        )
        ae(
            sss["c4"].attack_line(sss["b3"]),
            (("b3", "a2"), ("d5", "e6", "f7", "g8")),
        )

    def test_10_Squares(self):
        ae = self.assertEqual
        sss = squares.fen_squares
        ae(sss["a1"].low_file_attacks, ())
        ae(sss["a2"].low_file_attacks, ("a1",))
        ae(sss["a3"].low_file_attacks, ("a2", "a1"))
        ae(sss["a4"].low_file_attacks, ("a3", "a2", "a1"))
        ae(sss["a5"].low_file_attacks, ("a4", "a3", "a2", "a1"))
        ae(sss["a6"].low_file_attacks, ("a5", "a4", "a3", "a2", "a1"))
        ae(sss["a7"].low_file_attacks, ("a6", "a5", "a4", "a3", "a2", "a1"))
        ae(
            sss["a8"].low_file_attacks,
            ("a7", "a6", "a5", "a4", "a3", "a2", "a1"),
        )
        ae(sss["b1"].low_file_attacks, ())
        ae(sss["b2"].low_file_attacks, ("b1",))
        ae(sss["b3"].low_file_attacks, ("b2", "b1"))
        ae(sss["b4"].low_file_attacks, ("b3", "b2", "b1"))
        ae(sss["b5"].low_file_attacks, ("b4", "b3", "b2", "b1"))
        ae(sss["b6"].low_file_attacks, ("b5", "b4", "b3", "b2", "b1"))
        ae(sss["b7"].low_file_attacks, ("b6", "b5", "b4", "b3", "b2", "b1"))
        ae(
            sss["b8"].low_file_attacks,
            ("b7", "b6", "b5", "b4", "b3", "b2", "b1"),
        )
        ae(sss["c1"].low_file_attacks, ())
        ae(sss["c2"].low_file_attacks, ("c1",))
        ae(sss["c3"].low_file_attacks, ("c2", "c1"))
        ae(sss["c4"].low_file_attacks, ("c3", "c2", "c1"))
        ae(sss["c5"].low_file_attacks, ("c4", "c3", "c2", "c1"))
        ae(sss["c6"].low_file_attacks, ("c5", "c4", "c3", "c2", "c1"))
        ae(sss["c7"].low_file_attacks, ("c6", "c5", "c4", "c3", "c2", "c1"))
        ae(
            sss["c8"].low_file_attacks,
            ("c7", "c6", "c5", "c4", "c3", "c2", "c1"),
        )
        ae(sss["d1"].low_file_attacks, ())
        ae(sss["d2"].low_file_attacks, ("d1",))
        ae(sss["d3"].low_file_attacks, ("d2", "d1"))
        ae(sss["d4"].low_file_attacks, ("d3", "d2", "d1"))
        ae(sss["d5"].low_file_attacks, ("d4", "d3", "d2", "d1"))
        ae(sss["d6"].low_file_attacks, ("d5", "d4", "d3", "d2", "d1"))
        ae(sss["d7"].low_file_attacks, ("d6", "d5", "d4", "d3", "d2", "d1"))
        ae(
            sss["d8"].low_file_attacks,
            ("d7", "d6", "d5", "d4", "d3", "d2", "d1"),
        )
        ae(sss["e1"].low_file_attacks, ())
        ae(sss["e2"].low_file_attacks, ("e1",))
        ae(sss["e3"].low_file_attacks, ("e2", "e1"))
        ae(sss["e4"].low_file_attacks, ("e3", "e2", "e1"))
        ae(sss["e5"].low_file_attacks, ("e4", "e3", "e2", "e1"))
        ae(sss["e6"].low_file_attacks, ("e5", "e4", "e3", "e2", "e1"))
        ae(sss["e7"].low_file_attacks, ("e6", "e5", "e4", "e3", "e2", "e1"))
        ae(
            sss["e8"].low_file_attacks,
            ("e7", "e6", "e5", "e4", "e3", "e2", "e1"),
        )
        ae(sss["f1"].low_file_attacks, ())
        ae(sss["f2"].low_file_attacks, ("f1",))
        ae(sss["f3"].low_file_attacks, ("f2", "f1"))
        ae(sss["f4"].low_file_attacks, ("f3", "f2", "f1"))
        ae(sss["f5"].low_file_attacks, ("f4", "f3", "f2", "f1"))
        ae(sss["f6"].low_file_attacks, ("f5", "f4", "f3", "f2", "f1"))
        ae(sss["f7"].low_file_attacks, ("f6", "f5", "f4", "f3", "f2", "f1"))
        ae(
            sss["f8"].low_file_attacks,
            ("f7", "f6", "f5", "f4", "f3", "f2", "f1"),
        )
        ae(sss["g1"].low_file_attacks, ())
        ae(sss["g2"].low_file_attacks, ("g1",))
        ae(sss["g3"].low_file_attacks, ("g2", "g1"))
        ae(sss["g4"].low_file_attacks, ("g3", "g2", "g1"))
        ae(sss["g5"].low_file_attacks, ("g4", "g3", "g2", "g1"))
        ae(sss["g6"].low_file_attacks, ("g5", "g4", "g3", "g2", "g1"))
        ae(sss["g7"].low_file_attacks, ("g6", "g5", "g4", "g3", "g2", "g1"))
        ae(
            sss["g8"].low_file_attacks,
            ("g7", "g6", "g5", "g4", "g3", "g2", "g1"),
        )
        ae(
            sss["h1"].low_file_attacks,
            (),
        )
        ae(sss["h2"].low_file_attacks, ("h1",))
        ae(sss["h3"].low_file_attacks, ("h2", "h1"))
        ae(sss["h4"].low_file_attacks, ("h3", "h2", "h1"))
        ae(sss["h5"].low_file_attacks, ("h4", "h3", "h2", "h1"))
        ae(sss["h6"].low_file_attacks, ("h5", "h4", "h3", "h2", "h1"))
        ae(sss["h7"].low_file_attacks, ("h6", "h5", "h4", "h3", "h2", "h1"))
        ae(
            sss["h8"].low_file_attacks,
            ("h7", "h6", "h5", "h4", "h3", "h2", "h1"),
        )
        ae(
            sss["a1"].high_file_attacks,
            ("a2", "a3", "a4", "a5", "a6", "a7", "a8"),
        )
        ae(sss["a2"].high_file_attacks, ("a3", "a4", "a5", "a6", "a7", "a8"))
        ae(sss["a3"].high_file_attacks, ("a4", "a5", "a6", "a7", "a8"))
        ae(sss["a4"].high_file_attacks, ("a5", "a6", "a7", "a8"))
        ae(sss["a5"].high_file_attacks, ("a6", "a7", "a8"))
        ae(sss["a6"].high_file_attacks, ("a7", "a8"))
        ae(sss["a7"].high_file_attacks, ("a8",))
        ae(sss["a8"].high_file_attacks, ())
        ae(
            sss["b1"].high_file_attacks,
            ("b2", "b3", "b4", "b5", "b6", "b7", "b8"),
        )
        ae(sss["b2"].high_file_attacks, ("b3", "b4", "b5", "b6", "b7", "b8"))
        ae(sss["b3"].high_file_attacks, ("b4", "b5", "b6", "b7", "b8"))
        ae(sss["b4"].high_file_attacks, ("b5", "b6", "b7", "b8"))
        ae(sss["b5"].high_file_attacks, ("b6", "b7", "b8"))
        ae(sss["b6"].high_file_attacks, ("b7", "b8"))
        ae(sss["b7"].high_file_attacks, ("b8",))
        ae(sss["b8"].high_file_attacks, ())
        ae(
            sss["c1"].high_file_attacks,
            ("c2", "c3", "c4", "c5", "c6", "c7", "c8"),
        )
        ae(sss["c2"].high_file_attacks, ("c3", "c4", "c5", "c6", "c7", "c8"))
        ae(sss["c3"].high_file_attacks, ("c4", "c5", "c6", "c7", "c8"))
        ae(sss["c4"].high_file_attacks, ("c5", "c6", "c7", "c8"))
        ae(sss["c5"].high_file_attacks, ("c6", "c7", "c8"))
        ae(sss["c6"].high_file_attacks, ("c7", "c8"))
        ae(sss["c7"].high_file_attacks, ("c8",))
        ae(sss["c8"].high_file_attacks, ())
        ae(
            sss["d1"].high_file_attacks,
            ("d2", "d3", "d4", "d5", "d6", "d7", "d8"),
        )
        ae(sss["d2"].high_file_attacks, ("d3", "d4", "d5", "d6", "d7", "d8"))
        ae(sss["d3"].high_file_attacks, ("d4", "d5", "d6", "d7", "d8"))
        ae(sss["d4"].high_file_attacks, ("d5", "d6", "d7", "d8"))
        ae(sss["d5"].high_file_attacks, ("d6", "d7", "d8"))
        ae(sss["d6"].high_file_attacks, ("d7", "d8"))
        ae(sss["d7"].high_file_attacks, ("d8",))
        ae(sss["d8"].high_file_attacks, ())
        ae(
            sss["e1"].high_file_attacks,
            ("e2", "e3", "e4", "e5", "e6", "e7", "e8"),
        )
        ae(sss["e2"].high_file_attacks, ("e3", "e4", "e5", "e6", "e7", "e8"))
        ae(sss["e3"].high_file_attacks, ("e4", "e5", "e6", "e7", "e8"))
        ae(sss["e4"].high_file_attacks, ("e5", "e6", "e7", "e8"))
        ae(sss["e5"].high_file_attacks, ("e6", "e7", "e8"))
        ae(sss["e6"].high_file_attacks, ("e7", "e8"))
        ae(sss["e7"].high_file_attacks, ("e8",))
        ae(sss["e8"].high_file_attacks, ())
        ae(
            sss["f1"].high_file_attacks,
            ("f2", "f3", "f4", "f5", "f6", "f7", "f8"),
        )
        ae(sss["f2"].high_file_attacks, ("f3", "f4", "f5", "f6", "f7", "f8"))
        ae(sss["f3"].high_file_attacks, ("f4", "f5", "f6", "f7", "f8"))
        ae(sss["f4"].high_file_attacks, ("f5", "f6", "f7", "f8"))
        ae(sss["f5"].high_file_attacks, ("f6", "f7", "f8"))
        ae(sss["f6"].high_file_attacks, ("f7", "f8"))
        ae(sss["f7"].high_file_attacks, ("f8",))
        ae(sss["f8"].high_file_attacks, ())
        ae(
            sss["g1"].high_file_attacks,
            ("g2", "g3", "g4", "g5", "g6", "g7", "g8"),
        )
        ae(sss["g2"].high_file_attacks, ("g3", "g4", "g5", "g6", "g7", "g8"))
        ae(sss["g3"].high_file_attacks, ("g4", "g5", "g6", "g7", "g8"))
        ae(sss["g4"].high_file_attacks, ("g5", "g6", "g7", "g8"))
        ae(sss["g5"].high_file_attacks, ("g6", "g7", "g8"))
        ae(sss["g6"].high_file_attacks, ("g7", "g8"))
        ae(sss["g7"].high_file_attacks, ("g8",))
        ae(sss["g8"].high_file_attacks, ())
        ae(
            sss["h1"].high_file_attacks,
            ("h2", "h3", "h4", "h5", "h6", "h7", "h8"),
        )
        ae(sss["h2"].high_file_attacks, ("h3", "h4", "h5", "h6", "h7", "h8"))
        ae(sss["h3"].high_file_attacks, ("h4", "h5", "h6", "h7", "h8"))
        ae(sss["h4"].high_file_attacks, ("h5", "h6", "h7", "h8"))
        ae(sss["h5"].high_file_attacks, ("h6", "h7", "h8"))
        ae(sss["h6"].high_file_attacks, ("h7", "h8"))
        ae(sss["h7"].high_file_attacks, ("h8",))
        ae(sss["h8"].high_file_attacks, ())
        ae(sss["a1"].low_lrd_attacks, ())
        ae(sss["a2"].low_lrd_attacks, ("b1",))
        ae(sss["a3"].low_lrd_attacks, ("b2", "c1"))
        ae(sss["a4"].low_lrd_attacks, ("b3", "c2", "d1"))
        ae(sss["a5"].low_lrd_attacks, ("b4", "c3", "d2", "e1"))
        ae(sss["a6"].low_lrd_attacks, ("b5", "c4", "d3", "e2", "f1"))
        ae(sss["a7"].low_lrd_attacks, ("b6", "c5", "d4", "e3", "f2", "g1"))
        ae(
            sss["a8"].low_lrd_attacks,
            ("b7", "c6", "d5", "e4", "f3", "g2", "h1"),
        )
        ae(sss["b1"].low_lrd_attacks, ())
        ae(sss["b2"].low_lrd_attacks, ("c1",))
        ae(sss["b3"].low_lrd_attacks, ("c2", "d1"))
        ae(sss["b4"].low_lrd_attacks, ("c3", "d2", "e1"))
        ae(sss["b5"].low_lrd_attacks, ("c4", "d3", "e2", "f1"))
        ae(sss["b6"].low_lrd_attacks, ("c5", "d4", "e3", "f2", "g1"))
        ae(sss["b7"].low_lrd_attacks, ("c6", "d5", "e4", "f3", "g2", "h1"))
        ae(sss["b8"].low_lrd_attacks, ("c7", "d6", "e5", "f4", "g3", "h2"))
        ae(sss["c1"].low_lrd_attacks, ())
        ae(sss["c2"].low_lrd_attacks, ("d1",))
        ae(sss["c3"].low_lrd_attacks, ("d2", "e1"))
        ae(sss["c4"].low_lrd_attacks, ("d3", "e2", "f1"))
        ae(sss["c5"].low_lrd_attacks, ("d4", "e3", "f2", "g1"))
        ae(sss["c6"].low_lrd_attacks, ("d5", "e4", "f3", "g2", "h1"))
        ae(sss["c7"].low_lrd_attacks, ("d6", "e5", "f4", "g3", "h2"))
        ae(sss["c8"].low_lrd_attacks, ("d7", "e6", "f5", "g4", "h3"))
        ae(sss["d1"].low_lrd_attacks, ())
        ae(sss["d2"].low_lrd_attacks, ("e1",))
        ae(sss["d3"].low_lrd_attacks, ("e2", "f1"))
        ae(sss["d4"].low_lrd_attacks, ("e3", "f2", "g1"))
        ae(sss["d5"].low_lrd_attacks, ("e4", "f3", "g2", "h1"))
        ae(sss["d6"].low_lrd_attacks, ("e5", "f4", "g3", "h2"))
        ae(sss["d7"].low_lrd_attacks, ("e6", "f5", "g4", "h3"))
        ae(sss["d8"].low_lrd_attacks, ("e7", "f6", "g5", "h4"))
        ae(sss["e1"].low_lrd_attacks, ())
        ae(sss["e2"].low_lrd_attacks, ("f1",))
        ae(sss["e3"].low_lrd_attacks, ("f2", "g1"))
        ae(sss["e4"].low_lrd_attacks, ("f3", "g2", "h1"))
        ae(sss["e5"].low_lrd_attacks, ("f4", "g3", "h2"))
        ae(sss["e6"].low_lrd_attacks, ("f5", "g4", "h3"))
        ae(sss["e7"].low_lrd_attacks, ("f6", "g5", "h4"))
        ae(sss["e8"].low_lrd_attacks, ("f7", "g6", "h5"))
        ae(sss["f1"].low_lrd_attacks, ())
        ae(sss["f2"].low_lrd_attacks, ("g1",))
        ae(sss["f3"].low_lrd_attacks, ("g2", "h1"))
        ae(sss["f4"].low_lrd_attacks, ("g3", "h2"))
        ae(sss["f5"].low_lrd_attacks, ("g4", "h3"))
        ae(sss["f6"].low_lrd_attacks, ("g5", "h4"))
        ae(sss["f7"].low_lrd_attacks, ("g6", "h5"))
        ae(sss["f8"].low_lrd_attacks, ("g7", "h6"))
        ae(sss["g1"].low_lrd_attacks, ())
        ae(sss["g2"].low_lrd_attacks, ("h1",))
        ae(sss["g3"].low_lrd_attacks, ("h2",))
        ae(sss["g4"].low_lrd_attacks, ("h3",))
        ae(sss["g5"].low_lrd_attacks, ("h4",))
        ae(sss["g6"].low_lrd_attacks, ("h5",))
        ae(sss["g7"].low_lrd_attacks, ("h6",))
        ae(sss["g8"].low_lrd_attacks, ("h7",))
        ae(sss["h1"].low_lrd_attacks, ())
        ae(sss["h2"].low_lrd_attacks, ())
        ae(sss["h3"].low_lrd_attacks, ())
        ae(sss["h4"].low_lrd_attacks, ())
        ae(sss["h5"].low_lrd_attacks, ())
        ae(sss["h6"].low_lrd_attacks, ())
        ae(sss["h7"].low_lrd_attacks, ())
        ae(sss["h8"].low_lrd_attacks, ())
        ae(sss["a1"].high_lrd_attacks, ())
        ae(sss["a2"].high_lrd_attacks, ())
        ae(sss["a3"].high_lrd_attacks, ())
        ae(sss["a4"].high_lrd_attacks, ())
        ae(sss["a5"].high_lrd_attacks, ())
        ae(sss["a6"].high_lrd_attacks, ())
        ae(sss["a7"].high_lrd_attacks, ())
        ae(sss["a8"].high_lrd_attacks, ())
        ae(sss["b1"].high_lrd_attacks, ("a2",))
        ae(sss["b2"].high_lrd_attacks, ("a3",))
        ae(sss["b3"].high_lrd_attacks, ("a4",))
        ae(sss["b4"].high_lrd_attacks, ("a5",))
        ae(sss["b5"].high_lrd_attacks, ("a6",))
        ae(sss["b6"].high_lrd_attacks, ("a7",))
        ae(sss["b7"].high_lrd_attacks, ("a8",))
        ae(sss["b8"].high_lrd_attacks, ())
        ae(sss["c1"].high_lrd_attacks, ("b2", "a3"))
        ae(sss["c2"].high_lrd_attacks, ("b3", "a4"))
        ae(sss["c3"].high_lrd_attacks, ("b4", "a5"))
        ae(sss["c4"].high_lrd_attacks, ("b5", "a6"))
        ae(sss["c5"].high_lrd_attacks, ("b6", "a7"))
        ae(sss["c6"].high_lrd_attacks, ("b7", "a8"))
        ae(sss["c7"].high_lrd_attacks, ("b8",))
        ae(sss["c8"].high_lrd_attacks, ())
        ae(sss["d1"].high_lrd_attacks, ("c2", "b3", "a4"))
        ae(sss["d2"].high_lrd_attacks, ("c3", "b4", "a5"))
        ae(sss["d3"].high_lrd_attacks, ("c4", "b5", "a6"))
        ae(sss["d4"].high_lrd_attacks, ("c5", "b6", "a7"))
        ae(sss["d5"].high_lrd_attacks, ("c6", "b7", "a8"))
        ae(sss["d6"].high_lrd_attacks, ("c7", "b8"))
        ae(sss["d7"].high_lrd_attacks, ("c8",))
        ae(sss["d8"].high_lrd_attacks, ())
        ae(sss["e1"].high_lrd_attacks, ("d2", "c3", "b4", "a5"))
        ae(sss["e2"].high_lrd_attacks, ("d3", "c4", "b5", "a6"))
        ae(sss["e3"].high_lrd_attacks, ("d4", "c5", "b6", "a7"))
        ae(sss["e4"].high_lrd_attacks, ("d5", "c6", "b7", "a8"))
        ae(sss["e5"].high_lrd_attacks, ("d6", "c7", "b8"))
        ae(sss["e6"].high_lrd_attacks, ("d7", "c8"))
        ae(sss["e7"].high_lrd_attacks, ("d8",))
        ae(sss["e8"].high_lrd_attacks, ())
        ae(sss["f1"].high_lrd_attacks, ("e2", "d3", "c4", "b5", "a6"))
        ae(sss["f2"].high_lrd_attacks, ("e3", "d4", "c5", "b6", "a7"))
        ae(sss["f3"].high_lrd_attacks, ("e4", "d5", "c6", "b7", "a8"))
        ae(sss["f4"].high_lrd_attacks, ("e5", "d6", "c7", "b8"))
        ae(sss["f5"].high_lrd_attacks, ("e6", "d7", "c8"))
        ae(sss["f6"].high_lrd_attacks, ("e7", "d8"))
        ae(sss["f7"].high_lrd_attacks, ("e8",))
        ae(sss["f8"].high_lrd_attacks, ())
        ae(sss["g1"].high_lrd_attacks, ("f2", "e3", "d4", "c5", "b6", "a7"))
        ae(sss["g2"].high_lrd_attacks, ("f3", "e4", "d5", "c6", "b7", "a8"))
        ae(sss["g3"].high_lrd_attacks, ("f4", "e5", "d6", "c7", "b8"))
        ae(sss["g4"].high_lrd_attacks, ("f5", "e6", "d7", "c8"))
        ae(sss["g5"].high_lrd_attacks, ("f6", "e7", "d8"))
        ae(sss["g6"].high_lrd_attacks, ("f7", "e8"))
        ae(sss["g7"].high_lrd_attacks, ("f8",))
        ae(sss["g8"].high_lrd_attacks, ())
        ae(
            sss["h1"].high_lrd_attacks,
            ("g2", "f3", "e4", "d5", "c6", "b7", "a8"),
        )
        ae(sss["h2"].high_lrd_attacks, ("g3", "f4", "e5", "d6", "c7", "b8"))
        ae(sss["h3"].high_lrd_attacks, ("g4", "f5", "e6", "d7", "c8"))
        ae(sss["h4"].high_lrd_attacks, ("g5", "f6", "e7", "d8"))
        ae(sss["h5"].high_lrd_attacks, ("g6", "f7", "e8"))
        ae(sss["h6"].high_lrd_attacks, ("g7", "f8"))
        ae(sss["h7"].high_lrd_attacks, ("g8",))
        ae(sss["h8"].high_lrd_attacks, ())
        ae(sss["a1"].low_rld_attacks, ())
        ae(sss["a2"].low_rld_attacks, ())
        ae(sss["a3"].low_rld_attacks, ())
        ae(sss["a4"].low_rld_attacks, ())
        ae(sss["a5"].low_rld_attacks, ())
        ae(sss["a6"].low_rld_attacks, ())
        ae(sss["a7"].low_rld_attacks, ())
        ae(sss["a8"].low_rld_attacks, ())
        ae(sss["b1"].low_rld_attacks, ())
        ae(sss["b2"].low_rld_attacks, ("a1",))
        ae(sss["b3"].low_rld_attacks, ("a2",))
        ae(sss["b4"].low_rld_attacks, ("a3",))
        ae(sss["b5"].low_rld_attacks, ("a4",))
        ae(sss["b6"].low_rld_attacks, ("a5",))
        ae(sss["b7"].low_rld_attacks, ("a6",))
        ae(sss["b8"].low_rld_attacks, ("a7",))
        ae(sss["c1"].low_rld_attacks, ())
        ae(sss["c2"].low_rld_attacks, ("b1",))
        ae(sss["c3"].low_rld_attacks, ("b2", "a1"))
        ae(sss["c4"].low_rld_attacks, ("b3", "a2"))
        ae(sss["c5"].low_rld_attacks, ("b4", "a3"))
        ae(sss["c6"].low_rld_attacks, ("b5", "a4"))
        ae(sss["c7"].low_rld_attacks, ("b6", "a5"))
        ae(sss["c8"].low_rld_attacks, ("b7", "a6"))
        ae(sss["d1"].low_rld_attacks, ())
        ae(sss["d2"].low_rld_attacks, ("c1",))
        ae(sss["d3"].low_rld_attacks, ("c2", "b1"))
        ae(sss["d4"].low_rld_attacks, ("c3", "b2", "a1"))
        ae(sss["d5"].low_rld_attacks, ("c4", "b3", "a2"))
        ae(sss["d6"].low_rld_attacks, ("c5", "b4", "a3"))
        ae(sss["d7"].low_rld_attacks, ("c6", "b5", "a4"))
        ae(sss["d8"].low_rld_attacks, ("c7", "b6", "a5"))
        ae(sss["e1"].low_rld_attacks, ())
        ae(sss["e2"].low_rld_attacks, ("d1",))
        ae(sss["e3"].low_rld_attacks, ("d2", "c1"))
        ae(sss["e4"].low_rld_attacks, ("d3", "c2", "b1"))
        ae(sss["e5"].low_rld_attacks, ("d4", "c3", "b2", "a1"))
        ae(sss["e6"].low_rld_attacks, ("d5", "c4", "b3", "a2"))
        ae(sss["e7"].low_rld_attacks, ("d6", "c5", "b4", "a3"))
        ae(sss["e8"].low_rld_attacks, ("d7", "c6", "b5", "a4"))
        ae(sss["f1"].low_rld_attacks, ())
        ae(sss["f2"].low_rld_attacks, ("e1",))
        ae(sss["f3"].low_rld_attacks, ("e2", "d1"))
        ae(sss["f4"].low_rld_attacks, ("e3", "d2", "c1"))
        ae(sss["f5"].low_rld_attacks, ("e4", "d3", "c2", "b1"))
        ae(sss["f6"].low_rld_attacks, ("e5", "d4", "c3", "b2", "a1"))
        ae(sss["f7"].low_rld_attacks, ("e6", "d5", "c4", "b3", "a2"))
        ae(sss["f8"].low_rld_attacks, ("e7", "d6", "c5", "b4", "a3"))
        ae(sss["g1"].low_rld_attacks, ())
        ae(sss["g2"].low_rld_attacks, ("f1",))
        ae(sss["g3"].low_rld_attacks, ("f2", "e1"))
        ae(sss["g4"].low_rld_attacks, ("f3", "e2", "d1"))
        ae(sss["g5"].low_rld_attacks, ("f4", "e3", "d2", "c1"))
        ae(sss["g6"].low_rld_attacks, ("f5", "e4", "d3", "c2", "b1"))
        ae(sss["g7"].low_rld_attacks, ("f6", "e5", "d4", "c3", "b2", "a1"))
        ae(sss["g8"].low_rld_attacks, ("f7", "e6", "d5", "c4", "b3", "a2"))
        ae(sss["h1"].low_rld_attacks, ())
        ae(sss["h2"].low_rld_attacks, ("g1",))
        ae(sss["h3"].low_rld_attacks, ("g2", "f1"))
        ae(sss["h4"].low_rld_attacks, ("g3", "f2", "e1"))
        ae(sss["h5"].low_rld_attacks, ("g4", "f3", "e2", "d1"))
        ae(sss["h6"].low_rld_attacks, ("g5", "f4", "e3", "d2", "c1"))
        ae(sss["h7"].low_rld_attacks, ("g6", "f5", "e4", "d3", "c2", "b1"))
        ae(
            sss["h8"].low_rld_attacks,
            ("g7", "f6", "e5", "d4", "c3", "b2", "a1"),
        )
        ae(
            sss["a1"].high_rld_attacks,
            ("b2", "c3", "d4", "e5", "f6", "g7", "h8"),
        )
        ae(sss["a2"].high_rld_attacks, ("b3", "c4", "d5", "e6", "f7", "g8"))
        ae(sss["a3"].high_rld_attacks, ("b4", "c5", "d6", "e7", "f8"))
        ae(sss["a4"].high_rld_attacks, ("b5", "c6", "d7", "e8"))
        ae(sss["a5"].high_rld_attacks, ("b6", "c7", "d8"))
        ae(sss["a6"].high_rld_attacks, ("b7", "c8"))
        ae(sss["a7"].high_rld_attacks, ("b8",))
        ae(sss["a8"].high_rld_attacks, ())
        ae(sss["b1"].high_rld_attacks, ("c2", "d3", "e4", "f5", "g6", "h7"))
        ae(sss["b2"].high_rld_attacks, ("c3", "d4", "e5", "f6", "g7", "h8"))
        ae(sss["b3"].high_rld_attacks, ("c4", "d5", "e6", "f7", "g8"))
        ae(sss["b4"].high_rld_attacks, ("c5", "d6", "e7", "f8"))
        ae(sss["b5"].high_rld_attacks, ("c6", "d7", "e8"))
        ae(sss["b6"].high_rld_attacks, ("c7", "d8"))
        ae(sss["b7"].high_rld_attacks, ("c8",))
        ae(sss["b8"].high_rld_attacks, ())
        ae(sss["c1"].high_rld_attacks, ("d2", "e3", "f4", "g5", "h6"))
        ae(sss["c2"].high_rld_attacks, ("d3", "e4", "f5", "g6", "h7"))
        ae(sss["c3"].high_rld_attacks, ("d4", "e5", "f6", "g7", "h8"))
        ae(sss["c4"].high_rld_attacks, ("d5", "e6", "f7", "g8"))
        ae(sss["c5"].high_rld_attacks, ("d6", "e7", "f8"))
        ae(sss["c6"].high_rld_attacks, ("d7", "e8"))
        ae(sss["c7"].high_rld_attacks, ("d8",))
        ae(sss["c8"].high_rld_attacks, ())
        ae(sss["d1"].high_rld_attacks, ("e2", "f3", "g4", "h5"))
        ae(sss["d2"].high_rld_attacks, ("e3", "f4", "g5", "h6"))
        ae(sss["d3"].high_rld_attacks, ("e4", "f5", "g6", "h7"))
        ae(sss["d4"].high_rld_attacks, ("e5", "f6", "g7", "h8"))
        ae(sss["d5"].high_rld_attacks, ("e6", "f7", "g8"))
        ae(sss["d6"].high_rld_attacks, ("e7", "f8"))
        ae(sss["d7"].high_rld_attacks, ("e8",))
        ae(sss["d8"].high_rld_attacks, ())
        ae(sss["e1"].high_rld_attacks, ("f2", "g3", "h4"))
        ae(sss["e2"].high_rld_attacks, ("f3", "g4", "h5"))
        ae(sss["e3"].high_rld_attacks, ("f4", "g5", "h6"))
        ae(sss["e4"].high_rld_attacks, ("f5", "g6", "h7"))
        ae(sss["e5"].high_rld_attacks, ("f6", "g7", "h8"))
        ae(sss["e6"].high_rld_attacks, ("f7", "g8"))
        ae(sss["e7"].high_rld_attacks, ("f8",))
        ae(sss["e8"].high_rld_attacks, ())
        ae(sss["f1"].high_rld_attacks, ("g2", "h3"))
        ae(sss["f2"].high_rld_attacks, ("g3", "h4"))
        ae(sss["f3"].high_rld_attacks, ("g4", "h5"))
        ae(sss["f4"].high_rld_attacks, ("g5", "h6"))
        ae(sss["f5"].high_rld_attacks, ("g6", "h7"))
        ae(sss["f6"].high_rld_attacks, ("g7", "h8"))
        ae(sss["f7"].high_rld_attacks, ("g8",))
        ae(sss["f8"].high_rld_attacks, ())
        ae(sss["g1"].high_rld_attacks, ("h2",))
        ae(sss["g2"].high_rld_attacks, ("h3",))
        ae(sss["g3"].high_rld_attacks, ("h4",))
        ae(sss["g4"].high_rld_attacks, ("h5",))
        ae(sss["g5"].high_rld_attacks, ("h6",))
        ae(sss["g6"].high_rld_attacks, ("h7",))
        ae(sss["g7"].high_rld_attacks, ("h8",))
        ae(sss["g8"].high_rld_attacks, ())
        ae(sss["h1"].high_rld_attacks, ())
        ae(sss["h2"].high_rld_attacks, ())
        ae(sss["h3"].high_rld_attacks, ())
        ae(sss["h4"].high_rld_attacks, ())
        ae(sss["h5"].high_rld_attacks, ())
        ae(sss["h6"].high_rld_attacks, ())
        ae(sss["h7"].high_rld_attacks, ())
        ae(sss["h8"].high_rld_attacks, ())

    def test_11_Squares_highlow_low_file_attacks(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for sqr in square.low_file_attacks:
                with self.subTest(square=square, sqr=sqr):
                    ae(square.higher_than(sss[sqr]), True)
                    ae(square.file, sss[sqr].file)
                    ane(square.rank, sss[sqr].rank)
                    ane(
                        square.left_to_right_down_diagonal,
                        sss[sqr].left_to_right_down_diagonal,
                    )
                    ane(
                        square.right_to_left_down_diagonal,
                        sss[sqr].right_to_left_down_diagonal,
                    )

    def test_12_Squares_highlow_low_rank_attacks(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for sqr in square.low_rank_attacks:
                with self.subTest(square=square, sqr=sqr):
                    ae(square.higher_than(sss[sqr]), True)
                    ae(square.rank, sss[sqr].rank)
                    ane(square.file, sss[sqr].file)
                    ane(
                        square.left_to_right_down_diagonal,
                        sss[sqr].left_to_right_down_diagonal,
                    )
                    ane(
                        square.right_to_left_down_diagonal,
                        sss[sqr].right_to_left_down_diagonal,
                    )

    def test_13_Squares_highlow_low_lrd_attacks(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for sqr in square.low_lrd_attacks:
                with self.subTest(square=square, sqr=sqr):
                    ae(square.higher_than(sss[sqr]), True)
                    ae(
                        square.left_to_right_down_diagonal,
                        sss[sqr].left_to_right_down_diagonal,
                    )
                    ane(square.rank, sss[sqr].rank)
                    ane(square.file, sss[sqr].file)
                    ane(
                        square.right_to_left_down_diagonal,
                        sss[sqr].right_to_left_down_diagonal,
                    )

    def test_14_Squares_highlow_low_rld_attacks(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for sqr in square.low_rld_attacks:
                with self.subTest(square=square, sqr=sqr):
                    ae(square.higher_than(sss[sqr]), True)
                    ae(
                        square.right_to_left_down_diagonal,
                        sss[sqr].right_to_left_down_diagonal,
                    )
                    ane(square.rank, sss[sqr].rank)
                    ane(square.file, sss[sqr].file)
                    ane(
                        square.left_to_right_down_diagonal,
                        sss[sqr].left_to_right_down_diagonal,
                    )

    def test_15_Squares_highlow_high_file_attacks(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for sqr in square.high_file_attacks:
                with self.subTest(square=square, sqr=sqr):
                    ae(square.lower_than(sss[sqr]), True)
                    ae(square.file, sss[sqr].file)
                    ane(square.rank, sss[sqr].rank)
                    ane(
                        square.left_to_right_down_diagonal,
                        sss[sqr].left_to_right_down_diagonal,
                    )
                    ane(
                        square.right_to_left_down_diagonal,
                        sss[sqr].right_to_left_down_diagonal,
                    )

    def test_16_Squares_highlow_high_rank_attacks(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for sqr in square.high_rank_attacks:
                with self.subTest(square=square, sqr=sqr):
                    ae(square.lower_than(sss[sqr]), True)
                    ae(square.rank, sss[sqr].rank)
                    ane(square.file, sss[sqr].file)
                    ane(
                        square.left_to_right_down_diagonal,
                        sss[sqr].left_to_right_down_diagonal,
                    )
                    ane(
                        square.right_to_left_down_diagonal,
                        sss[sqr].right_to_left_down_diagonal,
                    )

    def test_17_Squares_highlow_high_lrd_attacks(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for sqr in square.high_lrd_attacks:
                with self.subTest(square=square, sqr=sqr):
                    ae(square.lower_than(sss[sqr]), True)
                    ae(
                        square.left_to_right_down_diagonal,
                        sss[sqr].left_to_right_down_diagonal,
                    )
                    ane(square.rank, sss[sqr].rank)
                    ane(square.file, sss[sqr].file)
                    ane(
                        square.right_to_left_down_diagonal,
                        sss[sqr].right_to_left_down_diagonal,
                    )

    def test_18_Squares_highlow_high_rld_attacks(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for sqr in square.high_rld_attacks:
                with self.subTest(square=square, sqr=sqr):
                    ae(square.lower_than(sss[sqr]), True)
                    ae(
                        square.right_to_left_down_diagonal,
                        sss[sqr].right_to_left_down_diagonal,
                    )
                    ane(square.rank, sss[sqr].rank)
                    ane(square.file, sss[sqr].file)
                    ane(
                        square.left_to_right_down_diagonal,
                        sss[sqr].left_to_right_down_diagonal,
                    )

    def test_19_Squares_point_to_point(self):
        ae = self.assertEqual
        ane = self.assertNotEqual
        sss = squares.fen_squares
        for square in sss.values():
            for name, names in square.point_to_point.items():
                sqr = sss[name]
                with self.subTest(square=square, sqr=sqr, names=names):
                    if square is sqr:
                        ae(sqr is square, False)
                    elif square.number < sqr.number:
                        for linesqr in names:
                            ae(square.number < sss[linesqr].number, True)
                            ae(sqr.number > sss[linesqr].number, True)
                    elif square.number > sqr.number:
                        for linesqr in names:
                            ae(square.number > sss[linesqr].number, True)
                            ae(sqr.number < sss[linesqr].number, True)
                    for lname in names:
                        for line in square.attack_lines():
                            ae(lname in line, name in line)

    def test_20_en_passant_target_squares(self):
        self.assertEqual(
            squares.en_passant_target_squares,
            {
                "w": {
                    ("a5", "a7"): "a6",
                    ("b5", "b7"): "b6",
                    ("c5", "c7"): "c6",
                    ("d5", "d7"): "d6",
                    ("e5", "e7"): "e6",
                    ("f5", "f7"): "f6",
                    ("g5", "g7"): "g6",
                    ("h5", "h7"): "h6",
                },
                "b": {
                    ("a4", "a2"): "a3",
                    ("b4", "b2"): "b3",
                    ("c4", "c2"): "c3",
                    ("d4", "d2"): "d3",
                    ("e4", "e2"): "e3",
                    ("f4", "f2"): "f3",
                    ("g4", "g2"): "g3",
                    ("h4", "h2"): "h3",
                },
                "axb6": "b5",
                "bxc6": "c5",
                "bxa6": "a5",
                "cxd6": "d5",
                "cxb6": "b5",
                "dxe6": "e5",
                "dxc6": "c5",
                "exf6": "f5",
                "exd6": "d5",
                "fxg6": "g5",
                "fxe6": "e5",
                "gxh6": "h5",
                "gxf6": "f5",
                "hxg6": "g5",
                "axb3": "b4",
                "bxc3": "c4",
                "bxa3": "a4",
                "cxd3": "d4",
                "cxb3": "b4",
                "dxe3": "e4",
                "dxc3": "c4",
                "exf3": "f4",
                "exd3": "d4",
                "fxg3": "g4",
                "fxe3": "e4",
                "gxh3": "h4",
                "gxf3": "f4",
                "hxg3": "g4",
            },
        )

    def test_21_fen_source_squares(self):
        ae = self.assertEqual
        sss = squares.source_squares
        fss = squares.fen_source_squares
        ae(fss["K"] is sss["K"], True)
        ae(fss["Q"] is sss["Q"], True)
        ae(fss["R"] is sss["R"], True)
        ae(fss["B"] is sss["B"], True)
        ae(fss["N"] is sss["N"], True)
        ae(fss["P"] is sss["Px"], True)
        ae(fss["k"] is sss["K"], True)
        ae(fss["q"] is sss["Q"], True)
        ae(fss["r"] is sss["R"], True)
        ae(fss["b"] is sss["B"], True)
        ae(fss["n"] is sss["N"], True)
        ae(fss["p"] is sss["px"], True)
        ae(len(fss), 12)

    def test_22_source_squares(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(set(sss), {"K", "Q", "R", "B", "N", "P", "p", "Px", "px"})

    def test_23_source_squares_king(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["K"],
            {
                "a8": {"b8", "a7", "b7"},
                "a7": {"b8", "a6", "a8", "b6", "b7"},
                "a6": {"b5", "a7", "a5", "b6", "b7"},
                "a5": {"a4", "b5", "a6", "b4", "b6"},
                "a4": {"b3", "b5", "b4", "a5", "a3"},
                "a3": {"a4", "b3", "a2", "b4", "b2"},
                "a2": {"a1", "b3", "b1", "b2", "a3"},
                "a1": {"b1", "b2", "a2"},
                "b8": {"a7", "c8", "a8", "c7", "b7"},
                "b7": {"b8", "a7", "a6", "c6", "c8", "b6", "a8", "c7"},
                "b6": {"c5", "b5", "a7", "a6", "a5", "c6", "c7", "b7"},
                "b5": {"c5", "a4", "c4", "a6", "b4", "a5", "c6", "b6"},
                "b4": {"c5", "a4", "c4", "b3", "b5", "c3", "a5", "a3"},
                "b3": {"a4", "c4", "c3", "a2", "b4", "b2", "c2", "a3"},
                "b2": {"c1", "a1", "b3", "c3", "a2", "b1", "c2", "a3"},
                "b1": {"c1", "a1", "a2", "b2", "c2"},
                "c8": {"b8", "d8", "d7", "c7", "b7"},
                "c7": {"b8", "d8", "d6", "b6", "c6", "c8", "d7", "b7"},
                "c6": {"d5", "c5", "b5", "d6", "b6", "d7", "c7", "b7"},
                "c5": {"d5", "c4", "b5", "b4", "d6", "c6", "b6", "d4"},
                "c4": {"d5", "d3", "c5", "b3", "b5", "c3", "b4", "d4"},
                "c3": {"d3", "c4", "b3", "b4", "b2", "c2", "d4", "d2"},
                "c2": {"d3", "c1", "b3", "c3", "b1", "b2", "d2", "d1"},
                "c1": {"b1", "b2", "c2", "d2", "d1"},
                "d8": {"c7", "e7", "c8", "d7", "e8"},
                "d7": {"c7", "e6", "c6", "d6", "c8", "d8", "e7", "e8"},
                "d6": {"d5", "c5", "d7", "e5", "e6", "c6", "e7", "c7"},
                "d5": {"c5", "c4", "e5", "e6", "c6", "d6", "d4", "e4"},
                "d4": {"d5", "d3", "c5", "c4", "e5", "c3", "e3", "e4"},
                "d3": {"c4", "e2", "c3", "e3", "c2", "d4", "d2", "e4"},
                "d2": {"d3", "c1", "e2", "c3", "e3", "c2", "d1", "e1"},
                "d1": {"c1", "e2", "c2", "d2", "e1"},
                "e8": {"d7", "f7", "f8", "d8", "e7"},
                "e7": {"f6", "f8", "f7", "e6", "d6", "d8", "d7", "e8"},
                "e6": {"d5", "e7", "e5", "f6", "f7", "d6", "f5", "d7"},
                "e5": {"d5", "f6", "e6", "d6", "f5", "d4", "f4", "e4"},
                "e4": {"d5", "f3", "d3", "e5", "f5", "e3", "d4", "f4"},
                "e3": {"f3", "d3", "f2", "e2", "d4", "f4", "d2", "e4"},
                "e2": {"f3", "d3", "f2", "f1", "e3", "d2", "d1", "e1"},
                "e1": {"f2", "e2", "f1", "d2", "d1"},
                "f8": {"g7", "f7", "g8", "e7", "e8"},
                "f7": {"g7", "e7", "f6", "f8", "e6", "g8", "e8", "g6"},
                "f6": {"g7", "g5", "e5", "f7", "e6", "f5", "e7", "g6"},
                "f5": {"g5", "e5", "f6", "e6", "g4", "f4", "e4", "g6"},
                "f4": {"f3", "g5", "e5", "g3", "f5", "e3", "e4", "g4"},
                "f3": {"f2", "e2", "g2", "g3", "e3", "f4", "e4", "g4"},
                "f2": {"f3", "e2", "f1", "g2", "g3", "g1", "e3", "e1"},
                "f1": {"f2", "e2", "g2", "g1", "e1"},
                "g8": {"g7", "f7", "f8", "h7", "h8"},
                "g7": {"f6", "f7", "f8", "h7", "h8", "g8", "h6", "g6"},
                "g6": {"g7", "g5", "f6", "f7", "h7", "h5", "f5", "h6"},
                "g5": {"g6", "f6", "h4", "h5", "f5", "f4", "h6", "g4"},
                "g4": {"f3", "g5", "h5", "g3", "f5", "f4", "h3", "h4"},
                "g3": {"f3", "f2", "g4", "g2", "h2", "f4", "h3", "h4"},
                "g2": {"f3", "f2", "h1", "f1", "h2", "g3", "g1", "h3"},
                "g1": {"f2", "h1", "f1", "g2", "h2"},
                "h8": {"g8", "h7", "g7"},
                "h7": {"g7", "h8", "g8", "h6", "g6"},
                "h6": {"g7", "g5", "h7", "h5", "g6"},
                "h5": {"g6", "g5", "h4", "h6", "g4"},
                "h4": {"g5", "h5", "g3", "h3", "g4"},
                "h3": {"g4", "g2", "h2", "g3", "h4"},
                "h2": {"h1", "g2", "g3", "g1", "h3"},
                "h1": {"h2", "g2", "g1"},
            },
        )

    def test_24_source_squares_queen(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["Q"],
            {
                "a8": {
                    "f3",
                    "h1",
                    "f8",
                    "a6",
                    "a5",
                    "g8",
                    "a3",
                    "d5",
                    "b7",
                    "a4",
                    "a1",
                    "b8",
                    "a7",
                    "a2",
                    "g2",
                    "d8",
                    "c8",
                    "c6",
                    "h8",
                    "e8",
                    "e4",
                },
                "a7": {
                    "c5",
                    "f7",
                    "h7",
                    "a6",
                    "a5",
                    "b6",
                    "d4",
                    "d7",
                    "c7",
                    "a3",
                    "b7",
                    "a4",
                    "f2",
                    "a1",
                    "g7",
                    "b8",
                    "a2",
                    "g1",
                    "a8",
                    "e3",
                    "e7",
                },
                "a6": {
                    "f1",
                    "a5",
                    "d6",
                    "b6",
                    "h6",
                    "a3",
                    "b7",
                    "d3",
                    "a4",
                    "c4",
                    "a1",
                    "e2",
                    "b5",
                    "f6",
                    "a7",
                    "a2",
                    "e6",
                    "c6",
                    "a8",
                    "c8",
                    "g6",
                },
                "a5": {
                    "c5",
                    "c3",
                    "a6",
                    "h5",
                    "b4",
                    "b6",
                    "c7",
                    "a3",
                    "d5",
                    "a4",
                    "a1",
                    "b5",
                    "e5",
                    "g5",
                    "a7",
                    "a2",
                    "d8",
                    "a8",
                    "f5",
                    "d2",
                    "e1",
                },
                "a4": {
                    "d1",
                    "b3",
                    "a6",
                    "a5",
                    "b4",
                    "d4",
                    "d7",
                    "a3",
                    "c4",
                    "a1",
                    "b5",
                    "a7",
                    "a2",
                    "h4",
                    "c6",
                    "a8",
                    "c2",
                    "f4",
                    "e8",
                    "e4",
                    "g4",
                },
                "a3": {
                    "f3",
                    "c5",
                    "c1",
                    "b3",
                    "f8",
                    "c3",
                    "a6",
                    "a5",
                    "b4",
                    "b2",
                    "d6",
                    "d3",
                    "a4",
                    "a1",
                    "a7",
                    "a2",
                    "g3",
                    "a8",
                    "e3",
                    "e7",
                    "h3",
                },
                "a2": {
                    "b3",
                    "f7",
                    "a6",
                    "b1",
                    "h2",
                    "a5",
                    "b2",
                    "g8",
                    "a3",
                    "d5",
                    "a4",
                    "f2",
                    "c4",
                    "a1",
                    "e2",
                    "a7",
                    "e6",
                    "g2",
                    "a8",
                    "c2",
                    "d2",
                },
                "a1": {
                    "c1",
                    "h1",
                    "c3",
                    "f1",
                    "a6",
                    "b1",
                    "a5",
                    "b2",
                    "d4",
                    "a3",
                    "a4",
                    "g7",
                    "f6",
                    "e5",
                    "a7",
                    "a2",
                    "g1",
                    "a8",
                    "h8",
                    "d1",
                    "e1",
                },
                "b8": {
                    "b3",
                    "f8",
                    "b1",
                    "h2",
                    "b4",
                    "b2",
                    "d6",
                    "b6",
                    "g8",
                    "c7",
                    "b7",
                    "b5",
                    "e5",
                    "a7",
                    "g3",
                    "d8",
                    "c8",
                    "a8",
                    "h8",
                    "f4",
                    "e8",
                },
                "b7": {
                    "f3",
                    "h1",
                    "b3",
                    "f7",
                    "h7",
                    "a6",
                    "b1",
                    "b4",
                    "b2",
                    "b6",
                    "d7",
                    "c7",
                    "d5",
                    "b8",
                    "g7",
                    "b5",
                    "a7",
                    "g2",
                    "c6",
                    "a8",
                    "c8",
                    "e7",
                    "e4",
                },
                "b6": {
                    "c5",
                    "e3",
                    "b3",
                    "a6",
                    "b1",
                    "b4",
                    "a5",
                    "b2",
                    "d6",
                    "d4",
                    "c7",
                    "h6",
                    "b7",
                    "f2",
                    "b8",
                    "b5",
                    "f6",
                    "a7",
                    "e6",
                    "c6",
                    "g1",
                    "d8",
                    "g6",
                },
                "b5": {
                    "c5",
                    "b3",
                    "f1",
                    "a6",
                    "b1",
                    "b4",
                    "a5",
                    "b2",
                    "h5",
                    "b6",
                    "d7",
                    "b7",
                    "d5",
                    "d3",
                    "a4",
                    "c4",
                    "e2",
                    "b8",
                    "g5",
                    "e5",
                    "c6",
                    "f5",
                    "e8",
                },
                "b4": {
                    "d2",
                    "c5",
                    "b3",
                    "f8",
                    "c3",
                    "b1",
                    "a5",
                    "b2",
                    "d6",
                    "b6",
                    "d4",
                    "e1",
                    "b7",
                    "a3",
                    "a4",
                    "c4",
                    "b8",
                    "b5",
                    "h4",
                    "f4",
                    "e7",
                    "e4",
                    "g4",
                },
                "b3": {
                    "f3",
                    "f7",
                    "c3",
                    "b1",
                    "b4",
                    "b2",
                    "b6",
                    "g8",
                    "b7",
                    "a3",
                    "d3",
                    "d5",
                    "a4",
                    "c4",
                    "b8",
                    "b5",
                    "e6",
                    "a2",
                    "g3",
                    "e3",
                    "c2",
                    "d1",
                    "h3",
                },
                "b2": {
                    "h8",
                    "c1",
                    "b3",
                    "c3",
                    "b1",
                    "h2",
                    "b4",
                    "b6",
                    "d4",
                    "b7",
                    "a3",
                    "f2",
                    "e2",
                    "b8",
                    "a1",
                    "b5",
                    "g7",
                    "f6",
                    "e5",
                    "a2",
                    "g2",
                    "c2",
                    "d2",
                },
                "b1": {
                    "g6",
                    "e4",
                    "c1",
                    "h1",
                    "b3",
                    "h7",
                    "f1",
                    "b4",
                    "b2",
                    "b6",
                    "b7",
                    "d3",
                    "a1",
                    "b8",
                    "b5",
                    "a2",
                    "g1",
                    "f5",
                    "c2",
                    "d1",
                    "e1",
                },
                "c8": {
                    "h8",
                    "c5",
                    "c1",
                    "f8",
                    "c3",
                    "a6",
                    "g8",
                    "c7",
                    "d7",
                    "b7",
                    "c4",
                    "b8",
                    "e6",
                    "g4",
                    "c6",
                    "d8",
                    "a8",
                    "c2",
                    "f5",
                    "e8",
                    "h3",
                },
                "c7": {
                    "c5",
                    "c1",
                    "f7",
                    "c3",
                    "h7",
                    "h2",
                    "a5",
                    "d6",
                    "b6",
                    "d7",
                    "b7",
                    "c4",
                    "g7",
                    "b8",
                    "e5",
                    "a7",
                    "g3",
                    "c6",
                    "c8",
                    "d8",
                    "c2",
                    "f4",
                    "e7",
                },
                "c6": {
                    "f3",
                    "c5",
                    "c1",
                    "h1",
                    "c3",
                    "a6",
                    "d6",
                    "b6",
                    "d7",
                    "c7",
                    "h6",
                    "b7",
                    "d5",
                    "a4",
                    "c4",
                    "b5",
                    "f6",
                    "e6",
                    "g2",
                    "c8",
                    "a8",
                    "c2",
                    "e8",
                    "e4",
                    "g6",
                },
                "c5": {
                    "e3",
                    "c1",
                    "f8",
                    "c3",
                    "a5",
                    "h5",
                    "b4",
                    "d6",
                    "b6",
                    "d4",
                    "c7",
                    "a3",
                    "d5",
                    "f2",
                    "c4",
                    "b5",
                    "e5",
                    "g5",
                    "a7",
                    "c6",
                    "c8",
                    "f5",
                    "c2",
                    "g1",
                    "e7",
                },
                "c4": {
                    "c5",
                    "c1",
                    "b3",
                    "f7",
                    "c3",
                    "f1",
                    "a6",
                    "b4",
                    "d4",
                    "g8",
                    "c7",
                    "d5",
                    "d3",
                    "a4",
                    "e2",
                    "b5",
                    "e6",
                    "a2",
                    "g4",
                    "c6",
                    "c8",
                    "c2",
                    "f4",
                    "e4",
                    "h4",
                },
                "c3": {
                    "h8",
                    "f3",
                    "c5",
                    "c1",
                    "b3",
                    "b4",
                    "a5",
                    "b2",
                    "d4",
                    "e1",
                    "c7",
                    "a3",
                    "d3",
                    "c4",
                    "a1",
                    "g7",
                    "f6",
                    "e5",
                    "g3",
                    "c6",
                    "c8",
                    "e3",
                    "c2",
                    "d2",
                    "h3",
                },
                "c2": {
                    "d1",
                    "c5",
                    "c1",
                    "b3",
                    "c3",
                    "h7",
                    "b1",
                    "h2",
                    "b2",
                    "c7",
                    "d3",
                    "f2",
                    "a4",
                    "c4",
                    "e2",
                    "a2",
                    "g2",
                    "c6",
                    "c8",
                    "f5",
                    "d2",
                    "e4",
                    "g6",
                },
                "c1": {
                    "c5",
                    "e3",
                    "h1",
                    "c3",
                    "f1",
                    "b1",
                    "b2",
                    "c7",
                    "h6",
                    "a3",
                    "c4",
                    "a1",
                    "g5",
                    "c6",
                    "c8",
                    "g1",
                    "c2",
                    "f4",
                    "d2",
                    "d1",
                    "e1",
                },
                "d8": {
                    "f8",
                    "a5",
                    "d6",
                    "b6",
                    "d4",
                    "d7",
                    "g8",
                    "c7",
                    "d5",
                    "d3",
                    "b8",
                    "g5",
                    "f6",
                    "e7",
                    "c8",
                    "a8",
                    "h8",
                    "d2",
                    "e8",
                    "d1",
                    "h4",
                },
                "d7": {
                    "d2",
                    "f7",
                    "h7",
                    "d6",
                    "d4",
                    "c7",
                    "b7",
                    "d5",
                    "d3",
                    "a4",
                    "g7",
                    "b5",
                    "a7",
                    "e6",
                    "g4",
                    "d8",
                    "c8",
                    "f5",
                    "c6",
                    "e7",
                    "e8",
                    "d1",
                    "h3",
                },
                "d6": {
                    "c5",
                    "f8",
                    "a6",
                    "h2",
                    "b4",
                    "b6",
                    "d4",
                    "d7",
                    "c7",
                    "h6",
                    "a3",
                    "d5",
                    "d3",
                    "b8",
                    "e7",
                    "f6",
                    "e5",
                    "e6",
                    "g3",
                    "d8",
                    "c6",
                    "f4",
                    "d2",
                    "d1",
                    "g6",
                },
                "d5": {
                    "f3",
                    "e4",
                    "c5",
                    "h1",
                    "b3",
                    "f7",
                    "a5",
                    "h5",
                    "d6",
                    "d4",
                    "d7",
                    "g8",
                    "b7",
                    "d3",
                    "c4",
                    "b5",
                    "e5",
                    "g5",
                    "e6",
                    "a2",
                    "g2",
                    "d8",
                    "f5",
                    "c6",
                    "a8",
                    "d2",
                    "d1",
                },
                "d4": {
                    "e4",
                    "c5",
                    "c3",
                    "b4",
                    "d6",
                    "b2",
                    "b6",
                    "d7",
                    "d5",
                    "d3",
                    "a4",
                    "f2",
                    "c4",
                    "a1",
                    "g7",
                    "f6",
                    "e5",
                    "a7",
                    "g4",
                    "d8",
                    "g1",
                    "e3",
                    "h8",
                    "f4",
                    "d2",
                    "d1",
                    "h4",
                },
                "d3": {
                    "f3",
                    "e4",
                    "g6",
                    "b3",
                    "c3",
                    "h7",
                    "f1",
                    "a6",
                    "b1",
                    "d6",
                    "d4",
                    "d7",
                    "a3",
                    "d5",
                    "c4",
                    "e2",
                    "b5",
                    "g3",
                    "d8",
                    "f5",
                    "e3",
                    "c2",
                    "d2",
                    "d1",
                    "h3",
                },
                "d2": {
                    "c1",
                    "c3",
                    "h2",
                    "b4",
                    "a5",
                    "d6",
                    "b2",
                    "d4",
                    "d7",
                    "h6",
                    "d5",
                    "d3",
                    "f2",
                    "e2",
                    "g5",
                    "a2",
                    "g2",
                    "d8",
                    "e3",
                    "c2",
                    "f4",
                    "d1",
                    "e1",
                },
                "d1": {
                    "f3",
                    "c1",
                    "h1",
                    "b3",
                    "f1",
                    "b1",
                    "h5",
                    "d6",
                    "d4",
                    "d7",
                    "d5",
                    "d3",
                    "a4",
                    "a1",
                    "e2",
                    "g4",
                    "d8",
                    "g1",
                    "c2",
                    "d2",
                    "e1",
                },
                "e8": {
                    "g6",
                    "f7",
                    "f8",
                    "h5",
                    "g8",
                    "d7",
                    "a4",
                    "e2",
                    "b8",
                    "b5",
                    "e5",
                    "e6",
                    "d8",
                    "c8",
                    "e3",
                    "h8",
                    "a8",
                    "c6",
                    "e7",
                    "e4",
                    "e1",
                },
                "e7": {
                    "c5",
                    "f7",
                    "f8",
                    "h7",
                    "b4",
                    "d6",
                    "d7",
                    "c7",
                    "b7",
                    "a3",
                    "e2",
                    "g7",
                    "g5",
                    "e5",
                    "f6",
                    "a7",
                    "e6",
                    "h4",
                    "d8",
                    "e3",
                    "e8",
                    "e4",
                    "e1",
                },
                "e6": {
                    "g6",
                    "b3",
                    "f7",
                    "a6",
                    "d6",
                    "b6",
                    "g8",
                    "d7",
                    "h3",
                    "h6",
                    "d5",
                    "c4",
                    "e2",
                    "e5",
                    "f6",
                    "a2",
                    "g4",
                    "c6",
                    "c8",
                    "e3",
                    "f5",
                    "e7",
                    "e8",
                    "e4",
                    "e1",
                },
                "e5": {
                    "c5",
                    "c3",
                    "h2",
                    "a5",
                    "h5",
                    "d6",
                    "b2",
                    "d4",
                    "c7",
                    "d5",
                    "e2",
                    "a1",
                    "b8",
                    "b5",
                    "g5",
                    "g7",
                    "f6",
                    "e6",
                    "g3",
                    "f5",
                    "e3",
                    "h8",
                    "f4",
                    "e7",
                    "e8",
                    "e4",
                    "e1",
                },
                "e4": {
                    "f3",
                    "g6",
                    "h1",
                    "h7",
                    "b1",
                    "b4",
                    "d4",
                    "b7",
                    "d5",
                    "d3",
                    "c2",
                    "a4",
                    "c4",
                    "e2",
                    "e5",
                    "e6",
                    "g4",
                    "h4",
                    "g2",
                    "c6",
                    "a8",
                    "e3",
                    "f5",
                    "f4",
                    "e7",
                    "e8",
                    "e1",
                },
                "e3": {
                    "f3",
                    "d2",
                    "c5",
                    "c1",
                    "b3",
                    "c3",
                    "b6",
                    "d4",
                    "h3",
                    "h6",
                    "a3",
                    "d3",
                    "f2",
                    "e2",
                    "g5",
                    "e5",
                    "a7",
                    "e6",
                    "g3",
                    "g1",
                    "f4",
                    "e7",
                    "e8",
                    "e4",
                    "e1",
                },
                "e2": {
                    "d2",
                    "f3",
                    "d1",
                    "f1",
                    "a6",
                    "h2",
                    "h5",
                    "b2",
                    "d3",
                    "f2",
                    "c4",
                    "b5",
                    "e5",
                    "e6",
                    "a2",
                    "g4",
                    "g2",
                    "e3",
                    "c2",
                    "e7",
                    "e8",
                    "e4",
                    "e1",
                },
                "e1": {
                    "d1",
                    "d2",
                    "c1",
                    "h1",
                    "c3",
                    "f1",
                    "b1",
                    "b4",
                    "a5",
                    "f2",
                    "e2",
                    "a1",
                    "e5",
                    "e6",
                    "g3",
                    "g1",
                    "e3",
                    "e7",
                    "e8",
                    "e4",
                    "h4",
                },
                "f8": {
                    "f3",
                    "c5",
                    "f7",
                    "f1",
                    "b4",
                    "d6",
                    "g8",
                    "h6",
                    "a3",
                    "f2",
                    "b8",
                    "g7",
                    "f6",
                    "d8",
                    "f5",
                    "c8",
                    "h8",
                    "a8",
                    "f4",
                    "e7",
                    "e8",
                },
                "f7": {
                    "f3",
                    "b3",
                    "f8",
                    "h7",
                    "f1",
                    "h5",
                    "d7",
                    "c7",
                    "g8",
                    "b7",
                    "d5",
                    "f2",
                    "c4",
                    "g7",
                    "f6",
                    "a7",
                    "e6",
                    "a2",
                    "f5",
                    "f4",
                    "e7",
                    "e8",
                    "g6",
                },
                "f6": {
                    "f3",
                    "f7",
                    "f8",
                    "c3",
                    "f1",
                    "a6",
                    "d6",
                    "b2",
                    "b6",
                    "d4",
                    "h6",
                    "f2",
                    "a1",
                    "g7",
                    "g5",
                    "e5",
                    "e6",
                    "h4",
                    "c6",
                    "f5",
                    "d8",
                    "h8",
                    "f4",
                    "e7",
                    "g6",
                },
                "f5": {
                    "f3",
                    "c5",
                    "f7",
                    "f8",
                    "h7",
                    "f1",
                    "b1",
                    "a5",
                    "h5",
                    "d7",
                    "h3",
                    "d5",
                    "d3",
                    "f2",
                    "b5",
                    "f6",
                    "e5",
                    "g5",
                    "e6",
                    "g4",
                    "c8",
                    "c2",
                    "f4",
                    "e4",
                    "g6",
                },
                "f4": {
                    "f3",
                    "c1",
                    "f7",
                    "f8",
                    "f1",
                    "h2",
                    "b4",
                    "d6",
                    "d4",
                    "c7",
                    "h6",
                    "f2",
                    "a4",
                    "c4",
                    "b8",
                    "g5",
                    "f6",
                    "e5",
                    "g4",
                    "g3",
                    "f5",
                    "e3",
                    "d2",
                    "e4",
                    "h4",
                },
                "f3": {
                    "e4",
                    "h1",
                    "b3",
                    "f7",
                    "f8",
                    "c3",
                    "f1",
                    "h5",
                    "a3",
                    "d5",
                    "d3",
                    "b7",
                    "f2",
                    "e2",
                    "f6",
                    "g4",
                    "g2",
                    "g3",
                    "c6",
                    "f5",
                    "e3",
                    "a8",
                    "f4",
                    "d1",
                    "h3",
                },
                "f2": {
                    "f3",
                    "c5",
                    "f7",
                    "f8",
                    "f1",
                    "h2",
                    "b2",
                    "b6",
                    "d4",
                    "e1",
                    "e2",
                    "f6",
                    "a7",
                    "a2",
                    "g2",
                    "g3",
                    "g1",
                    "f5",
                    "e3",
                    "c2",
                    "f4",
                    "d2",
                    "h4",
                },
                "f1": {
                    "f3",
                    "c1",
                    "h1",
                    "f7",
                    "f8",
                    "a6",
                    "b1",
                    "h3",
                    "d3",
                    "f2",
                    "c4",
                    "a1",
                    "e2",
                    "b5",
                    "f6",
                    "g2",
                    "g1",
                    "f5",
                    "f4",
                    "d1",
                    "e1",
                },
                "g8": {
                    "g6",
                    "b3",
                    "f7",
                    "f8",
                    "h7",
                    "d5",
                    "c4",
                    "g7",
                    "b8",
                    "g5",
                    "e6",
                    "a2",
                    "g2",
                    "g3",
                    "g1",
                    "d8",
                    "c8",
                    "h8",
                    "a8",
                    "e8",
                    "g4",
                },
                "g7": {
                    "g6",
                    "f7",
                    "f8",
                    "c3",
                    "h7",
                    "b2",
                    "d4",
                    "g8",
                    "d7",
                    "c7",
                    "h6",
                    "b7",
                    "a1",
                    "g5",
                    "f6",
                    "e5",
                    "a7",
                    "g2",
                    "g3",
                    "g1",
                    "h8",
                    "e7",
                    "g4",
                },
                "g6": {
                    "f7",
                    "h7",
                    "a6",
                    "b1",
                    "h5",
                    "d6",
                    "b6",
                    "g8",
                    "h6",
                    "d3",
                    "g7",
                    "g5",
                    "f6",
                    "e6",
                    "g2",
                    "g3",
                    "g1",
                    "c6",
                    "f5",
                    "c2",
                    "e8",
                    "e4",
                    "g4",
                },
                "g5": {
                    "g6",
                    "c5",
                    "e3",
                    "c1",
                    "a5",
                    "h5",
                    "g8",
                    "h6",
                    "d5",
                    "g7",
                    "b5",
                    "e5",
                    "f6",
                    "e7",
                    "h4",
                    "g2",
                    "g3",
                    "g1",
                    "f5",
                    "d8",
                    "f4",
                    "d2",
                    "g4",
                },
                "g4": {
                    "g6",
                    "f3",
                    "d1",
                    "b4",
                    "h5",
                    "d4",
                    "g8",
                    "d7",
                    "h3",
                    "a4",
                    "c4",
                    "e2",
                    "g7",
                    "g5",
                    "e6",
                    "g2",
                    "g3",
                    "g1",
                    "c8",
                    "f5",
                    "f4",
                    "e4",
                    "h4",
                },
                "g3": {
                    "f3",
                    "g6",
                    "b3",
                    "c3",
                    "h2",
                    "d6",
                    "g8",
                    "c7",
                    "h3",
                    "e1",
                    "a3",
                    "d3",
                    "f2",
                    "g7",
                    "b8",
                    "g5",
                    "e5",
                    "h4",
                    "g2",
                    "g1",
                    "e3",
                    "f4",
                    "g4",
                },
                "g2": {
                    "g6",
                    "f3",
                    "h1",
                    "f1",
                    "h2",
                    "b2",
                    "g8",
                    "h3",
                    "b7",
                    "d5",
                    "f2",
                    "e2",
                    "g7",
                    "g5",
                    "a2",
                    "g3",
                    "g1",
                    "c6",
                    "a8",
                    "c2",
                    "d2",
                    "e4",
                    "g4",
                },
                "g1": {
                    "g6",
                    "c5",
                    "c1",
                    "h1",
                    "f1",
                    "b1",
                    "h2",
                    "b6",
                    "d4",
                    "g8",
                    "e1",
                    "f2",
                    "a1",
                    "g7",
                    "g5",
                    "a7",
                    "g2",
                    "g3",
                    "e3",
                    "d1",
                    "g4",
                },
                "h8": {
                    "h1",
                    "f8",
                    "c3",
                    "h7",
                    "h2",
                    "h5",
                    "b2",
                    "d4",
                    "g8",
                    "h3",
                    "h6",
                    "a1",
                    "b8",
                    "g7",
                    "f6",
                    "e5",
                    "d8",
                    "c8",
                    "a8",
                    "e8",
                    "h4",
                },
                "h7": {
                    "g6",
                    "h1",
                    "f7",
                    "b1",
                    "h2",
                    "h5",
                    "d7",
                    "c7",
                    "h3",
                    "h6",
                    "b7",
                    "c2",
                    "d3",
                    "g8",
                    "g7",
                    "a7",
                    "f5",
                    "h8",
                    "e7",
                    "e4",
                    "h4",
                },
                "h6": {
                    "g6",
                    "c1",
                    "h1",
                    "f8",
                    "h7",
                    "a6",
                    "h2",
                    "h5",
                    "d6",
                    "b6",
                    "h3",
                    "g7",
                    "g5",
                    "f6",
                    "e6",
                    "c6",
                    "e3",
                    "h8",
                    "f4",
                    "d2",
                    "h4",
                },
                "h5": {
                    "f3",
                    "g6",
                    "c5",
                    "h1",
                    "f7",
                    "h7",
                    "h2",
                    "a5",
                    "h3",
                    "h6",
                    "d5",
                    "e2",
                    "b5",
                    "e5",
                    "g5",
                    "g4",
                    "f5",
                    "h8",
                    "e8",
                    "d1",
                    "h4",
                },
                "h4": {
                    "h1",
                    "h7",
                    "h2",
                    "h5",
                    "b4",
                    "d4",
                    "e1",
                    "h6",
                    "a4",
                    "f2",
                    "c4",
                    "g5",
                    "f6",
                    "g4",
                    "g3",
                    "d8",
                    "h8",
                    "f4",
                    "e7",
                    "e4",
                    "h3",
                },
                "h3": {
                    "f3",
                    "h1",
                    "b3",
                    "c3",
                    "h7",
                    "f1",
                    "h2",
                    "h5",
                    "d7",
                    "h6",
                    "a3",
                    "d3",
                    "e6",
                    "g4",
                    "g2",
                    "g3",
                    "c8",
                    "f5",
                    "e3",
                    "h8",
                    "h4",
                },
                "h2": {
                    "h1",
                    "h7",
                    "h5",
                    "b2",
                    "d6",
                    "c7",
                    "h3",
                    "h6",
                    "c2",
                    "f2",
                    "e2",
                    "b8",
                    "e5",
                    "a2",
                    "g2",
                    "g3",
                    "g1",
                    "h8",
                    "f4",
                    "d2",
                    "h4",
                },
                "h1": {
                    "f3",
                    "e4",
                    "c1",
                    "h7",
                    "f1",
                    "b1",
                    "h2",
                    "h5",
                    "e1",
                    "h3",
                    "h6",
                    "b7",
                    "d5",
                    "a1",
                    "g2",
                    "g1",
                    "c6",
                    "a8",
                    "h8",
                    "d1",
                    "h4",
                },
            },
        )

    def test_25_source_squares_rook(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["R"],
            {
                "a8": {
                    "a4",
                    "a1",
                    "b8",
                    "f8",
                    "a7",
                    "a2",
                    "a6",
                    "a5",
                    "d8",
                    "c8",
                    "h8",
                    "g8",
                    "e8",
                    "a3",
                },
                "a7": {
                    "b7",
                    "a4",
                    "a1",
                    "g7",
                    "e7",
                    "f7",
                    "a2",
                    "h7",
                    "a6",
                    "a5",
                    "a8",
                    "d7",
                    "c7",
                    "a3",
                },
                "a6": {
                    "g6",
                    "a4",
                    "b6",
                    "a1",
                    "f6",
                    "a7",
                    "a2",
                    "e6",
                    "a5",
                    "d6",
                    "a8",
                    "c6",
                    "h6",
                    "a3",
                },
                "a5": {
                    "d5",
                    "a4",
                    "c5",
                    "a1",
                    "b5",
                    "e5",
                    "g5",
                    "a7",
                    "a2",
                    "a6",
                    "h5",
                    "a8",
                    "f5",
                    "a3",
                },
                "a4": {
                    "c4",
                    "a1",
                    "a7",
                    "a2",
                    "a6",
                    "h4",
                    "g4",
                    "a5",
                    "b4",
                    "a8",
                    "d4",
                    "f4",
                    "e4",
                    "a3",
                },
                "a3": {
                    "d3",
                    "f3",
                    "a4",
                    "a1",
                    "b3",
                    "a7",
                    "c3",
                    "a2",
                    "a6",
                    "a5",
                    "g3",
                    "a8",
                    "e3",
                    "h3",
                },
                "a2": {
                    "a4",
                    "f2",
                    "a1",
                    "e2",
                    "a7",
                    "a6",
                    "g2",
                    "a5",
                    "h2",
                    "b2",
                    "a8",
                    "c2",
                    "d2",
                    "a3",
                },
                "a1": {
                    "a4",
                    "c1",
                    "h1",
                    "a7",
                    "a2",
                    "f1",
                    "a6",
                    "b1",
                    "a5",
                    "g1",
                    "a8",
                    "e1",
                    "d1",
                    "a3",
                },
                "b8": {
                    "h8",
                    "b3",
                    "b5",
                    "f8",
                    "b1",
                    "b4",
                    "b2",
                    "d8",
                    "b6",
                    "c8",
                    "a8",
                    "g8",
                    "e8",
                    "b7",
                },
                "b7": {
                    "b8",
                    "b3",
                    "b5",
                    "g7",
                    "f7",
                    "a7",
                    "e7",
                    "h7",
                    "b1",
                    "b4",
                    "b2",
                    "b6",
                    "d7",
                    "c7",
                },
                "b6": {
                    "g6",
                    "b8",
                    "b3",
                    "b5",
                    "f6",
                    "e6",
                    "a6",
                    "b1",
                    "b4",
                    "b2",
                    "d6",
                    "c6",
                    "h6",
                    "b7",
                },
                "b5": {
                    "d5",
                    "c5",
                    "b8",
                    "b3",
                    "e5",
                    "g5",
                    "b1",
                    "b4",
                    "a5",
                    "b2",
                    "h5",
                    "b6",
                    "f5",
                    "b7",
                },
                "b4": {
                    "a4",
                    "c4",
                    "b8",
                    "b3",
                    "b5",
                    "b1",
                    "h4",
                    "g4",
                    "b2",
                    "b6",
                    "d4",
                    "f4",
                    "e4",
                    "b7",
                },
                "b3": {
                    "d3",
                    "f3",
                    "e3",
                    "b8",
                    "b5",
                    "c3",
                    "a3",
                    "b1",
                    "b4",
                    "g3",
                    "b2",
                    "b6",
                    "h3",
                    "b7",
                },
                "b2": {
                    "f2",
                    "e2",
                    "b8",
                    "b3",
                    "b5",
                    "a2",
                    "b1",
                    "g2",
                    "b4",
                    "h2",
                    "b6",
                    "c2",
                    "d2",
                    "b7",
                },
                "b1": {
                    "c1",
                    "a1",
                    "b8",
                    "b3",
                    "b5",
                    "h1",
                    "f1",
                    "b4",
                    "b2",
                    "g1",
                    "b6",
                    "e1",
                    "d1",
                    "b7",
                },
                "c8": {
                    "h8",
                    "c5",
                    "c4",
                    "c1",
                    "b8",
                    "f8",
                    "c3",
                    "c6",
                    "d8",
                    "c2",
                    "a8",
                    "e8",
                    "g8",
                    "c7",
                },
                "c7": {
                    "c5",
                    "c4",
                    "c1",
                    "g7",
                    "e7",
                    "f7",
                    "c3",
                    "a7",
                    "h7",
                    "c6",
                    "c8",
                    "c2",
                    "d7",
                    "b7",
                },
                "c6": {
                    "c5",
                    "b6",
                    "c4",
                    "c1",
                    "f6",
                    "c3",
                    "e6",
                    "a6",
                    "c8",
                    "d6",
                    "c2",
                    "c7",
                    "h6",
                    "g6",
                },
                "c5": {
                    "d5",
                    "c4",
                    "c1",
                    "b5",
                    "e5",
                    "g5",
                    "c3",
                    "a5",
                    "h5",
                    "c6",
                    "c8",
                    "f5",
                    "c2",
                    "c7",
                },
                "c4": {
                    "c5",
                    "a4",
                    "c1",
                    "c3",
                    "g4",
                    "b4",
                    "c6",
                    "c8",
                    "c2",
                    "d4",
                    "f4",
                    "c7",
                    "e4",
                    "h4",
                },
                "c3": {
                    "d3",
                    "f3",
                    "c5",
                    "c4",
                    "c1",
                    "b3",
                    "a3",
                    "g3",
                    "c6",
                    "c8",
                    "e3",
                    "c2",
                    "c7",
                    "h3",
                },
                "c2": {
                    "c5",
                    "f2",
                    "c4",
                    "c1",
                    "e2",
                    "c3",
                    "a2",
                    "g2",
                    "h2",
                    "c6",
                    "c8",
                    "b2",
                    "d2",
                    "c7",
                },
                "c1": {
                    "c5",
                    "c4",
                    "a1",
                    "h1",
                    "c3",
                    "f1",
                    "b1",
                    "c6",
                    "c8",
                    "g1",
                    "c2",
                    "c7",
                    "d1",
                    "e1",
                },
                "d8": {
                    "d5",
                    "d3",
                    "d2",
                    "h8",
                    "b8",
                    "f8",
                    "g8",
                    "d6",
                    "c8",
                    "a8",
                    "d4",
                    "d7",
                    "e8",
                    "d1",
                },
                "d7": {
                    "d5",
                    "d3",
                    "d2",
                    "g7",
                    "e7",
                    "f7",
                    "a7",
                    "h7",
                    "d6",
                    "d8",
                    "d4",
                    "c7",
                    "d1",
                    "b7",
                },
                "d6": {
                    "d5",
                    "d3",
                    "d2",
                    "b6",
                    "h6",
                    "f6",
                    "e6",
                    "a6",
                    "d8",
                    "c6",
                    "d4",
                    "d7",
                    "d1",
                    "g6",
                },
                "d5": {
                    "d3",
                    "d2",
                    "c5",
                    "b5",
                    "e5",
                    "g5",
                    "a5",
                    "h5",
                    "d6",
                    "d8",
                    "f5",
                    "d4",
                    "d7",
                    "d1",
                },
                "d4": {
                    "d5",
                    "d3",
                    "d2",
                    "a4",
                    "e4",
                    "c4",
                    "g4",
                    "b4",
                    "d6",
                    "d8",
                    "f4",
                    "d7",
                    "d1",
                    "h4",
                },
                "d3": {
                    "d5",
                    "d2",
                    "f3",
                    "b3",
                    "c3",
                    "a3",
                    "g3",
                    "d6",
                    "d8",
                    "e3",
                    "d4",
                    "d7",
                    "d1",
                    "h3",
                },
                "d2": {
                    "d5",
                    "d3",
                    "f2",
                    "e2",
                    "a2",
                    "g2",
                    "h2",
                    "d6",
                    "d8",
                    "b2",
                    "c2",
                    "d4",
                    "d7",
                    "d1",
                },
                "d1": {
                    "d5",
                    "d3",
                    "d2",
                    "c1",
                    "a1",
                    "h1",
                    "f1",
                    "b1",
                    "d6",
                    "d8",
                    "g1",
                    "d4",
                    "d7",
                    "e1",
                },
                "e8": {
                    "h8",
                    "e2",
                    "b8",
                    "e5",
                    "f8",
                    "e6",
                    "g8",
                    "d8",
                    "c8",
                    "e3",
                    "a8",
                    "e7",
                    "e4",
                    "e1",
                },
                "e7": {
                    "b7",
                    "d7",
                    "e2",
                    "g7",
                    "c7",
                    "e5",
                    "f7",
                    "a7",
                    "e6",
                    "h7",
                    "e3",
                    "e8",
                    "e4",
                    "e1",
                },
                "e6": {
                    "g6",
                    "b6",
                    "e2",
                    "h6",
                    "e5",
                    "f6",
                    "a6",
                    "d6",
                    "c6",
                    "e3",
                    "e7",
                    "e8",
                    "e4",
                    "e1",
                },
                "e5": {
                    "d5",
                    "c5",
                    "e2",
                    "b5",
                    "g5",
                    "e6",
                    "a5",
                    "h5",
                    "f5",
                    "e3",
                    "e7",
                    "e8",
                    "e4",
                    "e1",
                },
                "e4": {
                    "a4",
                    "c4",
                    "e2",
                    "e5",
                    "e6",
                    "h4",
                    "g4",
                    "b4",
                    "e3",
                    "d4",
                    "f4",
                    "e7",
                    "e8",
                    "e1",
                },
                "e3": {
                    "d3",
                    "f3",
                    "e2",
                    "b3",
                    "e5",
                    "c3",
                    "e6",
                    "a3",
                    "g3",
                    "e7",
                    "e8",
                    "h3",
                    "e4",
                    "e1",
                },
                "e2": {
                    "d2",
                    "f2",
                    "e5",
                    "e6",
                    "a2",
                    "g2",
                    "h2",
                    "b2",
                    "e3",
                    "c2",
                    "e7",
                    "e8",
                    "e4",
                    "e1",
                },
                "e1": {
                    "d1",
                    "c1",
                    "e2",
                    "a1",
                    "h1",
                    "e5",
                    "e6",
                    "f1",
                    "b1",
                    "g1",
                    "e3",
                    "e7",
                    "e8",
                    "e4",
                },
                "f8": {
                    "h8",
                    "f3",
                    "f2",
                    "b8",
                    "f7",
                    "f6",
                    "f1",
                    "d8",
                    "f5",
                    "c8",
                    "a8",
                    "f4",
                    "g8",
                    "e8",
                },
                "f7": {
                    "f3",
                    "f2",
                    "g7",
                    "e7",
                    "f8",
                    "f6",
                    "a7",
                    "h7",
                    "f1",
                    "f5",
                    "f4",
                    "d7",
                    "c7",
                    "b7",
                },
                "f6": {
                    "f3",
                    "f2",
                    "b6",
                    "f7",
                    "f8",
                    "e6",
                    "f1",
                    "a6",
                    "d6",
                    "f5",
                    "c6",
                    "f4",
                    "h6",
                    "g6",
                },
                "f5": {
                    "d5",
                    "f3",
                    "f2",
                    "c5",
                    "b5",
                    "f7",
                    "f8",
                    "f6",
                    "e5",
                    "g5",
                    "f1",
                    "a5",
                    "h5",
                    "f4",
                },
                "f4": {
                    "f3",
                    "f2",
                    "a4",
                    "c4",
                    "f7",
                    "f8",
                    "f6",
                    "f1",
                    "g4",
                    "b4",
                    "f5",
                    "d4",
                    "e4",
                    "h4",
                },
                "f3": {
                    "d3",
                    "f2",
                    "b3",
                    "f7",
                    "f8",
                    "f6",
                    "c3",
                    "f1",
                    "a3",
                    "g3",
                    "f5",
                    "e3",
                    "f4",
                    "h3",
                },
                "f2": {
                    "f3",
                    "e2",
                    "f7",
                    "f8",
                    "f6",
                    "a2",
                    "f1",
                    "g2",
                    "h2",
                    "b2",
                    "f5",
                    "c2",
                    "f4",
                    "d2",
                },
                "f1": {
                    "f3",
                    "f2",
                    "c1",
                    "a1",
                    "h1",
                    "f7",
                    "f8",
                    "f6",
                    "b1",
                    "g1",
                    "f5",
                    "f4",
                    "d1",
                    "e1",
                },
                "g8": {
                    "h8",
                    "g6",
                    "g7",
                    "b8",
                    "g5",
                    "f8",
                    "g2",
                    "g3",
                    "g1",
                    "d8",
                    "c8",
                    "a8",
                    "e8",
                    "g4",
                },
                "g7": {
                    "g6",
                    "b7",
                    "d7",
                    "g5",
                    "f7",
                    "e7",
                    "a7",
                    "h7",
                    "g2",
                    "g3",
                    "g1",
                    "g8",
                    "c7",
                    "g4",
                },
                "g6": {
                    "b6",
                    "g7",
                    "g5",
                    "f6",
                    "e6",
                    "a6",
                    "g2",
                    "g3",
                    "g1",
                    "d6",
                    "c6",
                    "g8",
                    "h6",
                    "g4",
                },
                "g5": {
                    "d5",
                    "g6",
                    "c5",
                    "g7",
                    "b5",
                    "e5",
                    "g2",
                    "a5",
                    "g3",
                    "g1",
                    "h5",
                    "f5",
                    "g8",
                    "g4",
                },
                "g4": {
                    "g6",
                    "a4",
                    "c4",
                    "g7",
                    "g5",
                    "h4",
                    "g2",
                    "b4",
                    "g3",
                    "g1",
                    "d4",
                    "f4",
                    "g8",
                    "e4",
                },
                "g3": {
                    "g6",
                    "d3",
                    "f3",
                    "g7",
                    "b3",
                    "g5",
                    "c3",
                    "a3",
                    "g2",
                    "g1",
                    "e3",
                    "g8",
                    "h3",
                    "g4",
                },
                "g2": {
                    "g6",
                    "d2",
                    "f2",
                    "e2",
                    "g7",
                    "g5",
                    "a2",
                    "h2",
                    "g3",
                    "g1",
                    "b2",
                    "c2",
                    "g8",
                    "g4",
                },
                "g1": {
                    "g6",
                    "e1",
                    "c1",
                    "a1",
                    "g7",
                    "h1",
                    "g5",
                    "f1",
                    "b1",
                    "g2",
                    "g3",
                    "g8",
                    "d1",
                    "g4",
                },
                "h8": {
                    "h1",
                    "b8",
                    "f8",
                    "h7",
                    "h2",
                    "h5",
                    "d8",
                    "c8",
                    "a8",
                    "g8",
                    "e8",
                    "h3",
                    "h6",
                    "h4",
                },
                "h7": {
                    "b7",
                    "h1",
                    "g7",
                    "e7",
                    "f7",
                    "a7",
                    "h2",
                    "h5",
                    "h8",
                    "d7",
                    "c7",
                    "h3",
                    "h6",
                    "h4",
                },
                "h6": {
                    "g6",
                    "h1",
                    "f6",
                    "h7",
                    "e6",
                    "a6",
                    "h2",
                    "h5",
                    "d6",
                    "c6",
                    "b6",
                    "h8",
                    "h3",
                    "h4",
                },
                "h5": {
                    "d5",
                    "c5",
                    "h1",
                    "b5",
                    "e5",
                    "g5",
                    "h7",
                    "h2",
                    "a5",
                    "f5",
                    "h8",
                    "h3",
                    "h6",
                    "h4",
                },
                "h4": {
                    "e4",
                    "a4",
                    "c4",
                    "h1",
                    "h7",
                    "g4",
                    "h2",
                    "h5",
                    "b4",
                    "h8",
                    "d4",
                    "f4",
                    "h3",
                    "h6",
                },
                "h3": {
                    "d3",
                    "f3",
                    "h1",
                    "b3",
                    "c3",
                    "h7",
                    "a3",
                    "h2",
                    "h5",
                    "g3",
                    "e3",
                    "h8",
                    "h6",
                    "h4",
                },
                "h2": {
                    "c2",
                    "f2",
                    "h1",
                    "e2",
                    "h7",
                    "a2",
                    "h5",
                    "g2",
                    "b2",
                    "h8",
                    "d2",
                    "h3",
                    "h6",
                    "h4",
                },
                "h1": {
                    "d1",
                    "c1",
                    "a1",
                    "h7",
                    "f1",
                    "b1",
                    "h2",
                    "h5",
                    "g1",
                    "h8",
                    "e1",
                    "h3",
                    "h6",
                    "h4",
                },
            },
        )

    def test_26_source_squares_bishop(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["B"],
            {
                "a8": {"d5", "f3", "h1", "g2", "c6", "e4", "b7"},
                "a7": {"c5", "f2", "b6", "b8", "g1", "e3", "d4"},
                "a6": {"d3", "c4", "e2", "b5", "f1", "c8", "b7"},
                "a5": {"c3", "b4", "d8", "b6", "d2", "c7", "e1"},
                "a4": {"b3", "b5", "c6", "c2", "d7", "e8", "d1"},
                "a3": {"c5", "c1", "f8", "b4", "b2", "d6", "e7"},
                "a2": {"d5", "c4", "b3", "f7", "e6", "b1", "g8"},
                "a1": {"g7", "f6", "e5", "c3", "b2", "h8", "d4"},
                "b8": {"e5", "a7", "h2", "g3", "d6", "f4", "c7"},
                "b7": {"d5", "f3", "h1", "a6", "g2", "c6", "a8", "c8", "e4"},
                "b6": {"c5", "f2", "a7", "a5", "g1", "d8", "e3", "d4", "c7"},
                "b5": {"d3", "a4", "c4", "e2", "f1", "a6", "c6", "d7", "e8"},
                "b4": {"c5", "e7", "f8", "c3", "a3", "a5", "d6", "d2", "e1"},
                "b3": {"d5", "a4", "c4", "f7", "e6", "a2", "c2", "g8", "d1"},
                "b2": {"c1", "a1", "g7", "f6", "e5", "c3", "h8", "d4", "a3"},
                "b1": {"d3", "a2", "h7", "f5", "c2", "e4", "g6"},
                "c8": {"b7", "e6", "a6", "f5", "d7", "h3", "g4"},
                "c7": {"b8", "e5", "h2", "a5", "g3", "d6", "d8", "b6", "f4"},
                "c6": {
                    "d5",
                    "f3",
                    "a4",
                    "h1",
                    "b5",
                    "g2",
                    "a8",
                    "d7",
                    "e8",
                    "e4",
                    "b7",
                },
                "c5": {
                    "f2",
                    "b6",
                    "f8",
                    "a7",
                    "b4",
                    "g1",
                    "d6",
                    "e3",
                    "d4",
                    "e7",
                    "a3",
                },
                "c4": {
                    "d5",
                    "d3",
                    "e2",
                    "b3",
                    "b5",
                    "f7",
                    "e6",
                    "f1",
                    "a6",
                    "a2",
                    "g8",
                },
                "c3": {
                    "a1",
                    "g7",
                    "f6",
                    "e5",
                    "b4",
                    "a5",
                    "b2",
                    "h8",
                    "d4",
                    "d2",
                    "e1",
                },
                "c2": {"d3", "e4", "a4", "b3", "h7", "b1", "f5", "d1", "g6"},
                "c1": {"g5", "b2", "e3", "f4", "d2", "h6", "a3"},
                "d8": {"g5", "f6", "a5", "b6", "e7", "c7", "h4"},
                "d7": {"a4", "b5", "e6", "c8", "f5", "c6", "e8", "h3", "g4"},
                "d6": {
                    "c5",
                    "b8",
                    "e5",
                    "f8",
                    "h2",
                    "b4",
                    "g3",
                    "f4",
                    "e7",
                    "c7",
                    "a3",
                },
                "d5": {
                    "f3",
                    "c4",
                    "h1",
                    "b3",
                    "f7",
                    "e6",
                    "a2",
                    "g2",
                    "c6",
                    "a8",
                    "g8",
                    "e4",
                    "b7",
                },
                "d4": {
                    "c5",
                    "f2",
                    "b6",
                    "a1",
                    "g7",
                    "f6",
                    "e5",
                    "a7",
                    "c3",
                    "g1",
                    "b2",
                    "e3",
                    "h8",
                },
                "d3": {
                    "c4",
                    "e2",
                    "b5",
                    "h7",
                    "f1",
                    "a6",
                    "b1",
                    "f5",
                    "c2",
                    "e4",
                    "g6",
                },
                "d2": {"c1", "g5", "c3", "b4", "a5", "e3", "f4", "h6", "e1"},
                "d1": {"f3", "a4", "e2", "b3", "h5", "c2", "g4"},
                "e8": {"a4", "b5", "f7", "h5", "c6", "d7", "g6"},
                "e7": {"c5", "g5", "f6", "f8", "a3", "b4", "d8", "d6", "h4"},
                "e6": {
                    "d5",
                    "c4",
                    "b3",
                    "f7",
                    "a2",
                    "g8",
                    "c8",
                    "f5",
                    "d7",
                    "h3",
                    "g4",
                },
                "e5": {
                    "a1",
                    "b8",
                    "g7",
                    "f6",
                    "c3",
                    "h2",
                    "g3",
                    "d6",
                    "b2",
                    "h8",
                    "d4",
                    "f4",
                    "c7",
                },
                "e4": {
                    "d5",
                    "f3",
                    "d3",
                    "g6",
                    "h1",
                    "h7",
                    "b1",
                    "g2",
                    "c6",
                    "a8",
                    "f5",
                    "c2",
                    "b7",
                },
                "e3": {
                    "c5",
                    "f2",
                    "b6",
                    "c1",
                    "g5",
                    "a7",
                    "g1",
                    "d4",
                    "f4",
                    "d2",
                    "h6",
                },
                "e2": {"d3", "f3", "c4", "b5", "f1", "a6", "h5", "d1", "g4"},
                "e1": {"f2", "c3", "h4", "b4", "a5", "g3", "d2"},
                "f8": {"c5", "g7", "b4", "d6", "e7", "h6", "a3"},
                "f7": {"d5", "c4", "b3", "e6", "a2", "h5", "g8", "e8", "g6"},
                "f6": {
                    "a1",
                    "g7",
                    "g5",
                    "e5",
                    "c3",
                    "d8",
                    "b2",
                    "h8",
                    "d4",
                    "e7",
                    "h4",
                },
                "f5": {
                    "d3",
                    "g6",
                    "e6",
                    "h7",
                    "b1",
                    "c8",
                    "c2",
                    "d7",
                    "h3",
                    "e4",
                    "g4",
                },
                "f4": {
                    "c1",
                    "b8",
                    "g5",
                    "e5",
                    "h2",
                    "g3",
                    "d6",
                    "e3",
                    "d2",
                    "c7",
                    "h6",
                },
                "f3": {
                    "d5",
                    "d1",
                    "h1",
                    "e2",
                    "g4",
                    "g2",
                    "h5",
                    "c6",
                    "a8",
                    "e4",
                    "b7",
                },
                "f2": {"c5", "b6", "a7", "h4", "g3", "g1", "e3", "d4", "e1"},
                "f1": {"d3", "c4", "e2", "b5", "a6", "g2", "h3"},
                "g8": {"d5", "c4", "b3", "f7", "h7", "e6", "a2"},
                "g7": {"a1", "f6", "f8", "e5", "c3", "b2", "h8", "d4", "h6"},
                "g6": {"d3", "f7", "h7", "b1", "h5", "f5", "c2", "e8", "e4"},
                "g5": {"d2", "c1", "f6", "d8", "e3", "f4", "e7", "h6", "h4"},
                "g4": {"f3", "e2", "e6", "h5", "c8", "f5", "d7", "h3", "d1"},
                "g3": {"f2", "b8", "e5", "h4", "h2", "d6", "f4", "c7", "e1"},
                "g2": {"d5", "f3", "h1", "f1", "c6", "a8", "h3", "e4", "b7"},
                "g1": {"c5", "f2", "b6", "a7", "h2", "e3", "d4"},
                "h8": {"a1", "g7", "f6", "e5", "c3", "b2", "d4"},
                "h7": {"d3", "b1", "f5", "c2", "g8", "e4", "g6"},
                "h6": {"c1", "g7", "g5", "f8", "e3", "f4", "d2"},
                "h5": {"f3", "e2", "f7", "g4", "e8", "d1", "g6"},
                "h4": {"e1", "f2", "g5", "f6", "g3", "d8", "e7"},
                "h3": {"e6", "f1", "g2", "c8", "f5", "d7", "g4"},
                "h2": {"b8", "e5", "g3", "d6", "g1", "f4", "c7"},
                "h1": {"d5", "f3", "g2", "c6", "a8", "e4", "b7"},
            },
        )

    def test_27_source_squares_knight(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["N"],
            {
                "a8": {"c7", "b6"},
                "a7": {"b5", "c6", "c8"},
                "a6": {"b4", "c5", "c7", "b8"},
                "a5": {"b3", "c6", "c4", "b7"},
                "a4": {"c5", "c3", "b2", "b6"},
                "a3": {"c2", "b5", "b1", "c4"},
                "a2": {"b4", "c3", "c1"},
                "a1": {"c2", "b3"},
                "b8": {"a6", "d7", "c6"},
                "b7": {"d8", "c5", "a5", "d6"},
                "b6": {"d5", "a4", "c4", "c8", "a8", "d7"},
                "b5": {"c3", "a7", "d6", "d4", "c7", "a3"},
                "b4": {"d5", "d3", "a2", "a6", "c6", "c2"},
                "b3": {"c5", "c1", "a1", "a5", "d4", "d2"},
                "b2": {"d3", "a4", "c4", "d1"},
                "b1": {"d2", "c3", "a3"},
                "c8": {"e7", "a7", "d6", "b6"},
                "c7": {"d5", "b5", "e6", "a6", "a8", "e8"},
                "c6": {"b8", "e5", "a7", "a5", "b4", "d8", "d4", "e7"},
                "c5": {"d3", "a4", "b3", "e6", "a6", "d7", "e4", "b7"},
                "c4": {"b6", "e5", "a5", "d6", "b2", "e3", "d2", "a3"},
                "c3": {"d5", "e4", "a4", "e2", "b5", "a2", "b1", "d1"},
                "c2": {"a1", "b4", "e3", "d4", "e1", "a3"},
                "c1": {"b3", "d3", "a2", "e2"},
                "d8": {"f7", "c6", "e6", "b7"},
                "d7": {"c5", "b8", "e5", "f6", "f8", "b6"},
                "d6": {"c4", "b5", "f7", "c8", "f5", "e8", "e4", "b7"},
                "d5": {"e3", "f6", "c3", "b4", "b6", "f4", "e7", "c7"},
                "d4": {"f3", "e2", "b3", "b5", "e6", "c6", "f5", "c2"},
                "d3": {"f2", "c5", "c1", "e5", "b4", "b2", "f4", "e1"},
                "d2": {"f3", "c4", "b3", "f1", "b1", "e4"},
                "d1": {"f2", "c3", "b2", "e3"},
                "e8": {"f6", "c7", "d6", "g7"},
                "e7": {"d5", "c6", "c8", "f5", "g8", "g6"},
                "e6": {"c5", "g7", "g5", "f8", "d8", "d4", "f4", "c7"},
                "e5": {"f3", "d3", "c4", "f7", "g4", "c6", "d7", "g6"},
                "e4": {"f2", "c5", "g5", "f6", "c3", "g3", "d6", "d2"},
                "e3": {"d5", "c4", "f1", "g2", "f5", "c2", "d1", "g4"},
                "e2": {"c1", "c3", "g3", "g1", "d4", "f4"},
                "e1": {"c2", "f3", "g2", "d3"},
                "f8": {"e6", "d7", "h7", "g6"},
                "f7": {"g5", "e5", "d6", "d8", "h8", "h6"},
                "f6": {"d5", "h7", "h5", "g8", "d7", "e8", "e4", "g4"},
                "f5": {"g7", "g3", "d6", "e3", "d4", "e7", "h6", "h4"},
                "f4": {"d5", "d3", "e2", "e6", "g2", "h5", "h3", "g6"},
                "f3": {"e1", "g5", "e5", "h2", "g1", "d4", "d2", "h4"},
                "f2": {"d3", "e4", "h1", "h3", "d1", "g4"},
                "f1": {"h2", "d2", "g3", "e3"},
                "g8": {"f6", "e7", "h6"},
                "g7": {"f5", "h5", "e8", "e6"},
                "g6": {"e5", "f8", "h8", "f4", "e7", "h4"},
                "g5": {"f3", "f7", "e6", "h7", "e4", "h3"},
                "g4": {"f2", "e5", "f6", "h2", "e3", "h6"},
                "g3": {"e2", "h1", "f1", "h5", "f5", "e4"},
                "g2": {"f4", "e1", "e3", "h4"},
                "g1": {"f3", "e2", "h3"},
                "h8": {"f7", "g6"},
                "h7": {"g5", "f6", "f8"},
                "h6": {"f7", "g8", "f5", "g4"},
                "h5": {"f4", "f6", "g3", "g7"},
                "h4": {"f3", "g2", "f5", "g6"},
                "h3": {"g5", "f4", "f2", "g1"},
                "h2": {"f3", "g4", "f1"},
                "h1": {"f2", "g3"},
            },
        )

    def test_28_source_squares_white_pawn_non_capture(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["P"],
            {
                "a3": {"a2"},
                "a4": {"a2", "a3"},
                "a5": {"a4"},
                "a6": {"a5"},
                "a7": {"a6"},
                "a8": {"a7"},
                "b3": {"b2"},
                "b4": {"b3", "b2"},
                "b5": {"b4"},
                "b6": {"b5"},
                "b7": {"b6"},
                "b8": {"b7"},
                "c3": {"c2"},
                "c4": {"c2", "c3"},
                "c5": {"c4"},
                "c6": {"c5"},
                "c7": {"c6"},
                "c8": {"c7"},
                "d3": {"d2"},
                "d4": {"d3", "d2"},
                "d5": {"d4"},
                "d6": {"d5"},
                "d7": {"d6"},
                "d8": {"d7"},
                "e3": {"e2"},
                "e4": {"e2", "e3"},
                "e5": {"e4"},
                "e6": {"e5"},
                "e7": {"e6"},
                "e8": {"e7"},
                "f3": {"f2"},
                "f4": {"f3", "f2"},
                "f5": {"f4"},
                "f6": {"f5"},
                "f7": {"f6"},
                "f8": {"f7"},
                "g3": {"g2"},
                "g4": {"g2", "g3"},
                "g5": {"g4"},
                "g6": {"g5"},
                "g7": {"g6"},
                "g8": {"g7"},
                "h3": {"h2"},
                "h4": {"h2", "h3"},
                "h5": {"h4"},
                "h6": {"h5"},
                "h7": {"h6"},
                "h8": {"h7"},
            },
        )

    def test_29_source_squares_black_pawn_non_capture(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["p"],
            {
                "a6": {"a7"},
                "a5": {"a6", "a7"},
                "a4": {"a5"},
                "a3": {"a4"},
                "a2": {"a3"},
                "a1": {"a2"},
                "b6": {"b7"},
                "b5": {"b7", "b6"},
                "b4": {"b5"},
                "b3": {"b4"},
                "b2": {"b3"},
                "b1": {"b2"},
                "c6": {"c7"},
                "c5": {"c7", "c6"},
                "c4": {"c5"},
                "c3": {"c4"},
                "c2": {"c3"},
                "c1": {"c2"},
                "d6": {"d7"},
                "d5": {"d7", "d6"},
                "d4": {"d5"},
                "d3": {"d4"},
                "d2": {"d3"},
                "d1": {"d2"},
                "e6": {"e7"},
                "e5": {"e7", "e6"},
                "e4": {"e5"},
                "e3": {"e4"},
                "e2": {"e3"},
                "e1": {"e2"},
                "f6": {"f7"},
                "f5": {"f6", "f7"},
                "f4": {"f5"},
                "f3": {"f4"},
                "f2": {"f3"},
                "f1": {"f2"},
                "g6": {"g7"},
                "g5": {"g7", "g6"},
                "g4": {"g5"},
                "g3": {"g4"},
                "g2": {"g3"},
                "g1": {"g2"},
                "h6": {"h7"},
                "h5": {"h7", "h6"},
                "h4": {"h5"},
                "h3": {"h4"},
                "h2": {"h3"},
                "h1": {"h2"},
            },
        )

    def test_30_source_squares_white_pawn_capture(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["Px"],
            {
                "a3": {"b2"},
                "a4": {"b3"},
                "a5": {"b4"},
                "a6": {"b5"},
                "a7": {"b6"},
                "a8": {"b7"},
                "b3": {"c2", "a2"},
                "b4": {"c3", "a3"},
                "b5": {"a4", "c4"},
                "b6": {"c5", "a5"},
                "b7": {"a6", "c6"},
                "b8": {"a7", "c7"},
                "c3": {"d2", "b2"},
                "c4": {"b3", "d3"},
                "c5": {"d4", "b4"},
                "c6": {"d5", "b5"},
                "c7": {"d6", "b6"},
                "c8": {"d7", "b7"},
                "d3": {"c2", "e2"},
                "d4": {"c3", "e3"},
                "d5": {"c4", "e4"},
                "d6": {"e5", "c5"},
                "d7": {"c6", "e6"},
                "d8": {"e7", "c7"},
                "e3": {"d2", "f2"},
                "e4": {"f3", "d3"},
                "e5": {"d4", "f4"},
                "e6": {"d5", "f5"},
                "e7": {"f6", "d6"},
                "e8": {"f7", "d7"},
                "f3": {"g2", "e2"},
                "f4": {"g3", "e3"},
                "f5": {"e4", "g4"},
                "f6": {"g5", "e5"},
                "f7": {"e6", "g6"},
                "f8": {"e7", "g7"},
                "g3": {"h2", "f2"},
                "g4": {"f3", "h3"},
                "g5": {"f4", "h4"},
                "g6": {"h5", "f5"},
                "g7": {"f6", "h6"},
                "g8": {"f7", "h7"},
                "h3": {"g2"},
                "h4": {"g3"},
                "h5": {"g4"},
                "h6": {"g5"},
                "h7": {"g6"},
                "h8": {"g7"},
            },
        )

    def test_31_source_squares_black_pawn_capture(self):
        ae = self.assertEqual
        sss = squares.source_squares
        ae(
            sss["px"],
            {
                "a1": {"b2"},
                "a2": {"b3"},
                "a3": {"b4"},
                "a4": {"b5"},
                "a5": {"b6"},
                "a6": {"b7"},
                "b1": {"c2", "a2"},
                "b2": {"c3", "a3"},
                "b3": {"a4", "c4"},
                "b4": {"c5", "a5"},
                "b5": {"a6", "c6"},
                "b6": {"a7", "c7"},
                "c1": {"d2", "b2"},
                "c2": {"b3", "d3"},
                "c3": {"d4", "b4"},
                "c4": {"d5", "b5"},
                "c5": {"d6", "b6"},
                "c6": {"d7", "b7"},
                "d1": {"c2", "e2"},
                "d2": {"c3", "e3"},
                "d3": {"c4", "e4"},
                "d4": {"e5", "c5"},
                "d5": {"c6", "e6"},
                "d6": {"e7", "c7"},
                "e1": {"d2", "f2"},
                "e2": {"f3", "d3"},
                "e3": {"d4", "f4"},
                "e4": {"d5", "f5"},
                "e5": {"f6", "d6"},
                "e6": {"f7", "d7"},
                "f1": {"g2", "e2"},
                "f2": {"g3", "e3"},
                "f3": {"e4", "g4"},
                "f4": {"g5", "e5"},
                "f5": {"e6", "g6"},
                "f6": {"e7", "g7"},
                "g1": {"h2", "f2"},
                "g2": {"f3", "h3"},
                "g3": {"f4", "h4"},
                "g4": {"h5", "f5"},
                "g5": {"f6", "h6"},
                "g6": {"f7", "h7"},
                "h1": {"g2"},
                "h2": {"g3"},
                "h3": {"g4"},
                "h4": {"g5"},
                "h5": {"g6"},
                "h6": {"g7"},
            },
        )


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase

    runner().run(loader(_Square))
    runner().run(loader(Squares))
