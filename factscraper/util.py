import unicodedata

from urllib.parse import urlparse, urlunparse

def clean_url(url, scheme=None):
    """Returns a cleaner url, i.e. without queries or parameters."""
    parsed_url = urlparse(url)
    if scheme is None:
        scheme = parsed_url.scheme
    url = urlunparse(
        (scheme,
         parsed_url.netloc,
         parsed_url.path,
         "", "", ""))
    return url

def get_domain(url):
    """Returns the domain from a url."""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def get_scheme(url):
    """Returns the scheme from a url, e.g. http or https."""
    parsed_url = urlparse(url)
    return parsed_url.scheme

def clean_string(string):
    """Returns a unicode normalized, whitespace stripped string."""
    return unicodedata.normalize('NFKC', string).replace('\u200b', '').strip()
