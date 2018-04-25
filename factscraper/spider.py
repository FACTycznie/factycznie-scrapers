import scrapy

from factscraper import InvalidArticleError, RELIABLE_DOMAINS
from factscraper.parsers import select_parser
from factscraper.util import get_domain, get_scheme

def _append_prefix(response, local_url):
    out_url = local_url
    if get_domain(out_url) == "":
        out_url = get_domain(response.url) + out_url
    if get_scheme(out_url) == "":
        out_url = get_scheme(response.url) + "://" + out_url
    return out_url

def _gather_links(response):
    links = []
    # RSS feeds
    links.extend(response.xpath("//item/link/text()").extract())
    # fakty.interia.pl frontpage
    links.extend(response.xpath(
        "/html/body/div/div/div/section/ul/li/div/div/h2/a/@href").extract())
    # desperate to get all links
    links.extend(response.xpath("//a/@href").extract())

    out_links = set()
    for link in links:
        if get_domain(link) == "" or get_scheme(link) == "":
            link = _append_prefix(response, link)
        out_links.add(link)
    return out_links

class FactycznieSpider(scrapy.Spider):
    name = 'factycznie.spider'

    allowed_domains = RELIABLE_DOMAINS

    start_urls = [
        'http://fakty.interia.pl/',
        'https://www.tvn24.pl/najwazniejsze.xml',
        'http://www.rmf24.pl/fakty/feed']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,
                             self.parse_frontpage)
       
    def parse_frontpage(self, response):
        links = _gather_links(response)
        for link in links:
            yield response.follow(link, callback=self.parse)

    def parse(self, response):
        try:
            yield select_parser(response.url).parse(response)
        except InvalidArticleError:
            pass
        links = _gather_links(response)
        for link in links:
            yield scrapy.Request(link, callback=self.parse)
