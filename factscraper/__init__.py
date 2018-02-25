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

# Maximum length of characters that the last line can be for us to
# still consider it a signature line
MAXIMUM_AUTHOR_LINE_LENGTH = 50

from factscraper import parsers, downloader

def analyze_url(url):
    """Returns analysis results of an article with the given url."""
    response = downloader.download(url)
    parser = parsers.select_parser(response.url)
    parsed_article = parser.parse(response)
    return parsed_article
