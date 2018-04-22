"""
factscraper
===========
This package contains scrapers designed to parse and retrieve usable
information from Polish news sites.
"""
class InvalidArticleError(Exception):
    """Raised when a webpage is not an article"""

# Minimum length of the body of an article in characters
MINIMUM_ARTICLE_LENGTH = 300

# Domains from which articles had been confirmed to be parsed correctly
RELIABLE_DOMAINS = [
    "nt.interia.pl",
    "wiadomosci.onet.pl",
    "wiadomosci.gazeta.pl",
    "www.newsweek.pl",
    "www.se.pl",
    "fakty.interia.pl",
    "wroclaw.onet.pl",
    "www.rmf24.pl",
    "www.tvn24.pl"]

from factscraper import parsers, downloader

def analyze_url(url, verbose=False, parser=None, validate=True):
    """Returns analysis results of an article with the given url."""
    response = downloader.download(url)
    return analyze_response(response, verbose=verbose, parser=parser,
                            validate=validate)

def analyze_response(response, verbose=False, parser=None, validate=True):
    """Returns analysis results of an article from a response instance."""
    if parser is None:
        parser = parsers.select_parser(response.url)
    if verbose:
        print("Using parser", parser.__name__)
    parsed_article = parser.parse(response, validate=validate)
    return parsed_article
