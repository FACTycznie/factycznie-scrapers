"""This file contains tests that check if our download system works."""
import unittest

import scrapy

from factscraper import downloader

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
