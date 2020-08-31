import scrapy
import pymysql
from scrapyspider.items import PageLinkItem
import time
from bs4 import BeautifulSoup

# 继承自scrapy.Spider
class TripadvisorSpider(scrapy.Spider):
    name = "tripadvisor_page_link"
    start_urls = ['https://www.tripadvisor.com/SearchForums?q=covid-19']

    def start_requests(self):
        urls = []
        urls.append("https://www.tripadvisor.com/SearchForums?q=covid-19&s=")
        url_prefix = "https://www.tripadvisor.com/SearchForums?q=covid-19&s=%20&o="
        for i in range(1, 1683):
            urls.append(url_prefix + str(i * 10))
        url_prefix += str((1683 - 1) * 10)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        html_doc = response.body
        soup = BeautifulSoup(html_doc, 'lxml')

        trs = soup.find_all(attrs={"class": "topicrow"})
        for tr in trs:
            pageLinkItem = PageLinkItem()
            pageLinkItem["href"] = tr.td.a["href"]
            pageLinkItem["title"] = tr.td.a.b.text
            yield pageLinkItem