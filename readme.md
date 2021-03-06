# 文件介绍

**data_csv** :保存为csv文件的数据，文件名为page_link.id（page_link表的主键） + page_link.title(即这个帖子的标题)，每个文件仅有一列，为回复的内容。

**data_mysql** :转储的sql文件，tripadvisor_co.sql经过去重，tripadvisor_co2.sql没经过去重

**scrapyspider**:爬取帖子内容

**scrapyspider2**：爬取链接

# 细节介绍

1.一开始搜出来有16830条链接，最后去重只剩下784条链接，这一步我是比较迷惑的，要么就是我有问题，要么就是tripadvisor按照关键词搜索出来的那些帖子链接有大量重复

2.对照着看了俩帖子的数据，能对上，最终问题应该不大。。。但还是有如下几个问题，正在完善修改

​				1）带表情的回复并没有存储下来，数据库表结构类型的设计问题，正在改，然后今天晚上放那重新爬一遍

​				2）有些爬取到的回复是没有用的（被删除掉了），需要去掉。

![1598882125436](新建文件夹\1598882125436.png)

# 爬取步骤

1.运行第一个爬虫tripadvisor_pge_link，爬取帖子链接  - >获取到16830个链接

​			2.运行sql语句，进行去重   - >获取784个链接

```mysql
DELETE
FROM page_link
WHERE href IN(SELECT
               href
             FROM (SELECT
                     href
                   FROM page_link
                   GROUP BY href
                   HAVING COUNT(href) > 1) a)
    AND id NOT IN(SELECT
                    *
                  FROM (SELECT
                          MIN(id)
                        FROM page_link
                        GROUP BY href
                        HAVING COUNT(href) > 1) b)
```



​			3.运行第二个爬虫，爬取这784个链接内的回复 ->获取61142条回复

​			4.运行python脚本，为这些回复添加帖子链接的外键

```python
from pymysql import connect

def connectDB():
    db = connect('127.0.0.1', 'root', '123456', 'tripadvisor_co')
    return db

class Review:
    id = ''
    pl_id = ''
    
db = connectDB()
cursor = db.cursor()

page_link_all_sql = "SELECT id,href FROM page_link"
cursor.execute(page_link_all_sql)
page_links_results = cursor.fetchall()
page_link_dict ={}
for i in range(len(page_links_results)):
    key_list = page_links_results[i][1].split("-")
    "/ShowTopic-g662290-i11495-k13360913-Anyone_else_risking_it-Puerto_Del_Carmen_Lanzarote_Canary_Islands.html"
    key = key_list[1] +key_list[2] +key_list[3]
    page_link_dict[key] = page_links_results[i][0]
    

    
    

review_1_sql = "SELECT id,href FROM review"
cursor.execute(review_1_sql)

review_1_results = cursor.fetchall()
review_list =[]
for i in range(len(review_1_results)):
    review = Review()
    review.id = review_1_results[i][0]
    key_list = review_1_results[i][1].split("-")
    key = key_list[1] + key_list[2] + key_list[3]
    review.pl_id = page_link_dict.get(key)
    review_list.append(review)
    
    
def update_db(db,review_list):
    cursor = db.cursor()
    sql = "UPDATE review SET pl_id = %s WHERE id = %s"
    for review in review_list:
        cursor.execute(sql,[review.pl_id,review.id])
    db.commit()
    
    
update_db(db,review_list)
    
```



​			5.运行sql语句，进行去重  —>获取60711条回复

```sql
DELETE
FROM review
WHERE (content,pl_id,user_name,time)IN(SELECT
                          content,
                          pl_id,
                          user_name,
													time
                        FROM (SELECT
                                content,
                                pl_id,
                                user_name,
																time
                              FROM review
                              GROUP BY content,pl_id,user_name,time
                              HAVING COUNT( * ) > 1) a)
    AND id NOT IN(SELECT
                    MIN(id)
                  FROM (SELECT
                          MIN(id) AS id
                        FROM review
                        GROUP BY content,pl_id,user_name,time
                        HAVING COUNT( * ) > 1) b)
```

6.运行python脚本，将数据保存至csv文件，文件名为page_link.id + page_link.title

```python
from pymysql import connect
import csv

def connectDB():
    """
    数据库连接的相关信息在此修改
    """
    host = '127.0.0.1'
    user_name = 'root'
    password = '123456'
    database = 'tripadvisor_co'
    db = connect(host=host, user=user_name, password=password, db=database)
    return db

db = connectDB()
cursor = db.cursor()

#读取page_link和review数据
sql = "SELECT * FROM review"
sql2 = "SELECT * FROM page_link"
cursor.execute(sql)
reviews = cursor.fetchall()
cursor.execute(sql2)
page_links = cursor.fetchall()

#以review的外键pl_id(即page_lin的id)为键，对应的content组成的list为值
reviews_dict = {}
for review in reviews:
    if review[2] not in reviews_dict.keys():
        reviews_dict[review[2]] = [review[1].replace('\n','')]
    else:
        reviews_dict[review[2]].append(review[1].replace('\n',''))

#以page_lin的id为键，对应的title为值        
id_title_dict = {}
for page_link in page_links:
    id_title_dict[page_link[0]] = page_link[2]
        
        
        
#写入csv文件
for k,v in reviews_dict.items():
    file_name = 'd:/study/data/' + str(k) + '.csv'
    with open (file_name, "w", newline='',encoding='utf8') as f :       #newline参数控制行之间是否空行
        f_csv = csv.writer(f)
        review_to_file = []
        for i in v:
            if i not in review_to_file:
                review_to_file.append(i)
        for j in review_to_file:
            f_csv.writerow([j])


 

```

