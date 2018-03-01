"""This file contains tests that check how well our parsers retrieve
information from articles.
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import unittest
import re
import json

import scrapy
from datetime import date, datetime
import editdistance

from factscraper import analyze_url, InvalidArticleError

# Maximum ratio of Levenshtein distance between article text parsing
# result and the original to the original's length for us to consider
# the test passed
ARTICLE_TEXT_EDIT_DISTANCE_THRESHOLD = 0.05

#
###  Loading groundtruth test articles ###
#

test_articles = []
try:
    with open("test_articles.jsonl") as jsonl_file:
        for line in jsonl_file.readlines():
            article = json.loads(line)
            article['title'] = article['title'].strip() # might be redundant
            article['publish_date'] = datetime.strptime(
                article['publish_date'], "%Y-%m-%d")
            test_articles.append(json.loads(line))

except FileNotFoundError:
    raise FileNotFoundError(("test_articles.jsonl file not found. Please "
                             "create it with add_test_article.py script."))

#
###  Downloading all test samples from the wild ###
#

_downloaded_articles = []
for test_article in test_articles:
    try:
        _downloaded_articles.append(analyze_url(test_article['url']))
    except InvalidArticleError:
        pass

#
###  Testing stuff ###
#

class TestArticleDetection(unittest.TestCase):
    """This test case checks how accurately we can detect if a webpage
    contains an article.
    """
    def setUp(self):
        self.correct_urls = [article['url'] for article in test_articles]
        self.invalid_urls = [
            "http://wiadomosci.gazeta.pl/wiadomosci/0,156046.html#TRNavSST",
            "http://weekend.gazeta.pl/weekend/0,0.html",
            "http://fakty.interia.pl/opinie",
            "http://firma.interia.pl/regulamin",
            "http://fakty.interia.pl/inne-serwisy",
            "https://wp.pl/",
            "http://kultura.gazeta.pl/kultura/56,114526,22658501,najlepsze-koncerty-wystawy-i-wydarzenia-z-calej-polski-tym.html",
        ]

    def test_correct_urls(self):
        """This tests for false negatives."""
        for url in self.correct_urls:
            with self.subTest(url=url):
                try:
                    analyze_url(url)
                except InvalidArticleError:
                    self.fail("analyze_url raised InvalidArticleError on an "
                              "actual article. url: {}".format(url))

    def test_invalid_urls(self):
        """This tests for false positives."""
        for url in self.invalid_urls:
            with self.subTest(url=url):
                try:
                    analyze_url(url)
                    self.fail("analyze_url detected an article where there "
                              "was none. url: {}".format(url))
                except InvalidArticleError:
                    pass

class TestGeneralAnalysis(unittest.TestCase):
    """This test case downloads and analyzes all articles from
    test_articles, and each test within it checks if an attribute
    analyzed is the same as desired for all articles.
    """
    def setUp(self):
        self.articles = _downloaded_articles

    def _check_all(self, function):
        """This helper method runs a given assert function on all articles."""
        for analyzed, desired in zip(self.articles, test_articles):
            with self.subTest(url=desired['url']):
                function(analyzed, desired, 
                         msg="\nError when analyzing {}".format(desired['url']))
    
    def test_title(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['title'], desired['title'], msg))
    
    def _check_text_equality(self, analyzed, desired, msg):
        levenshtein_distance = editdistance.eval(analyzed['text'],
                                                 desired['text'])
        ratio = levenshtein_distance / len(desired['text'])
        self.assertLess(ratio, ARTICLE_TEXT_EDIT_DISTANCE_THRESHOLD, msg=msg)

    def test_text(self):
        self._check_all(self._check_text_equality)

    def test_date(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['publish_date'], desired['publish_date'], msg))

    def test_sources(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertSetEqual(
                set(analyzed['sources']), set(desired['sources']), msg))

    def test_authors(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertSetEqual(
                set(analyzed['authors']), set(desired['authors']), msg))

if __name__ == "__main__":
    unittest.main()
