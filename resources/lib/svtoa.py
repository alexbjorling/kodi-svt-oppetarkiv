# -*- coding: utf-8 -*-

import requests
import HTMLParser
import json

API_URL = 'https://origin-www.svt.se/oppet-arkiv-api'
GENRES_URL = 'https://www.oppetarkiv.se/genrer'

class Item(object):
    """ Implements a program/folder item with name, url and image.
    """
    def __init__(self):
        self.name = ''
        self.url = ''
        self.image = ''
    def __unicode__(self):
        return "*** Item object\n  * name = '%s' \n  * url = '%s' \n  * image = '%s'" % (self.name, self.url, self.image)
    def __str__(self):
        return unicode(self).encode('utf-8')

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
        # check if there is an open item in construction and if this is its image
        elif self._item and (tag == 'img' and 'class' in attrs.keys() and 'svtoa_genre-list__link-item-image' in attrs['class']):
            self._item.image = attrs['src']
    def handle_data(self, data):
        # check if there is an open item in construction and if this is its name
        if self._item and data.strip():
            self._item.name += data.encode('utf-8')
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
    """ Returns a list of Item objects with empty url fields.
    """
    r = requests.get(GENRES_URL)
    gp = GenreParser()
    gp.feed(r.text)
    return gp.data

def getProgramsByGenre(genre):
    """ Returns a list of Item objects. The url field contains the program's titleFacet later used for getting episodes.
    """
    r = requests.get(API_URL + '/search/titles' + '?genreFacet=%s' % genre + '&count=%s' % 1)
    jsonData = json.loads(r.text)
    N = int(jsonData['total'])
    r = requests.get(API_URL + '/search/titles' + '?genreFacet=%s' % genre + '&count=%d' % N + '&sort=alpha')
    jsonData = json.loads(r.text)
    items = []
    for entry in jsonData['entries']:
        item_ = Item()
        item_.name = entry['name'].encode('utf-8')
        item_.url = entry['term']
        print item_.name, item_.url
        try:
            item_.image = entry['thumbnailMedium']
        except: pass
        items.append(item_)
    return items

def getVideosByProgram(program):
    """ Returns a list of Item objects. The url field is the actual video url.
    """
    r = requests.get(API_URL + '/search/tags' + '?titleFacet=%s' % program + '&count=%s' % 1)
    jsonData = json.loads(r.text)
    N = int(jsonData['total'])
    r = requests.get(API_URL + '/search/tags' + '?titleFacet=%s' % program + '&count=%d' % N + '&sort=date_asc')
    jsonData = json.loads(r.text)
    items = []
    for entry in jsonData['entries']:
        item_ = Item()
        item_.name = entry['title'].encode('utf-8')
        item_.url = ''
        item_.image = entry['thumbnailMedium']
        items.append(item_)
    return items
