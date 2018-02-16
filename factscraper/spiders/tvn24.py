# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import re
import json

file_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")


class Tvn24Spider(scrapy.Spider):
    name = 'tvn24'
    start_urls = [
        'https://tvnwarszawa.tvn24.pl/ulice,news,zderzenie-trzech-samochodow-brw-alei-niepodleglosci,252839.html',
        'https://tvnwarszawa.tvn24.pl/informacje,news,pali-sie-warsztat-na-mokotowie,252843.html',
        'https://tvnwarszawa.tvn24.pl/ulice,news,nie-ustapil-pierwszenstwa-mial-poltora-promila-alkoholu,252815.html',
        'https://tvnwarszawa.tvn24.pl/informacje,news,dwa-tygodnie-bezplatnych-zajec-warsztatow-i-sportu,250180.html'
        'https://tvnwarszawa.tvn24.pl/informacje,news,pozar-golfa-przy-belwederskiej,85305.html',
        'https://tvnwarszawa.tvn24.pl/informacje,news,pozar-budynku-przy-modlinskiej,151326.html',
        'https://tvnwarszawa.tvn24.pl/informacje,news,wyrzna-drzewa-zakopia-gazociag-bra-co-potem-konkretow-brak,252345.html',
        'https://tvnwarszawa.tvn24.pl/informacje,news,naczelnik-skarbowki-powiesil-siebr-w-areszcie-zarzuty-dla-straznikow,252836.html'
    ]

    def parse(self, response):
        title = response.css('div.heading').css('h1::text').extract_first()
        timestamp = response.css('div.heading').css('p.date').css("span::text").extract_first()

        tags = response.css("ul.tagList").css("a::text").extract()

        comments_xpath = '//*[@id="jCommentsContainer"]/li/h3[2]/text()'
        comments_count = response.xpath(comments_xpath).extract_first()

        text_parts = []
        content = response.css("div.content").css("p::text")
        for part in content:
            text_parts.append(part.extract())
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

        file_path = 'results.{}.{}.jsonl'.format(Tvn24Spider.name,
                                                 file_timestamp)

        with open(file_path, 'a') as f:
            json_data = json.dumps(data, ensure_ascii=False)
            f.write("{}\n".format(json_data))


    def normalize(self, data):
        data["timestamp"] = re.sub("[\n\r]*", "", data["timestamp"]).strip()
        if " " in data["timestamp"]:
            data["timestamp"] = datetime.strptime(data["timestamp"], "%d.%m.%Y %H:%M")
        else:
            date_now = datetime.combine(datetime.today(), datetime.min.time())
            time = datetime.strptime(data["timestamp"], "%H:%M")
            data["timestamp"] = date_now.replace(hour=time.hour, minute=time.minute)
        data["timestamp"] = data["timestamp"].strftime( "%Y-%m-%d %H:%M")
        return data
