# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json

file_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class NaseMiastoSpider(scrapy.Spider):
    name = 'naszemiasto'
    start_urls = [
        'http://warszawa.naszemiasto.pl/artykul/pozar-na-mokotowie-plonie-budynek-przy-ul-raclawickiej,4411718,artgal,t,id,tm.html',
        'http://warszawa.naszemiasto.pl/artykul/przez-dwie-zimy-fotografowal-pasazerow-w-tramwajach-znajda,4411994,artgal,t,id,tm.html',
        'http://warszawa.naszemiasto.pl/artykul/remonty-drog-i-nowe-sciezki-rowerowe-w-warszawie-czekaja,4411958,galop,t,id,tm.html',
        'http://warszawa.naszemiasto.pl/artykul/na-woli-powstal-parking-przyszlosci-winda-odstawi-samochod,4411726,artgal,t,id,tm.html',
        'http://warszawa.naszemiasto.pl/artykul/smog-w-warszawie-powstala-mapa-miejskich-kopciuchow-wiemy,4410590,art,t,id,tm.html',
        'http://warszawa.naszemiasto.pl/artykul/zaginal-na-wysokosci-7400-metrow-himalaisty-z-warszawy,4389276,art,t,id,tm.html',
        'http://warszawa.naszemiasto.pl/artykul/na-warszawskich-ulicach-jest-coraz-bezpieczniej-miasto,4326209,art,t,id,tm.html'
    ]

    def parse(self, response):
        title = response.css('h1.matTytul::text').extract_first().strip()
        timestamp = response.css('div.matZrodlo').css("span::text").extract_first().strip().split(',')[0]

        tags = []

        comments_xpath = '//*[@id="skomentuj-ilosc"]/text()'
        comments_count = response.xpath(comments_xpath).extract_first()

        text_parts = []
        article_preview = response.css("p.zajawka::text").extract_first()
        text_parts.append(article_preview)

        content_xpath = '//*[@id="tresc"]/text()'
        content = response.xpath(content_xpath).extract_first()
        text_parts.append(content)

        text = " ".join(text_parts)

        data = {
            "url": response.url,
            "title": title,
            "timestamp": timestamp,
            "tag": tags,
            "comments_count": comments_count[1:-1],
            "text": text
        }

        data = self.normalize(data)

        file_path = 'results.{}.{}.jsonl'.format(NaseMiastoSpider.name,
                                                 file_timestamp)

        with open(file_path, 'a') as f:
            json_data = json.dumps(data, ensure_ascii=False)
            f.write("{}\n".format(json_data))

    def normalize(self, data):
        data["timestamp"] = datetime.strptime(data["timestamp"], "%Y-%m-%d")
        data["timestamp"] = data["timestamp"].strftime( "%Y-%m-%d %H:%M")
        return data
