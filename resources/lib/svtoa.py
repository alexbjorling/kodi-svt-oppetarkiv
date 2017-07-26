# -*- coding: utf-8 -*-

import requests
import HTMLParser

GENRES_URL = 'https://www.oppetarkiv.se/genrer'

class Item(object):
    """ Implements a program/folder item with name, url and image.
    """
    def __init__(self):
        self.name = ''
        self.url = ''
        self.image = ''
    def __unicode__(self):
        return "*** Item object, complete = %r\n  * name = '%s' \n  * url = '%s' \n  * image = '%s'" % (self.complete, self.name, self.url, self.image)
    def __str__(self):
        return unicode(self).encode('utf-8')
    @property
    def complete(self):
        if self.name and self.url and self.image:
            return True
        return False

class GenreParser(HTMLParser.HTMLParser, object):
    def __init__(self):
        self.data = []
        self._item = None
        super(GenreParser, self).__init__()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # check if this tag is a new genre tag
        if tag == 'a' and 'class' in attrs.keys() and 'svtoa_genre-list__link-item' in attrs['class']:
            self._item = Item()
            self._item.url = attrs['href']
        # check if there is an open item in construction and if this is its image
        elif self._item and (tag == 'img' and 'class' in attrs.keys() and 'svtoa_genre-list__link-item-image' in attrs['class']):
            self._item.image = attrs['src']
    def handle_data(self, data):
        # check if there is an open item in construction and if this is its name
        if self._item and data.strip():
            self._item.name += data
    def handle_entityref(self, ref):
        # entity refs (special characters) need to be handled separately
        self.handle_data(self.unescape('&'+ref+';'))
    def handle_endtag(self, tag):
        # if there is an open item in construction and the genre tag closes, then close the item
        if tag == 'a':
            if self._item:
                self.data.append(self._item)
                self._item = None

def getGenres():
    """ Returns a list of Item objects.
    """
    r = requests.get(GENRES_URL)
    gp = GenreParser()
    gp.feed(r.text)
    return gp.data
