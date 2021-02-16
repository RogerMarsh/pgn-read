# testparser.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test Portable Game Notation (PGN) parser."""


if __name__ == '__main__':

    from pgn.core.parser import PGN

    tags = '\n'.join((
        '[Event "4NCL-9899A BA1-BA2"]',
        '[Site "Rd1-Warwick"]',
        '[Date "1998.10.24"]',
        '[Round "1.1"]',
        '[White "Kopec, Danny"]',
        '[Black "Crouch, Colin"]',
        '[Result "1/2-1/2"]',
        '[ECO "B02"]',
        '[WhiteElo "2400"]',
        '[BlackElo "2410"]',
        '[PlyCount "67"]',
        '[EventDate "1998.10.24"]',
        '',
        ))
    movetext = '\n'.join((
        '1. e4 Nf6 2. e5 Nd5 3. Nc3 Nxc3 4. dxc3 Nc6 5. Nf3 d6 $4 6. Bb5 e6 7. Bf4 Be7 8.',
        'Qe2 a6 9. Bxc6+ bxc6 10. Rd1 d5 11. h4 Bd7 12. Bg5 O-O 13. Rd4 f5 14. exf6 gxf6',
        '15. Bh6 Rf7 16. Rg4+ Kh8 17. Rf4 Be8 18. Qxe6 Bd6 19. Rg4 Qe7 20. Qxe7 Rxe7+',
        '21. Kd2 Bd7 22. Ra4 c5 23. Ra5 Bb5 24. a4 Bd7 25. Re1 Rxe1 26. Nxe1 c6 27. Nd3',
        'Bc7 28. Rxc5 Bb6 29. Be3 Bxc5 30. Nxc5 Bc8 31. a5 Kg7 32. g3 Kf7 33. Bf4 Bg4',
        '34. b4 1/2-1/2',
        '',
        ))

    tags1 = ''.join((
        '[Event"National Club: Gosport - Wood Green"]',
        '[Site"Gosport"]',
        '[Date"1989.05.07"]',
        '[Round"QFinal"]',
        '[White"Sowray P J"]',
        '[Black"Marsh R"]',
        '[Result"1-0"]',
        ))
    movetext1 = ''.join((
        'e4c6d4d5exd5cxd5c4Nf6c5e6Nc3b6b4a5Bf4axb4Nb5Na6Qa4Bd7',
        'Bc7Na6xc5Qd1Qc8dxc5bxc5Nf3Qb7Nd6Bxd6Bxd6Qb6Be5Ke7Be2Ne4O-Of6Bb2Nc3',
        'Bxc3bxc3Qd3(Qb3)Ra3Rfb1Qa7Qc2g6Rb3d4Bc4Rxb3Bxb3Qa6a4Rb8a5e5Bd5Rb2',
        'Qe4Bf5Qh4Qd3(c2(g5))g4Rb1Rxb1Qxb1Kg2Kd6Qxf6Kxd5Qxe5Kc6gxf5Qxf5',
        'Qe8Kc7Qe7Kc8Ne5c2Qxc5Kd8Qxd4Ke8Qe3Kf8Kg3Qc8Nd3Kg8f4Qc6Qb6',
        '1-0',
        ))

    pgn = PGN()
    pgn.extract_first_game(''.join((tags, movetext)))
    pgn.process_game()
    print(pgn._tags_valid, pgn._movetext_valid)
    print(pgn.is_tag_roster_valid(), pgn.is_movetext_valid())
    print(pgn._tag_string)
    print(pgn.tags)
    print(pgn.tags_in_order)
    print(pgn.tokens)
    print(pgn.gametokens)
    print()
    print('%%%%%%%%%%%%%%%%%%%%%%%%%')
    print()
    pgn.extract_first_game(''.join((tags1, movetext1)))
    pgn.process_game()
    print(pgn._tags_valid, pgn._movetext_valid)
    print(pgn.is_tag_roster_valid(), pgn.is_movetext_valid())
    print(pgn._tag_string)
    print(pgn.tags)
    print(pgn.tags_in_order)
    print(pgn.tokens)
    print(pgn.gametokens)
    print()
    
