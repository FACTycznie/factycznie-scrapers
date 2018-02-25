#!/usr/bin/env python3
import sys

from factscraper import analyze_url

to_print = ['url', 'title', 'text', 'publish_date', 
            'authors', 'sources', 'domain']

if len(sys.argv) == 2:
    parsed = analyze_url(sys.argv[1])
    for key in to_print:
        print("\t{}:\n{}".format(key.capitalize(), parsed[key]))
else:
    print("""Usage:
    parse_url.py <article-url>""")
