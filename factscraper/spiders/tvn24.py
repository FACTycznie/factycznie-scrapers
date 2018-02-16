# -*- coding: utf-8 -*-
import scrapy
import datetime

file_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


class Tvn24Spider(scrapy.Spider):
    name = 'tvn24'
    start_urls = [
        'https://tvnwarszawa.tvn24.pl/ulice,news,zderzenie-trzech-samochodow-brw-alei-niepodleglosci,252839.html',
        'https://tvnwarszawa.tvn24.pl/informacje,news,pali-sie-warsztat-na-mokotowie,252843.html',
        'https://tvnwarszawa.tvn24.pl/ulice,news,nie-ustapil-pierwszenstwa-mial-poltora-promila-alkoholu,252815.html',
        'https://tvnwarszawa.tvn24.pl/informacje,news,dwa-tygodnie-bezplatnych-zajec-warsztatow-i-sportu,250180.html'
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

        file_path = 'results.{}.{}.jsonl'.format(Tvn24Spider.name,
                                                 file_timestamp)

        with open(file_path, 'a') as f:
            f.write("{}\n".format(str(data)))
