import scrapy
import dateparser
import re

from factscraper import InvalidArticleError
from factscraper.parsers import FaktyInteriaParser

class FaktyInteriaSpider(scrapy.Spider):
    name = 'fakty.interia'

    allowed_domains = ['fakty.interia.pl']
    start_urls = ['http://fakty.interia.pl/']

    def start_requests(self):
        yield scrapy.Request('http://fakty.interia.pl/',
                             self.parse_frontpage)
       
    def parse_frontpage(self, response):
        # further pages from the front page
        links = response.xpath(
            "/html/body/div/div/div/section/ul/li/div/div/h2/a/@href").extract()
        for link in links:
            yield response.follow(link, callback=self.parse)

    def parse(self, response):
        try:
            return FaktyInteriaParser.parse(response)
        except InvalidArticleError:
            pass
