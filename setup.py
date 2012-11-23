#!/usr/bin/env python

import os
import sys
from distutils.core import setup

src_dir = os.path.abspath('src')
sys.path.insert(0, src_dir)

import compfacts

setup(name='CompFacts',
    version=compfacts.__version__,
    description=compfacts.short_description,
    long_description=compfacts.long_description,
    author='Christopher Foo',
    author_email='chris.foo@gmail.com',
    url='https://github.com/chfoo/CompFacts',
    package_dir={'': 'src'},
    packages=['compfacts'],
    package_data={'compfacts': [
        'compfacts.atom',
        'corpus_data/*.grammar_text',
        'corpus_data/*/*.corpus_text',
        'corpus_data/*/*.grammar_text',
    ], },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English',
    ],
    requires=['nltk'],
)
