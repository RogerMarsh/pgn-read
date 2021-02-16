# setup.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

from distutils.core import setup

from version import _pgn_version

setup(
    name='pgn',
    version=_pgn_version,
    description='PGN parser classes',
    author='solentware.co.uk',
    author_email='roger.marsh@solentware.co.uk',
    url='http://www.solentware.co.uk',
    package_dir={'pgn':''},
    packages=[
        'pgn',
        'pgn.core',
        ],
    package_data={
        'pgn': ['LICENCE'],
        },
    long_description='''PGN parser classes

    Parse game scores in PGN format.  Both the strict export format and many
    less strict import formats are supported.

    Base classes for handling a single game and files of games are provided.

    These classes verify that a game score represents a legal game.
    
    ''',
    )
