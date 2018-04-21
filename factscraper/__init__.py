"""
factscraper
===========
This package contains scrapers designed to parse and retrieve usable
information from Polish news sites.
"""
class InvalidArticleError(Exception):
    """Raised when a webpage is not an article"""

# Minimum length of the body of an article in characters
MINIMUM_ARTICLE_LENGTH = 400

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
