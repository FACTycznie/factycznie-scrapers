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
    domain = None

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
        text = " ".join(response.xpath("//div[@class='article-body']/node()[not(descendant-or-self::div)]//text()").re("[^\ '\\xa0']+"))
        return text

    @classmethod
    def parse_date(cls, response):
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
    domain = 'fakty.interia.pl'

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

def _is_parser(obj):
    is_class = inspect.isclass(obj)
    if is_class:
        return issubclass(obj, GenericParser)
    return False

_parser_collection = inspect.getmembers(
    sys.modules[__name__], _is_parser)

parser_dict = {
    parser_tuple[1].domain: parser_tuple[1] for parser_tuple in _parser_collection}

def select_parser(url):
    """Selects the correct parser for a url based on its domain."""
    domain = get_domain(url)
    if domain in parser_dict:
        return parser_dict[domain]
    else:
        return GenericParser
