# testreader_stats.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Test Portable Game Notation (PGN) reader."""


if __name__ == '__main__':

    import Tkinter

    import os
    import datetime
    import cStringIO

    from basesup.tools import dialogues

    from pgn.core.reader import PGNReader

    pgndata = '\n'.join((
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
        '1. e4 Nf6 2. e5 Nd5 3. Nc3 Nxc3 4. dxc3 Nc6 5. Nf3 d6 6. Bb5 e6 7. Bf4 Be7 8.',
        'Qe2 a6 9. Bxc6+ bxc6 10. Rd1 d5 11. h4 Bd7 12. Bg5 O-O 13. Rd4 f5 14. exf6 gxf6',
        '15. Bh6 Rf7 16. Rg4+ Kh8 17. Rf4 Be8 18. Qxe6 Bd6 19. Rg4 Qe7 20. Qxe7 Rxe7+',
        '21. Kd2 Bd7 22. Ra4 c5 23. Ra5 Bb5 24. a4 Bd7 25. Re1 Rxe1 26. Nxe1 c6 27. Nd3',
        'Bc7 28. Rxc5 Bb6 29. Be3 Bxc5 30. Nxc5 Bc8 31. a5 Kg7 32. g3 Kf7 33. Bf4 Bg4',
        '34. b4 1/2-1/2',
        '',
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
        '',
        '1. c4 e6 2. Nf3 f5 3. g3 Nf6 4. Bg2 Be7 5. O-O O-O 6. b3 $4 Ne4 7. Bb2 Bf6 8. Qc1',
        'Nc6 9. d3 Bxb2 10. Qxb2 Qf6 11. Qxf6 Nxf6 12. Nc3 d6 13. Rab1 Bd7 14. Rfc1 a6',
        '15. b4 h6 16. d4 Rae8 17. e3 Nd8 18. a4 g5 19. a5 f4 20. exf4 gxf4 21. b5 fxg3',
        '22. hxg3 Ng4 23. Rb2 Kg7 24. Ne4 Nf7 25. Nh2 Nxh2 26. Kxh2 Rb8 27. Kg1 Rfc8 28.',
        'Rcb1 axb5 29. cxb5 Ra8 30. Ra2 Ra7 31. a6 Rca8 32. Nc3 d5 33. Nxd5 exd5 34.',
        'Bxd5 Rd8 35. axb7 Rxa2 36. Bxa2 Nd6 37. b6 c6 1/2-1/2',
        '',
        ))

    def game_report():
        if len(valid):
            counter = gamecount + errorcount
            if fo:
                report.write(''.join(
                    (repr(counter), '  ************  ', repr(counter),
                     '   ', valid,
                     '\n\n\n',
                     )))
                report.write('Raw Tag data:\n\n')
                report.write(repr(pgn._tag_string))
                report.write('\n\nRaw Movetext data:\n\n')
                report.write(repr(pgn._move_string))
                report.write('\n\nTags:\n\n')
                report.write(repr(pgn.tags))
                report.write('\n\nMovetext:\n\n')
                report.write(repr(pgn.tokens))
                report.write('\n\nMoves:\n\n')
                report.write(repr(pgn.gametokens))
                report.write('\n\n\n')
            else:
                print repr(counter), '  ************  ', repr(counter)
                print

    def timestamp():
        if fo:
            report.write(''.join(
                (datetime.datetime.now().isoformat(),
                 '\n\n\n',
                 )))
        else:
            print datetime.datetime.now().isoformat()
            print

    def stat_report(final=True):
        if final:
            title = 'Final report'
            repsize = size
        else:
            title = ' '.join(('Report after', str(gamecount), 'games'))
            repsize = rawtagbytecount + rawmovebytecount
        if fo:
            report.write(''.join(
                (title,
                 '\n\nFile size bytes: ', repr(repsize),
                 '\n\nTotal data bytes: ', repr(tagbytecount + movebytecount),
                 '\nTag bytes: ', repr(tagbytecount),
                 '\nMove bytes: ', repr(movebytecount),
                 '\n\nAll tokens: ', repr(tokencount),
                 '\nMove tokens: ', repr(gametokencount),
                 '\n\nGames: ', repr(gamecount),
                 '\nPositions: ', repr(positioncount),
                 '\nPieces: ', repr(piecesquaremovecount),
                 '\n\nPositions per Game: ', repr(positioncount / gamecount),
                 '\nPieces per Position: ',
                 repr(piecesquaremovecount / positioncount),
                 '\nPieces per Game: ', repr(piecesquaremovecount / gamecount),
                 '\nTag bytes per Game: ', repr(tagbytecount / gamecount),
                 '\nMove bytes per Game: ', repr(movebytecount / gamecount),
                 '\n\nData bytes per Game: ',
                 repr((tagbytecount + movebytecount) / gamecount),
                 '\n\nIndex entries per Game (7 tags + positions + pieces): ',
                 repr((7 * gamecount + positioncount + piecesquaremovecount) /
                      gamecount),
                 '\n\nPGN file bytes per Game: ', repr(repsize / gamecount),
                 '\n\n',
                 )))
        else:
            print title
            print
            print 'File size bytes:', repsize
            print
            print 'Total bytes:', tagbytecount + movebytecount
            print 'Tag bytes:', tagbytecount
            print 'Move bytes:', movebytecount
            print
            print 'All tokens:', tokencount
            print 'Move tokens:', gametokencount
            print
            print 'Games:', gamecount
            print 'Positions:', positioncount
            print 'Pieces:', piecesquaremovecount
            print
            print 'Positions per Game:', positioncount / gamecount
            print 'Pieces per Position:', piecesquaremovecount / positioncount
            print 'Pieces per Game:', piecesquaremovecount / gamecount
            print 'Tag bytes per Game:', tagbytecount / gamecount
            print 'Move bytes per Game:', movebytecount / gamecount
            print
            print 'Data bytes per Game:',
            print (tagbytecount + movebytecount) / gamecount
            print
            print 'Index entries per Game (7 tags + positions + pieces):',
            print ((7 * gamecount + positioncount + piecesquaremovecount) /
                   gamecount)
            print
            print 'PGN file bytes per Game:', repsize / gamecount
            print

    def validtext():
        if pgn.is_movetext_valid():
            if pgn.is_tag_roster_valid():
                return ''
            else:
                return 'Tag Errors'
        else:
            if pgn.is_tag_roster_valid():
                return 'Movetext Errors'
            else:
                return 'Tag and Movetext Errors'

    pgn = PGNReader()

    root = Tkinter.Tk()
    root.wm_title('Test PGN Reader')
    fi = dialogues.askopenfilename(
        parent=root,
        title='Open PGN file',
        filetypes=(
            ('PGN files', '*.pgn *.PGN'),
            ))
    fo = dialogues.asksaveasfilename(
        parent=root,
        title='Save Test Results As',
        filetypes=(
            ('All files', '*'),
            ('Text', '*.txt'),
            ))

    if fi:
        size = os.path.getsize(fi)
        source = open(fi, 'rbU')
    else:
        size = len(pgndata)
        source = cStringIO.StringIO(pgndata)
    if fo:
        report = open(fo, mode='wb')
    else:
        fo = None

    timestamp()
    errorcount = 0
    rawtagbytecount = 0
    rawmovebytecount = 0
    tagbytecount = 0
    movebytecount = 0
    gamecount = 0
    tokencount = 0
    gametokencount = 0
    positioncount = 0
    piecesquaremovecount = 0
    try:
        for d in pgn.get_games(source):
            pgn.process_game()
            valid = validtext()
            if len(valid):
                errorcount += 1
            else:
                rawtagbytecount += len(pgn._tag_string)
                rawmovebytecount += len(pgn._move_string)
                tagbytecount += len(''.join(
                    [''.join((''.join(('[', k)), ''.join(('"', v, '"]'))))
                     for k, v in pgn.tags.iteritems()]))
                movebytecount += len(''.join(pgn.gametokens))
                gamecount += 1
                tokencount += len(pgn.tokens)
                gametokencount += len(pgn.gametokens)
                positioncount += len(pgn.positions)
                piecesquaremovecount += len(pgn.piecesquaremoves)
            game_report()
            if not gamecount % 1000:
                stat_report(final=False)
    except:
        if fo:
            report.write(''.join(
                (repr(pgn._token_groups),
                 '\n\n',
                 repr(pgn.tokens),
                 '\n\n',
                 repr(pgn.piece_locations),
                 '\n\n',
                 repr(pgn.occupied_square_pieces),
                 '\n\n',
                 repr(pgn.side_to_move),
                 '\n\n',
                 )))
        else:
            print pgn._token_groups
            print
            print pgn.tokens
            print
            print pgn.piece_locations
            print
            print pgn.occupied_square_pieces
            print
            print pgn.side_to_move
        raise
    source.close()
    timestamp()
    stat_report()

    if fo:
        report.close()
        del report
    
    root.destroy()
    del root
