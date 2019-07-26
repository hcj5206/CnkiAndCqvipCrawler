## 20190726 更新readme.md 文档 以及打包成exe
# 使用说明
## 2019年0715版本 1.修复了书名号  2无效链接的优化
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
	bs4  
	pymysql  
	DBUtils   
	urllib3   
	certifi  
	lxml
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
## 通过设置ini 的[Setting]内容来调解爬取频率，可根据自己的网络情况和计算机性能进行设置 以下是默认值。
#### **tip： 万方入口有限制，不能太快，不然会出现验证码，推荐用目前的默认值**
```bash
[Setting]
cnki_collectnum = 10 ; url收集线程
cnki_parsenum = 5 ; url解析线程
cnki_interval = 1 ; url访问间隔 
cqvip_collectnum = 10
cqvip_parsenum = 5
cqvip_interval = 1
wanfang_collectnum = 3
wanfang_parsenum = 3
wanfang_interval = 6

```