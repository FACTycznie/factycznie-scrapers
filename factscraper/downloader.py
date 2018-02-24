"""This module contains functions for directly downloading webpages."""
import requests
import scrapy

def download(url):
    """Returns a `scrapy.http.HtmlResponse` downloaded from a url."""
    requests_response = requests.get(url)
    return scrapy.http.HtmlResponse(requests_response.url,
                                    status=requests_response.status_code,
                                    headers=requests_response.headers,
                                    body=requests_response.content)
