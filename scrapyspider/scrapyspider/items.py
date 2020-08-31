# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Review(scrapy.Item):
    # 评论日期
    user_name = scrapy.Field()
    # 评论内容
    content = scrapy.Field()

    time = scrapy.Field()
    href = scrapy.Field()
    title = scrapy.Field()
    pass

