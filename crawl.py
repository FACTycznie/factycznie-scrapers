#!/usr/bin/env python3
import sys

from factscraper import crawl

if len(sys.argv) < 2:
    print("""Usage:
    ./crawl.py <url> ...
""")
    exit(1)
urls = sys.argv[1:]
for url in urls:
    crawl(url, verbose=True)
