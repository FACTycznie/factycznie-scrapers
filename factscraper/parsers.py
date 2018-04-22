"""This module contains functions that can parse downloaded webpages and
retrieve desired information from them by combining functionalities
from other `factscraper` modules.
"""
import inspect
import sys

import dateparser
import re

from factscraper import InvalidArticleError, MINIMUM_ARTICLE_LENGTH
from factscraper.util import clean_url, get_domain, clean_string

def validate_article(article_dict):
    """Checks whether a parsed article dict is valid, and returns an
    exception if it isn't.
    """
    needed_attributes = ['title', 'text', 'publish_date', 'url', 'domain']
    for attribute in needed_attributes:
        if attribute not in article_dict:
            return InvalidArticleError("Attribute {} not present".format(
                                       attribute))
    for attribute in ['title', 'text']:
        if article_dict[attribute] is None:
            return InvalidArticleError("Attribute {} is empty".format(
                                       attribute))
    if len(article_dict['text']) < MINIMUM_ARTICLE_LENGTH:
        return InvalidArticleError("Article is too short")

def _try_parsing(function, argument):
    try:
        return function(argument)
    except Exception as exc:
        return None

class GenericParser:
    """Generic parser that is designed to work on as many sites as
    possible.
    """
    domains = []

    @classmethod
    def parse(cls, response, validate=True):
        if validate:
            try:
                out_dict = {
                    'url': clean_url(response.url),
                    'domain': get_domain(response.url),
                    'title': cls.parse_title(response),
                    'text': cls.parse_text(response),
                    'publish_date': cls.parse_date(response)}
            except Exception as exc:
                raise InvalidArticleError from exc
            invalid_article_exception = validate_article(out_dict)
            if invalid_article_exception is not None:
                raise invalid_article_exception
        else:
            out_dict = {
                'url': _try_parsing(clean_url, response.url),
                'domain': _try_parsing(get_domain, response.url),
                'title': _try_parsing(cls.parse_title, response),
                'text': _try_parsing(cls.parse_text, response),
                'publish_date': _try_parsing(cls.parse_date, response)}
        return out_dict

    @classmethod
    def parse_title(cls, response):
        try:
            return clean_string(response.xpath(
                "//meta[@property='og:title']/@content").extract_first())
        except AttributeError:
            pass

    @classmethod
    def parse_text(cls, response):
        article_lead = response.xpath(
            "//div[contains(@id, 'lead')][contains(@id, 'article')]/text()").extract()
        article_body = response.xpath(
            "normalize-space(//div[contains(@id, 'ody')][contains(@id, 'article')])").extract()
        article_content = response.xpath("//div[contains(@class, 'ontent')][contains(@class, 'article')]/p").xpath("normalize-space(.)").extract()
        complete_article = article_lead + article_body + article_content
        text = "\n".join(complete_article)
        if len(text) < MINIMUM_ARTICLE_LENGTH:
            text = " ".join(response.xpath("//div[@class='article-body']/node()[not(descendant-or-self::div)]//text()").re("[^\ '\\xa0']+"))
        return text

    @classmethod
    def parse_date(cls, response):
        date_string = response.xpath(
            "//meta[@property='article:published_time']/@content").extract_first()
        if date_string is None:
            date_string = response.xpath(
                "//meta[@itemprop='datePublished']/@content").extract_first()
        try:
            return dateparser.parse(date_string).date()
        except TypeError:
            pass
    
class FaktyInteriaParser(GenericParser):
    domains = ['fakty.interia.pl']
    @classmethod
    def parse_text(cls, response):
        text = " ".join(response.xpath("//div[@class='article-body']/node()[not(descendant-or-self::div)]//text()").re("[^\ '\\xa0']+"))
        return text

class WiadomosciOnetParser(GenericParser):
    domains = ['wiadomosci.onet.pl', 'wroclaw.onet.pl']
    @classmethod
    def parse_text(cls, response):
        article_lead = response.xpath("normalize-space(//div[@id='lead']/text())").extract()[0]
        article_body = "\n".join(response.xpath("//div[@itemprop='articleBody']/p/text()").extract())
        text = article_lead + "\n" + article_body
        return text

class WiadomosciGazetaParser(GenericParser):
    domains = ['wiadomosci.gazeta.pl']
    @classmethod
    def parse_date(cls, response):
        try:
            return dateparser.parse(response.xpath(
                "//div[@id='gazeta_article_date']//time/@datetime").extract_first()).date()
        except TypeError:
            pass

class SeParser(GenericParser):
    domains = ['www.se.pl']
    @classmethod
    def parse_text(cls, response):
        lead = response.xpath("//div[@class='lead']/p/text()").extract_first()
        body = "\n".join(response.xpath("//div[@class='text-block']/p//text()").extract())
        return lead + body

class NtInteriaParser(GenericParser):
    domains = ['nt.interia.pl']
    @classmethod
    def parse_text(cls, response):
        return "\n".join(response.xpath(
            "//div[@class='article-body']/p/text()").extract())

class TVN24Parser(GenericParser):
    domains = ['www.tvn24.pl']
    @classmethod
    def parse_text(cls, response):
        try:
            article_sel = response.xpath("//article")[0]
        except IndexError as exc:
            raise InvalidArticleError("Article container not found") from exc
        lead = article_sel.xpath('normalize-space(h2//text())').extract_first()
        body = "\n".join(article_sel.xpath('p/text()').extract())
        return lead + "\n" + body
    @classmethod
    def parse_date(cls, response):
        try:
            return dateparser.parse(
                response.xpath("//div[contains(@class, 'mainContainer')]//time/@datetime").extract_first()).date()
        except:
            pass

class RMF24Parser(GenericParser):
    domains = ['www.rmf24.pl']
    @classmethod
    def parse_text(cls, response):
        return "\n".join([clean_string(paragraph) for paragraph in response.xpath("//div[@class='article-container']//p//text()").extract()])

class NewsweekParser(GenericParser):
    domains = ['www.newsweek.pl']
    @classmethod
    def parse_text(cls, response):
        try:
            article_sel = response.xpath("//div[@class='artLeft']")[0]
        except IndexError as exc:
            raise InvalidArticleError("Article container not found") from exc
        paragraphs = article_sel.xpath(".//p[not(descendant-or-self::script)]//text()").extract()
        text = "\n".join(map(clean_string, paragraphs))
        return text

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
