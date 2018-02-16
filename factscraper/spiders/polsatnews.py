# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json

file_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class PolsatNewsSpider(scrapy.Spider):
    name = 'polsatnews'
    start_urls = [
        'http://www.polsatnews.pl/wiadomosc/2018-01-20/pozar-mieszkania-na-warszawskim-mokotowie-jedna-osoba-zginela',
        'http://www.polsatnews.pl/wiadomosc/2018-02-16/nowelizacja-ustawy-o-ochronie-praw-lokatorow-z-podpisem-prezydenta/?ref=aside_najnowsze',
        'http://www.polsatnews.pl/wiadomosc/2018-02-16/dziennikarz-die-welt-zwolniony-z-aresztu-w-turcji/',
        'http://www.polsatnews.pl/wiadomosc/2018-02-16/sad-odmowil-rejestracji-nazwy-partii-porozumienie-bedzie-wiec-porozumienie-jaroslawa-gowina/?ref=aside_najnowsze',
        'http://www.polsatnews.pl/wiadomosc/2018-02-16/rpo-prosi-o-wyjasnienia-ws-zatrzymania-frasyniuka-pyta-m-in-o-kajdanki-i-pore-przyjscia-policji/?ref=najwazniejsze',
        'http://www.polsatnews.pl/wiadomosc/2018-02-16/starosta-wodzislawski-zlozyl-w-sadzie-wniosek-o-delegalizacje-stowarzyszenia-duma-i-nowoczesnosc/?ref=najwazniejsze',
        'http://www.polsatnews.pl/wiadomosc/2018-02-16/40-proc-polakow-za-nowela-ustawy-o-ipn-51-proc-uwaza-ze-z-dezinformacja-nalezy-walczyc-inaczej/?ref=najwazniejsze',
        'http://www.polsatnews.pl/wiadomosc/2018-02-16/czterech-polakow-powalczy-o-medale-w-olimpijskim-konkursie-na-duzej-skoczni/?ref=najwazniejsze',
        'http://www.polsatnews.pl/wiadomosc/2018-02-16/yad-vashem-chce-zmian-w-nowelizacji-ustawy-o-ipn-udzial-polakow-w-mordowaniu-zydow-byl-powszechny/?ref=najwazniejsze',
    ]

    def parse(self, response):
        title = response.css('article.article').css('h1::text').extract_first()
        timestamp = response.css('div.article-meta-data').css("div.fl-right::text").extract_first()

        tags = response.css("div.tags").css("a.tag::text").extract()

        comments_count = None

        text_parts = []
        article_preview = response.css("div.article-preview::text").extract_first()
        text_parts.append(article_preview)

        content = response.css("div.article-text").css("p::text")
        for part in content:
            text_parts.append(part.extract())

        text = " ".join(text_parts)

        data = {
            "url": response.url,
            "title": title,
            "timestamp": timestamp,
            "tag": tags,
            "comments_count": comments_count,
            "text": text
        }

        data = self.normalize(data)

        file_path = 'results.{}.{}.jsonl'.format(PolsatNewsSpider.name,
                                                 file_timestamp)

        with open(file_path, 'a') as f:
            json_data = json.dumps(data, ensure_ascii=False)
            f.write("{}\n".format(json_data))

    def normalize(self, data):
        data["timestamp"] = datetime.strptime(data["timestamp"], "%Y-%m-%d, %H:%M")
        data["timestamp"] = data["timestamp"].strftime( "%Y-%m-%d %H:%M")
        return data
