# -*- coding: utf-8 -*-

import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
import resources.lib.svtoa as svtoa

# default parameters
DEFAULT = {'page': ['root'],
           'genre': [''],
           'program': [''],
           'letter': [''],
           }

ABC = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['Å', 'Ä', 'Ö']

# parse arguments from kodi
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
newargs = urlparse.parse_qs(sys.argv[2][1:])
args = DEFAULT.copy()
args.update(newargs)

# constants for page identification
PAGE_ROOT = 'root'
PAGE_ABC = 'abc'
PAGE_PROGRAMS = 'programs'
PAGE_GENRES = 'genres'
PAGE_SEARCH = 'search'
PAGE_GENRE = 'genre'
PAGE_PROGRAM = 'program'

# set content type for the addon
xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

# Following the website, there are three main ways to access 
# content. This hard-coded switch provides access to these.
page = args['page'][0]
if page == PAGE_ROOT:
    # item for the Program interface
    url = build_url({'page': PAGE_ABC})
    li = xbmcgui.ListItem('Program A-Ö', iconImage='DefaultFile.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
    # item for the Genres interface
    url = build_url({'page': PAGE_GENRES})
    li = xbmcgui.ListItem('Genrer', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
    # item for the Search interface
    url = build_url({'page': PAGE_SEARCH})
    li = xbmcgui.ListItem('Sök', iconImage='DefaultSearch.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif page == PAGE_ABC:
    # special case for 0-9
    url = build_url({'page': 'programs', 'letter': '0'})
    li = xbmcgui.ListItem('0-9')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, 
        listitem=li, isFolder=True)
    # the rest of the alphabet
    for letter in ABC:
        url = build_url({'page': 'programs', 'letter': letter})
        li = xbmcgui.ListItem(letter)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, 
            listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)    

elif page == PAGE_PROGRAMS:
    programs = svtoa.getPrograms()
    letter = args['letter'][0]
    for item in programs:
        # comparison which takes care of ÅÄÖ
        if item.name.upper().startswith(letter.upper()) or (letter == '0' and item.name[0].upper() not in ABC and item.name[:2].upper() not in ABC):
            url = build_url({'page': 'program', 'program': item.url})
            image = svtoa.getProgramImage(item.url)
            li = xbmcgui.ListItem(item.name, iconImage=image)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, 
                listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif page == PAGE_GENRES:
    genres = svtoa.getGenres()
    for item in genres:
        url = build_url({'page': 'genre', 'genre': urllib.quote(item.name)})
        li = xbmcgui.ListItem(item.name, iconImage=item.image)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, 
            listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif page == PAGE_GENRE:
    genre = args['genre'][0]
    programs = svtoa.getProgramsByGenre(genre)
    for item in programs:
        url = build_url({'page': 'program', 'program': item.url})
        li = xbmcgui.ListItem(item.name, iconImage=item.image)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, 
            listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif page == PAGE_PROGRAM:
    program = args['program'][0]
    videos = svtoa.getVideosByProgram(program)
    for item in videos:
        li = xbmcgui.ListItem(item.name, iconImage=item.image)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=item.url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)

elif page == PAGE_SEARCH:
    xbmcgui.Dialog().ok('Not implemented', 'The Öppet arkiv search function is not yet implemented.')
