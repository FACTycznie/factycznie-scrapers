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
        raise
