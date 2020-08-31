import scrapy
import pymysql
from bs4 import BeautifulSoup
from scrapyspider.items import Review
import time


# 继承自scrapy.Spider
class TripadvisorSpider(scrapy.Spider):

    name = "tripadvisor_co"
    def start_requests(self):
        my_sql = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', charset='utf8',
                                 db='tripadvisor_co', use_unicode=True)
        cur = my_sql.cursor()
        cur.execute("SELECT href FROM page_link2")
        urls = cur.fetchall()
        for url in urls :
            url = "https://www.tripadvisor.com" + url[0]

            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self,response):
        html_doc = response.body
        soup = BeautifulSoup(html_doc, 'lxml')

        posts = soup.find_all(attrs={"class": "post"})

        href = response.request.url
        for post in posts:
            [s.extract() for s in post("script")]
            # 这里还需要处理
            review = Review()
            review['content'] = post.find(attrs={"class": "postBody"}).text
            user_name= post.find(attrs={"class": "username"})
            review['user_name'] = user_name.text if user_name is not None else ""
            review['time'] = post.find(attrs={"class": "postDate"}).text
            title =  post.find(attrs={"class": "titleText"})
            review['title'] = title.text if title is not None else ""
            review['href'] = href
            yield review

        next_page = soup.find(attrs={"class":"sprite-pageNext"})

        if next_page is not None:
            next_page = response.urljoin(next_page.get("href"))
            yield scrapy.Request(next_page, callback=self.parse)

