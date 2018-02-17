#!/usr/bin/env python3
"""
crawl.py
========
This script allows you to easily download masses of articles from an arbitrary
news source.

It is currently configured for Polish sites (see `language='pl'` keywords in
`factscraper/__init__.py`).

Usage:
    ./crawl.py <article-urls> ... [options]

Options:
    -n NUM  Number of articles to download per domain. [default: 500]
            If `infinite` never stop.
"""
import sys

from docopt import docopt
from factscraper import crawl, _get_domain
from requests.exceptions import MissingSchema, ConnectionError

def _interpret_num(val):
    try:
        return int(val)
    except ValueError:
        if val == "infinite":
            return -1
        else:
            raise

opts = docopt(__doc__, help=True)

urls = opts['<article-urls>']

for url in urls:
    try:
        download_limit = _interpret_num(opts['-n'])
    except ValueError:
        print("Error: Invalid -n argument")
        exit(1)
    try:
        domain = _get_domain(url)
        urls = set()
        try:
            with open('articles/{}.urls'.format(domain)) as url_file:
                for line in url_file:
                    urls.add(line)
        except FileNotFoundError:
            pass
        crawl(url, verbose=True, blacklist=urls, download_limit=download_limit)
    except MissingSchema: 
        print("Error: Invalid url - missing schema: {}".format(url))
    except ConnectionError:
        print("Error: Connection error")
