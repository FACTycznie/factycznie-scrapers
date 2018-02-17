import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

def get_timestamp(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')
    # interia
    try:
        maybs = soup.findAll("a", {"class":"article-date"})[0].get('href')[-10:]
        return datetime.strptime(maybs, "%Y-%m-%d")
    except:
        pass
    # naszemiasto
    try:
        maybs = soup.findAll("div", {"class":"matZrodlo"})[0].span.text.strip()
        date = re.findall("[0-9]{4}-[0-9]{2}-[0-9]{2}", maybs)[0]
        return datetime.strptime(date, "%Y-%m-%d")
    except:
        pass
    # wiadomosci.gazeta.pl
    try:
        maybs = soup.findAll("div", {"id":"gazeta_article_date"})[0].text.strip()
        date = re.findall("[0-9]{2}.[0-9]{2}.[0-9]{4}", maybs)[0]
        return datetime.strptime(date, "%d.%m.%Y")
    except:
        pass
    # rp.pl
    try:
        maybs = re.findall("Publikacja\: \<time\>[0-9\.]{10}", str(html))[0]
        date = re.findall("[0-9]{2}.[0-9]{2}.[0-9]{4}", maybs)[0]
        return datetime.strptime(date, "%d.%m.%Y")
    except:
        pass
    # tvn24.pl
    try:
        maybs = soup.findAll("div", {"class":"articleDateContainer borderGreyBottom"})[0].time.get("datetime")
        date = re.findall("[0-9]{4}-[0-9]{2}-[0-9]{2}", maybs)[0]
        return datetime.strptime(date, "%Y-%m-%d")
    except:
        pass
