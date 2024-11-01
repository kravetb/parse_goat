import scrapy


class GoatSpiderSpider(scrapy.Spider):
    name = "goat_spider"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    def parse(self, response):
        pass
