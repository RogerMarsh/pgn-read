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


if __name__ == "__main__":
    runner = unittest.TextTestRunner
    loader = unittest.defaultTestLoader.loadTestsFromTestCase

    runner().run(loader(_Square))
    runner().run(loader(Squares))
