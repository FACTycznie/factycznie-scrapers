#!/usr/bin/env python3
import sys

from factscraper import crawl, _get_domain

if len(sys.argv) < 2:
    print("""Usage:
    ./crawl.py <url> ...
""")
    exit(1)
urls = sys.argv[1:]
for url in urls:
    domain = _get_domain(url)
    urls = set()
    try:
        with open('articles/{}.urls'.format(domain)) as url_file:
            for line in url_file:
                urls.add(line)
    except FileNotFoundError:
        pass
    crawl(url, verbose=True, blacklist=urls)
