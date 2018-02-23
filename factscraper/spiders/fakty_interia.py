import scrapy
import dateparser
import re

from factscraper import InvalidArticleError, MINIMUM_ARTICLE_LENGTH, MAXIMUM_AUTHOR_LINE_LENGTH

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
            title = response.xpath("/html/body/div/div/div/article/header/div/h1/text()").extract_first().strip() 
            text = " ".join(
                response.xpath("/html/body/div/div/div/article/div/div/p/text()").extract()).replace("\xa0", " ")
            text = " ".join(response.xpath("//div[@class='article-body']/node()[not(descendant-or-self::div)]//text()").re("[^\ '\\xa0']+"))
            if len(text) < MINIMUM_ARTICLE_LENGTH:
                raise InvalidArticleError

            # Last line might have the author
            last_line = " ".join(response.xpath("//div[@class='article-body']/node()[not(descendant-or-self::div)][normalize-space()][string-length()>6][last()]//text()").re("[^\ '\\xa0']+"))
            capitalized_word_pairs = re.findall("(?:([A-Z][a-z]*)\ ([A-Z][a-z]*))", last_line)
            if len(capitalized_word_pairs) >= 1 and len(last_line) < MAXIMUM_AUTHOR_LINE_LENGTH:
                author = " ".join(capitalized_word_pairs[-1])
                text = text.replace(last_line, " ")
            else:
                author = None

            # regex below looks for a number in the timestamp (day) and grabs
            # everything until a giant blob of whitespace
            article_date = dateparser.parse(response.xpath(
                "/html/body/div/div/div/article/div/div/div/a/text()").re('[0-9].*?(?=\s{2})')[0])
            sources = response.xpath("//cite[@itemtype='http://schema.org/Organization']//@content").extract()
            out_dict = {
                "title": title,
                "text": text,
                "publish_date": article_date,
                "sources": sources,
                "author": author}
            yield out_dict
        except AttributeError as e:
            if 'NoneType' in e.args[0]:
                pass
            else:
                raise
        except InvalidArticleError:
            pass
