# setup.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)
"""pgn-read setup file."""

from setuptools import setup

if __name__ == "__main__":

    long_description = open("README").read()

    setup(
        name="pgn-read",
        version="2.1.1",
        description="Portable Game Notation (PGN) parser",
        author="Roger Marsh",
        author_email="roger.marsh@solentware.co.uk",
        url="http://www.solentware.co.uk",
        packages=[
            "pgn_read",
            "pgn_read.core",
            "pgn_read.samples",
        ],
        long_description=long_description,
        license="BSD",
        classifiers=[
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Operating System :: OS Independent",
            "Topic :: Software Development",
            "Topic :: Games/Entertainment :: Board Games",
            "Intended Audience :: Developers",
            "Development Status :: 3 - Alpha",
        ],
    )
