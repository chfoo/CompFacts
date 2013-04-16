Computer facts generator
========================

CompFacts uses a context-free grammar to generate computer facts.

These facts are regularly posted to the Twitter account
`@CompFacts <https://twitter.com/CompFacts>`_.

An Atom feed is available at
`<http://www.torwuf.com/compfacts/compfacts.atom>`_.


How to help
===========

You can help by submitting enhancements on my GitHub repository
`<https://github.com/chfoo/CompFacts>`_. Just fork, change, commit, and
request me to pull your changes.

The Python version supported is 2.7.


Programming
===========

The grammar productions requires the `Python Natual Languge Toolkit
<http://nltk.org>`_. It can be installed through the Python Package Index.


Corpus and grammar format
+++++++++++++++++++++++++

The files are located in directory ``corpus_data``.

Corpus text files are simple lists. The first portion of the filename
the dot is the nonterminal name.

Grammar text files are the production rules. The filename does not
matter. The grammar follows the NLTK format.

All files support using ``#`` at the start of a line as a comment.


Generating facts
================

You can test out the generator by running::

    python -m compfacts.grammar


Running the server
==================

I included a sample Debian package which I use for running the package as a service.
The nginx config file is designed to be run behind lighttpd. The service
will refuse to run if the default ``compfacts.conf`` is not configured.
Symlink ``debian`` to ``pkg.debian`` for Debian package building.
The commands ``debuild -b -us -uc`` and ``dh_clean`` will build and clean
respectively.

The service requires `Tweepy <https://github.com/tweepy/tweepy>`_ for
Twitter status updates and 
`Tornado Web <http://tornadoweb.org>`_ for the RSS and service status pages.
Make sure to install Tweepy using ``pip`` for latest version.

The Twitter posting service's status can be checked at
`<http://www.torwuf.com/compfacts/server_status>`_.
