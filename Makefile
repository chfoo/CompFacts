PREFIX ?= /usr/
PYTHON=python

all:

build:
	$(PYTHON) setup.py build

install:
	mkdir -p -v $(DESTDIR)/$(PREFIX)/sbin/
	cp -v sbin/compfacts-service $(DESTDIR)/$(PREFIX)/sbin/
	cp -v sbin/compfacts-web-service $(DESTDIR)/$(PREFIX)/sbin/
	$(PYTHON) setup.py install --prefix $(DESTDIR)/$(PREFIX)
	mkdir -p -v $(DESTDIR)/$(PREFIX)/etc/ $(DESTDIR)/$(PREFIX)/etc/nginx/sites-available/
	cp -v etc/compfacts.conf $(DESTDIR)/$(PREFIX)/etc/
	cp -v etc/nginx/sites-available/50-compfacts $(DESTDIR)/$(PREFIX)/etc/nginx/sites-available/

clean:
	$(PYTHON) setup.py clean
