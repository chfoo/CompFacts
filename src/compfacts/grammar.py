# encoding=utf8
'''Context-free grammar'''
# Copyright 2012 by Christopher Foo <chris.foo@gmail.com>
# Licensed under GPLv3. See COPYING.txt for details.
from __future__ import (print_function, absolute_import, unicode_literals,
    with_statement)
from StringIO import StringIO
from compfacts import corpus
import glob
import logging
import nltk
import os.path
import random


_logger = logging.getLogger(__name__)


class FactBuilder(object):
    '''Computer facts builder.'''

    def __init__(self):
        self._grammar = self.build_grammar()
        self._nonterminal = self._grammar.start()
        check_grammar(self._grammar, self._nonterminal)

    def build_grammar_text(self):
        '''Return the context-free grammar represented as a string.'''

        buf = StringIO()

        grammar_path = os.path.join(os.path.dirname(__file__), 'corpus_data',
            'compfacts.grammar_text')

        paths = [grammar_path] + list(get_grammar_text_filenames())

        for path in paths:
            _logger.debug(u'Loading %s', path)

            for line in open(path, 'rb'):
                line = line.strip().decode('utf8')

                if line.startswith(u'#') or not line:
                    continue

                buf.write(line)
                buf.write(u'\n')

        for name, filename in corpus.get_corpus_text_names():
            _logger.debug(u'Loading %s from %s', name, filename)

            for line in open(filename, 'rb'):
                line = line.strip().decode('utf8')

                if line.startswith(u'#') or not line:
                    continue

                if u'"' in line:
                    _logger.warn(u'Corpus %s contains double quote', line)
                    line = line.replace(u'"', u'“')

                buf.write(name)
                buf.write(u' -> ')
                buf.write(u'"')
                buf.write(line.upper())
                buf.write(u'"\n')

        return buf

    def build_grammar(self):
        '''Use the corpus data and return a NLTK grammar.'''

        grammer_def = self.build_grammar_text().getvalue()
        grammar = nltk.parse_cfg(grammer_def.encode('utf8'))

        return grammar

    def fact(self):
        '''Return one computer fact.'''

        items = produce(self._grammar, self._nonterminal)

        return u''.join(items)


class EmptyProductionsError(ValueError):
    '''Error for when a Nonterminal has no RHS productions.'''
    pass


def check_grammar(grammar, nonterminal, _memo=None):
    '''Check that the grammar has no empty productions.

    :raises: :class:`EmptyProductionsError`
    '''

    if not grammar.is_nonempty():
        return

    if _memo is None:
        _memo = set()

    if nonterminal in _memo:
        return

    productions = grammar.productions(lhs=nonterminal)

    if not productions:
        raise EmptyProductionsError(
            'nonterminal %s has no rhs productions, lhs=%s' % (nonterminal,
            grammar.productions(rhs=nonterminal)))

    _memo.add(nonterminal)

    for production in productions:
        production_rhs = production.rhs()

        for production_rhs_item in production_rhs:
            if isinstance(production_rhs_item, nltk.grammar.Nonterminal):
                check_grammar(grammar, production_rhs_item, _memo)


def produce(grammar, nonterminal):
    '''Generate a random sentence given a grammar and a nonterminal.

    Special nonterminals
    ====================

    __CONTINUEnn__
        Given nn as a percent, this nonterminal will continue the production
        only nn percent of the time. In other words, the tree is pruned
        100 - nn times.

    '''
    productions = grammar.productions(lhs=nonterminal)

    production = random.choice(productions)
    production_rhs = production.rhs()

    for production_rhs_item in production_rhs:
        if isinstance(production_rhs_item, nltk.grammar.Nonterminal):

            if production_rhs_item.symbol().startswith('__CONTINUE'):
                prob = int(production_rhs_item.symbol().strip('_CONTINUE')
                    ) / 100.0

                if random.random() > prob:
                    yield ''
                    break
                else:
                    continue

            for item in produce(grammar, production_rhs_item):
                yield item
        else:
            yield production_rhs_item.decode('utf8')


def get_grammar_text_filenames():
    '''Return the grammar text filenames.'''

    path = os.path.join(os.path.dirname(__file__), 'corpus_data', '*')
    pattern = u'%s/*.grammar_text' % path

    return glob.glob(pattern)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    builder = FactBuilder()

    for dummy in xrange(0, 100):
        print(builder.fact().encode('utf8'))
