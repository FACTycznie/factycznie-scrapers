# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime, timedelta
import json

file_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class WiadomosciWPSpider(scrapy.Spider):
    name = 'wp'
    start_urls = [
        'https://wiadomosci.wp.pl/meksyk-katastrofa-wojskowego-helikoptera-zginely-dwie-osoby-na-ziemi-6221221229409921a',
        'https://wiadomosci.wp.pl/odkryli-ukryte-zycie-w-jaskiniach-antarktydy-szereg-skomplikowanych-form-6164918979733633a',
        'https://wiadomosci.wp.pl/aborcja-jak-wyjscie-po-bulki-wo-tlumacza-sie-z-okladki-6220966552807553a',
        'https://wiadomosci.wp.pl/niepokojacy-efekt-likwidacji-gimnazjow-rodzice-bija-na-alarm-6221251713738881a',
    ]

    def parse(self, response):
        title = response.css('h1.article--title::text').extract_first().strip()
        author = response.css("span.signature--author::text").extract_first()
        timestamp = response.css("div.signature--when").css("span::text")[0].extract()

        tags = []

        comments_count = None #response.xpath("span.forum__header-label-count::text").extract_first()

        content_lead = response.css("div.article--lead::text")
        text_parts = [content_lead[0].extract()]
        content = response.css("div.article--text").css('p *::text')
        for part in content:
            text_parts.append(part.extract())

        text = " ".join(text_parts)

        data = {
            "url": response.url,
            "title": title,
            "timestamp": timestamp,
            "tag": tags,
            "comments_count": comments_count,
            "text": text,
            "author":author
        }

        data = self.normalize(data)

        file_path = 'results.{}.{}.jsonl'.format(WiadomosciWPSpider.name,
                                                 file_timestamp)

        with open(file_path, 'a') as f:
            json_data = json.dumps(data, ensure_ascii=False)
            f.write("{}\n".format(json_data))

    def normalize(self, data):
        if "oprac. " in data["author"]:
            data["author"] = data["author"][7:]
        try:
            data["timestamp"] = datetime.strptime(data["timestamp"], "%d-%m-%Y (%H:%M)")
        except ValueError:
            if "h temu" in data["timestamp"]:
                hours_ago = timedelta(hours=int(data["timestamp"][:-6]))
                data["timestamp"] = datetime.today()-hours_ago
            elif "min. temu" in data["timestamp"]:
                hours_ago = timedelta(hours=int(data["timestamp"][:-9]))
                data["timestamp"] = datetime.today()-hours_ago
            else:
                data["timestamp"] = datetime.today()
        data["timestamp"] = data["timestamp"].strftime( "%Y-%m-%d %H:%M")
        return data
