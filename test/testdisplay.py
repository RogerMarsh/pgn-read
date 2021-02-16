# testdisplay.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test Portable Game Notation (PGN) parser."""


if __name__ == '__main__':

    from pgn.core.parser import PGNDisplay

    tags = '\n'.join((
        '[Event "Test Nc3e4"]',
        '[Site "Home"]',
        '[Date "2011.02.12"]',
        '[Round ""]',
        '[White "Me"]',
        '[Black "Me"]',
        '[Result "*"]',
        '[FEN "7k/8/8/2N3N1/8/2N5/8/K7 w - - 0 1"]',
        '',
        ))
    movetext = '\n'.join((
        'Kb1Kg8Nc3',
        ))

    pgn = PGNDisplay()
    pgn.extract_first_game(''.join((tags, movetext)))
    pgn.process_game()
    print pgn._tags_valid, pgn._movetext_valid
    print pgn.is_tag_roster_valid(), pgn.is_movetext_valid()
    print pgn._tag_string
    print pgn.tags
    print pgn.tags_in_order
    print pgn.tokens
    print pgn.gametokens
    print
    for t, v in zip(pgn.moves, pgn.gametokens):
        print t, '\t', v
