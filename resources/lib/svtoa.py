# -*- coding: utf-8 -*-

""" This module provides an interface to SVT Öppet arkiv. Since the API
    is incomplete (or at least incompletely described), web scraping is 
    used in combination with the API itself.
"""

import requests
import HTMLParser
import json

API_URL = 'https://origin-www.svt.se/oppet-arkiv-api'
GENRES_URL = 'https://www.oppetarkiv.se/genrer'
PROGRAMS_URL = 'https://www.oppetarkiv.se/program'

class Item(object):
    """ Implements a program/folder item with name, url and image.
    """
    def __init__(self):
        self.name = ''
        self.url = ''
        self.image = ''
        self.info = ''
    def __unicode__(self):
        return "*** Item object\n  * name = '%s' \n  * url = '%s' \n  * image = '%s'" % (self.name, self.url, self.image)
    def __str__(self):
        return unicode(self).encode('utf-8')

class GenreParser(HTMLParser.HTMLParser, object):
    """ HTML parser which collects genres from the website. After 
        feeding HTML content, the data object attribute contains a list
        of Item objects, each describing a genre.
    """
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

class ProgramParser(HTMLParser.HTMLParser, object):
    """ Analog to GenreParser, but collects program titles.
    """
    def __init__(self):
        self.data = []
        self._item = None
        super(ProgramParser, self).__init__()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # check if this tag is a new program tag
        if tag == 'a' and 'class' in attrs.keys() and 'svtoa-anchor-list-link' in attrs['class']:
            self._item = Item()
            self._item.url = attrs['href'].split('/')[-2]
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

def getProgramImage(program):
    """ Returns the image url for the requested program.
    """
    r = requests.get(API_URL + '/search/titles' + '?titleFacet=%s' % program)
    jsonData = json.loads(r.text)
    try:
        url = jsonData['entries'][0]['thumbnailMedium']
    except:
        url = ''
    return url

def getPrograms():
    """ Returns a list of Item objects, each describing a program title 
        as scraped from the website. The url field contains the 
        program's titleFacet as parsed from its web link.
    """
    r = requests.get(PROGRAMS_URL)
    pp = ProgramParser()
    pp.feed(r.text)
    return pp.data

def getGenres():
    """ Returns a list of Item objects, each describing a genre. The
        url field is empty.
    """
    r = requests.get(GENRES_URL)
    gp = GenreParser()
    gp.feed(r.text)
    return gp.data

def getProgramsByGenre(genre):
    """ Returns a list of Item objects, each describing a program title 
        of the requested genre. The url field contains the program's 
        titleFacet which is later used for getting episodes.
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
        try:
            item_.image = entry['thumbnailMedium']
        except: pass
        items.append(item_)
    return items

def getVideosByProgram(program):
    """ Returns a list of Item objects, each describing a video (an 
        episode) of the requested program title. The url field is the 
        actual video url.
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
        # it seems the ios link works, so find it if it exists
        item_.url = entry['videoReferences'][0]['url']
        for vid in entry['videoReferences']:
            if vid['playerType'] == 'ios':
                item_.url = vid['url']
        item_.image = entry['thumbnailMedium']
        # add extra metadata to the info attribute
        try:
            season = entry['seasonNumber']
            episode = entry['episodeNumber']
            episodes = entry['totalEpisodes']
            item_.info += 'Säsong %d, avsnitt %d/%d.' % (season, episode, episodes)
        except:
            pass
        items.append(item_)
    return items
