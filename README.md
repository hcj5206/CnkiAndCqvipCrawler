# 使用说明
## 2019年0703版本
**_———————————运行源码所需环境与模块———————————
环境：Python3.7版本+Pycharm_**

模块：
	argparse  
	queue  
	threading  
	quote  
	multiprocessing  
	urllib.request  
	requests  
	BeautifulSoup  
	re  
	pymysql  
	DBUtils   
	urllib3   
	certifi  
	lxml
    PooledDB  
    以及一些python自带的模块
运行方式 
``` bash
usage: main.py [-h] [-mode -m MODE] [-restart -r RESTART] [-title -t TITLE]
               [-authors -a AUTHORS] [-keywords -k KEYWORDS] [-unit -u UNIT]
               [-starttime -s STARTTIME] [-endtime -e ENDTIME]
               [-dbname -db EX_DBNAME]

Spider for gourmet shops in meituan.

optional arguments:
  -h, --help            show this help message and exit
  -mode -m MODE         选择模式：1:Cnki 2:Cqvip 3:Wanfang 12：Cnki+Cqvip 123:All
                        默认1
  -restart -r RESTART   是否重新开始爬取 1 重新开始 0：继续 默认为0
  -title -t TITLE       title：标题
  -authors -a AUTHORS   authors：作者
  -keywords -k KEYWORDS
                        keywords：关键词
  -unit -u UNIT         unit：单位
  -starttime -s STARTTIME
                        starttime：开始时间
  -endtime -e ENDTIME   endtime：结束时间
  -dbname -db EX_DBNAME
                        数据库后缀,默认为空，填xx,则表单为result

python main.py -h #帮助
python main.py -m 123 -r 1 -t #标题 -a #作者 -k #关键词 -u #单位 -s #开始时间 -e #结束时间 
```
