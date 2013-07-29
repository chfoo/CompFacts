'''Computer facts generator

CompFacts uses a context-free grammar to generate computer facts.

These facts are regularly posted to the Twitter account
<@CompFacts `https://twitter.com/CompFacts`>_.
'''
# Copyright 2012 by Christopher Foo <chris.foo@gmail.com>
# Licensed under GPLv3. See COPYING.txt for details.
import distutils.version

short_version = '1.5'  # N.N
__version__ = short_version + ''  # N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]

distutils.version.StrictVersion(__version__)

short_description, long_description = __doc__.split('\n', 1)
