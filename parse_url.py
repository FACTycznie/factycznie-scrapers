#!/usr/bin/env python3
import sys

from factscraper import analyze_url, InvalidArticleError

to_print = ['url', 'title', 'text', 'publish_date', 'domain']

if len(sys.argv) == 2:
    try:
        parsed = analyze_url(sys.argv[1], verbose=True)
    except InvalidArticleError:
        print("InvalidArticleError occured. Parsing without validation")
        parsed = analyze_url(sys.argv[1], verbose=True, validate=False)
    for key in to_print:
        print("\t{}:\n{}".format(key.capitalize(), parsed[key]))
else:
    print("""Usage:
    parse_url.py <article-url>""")
