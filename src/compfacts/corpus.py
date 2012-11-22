# encoding=utf8
'''Corpus text'''
# Copyright 2012 by Christopher Foo <chris.foo@gmail.com>
# Licensed under GPLv3. See COPYING.txt for details.
from __future__ import print_function
import argparse
import datetime
import glob
import logging
import os.path
import re
import sys

_logger = logging.getLogger(__name__)


class WikiNameListExtractor(object):
    '''Extracts names from Wikipedia lists Wikitext'''

    LINE_LINKED_RE = re.compile(r'''[\[\|]([\w'. -]*?)\]\]''', re.UNICODE)
    LINE_BOLD_RE = re.compile(r"""''([\w'. -]*?)''""", re.UNICODE)
    NAME_LENGTH = 4

    def __init__(self):
        pass

    def extract_line_fragment(self, line_fragment):
        '''Extract a name from a fragment of a line.

        The fragment may be plain words or words with some keyword
        wikitext markup.
        '''

        match_obj = re.search(WikiNameListExtractor.LINE_LINKED_RE,
            line_fragment)

        if not match_obj:
            match_obj = re.search(WikiNameListExtractor.LINE_BOLD_RE,
                line_fragment)

        if match_obj:
            s = match_obj.group(1)
        else:
            s = line_fragment

        s = s.split(u'(', 1)[0]
        s = s.split(u'<', 1)[0]  # <refs
        s = s.strip(u"'[]\" ")

        if s and WikiNameListExtractor.word_count(s) \
        <= WikiNameListExtractor.NAME_LENGTH:
            _logger.debug('Accept %s', s)
            return s
        else:
            _logger.debug('REJECT %s', s)

    def extract_line(self, line):
        '''Extract a name from a line of wikitext.

        The function checks for lines that are list definitions or
        part of a table.

        List definition format::
            * name here[,:-] some description
            * name here
        '''

        # list
        if line.lstrip().startswith(u'*'):
            stripped_line = line.lstrip(u' *')

            for delim_char in (u'—', u' – ', u', ', u': ', u' - '):
                if delim_char in stripped_line:
                    stripped_line = stripped_line.split(delim_char, 1)[0]

            s = self.extract_line_fragment(stripped_line)

            if s:
                return s

        # first column in table
        elif self._prev_line.startswith(u'|-') and line.startswith(u'|'):
            stripped_line = line.lstrip(u' |')
            s = self.extract_line_fragment(stripped_line)

            if s:
                return s
            else:
                _logger.debug('Reject %s', stripped_line)

    @classmethod
    def word_count(cls, s):
        '''Return a naive word count using the split function.'''

        return len(s.split())

    def reset(self):
        '''Reset the state of the extractor.'''

        self._prev_line = u''
        self._names = set()

    def extract(self, output_header=True, filter_text=None):
        '''Read and extract from standard input.'''

        _logger.info('Extract begin')
        self.reset()

        if output_header:
            print('# Extracted from Wikipedia, The Free Encyclopedia')
            print('# License CC-BY-SA')
            print('# Date extracted:', datetime.datetime.utcnow().isoformat())
            print('# Args:', ' '.join(sys.argv[1:]))

        while True:
            try:
                line = raw_input().decode('utf8')
            except EOFError:
                break

            name = self.extract_line(line)

            if filter_text and name and filter_text.lower() in name.lower():
                continue

            if name:
                self._names.add(name)

            self._prev_line = line

        _logger.info('Extract finish')

    def print_out(self):
        for name in sorted(self._names):
            print(name.encode('utf8'))


def get_corpus_text_names():
    '''Return corpus name and filename pairs.

    The general filename pattern is::

        corpus_data/*/*.META_DATA.corpus_text

    Where META_DATA can be an integer to split large files.
    '''

    path = os.path.join(os.path.dirname(__file__), u'corpus_data', u'*')
    pattern = u'%s/*.corpus_text' % path

    for filename in glob.glob(pattern):
        name = os.path.basename(filename).split(u'.', 1)[0]

        yield (name, filename)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser('Corpus Text Extractor')
    parser.add_argument('--wikipedia-list', action='store_true', default=False,
        help='Read wikitext from standard input')
    parser.add_argument('--filter', type=unicode, default=None)

    args = parser.parse_args()

    if args.wikipedia_list:
        e = WikiNameListExtractor()
        e.extract(filter_text=args.filter)
        e.print_out()
    else:
        parser.print_help()
