# -*- coding: utf-8 -*-

import urllib

def build_url(base_url, query):
    """ Helper which builds a url query from a dict.
    """
    return base_url + '?' + urllib.urlencode(query)