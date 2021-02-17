# setup.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

from setuptools import setup

if __name__ == '__main__':

    long_description = open('README').read()

    setup(
        name='pgn-read',
        version='1.2.1',
        description='Portable Game Notation (PGN) parser',
        author='Roger Marsh',
        author_email='roger.marsh@solentware.co.uk',
        url='http://www.solentware.co.uk',
        package_dir={'pgn_read':''},
        packages=[
            'pgn_read',
            'pgn_read.core',
            'pgn_read.core.test',
            'pgn_read.about',
            ],
        package_data={
            'pgn_read.about': ['LICENCE', 'CONTACT'],
            },
        long_description=long_description,
        license='BSD',
        classifiers=[
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Operating System :: OS Independent',
            'Topic :: Software Development',
            'Topic :: Games/Entertainment :: Board Games',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta',
            ],
        )
