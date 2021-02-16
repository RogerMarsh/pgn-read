# testpgndisplay.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test Portable Game Notation (PGN) parser."""


if __name__ == '__main__':

    from pgn.core.parser import PGNDisplay

    tags = ''.join((
        '[Event"?"]',
        '[Site"?"]',
        '[Date"????.??.??"]',
        '[Round"??"]',
        '[White"?"]',
        '[Black"?"]',
        '[Result"*"]',
        ))
    movetexts = (
        ''.join((
            'e4c6d4d5exd5cxd5c4Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5', 'g', 'exd5cxd5c4Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5', 'g', 'exd5cxd5c4', '(c3)', 'Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5exd5cxd5c4', '(c3g6Nf3Bg7)', 'Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5exd5cxd5c4', '(c3g6', 'g', 'Nf3Bg7)', 'Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5exd5cxd5c4', '(c3g6Nf3', '(g3)','Bg7)', 'Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5exd5cxd5c4', '(c3g6', 'g', 'Nf3', '(g3)','Bg7)',
            'Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5exd5cxd5', 'g', 'c4', '{Some comment}',
            'c4Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5exd5cxd5', 'g', 'c4', '(c3g6Nf3Bg7)',
            'c4Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c6d4d5exd5cxd5', 'g', 'c4', '(c3g6Nf3', '(g3)','Bg7)',
            'c4Nf6c5e6Nc3b6',
            '*',
            )),
        ''.join((
            'e4c612.....<>\n;comment\n<>{}\n\n\n%escape\n$45.{hello\n\n;ok}',
            '*',
            )),
        )

    pgn = PGNDisplay()
    for mt in movetexts:
        print
        print '%%%%%%%%%%%%%%%%%%%%%%%%%'
        print
        pgn.extract_first_game(''.join((tags, mt)))
        pgn.process_game()
        print pgn._tags_valid, pgn._movetext_valid
        print pgn.is_tag_roster_valid(), pgn.is_movetext_valid()
        print pgn._tag_string
        print pgn.tags
        print pgn.tags_in_order
        print pgn.tokens
        print pgn.gametokens
        for m in pgn.moves:
            if isinstance(m[1], int):
                print repr(pgn.gametokens[m[1]]),
            else:
                print '   ',
            print m
        print
    
