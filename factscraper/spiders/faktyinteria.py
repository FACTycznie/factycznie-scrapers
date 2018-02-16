# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json

file_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class FaktyInteriaSpider(scrapy.Spider):
    name = 'faktyinteria'
    start_urls = [
        'http://fakty.interia.pl/mazowieckie/news-duzy-pozar-na-mokotowie-trwa-akcja-strazakow,nId,2523273',
        'http://fakty.interia.pl/autor/jolanta-kaminska-aleksandra-gieracka/news-fedorowicz-tusk-powinien-byc-prezydentem-polski,nId,2521557',
        'http://film.interia.pl/wiadomosci/news-gilda-gray-sierota-z-krakowa-ktora-podbila-hollywood,nId,2522921',
        'http://fakty.interia.pl/swiat/news-turcja-wojskowy-samolot-rozbil-sie-w-czasie-lotu-szkoleniowe,nId,2523291',
        'http://fakty.interia.pl/polska/news-wicepremier-ukrainy-zmiany-w-ustawie-o-ipn-moga-pogorszyc-sy,nId,2546092',
        'http://fakty.interia.pl/wiadomosci-lokalne/news-gdansk-prywatni-prawnicy-z-miejskich-pieniedzy-prokuratura-s,nId,2546085',
        'http://fakty.interia.pl/raporty/raport-afera-reprywatyzacyjna-w-warszawie/aktualnosci/news-komisja-weryfikacyjna-z-wiekszymi-uprawnieniami-jest-podpis-,nId,2523375',
        'http://fakty.interia.pl/raporty/raport-wybory-samorzadowe-2018/aktualnosci/news-trzaskowski-porozumienie-z-nowoczesna-powinno-byc-poszerzone,nId,2523270',
    ]

    def parse(self, response):
        title = response.css('h1.article-title::text').extract_first().strip()
        timestamp = response.css("a.article-date::attr(href)").extract_first().split(',')[-1]

        tags = []

        comments_count = None #response.xpath("span.forum__header-label-count::text").extract_first()


        text_parts = []
        content = response.css("div.article-body").css("p::text")
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

        file_path = 'results.{}.{}.jsonl'.format(FaktyInteriaSpider.name,
                                                 file_timestamp)

        with open(file_path, 'a') as f:
            json_data = json.dumps(data, ensure_ascii=False)
            f.write("{}\n".format(json_data))

    def normalize(self, data):
        data["timestamp"] = datetime.strptime(data["timestamp"], "%Y-%m-%d")
        data["timestamp"] = data["timestamp"].strftime( "%Y-%m-%d %H:%M")
        return data
