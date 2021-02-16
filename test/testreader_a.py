# testreader_a.py
# Copyright 2015 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test Portable Game Notation (PGN) reader.

The *_b.pgn and *_c.pgn samples were not considered because fixing for *_a.pgn
got the source *.pgn file to not raise an exception.

The source pgn is a downloaded collection of California games - URL forgotten.

"""


if __name__ == '__main__':

    import datetime
    import io

    from pgn.core.reader import PGNReader

    pgndata = b'\n'.join((
        b'',
        b'[Event "Northern California Masters"]',
        b'[Site "Berkeley"]',
        b'[Date "1981.02.27"]',
        b'[Round "7"]',
        b'[White "Hanken, Jerome"]',
        b'[Black "Osbun, Erik"]',
        b'[Result "1-0"]',
        b'[ECO "A10"]',
        b'[PlyCount "91"]',
        b'[EventDate "1981.??.??"]',
        b'',
        b"1. c4 f5 2. Nc3 Nf6 3. g3 e6 4. Bg2 Be7 5. e3 {%02 [ Popularized in the",
        b"Botvinnik - Bronstein World Championship Match of 1951, when both players",
        b"tried it. ]} 5... O-O 6. Nge2 c6 7. O-O Na6 {%02 [ An interesting departure,",
        b"but perhaps best is 7...d6 8.d4 e5 9.d5 Qe8! 10.e4 Qh5 11.ef Bxf5 12.f3 Qg6 13.",
        b"Be3 Nbd7 14.Qd2 cd ( Botvinnik - Bronstein, 1st Match Game,1951 ). Whence 15.",
        b"Nxd5 Nxd5 16.cxd5 is thought to be approximately equal, Botvinnik. ]} 8. d4 d5",
        b'{%02 [ Last chance for 8...d6, but I chose the "Stonewall." ]} 9. b3 Nc7 10.',
        b"Bb2 Nce8 11. Qd3 Nd6 12. Ba3 {%02 [ ? White should play 12.f3, which reaches a",
        b"position that should have occurred with best play in the 22nd game of the",
        b"Bronstein - Botvinnik Match. White will play e4 as Boleslavsky analyzed. ]}",
        b"12... Qa5 {%02 [ ?! Forcing a decision that White had no doubt intended anyway,",
        b"so possibly 12...Bd7 makes more sense. ]} 13. Bxd6 Bxd6 14. c5 Be7 15. a3 Qd8",
        b"16. b4 Qe8 {%02 [ ?! Here also 16...Bd7 may be better. ]} 17. Qd1 {",
        b"[ Planning to meet 17...Qh5 with 18.Nf4 Qh6 19.Nd3. ]} 17... g5 18. f4 {",
        b"[ ? Very committing, 'better is' 18.f3. ]} 18... Ng4 19. Qd3 Qh5 20. h3 Nf6 21.",
        b"Kh2 Kh8 22. Nc1 Rg8 23. Qe2 Qh6 24. Nd3 Bd7 25. fxg5 {",
        b"[ ? This could have cost the game. 25.Ne5 Be8 should be played. ]} 25... Qxg5 {",
        # Removing the "%" stops the exception without changing either "1)" or "2)".
        # Exception is "IndexError: list index out of range" in method (it was line 1635)
        # _end_variation_containing_error at "if self.ravstack[-1] is not None:".
        b"%02 [ ? Wrong recapture, 25....Rxg5 as suggested by a team of post-mortem",
        # The "1)" causes an exception.
        b"analysts would win: 1) 26.Ne5 Ng4+ 27.Nxg4 Rxg4 28.Bf3 Rg7 29.Rg1 Rag8 30.Rg2",
        # The "2)" causes an exception when "1)" changed to, say, "1:".
        b"Bf6 followed by 31...e5, 2) 26.Nf4 R8g8 27.Rf3 Ne4 28.Qe1 Nxg3 29. Rxg3 Rxg3",
        b"30.Qxg3 Rxg3 31.Kxg3 Bf6 followed by 32...e5.]} 26. Qf2 Rg7 27. Qf4 {",
        # "%" escapes the "} 27... Qh5 {" and should generate a PGN error at "28. Bf3 ".
        b"%02 [ A great post for the Q. ]} 27... Qh5 {",
        b"[ ? 'better is' 27...R8g8, allowing the exchange of Qs. ]} 28. Bf3 Qe8 29. Ne2",
        b"Ne4 30. Bxe4 fxe4 {%02 [ ? Opens too many lines. 30...dxe4 is necessary. ]} 31.",
        b"Ne5 Kg8 32. h4 Rd8 33. Qf2 Qh5 34. Nf4 Qh6 35. Nh3 Be8 36. Qf4 Qh5 37. Rf2 Bg6",
        b"38. Ng4 Kh8 39. Nh6 Bf5 40. Nxf5 exf5 {%02 Adjourned.} 41. Qxf5 Qh6 42. Raf1",
        b"Qxe3 43. Qe5 Rdg8 44. Rf7 Qxg3+ {+} 45. Qxg3 Rxg3 46. Rxe7 {Black resigns.} 1-0",
        b'',
        ))

    print(datetime.datetime.now().isoformat())
    pgn = PGNReader()
    #source = open('/usr/home/roger/games_in_pgn/pgn/Crafty06.pgn', 'rbU')
    source = io.BytesIO(pgndata)
    gamecount = 0
    movecount = 0
    #positioncount = 0
    #positionlength = 0
    try:
        for d in pgn.get_games(source):
            pgn.process_game()
            gamecount += 1
            movecount += len(pgn.tokens)
            #positioncount += len(pgn.positions)
            #positionlength += sum([len(p) for p in pgn.positions])
            # len(pgn.positions) should be 53 if the first escape "%" is disabled somehow,
            # leaving the second escape "%" to exclude black's move 27.
            # With both escape "%"s disabled the length is 91.
            print(len(pgn.positions))
    except:
        # 50 with original text and exception raised.
        # 50 with "1)" changed to "1:" and exception raised.
        # 50 with "1)" and "2)" changed to "1:" and "2:" with no exception.
        print(len(pgn.positions))
        #print(pgn.gametokens)
        #print()
        #print(pgn.tokens)
        #print()
        #print(pgn.piece_locations)
        #print()
        #print(pgn.occupied_square_pieces)
        #print()
        #print(pgn.side_to_move)
        raise
    source.close()
    print(datetime.datetime.now().isoformat())
    print(gamecount, movecount)#, positioncount, positionlength / positioncount
    print(pgn._tags_valid, pgn.is_tag_roster_valid())
    
