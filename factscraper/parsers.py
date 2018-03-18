"""This module contains functions that can parse downloaded webpages and
retrieve desired information from them by combining functionalities
from other `factscraper` modules.
"""
import inspect
import sys

import dateparser
import re

from factscraper import InvalidArticleError, MINIMUM_ARTICLE_LENGTH, MAXIMUM_AUTHOR_LINE_LENGTH
from factscraper.util import clean_url, get_domain

class GenericParser:
    """Generic parser that is designed to work on as many sites as
    possible. All other parsers extend it.
    """
    ### For the time being this is a copy of FaktyInteriaParser ###
    domains = []

    @classmethod
    def parse(cls, response):
        out_dict = {
            'url': clean_url(response.url),
            'domain': get_domain(response.url),
            'title': cls.parse_title(response),
            'text': cls.parse_text(response),
            'publish_date': cls.parse_date(response),
            'sources': cls.parse_sources(response),
            'authors': cls.parse_authors(response)}

        if len(out_dict['text']) < MINIMUM_ARTICLE_LENGTH:
            raise InvalidArticleError("Article is too short")

        return out_dict

    @classmethod
    def parse_title(cls, response):
        title_str = response.xpath(
            "/html/body/div/div/div/article/header/div/h1/text()"
        ).extract_first()
        if title_str is not None:
            return title_str.strip() 
        return None

    @classmethod
    def parse_text(cls, response):
        article_lead = "\n".join(response.xpath("//div[contains(@id, 'lead')][contains(@id, 'article')]/text()").extract())
        article_body = "\n".join(response.xpath("normalize-space(//div[contains(@id, 'body')][contains(@id, 'article')])").extract())
        text = article_lead + "\n" + article_body
        if len(text) < MINIMUM_ARTICLE_LENGTH:
            text = " ".join(response.xpath("//div[@class='article-body']/node()[not(descendant-or-self::div)]//text()").re("[^\ '\\xa0']+"))
        return text

    @classmethod
    def parse_date(cls, response):
        date_strings = response.xpath("//meta[@property='article:published_time']/@content").extract()
        if len(date_strings) > 0:
            article_date = dateparser.parse(date_strings[0]).date()
            return article_date
        return None

    @classmethod
    def parse_sources(cls, response):
        sources = response.xpath(
            "//cite[@itemtype='http://schema.org/Organization']//@content"
        ).extract()
        return sources
    
    @classmethod
    def parse_authors(cls, response):
        text = cls.parse_text(response)
        last_sentence = re.split("[.!?]", text)[-1]
        capitalized_word_pairs = re.findall(
            "(?:([A-Z][a-z]*)\ ([A-Z][a-z]*))", 
            last_sentence)
        if len(capitalized_word_pairs) >= 1 and len(last_sentence) < MAXIMUM_AUTHOR_LINE_LENGTH:
            author = " ".join(capitalized_word_pairs[-1])
            return [author]
        return []

class FaktyInteriaParser(GenericParser):
    """Parser that works on fakty.interia.pl"""
    domains = ['fakty.interia.pl']

    @classmethod
    def parse_title(cls, response):
        title_str = response.xpath(
            "normalize-space(/html/body/div/div/div/article/header/div/h1/text())"
        ).extract_first()
        if title_str is not None:
            # Fix zero width spaces
            return title_str.strip().replace('\u200b', '')
        return None

    @classmethod
    def parse_text(cls, response):
        text = " ".join(response.xpath("//div[@class='article-body']/node()[not(descendant-or-self::div)]//text()").re("[^\ '\\xa0']+"))
        return text

    @classmethod
    def parse_date(cls, response):
        # regex below looks for a number in the timestamp (day) and grabs
        # everything until a giant blob of whitespace
        date_strings = response.xpath(
            "/html/body/div/div/div/article/div/div/div/a/text()").re(
                '[0-9].*?(?=\s{2})')
        if len(date_strings) > 0:
            article_date = dateparser.parse(date_strings[0]).date()
            return article_date
        return None

    @classmethod
    def parse_sources(cls, response):
        sources = response.xpath(
            "//cite[@itemtype='http://schema.org/Organization']//@content"
        ).extract()
        clean_sources = []
        for source in sources:
            clean_sources.extend(source.split("/"))
        return clean_sources
    
    @classmethod
    def parse_authors(cls, response):
        text = cls.parse_text(response)
        last_sentence = re.split("[.!?]", text)[-1]
        capitalized_word_pairs = re.findall(
            "(?:([A-Z][a-z]*)\ ([A-Z][a-z]*))", 
            last_sentence)
        if len(capitalized_word_pairs) >= 1 and len(last_sentence) < MAXIMUM_AUTHOR_LINE_LENGTH:
            author = " ".join(capitalized_word_pairs[-1])
            return [author]
        return []

class WiadomosciOnetParser(GenericParser):
    """Parser that works on wiadomosci.onet.pl"""
    domains = ['wiadomosci.onet.pl']

    @classmethod
    def _parse_authors_from_text(cls, text):
        """This method attempts to find authors from the last line of
        the text. We use it if an initial search for the author fails.
        """
        lines = text.split("\n")
        authors = []
        if re.search("^\([a-zA-Z0-9]*\)$", lines[-1]):
            authors = list(re.search("(?:\((.*)\))", lines[-1]).groups())
            del lines[-1]
        text = "\n".join(lines)
        return authors, text

    @classmethod
    def parse_title(cls, response):
        title_str = response.xpath(
            "normalize-space(//h1[@class='mainTitle']/text())"
        ).extract_first()
        if title_str is not None:
            # Fix zero width spaces
            return title_str.strip().replace('\u200b', '')
        return None

    @classmethod
    def parse_text(cls, response, clean=True):
        article_lead = response.xpath("normalize-space(//div[@id='lead']/text())").extract()[0]
        article_body = "\n".join(response.xpath("//div[@itemprop='articleBody']/p/text()").extract())
        text = article_lead + "\n" + article_body
        if clean:
            text = cls._parse_authors_from_text(text)[1]
        return text

    @classmethod
    def parse_sources(cls, response):
        sources = response.xpath("//span[@itemprop='sourceOrganization']//span[@itemprop='name']/text()").extract()
        return sources
    
    @classmethod
    def parse_authors(cls, response):
        authors = response.xpath("//span[@itemprop='author']//span[@itemprop='name']/text()").extract()
        if authors == []:
            authors = cls._parse_authors_from_text(cls.parse_text(response,
                                                                  clean=False))[0]
        return authors

    ### ### Parser choice ### ###

def _is_parser(obj):
    is_class = inspect.isclass(obj)
    if is_class:
        return issubclass(obj, GenericParser)
    return False

_parser_collection = inspect.getmembers(
    sys.modules[__name__], _is_parser)

parser_dict = {}
for parser_tuple in _parser_collection:
    for domain in parser_tuple[1].domains:
        if domain not in parser_dict:
            parser_dict[domain] = parser_tuple[1]
        else:
            raise ValueError("Domain {} already handled by {}".format(
                domain, parser_dict[domain].__name__))

def select_parser(url):
    """Selects the correct parser for a url based on its domain."""
    domain = get_domain(url)
    if domain in parser_dict:
        return parser_dict[domain]
    else:
        return GenericParser
