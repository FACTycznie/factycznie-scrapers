import scrapy


class FrondaSpider(scrapy.Spider):
    name = 'fronda'
    start_urls = [
        'https://www.fronda.pl/a/amerykanski-naukowiec-o-smolensku-w-przypadku-takiej-katastrofy-samolot-powinien-rozbic-sie-na-3-4-czesci,106620.html',
    ]

    # def start_requests(self):
    #     url = 'http://www.fronda.pl/c/wiadomosci,1.html'

    def parse(self, response):
        title = response.css('div.title-block').css('h1::text').extract_first()
        for title in response.css(''):
            yield {'title': title.css('h1::text').extract_first()}

        for next_page in response.css('div.prev-post > a'):
            yield response.follow(next_page, self.parse)
