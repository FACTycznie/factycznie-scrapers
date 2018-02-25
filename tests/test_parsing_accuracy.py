import unittest

import scrapy
from datetime import datetime

from factscraper import analyze_url, downloader

class _TestArticle:
    def __init__(self, initial_url, clean_url, domain, title, text, 
                 publish_date, sources, authors):
        self.initial_url = initial_url
        self.clean_url = clean_url
        self.domain = domain
        self.title = title
        self.text = text
        self.publish_date = publish_date
        self.sources = sources
        self.authors = authors

test_articles = [
    _TestArticle(
        "http://fakty.interia.pl/swiat/news-wenezuela-powstal-czarny-rynek-krwi,nId,2549737",
        "http://fakty.interia.pl/swiat/news-wenezuela-powstal-czarny-rynek-krwi,nId,2549737",
        "fakty.interia.pl",
        "Wenezuela: Powstał czarny rynek krwi",
        "",
        datetime(year=2018, month=2, day=24),
        ['PAP'],
        []),
    _TestArticle(
        "http://fakty.interia.pl/swiat/news-izraelskie-media-polski-rzad-zamraza-ustawe-o-ipn,nId,2549714",
        "http://fakty.interia.pl/swiat/news-izraelskie-media-polski-rzad-zamraza-ustawe-o-ipn,nId,2549714",
        "fakty.interia.pl",
        "Izraelskie media: Polski rząd zamraża ustawę o IPN",
        "",
        datetime(year=2018, month=2, day=24),
        ['IAR', 'PAP', 'INTERIA.PL'],
        [])]

class TestDownload(unittest.TestCase):
    """This test case checks if `factscraper.downloader` works."""
    def setUp(self):
        self.test_url = "https://wroclaw.onet.pl/tragiczny-wypadek-we-wroclawiu-nie-zyje-mezczyzna/v3kvx88"

    def test_download(self):
        download_result = downloader.download(self.test_url)
        self.assertIsInstance(
            download_result,
            scrapy.http.HtmlResponse)
        self.assertIn(bytes("article", 'utf-8'), download_result.body)


# Download them now so we don't have to redownload them for each test
_downloaded_articles = [analyze_url(article.initial_url)
                        for article in test_articles]

class TestGeneralAnalysis(unittest.TestCase):
    """This test case downloads and analyzes all articles from
    test_articles, and each test within it checks if an attribute
    analyzed is the same as desired for all articles.
    """
    # TODO: Test text equality
    def setUp(self):
        self.articles = _downloaded_articles

    def _check_all(self, function):
        for analyzed, desired in zip(self.articles, test_articles):
            function(analyzed, desired, 
                     msg="\nError when analyzing {}".format(desired.initial_url))
    
    def test_clean_url(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['url'], desired.clean_url, msg))

    def test_domain(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['domain'], desired.domain, msg))

    def test_title(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertEqual(
                analyzed['title'], desired.title, msg))

    def test_sources(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertSetEqual(
                set(analyzed['sources']), set(desired.sources), msg))

    def test_authors(self):
        self._check_all(
            lambda analyzed, desired, msg: self.assertSetEqual(
                set(analyzed['authors']), set(desired.authors), msg))

if __name__ == "__main__":
    unittest.main()
