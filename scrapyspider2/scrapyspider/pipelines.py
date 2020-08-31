
import pymysql
from scrapyspider.items import PageLinkItem
from scrapy import log


class ScrapyspiderPipeline(object):


    def process_item(self, item, spider):

       # 连接数据库
        my_sql = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', charset='utf8',
                                 db='tripadvisor_co', use_unicode=True)
        # 获取游标
        cur = my_sql.cursor()
        try:
            if isinstance(item, PageLinkItem):
                cur.execute("INSERT INTO page_link(href,title) VALUES(%s,%s)",
                            [item['href'],item['title']])
                # 提交
                my_sql.commit()
                # 关闭游标
                cur.close()
                # 关闭数据库连接
                my_sql.close()
        except Exception as e:
            log.msg("写入数据库出现异常", level=log.WARING)
            my_sql.commit()
            cur.close()
            my_sql.close()
        finally:
            return item
