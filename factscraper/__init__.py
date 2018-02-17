import os
import json
from datetime import datetime
from urllib.parse import urlparse, urlunparse

from tqdm import tqdm
from newspaper import Article, build as build_newspaper
from newspaper.article import ArticleException

def _clean_url(url):
    parsed_url = urlparse(url)
    url = urlunparse(
        (parsed_url.scheme,
         parsed_url.netloc,
         parsed_url.path,
         "", "", ""))
    return url, parsed_url.netloc

def _format_timestamp(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M")

def parse(url):
    """Returns a dict of information about an article with a given url."""
    article = Article(url, language='pl')
    return parse_article(article)

def parse_article(article):
    clean_url, netloc = _clean_url(article.url)

    article.download()
    article.parse()
    # FIXME: the date gets lost sometimes like: http://warszawa.wyborcza.pl/warszawa/7,54420,23034886,biurowce-kusza-parkingami-a-ratusz-nagina-wlasne-normy-zapisy.html?utm_source=facebook.com&utm_medium=SM&utm_campaign=FB_Warszawa_Wyborcza
    timestamp = article.publish_date
    if timestamp is not None:
        timestamp = _format_timestamp(timestamp)

    data = {
        "url": clean_url,
        "netloc": netloc,
        "title": article.title, 
        "timestamp": timestamp,
        "text": article.text,
        "authors": article.authors,
        "tags": list(article.tags)}
    return data

def save_article(article_dict, file_timestamp=None):
    try:
        os.makedirs('articles')
    except FileExistsError:
        pass

    if file_timestamp is None:
        file_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    file_path = 'articles/{}.{}.jsonl'.format(article_dict['netloc'],
                                              file_timestamp)
    with open(file_path, 'a') as file_:
        json_data = json.dumps(article_dict, ensure_ascii=False)
        file_.write("{}\n".format(json_data))

def _get_domain(url):
    domain = _clean_url(url)[1]
    return domain

def _filter_domain(article, wanted_domain):
    link_domain = _get_domain(article.url)
    return wanted_domain == link_domain

def crawl(url, verbose=False):
    """Searches for articles on a news website."""
    file_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    domain = _get_domain(url)
    if verbose:
        print("Retrieving site {} filtered for domain {}".format(url, domain))

    news_site = build_newspaper(url, language="pl")
    articles = list(filter(lambda x: _filter_domain(x, domain), news_site.articles))

    domains = {}
    for article in news_site.articles:
        dom = _get_domain(article.url)
        if dom not in domains:
            domains[dom] = 1
        else:
            domains[dom] += 1

    if verbose:
        print("Found {} articles in correct domain, {} articles total".format(
            len(articles), len(news_site.articles)))
        print("Domains:")
        for dom, number in domains.items():
            print("\t{}: {}".format(dom, number))
    
    if verbose:
        iterator = tqdm(articles)
    else:
        iterator = articles
    for article in iterator:
        try:
            article_dict = parse_article(article)
            save_article(article_dict, file_timestamp=file_timestamp)
        except ArticleException:
            pass
