# testconstants.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test Constants for Portable Game Notation (PGN) parser."""

if __name__ == '__main__':

    import re

    from pgn.core import constants

    games = ''.join((
        '[Event "4NCL-9899A BA1-BA2"]',
        '[Site "Rd1-Warwick"]',
        '[Date "1998.10.24"]',
        '[Round "1.2"]',
        '[White "Lewis, Andrew P"]',
        '[Black "Rogers, Jonathan"]',
        '[Result "1/2-1/2"]',
        '[ECO "A10"]',
        '[WhiteElo "2275"]',
        '[BlackElo "2355"]',
        '[PlyCount "74"]',
        '[EventDate "1998.10.24"]',
        '\n',
        '1. c4 e6 2. Nf3 f5 3. g3 Nf6 4. Bg2 Be7 5. O-O O-O 6. b3 Ne4 7. Bb2 Bf6 8. Qc1',
        'Nc6 9. d3 Bxb2 10. Qxb2 Qf6 11. Qxf6 Nxf6 12. Nc3 d6 13. Rab1 Bd7 14. Rfc1 a6',
        '15. b4 h6 16. d4 Rae8 17. e3 Nd8 18. a4 g5 19. a5 f4 20. exf4 gxf4 21. b5 fxg3',
        '22. hxg3 Ng4 23. Rb2 Kg7 24. Ne4 Nf7 25. Nh2 Nxh2 26. Kxh2 Rb8 27. Kg1 Rfc8 28.',
        'Rcb1 axb5 29. cxb5 Ra8 30. Ra2 Ra7 31. a6 Rca8 32. Nc3 d5 33. Nxd5 exd5 34.',
        'Bxd5 Rd8 35. axb7 Rxa2 36. Bxa2 Nd6 37. b6 c6 1/2-1/2',
        '\r\n',
        '[Event"National Club: Gosport - Wood Green"]',
        '[Site"Gosport"]',
        '[Date"1989.05.07"]',
        '[Round"QFinal"]',
        '[White"Sowray P J"]',
        '[  Black  "Mar\"sh R"   ]  \n ',
        '[Result"1-0"]',
        'e4c6d4d5exd5cxd5c4Nf6c5e6Nc3b6b4a5Bf4axb4Nb5Na6Qa4Bd7',
        'Bc7Nxc5Qd1Qc8dxc5bxc5Nf3Qb7Nd6Bxd6Bxd6Qb6Be5Ke7Be2Ne4O-Of6Bb2Nc3',
        'Bxc3bxc3Qd3(Qb3)Ra3Rfb1Qa7Qc2g6Rb3d4Bc4Rxb3Bxb3Qa6a4Rb8a5e5Bd5Rb2',
        'Qe4Bf5Qh4Qd3(c2(g5))g4Rb1Rxb1Qxb1Kg2Kd6Qxf6Kxd5Qxe5Kc6gxf5Qxf5',
        'Qe8*Kc7Qe7Kc8Ne5c2Qxc5Kd8Qxd4Ke8Qe3Kf8Kg3Qc8Nd3Kg8f4Qc6....Nc1\r\n\r\nQa4   Qb3',
        '1-0*',
        '\n',
        ))

    splitter = re.compile(constants.SPLIT_INTO_GAMES)
    moves = re.compile(constants.SPLIT_INTO_TOKENS)
    tags = re.compile(constants.SPLIT_INTO_TAGS)
    s = splitter.split(games)
    print s
    print
    for e in s:
        print repr(e)
        print
    s.pop(0)
    while s:
        tagtext = s.pop(0)
        if s:
            movetext = s.pop(0)
        else:
            movetext = ''
        for t in tags.split(tagtext):
            st = t.strip()
            if st:
                f, v = st.split('"', 1)
                f = f[1:].strip()
                v = v.rsplit('"', 1)[0]
                print repr(f), repr(v)
            else:
                print repr(t)
        print
        tokens = moves.split(movetext)
        print tokens
    print
