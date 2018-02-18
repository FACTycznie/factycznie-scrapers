#!/usr/bin/env python3
"""This scripts allows to easily test if our timestamp retrieval system works
for a given news website. It simply prints out the output we get, or throws the
exception it would give.
"""
from factscraper import parse
import sys

if len(sys.argv) < 2:
    print("""Usage:
    ./test_date.py <url to article>
""")
    exit(0)

parsed = parse(sys.argv[1])
print("Title:", parsed['title'])
print("Text:", parsed['text'])
print("Found authors:", parsed['authors'])
print("Found domain:", parsed['netloc'])
print("Found timestamp:", parsed['timestamp'])
print("Found sources:", parsed['sources'])
