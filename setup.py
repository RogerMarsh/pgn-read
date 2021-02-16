# setup.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

import sys
from distutils.core import setup

from pgn import _pgn_version

setup(
    name='-'.join(
        ('pgn',
         ''.join(
             ('py',
              '.'.join(
                  (str(sys.version_info[0]),
                   str(sys.version_info[1]))))),
         )),
    version=_pgn_version,
    description='PGN parser classes',
    author='solentware.co.uk',
    author_email='roger.marsh@solentware.co.uk',
    url='http://www.solentware.co.uk',
    packages=[
        'pgn',
        'pgn.core',
        ],
    package_data={
        'pgn': ['README', 'LICENCE'],
        },
    long_description='''PGN parser classes

    Parse game scores in PGN format.  Both the strict export format and many
    less strict import formats are supported.

    Base classes for handling a single game and files of games are provided.

    These classes verify that a game score represents a legal game.
    
    ''',
    )
