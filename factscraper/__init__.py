import os
import json
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from random import random
from time import sleep

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from newspaper import Article, build as build_newspaper
from newspaper.article import ArticleException

from factscraper.time_retriever import get_timestamp

def _clean_url(url):
    parsed_url = urlparse(url)
    url = urlunparse(
        ("https",
         parsed_url.netloc,
         parsed_url.path,
         "", "", ""))
    return url, parsed_url.netloc

def _format_timestamp(timestamp):
    return timestamp.strftime("%Y-%m-%d")

def _get_timestamp(url):
    return get_timestamp(url)

def _get_domain(url):
    domain = _clean_url(url)[1]
    return domain

def _filter_article(article, wanted_domain, blacklist):
    link_domain = _get_domain(article.url)
    return wanted_domain == link_domain and article.url not in blacklist

def _sleep_for_a_bit():
    sleep(0.5+(random()))

def get_all_links(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')
    urls = set([link.get('href') for link in soup.find_all('a')])
    bad_words = ['kontakt', 'regulamin']
    if urls is not None:
        urls = set(filter(lambda x: all(x is not None and word not in x.lower() for word in bad_words), urls))
    else:
        return []

    domain = _get_domain(url)
    out_urls = []
    for url in urls:
        parsed_url = urlparse(url)
        this_domain = parsed_url.netloc
        if this_domain == "":
            out_urls.append(urlunparse(("https", domain, parsed_url.path, "", "", "")))
        else:
            out_urls.append(urlunparse(("https", this_domain, parsed_url.path, "", "", "")))
    return out_urls

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
    if timestamp is None:
        timestamp = _get_timestamp(clean_url)
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
    
    json_file_path = 'articles/{}.jsonl'.format(article_dict['netloc'])
    with open(json_file_path, 'a') as file_:
        json_data = json.dumps(article_dict, ensure_ascii=False)
        file_.write("{}\n".format(json_data))

    sentences_file_path = 'articles/{}.sentences'.format(article_dict['netloc'])
    sentences_text = article_dict['text']
    for inter in [". ", "... ", "? ", "! ", ".", "...", "?", "!"]:
        stripped = inter.strip()
        sentences_text = sentences_text.replace(inter, stripped+"\n")
    sentences = sentences_text.split('\n')
    sentences = list(filter(lambda x: len(x) > 10, sentences))
    sentences_text = "\n".join(sentences)
    with open(sentences_file_path, 'a') as file_:
        file_.write("{}\n".format(sentences_text))

    titles_file_path = 'articles/{}.titles'.format(article_dict['netloc'])
    with open(titles_file_path, 'a') as file_:
        file_.write("{}\n".format(article_dict['title']))
    url_file_path = 'articles/{}.urls'.format(article_dict['netloc'])
    with open(url_file_path, 'a') as file_:
        file_.write("{}\n".format(article_dict['url']))

def crawl(url, verbose=False, blacklist=set(), to_explore=set(),
          minimum_title_len=12, download_limit=-1):
    """Searches for articles on a news website."""
    file_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    domain = _get_domain(url)
    if verbose:
        print("Retrieving site {} filtered for domain {}".format(url, domain))

#   news_site = build_newspaper(url, language="pl")
#   articles = list(filter(lambda x: _filter_article(x, domain, blacklist), news_site.articles))

    all_links = get_all_links(url)
    all_articles = [Article(x) for x in all_links]
    articles = list(filter(lambda x: _filter_article(x, domain,
                                                     blacklist), all_articles))

    blacklist = set.union(blacklist, [_clean_url(art.url)[0] for art in articles])
    to_explore = set.union(to_explore, [_clean_url(art.url)[0] for art in articles])

    domains = {}
    for article in all_articles:
        dom = _get_domain(article.url)
        if dom not in domains:
            domains[dom] = 1
        else:
            domains[dom] += 1
    if verbose:
        print(("Found {} unblacklisted articles in correct domain, {} articles"
               " total, {} on blacklist, {} left to explore").format(
            len(articles), len(all_articles), len(blacklist),
                  len(to_explore)))
        print("Domains:")
        for dom, number in domains.items():
            print("\t{}: {}".format(dom, number))

    if verbose:
        iterator = tqdm(articles)
    else:
        iterator = articles
    for article in iterator:
        try:
            _sleep_for_a_bit()
            article_dict = parse_article(article)
            if len(article_dict['title']) < minimum_title_len:
                continue
            if len(article_dict['text']) < minimum_title_len:
                continue
            save_article(article_dict, file_timestamp=file_timestamp)
        except ArticleException:
            continue
        if download_limit > 0:
            download_limit -= 1
        if download_limit == 0:
            break

    if len(to_explore) > 0:
        crawl(to_explore.pop(), verbose=verbose, blacklist=blacklist,
              to_explore=to_explore, download_limit=download_limit)

    return blacklist
