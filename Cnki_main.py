#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : Cqvip_main.py
# datetime:2019/6/19 9:43
import queue
import sys
import threading
from urllib.parse import quote
import multiprocessing

import math

from HCJ_py_timer import LoopTimer
import urllib.request
from bs4 import BeautifulSoup
import time
import re
from HCJ_Buff_Control import Read_buff,Write_buff
#构造不同条件的关键词搜索
from HCJ_DB_Helper import HCJ_MySQL

# 构造不同条件的关键词搜索
# values = {
#     '全文': 'qw',
#     '主题': 'theme',
#     '篇名': 'title',
#     '作者': 'author',
#     '摘要': 'abstract'
# }
values = {
    '1': 'qw',
    '2': 'theme',
    '3': 'title',
    '4': 'author',
    '5': 'abstract'
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
concurrent = 5 # 采集线程数
conparse = 10 # 解析线程数
# 生成请求队列
req_list = queue.Queue()
# 生成数据队列 ，请求以后，响应内容放到数据队列里
data_list = queue.Queue()
class Parse(threading.Thread):
    # 初始化属性
    def __init__(self, number, data_list, req_thread):
        super(Parse, self).__init__()
        self.number = number  # 线程编号
        self.data_list = data_list  # 数据队列
        self.req_thread = req_thread  # 请求队列，为了判断采集线程存活状态
        self.is_parse = True  # 判断是否从数据队列里提取数据

    def run(self):
        print('启动%d号解析线程' % self.number)
        # 无限循环，
        while True:
            # 如何判断解析线程的结束条件
            for t in self.req_thread:  # 循环所有采集线程
                if t.is_alive():  # 判断线程是否存活
                    break
            else:  # 如果循环完毕，没有执行break语句，则进入else
                if self.data_list.qsize() == 0:  # 判断数据队列是否为空
                    self.is_parse = False  # 设置解析为False
            # 判断是否继续解析

            if self.is_parse or int(Read_buff(file_buff="Config.ini", settion="Cqvip",info='stopflag'))==0:  # 解析
                try:
                    url,data = self.data_list.get(timeout=3)  # 从数据队列里提取一个数据
                except Exception as e:  # 超时以后进入异常
                    data = None
                # 如果成功拿到数据，则调用解析方法
                if data is not None:
                    parse(url,data)  # 调用解析方法
            else:
                break  # 结束while 无限循环

        print('退出%d号解析线程' % self.number)


class Crawl(threading.Thread): #采集线程类
    # 初始化
    def __init__(self, number, req_list, data_list):
        # 调用Thread 父类方法
        super(Crawl, self).__init__()
        # 初始化子类属性
        self.number = number
        self.req_list = req_list
        self.data_list = data_list
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
        }
    # 线程启动的时候调用

    def run(self):
        # 输出启动线程信息
        print('启动采集线程%d号' % self.number)
        # 如果请求队列不为空，则无限循环，从请求队列里拿请求url
        while self.req_list.qsize() > 0 or int(Read_buff(file_buff="Config.ini", settion="Cqvip",info='stopflag'))==0:
            # 从请求队列里提取url
            url = self.req_list.get()
            # print('%d号线程采集：%s' % (self.number, url))
            # 防止请求频率过快，随机设置阻塞时间
            time.sleep(0.1)
            # 发起http请求，获取响应内容，追加到数据队列里，等待解析
            response = GetSoup(url)
            if response: #存在
                self.data_list.put([url,response])  # 向数据队列里追加

def Up_division_int(A, B):
    '''
     向上整除
    :param A:
    :param B:
    :return:
    '''
    return int((A + B - 1) / B)
class Cqvip_Crawler:
    def __init__(self,db,Input=None,SearchMode=None,StartTime=None,EndTime=None,StartPage=None,SettingPath='./Config.ini'):
        self.db=db
        self.SearchName='Cqvip'  # 万方
        self.SettingPath=SettingPath # 配置文件地址
        self._Perpage=10 # 每页显示20
        self._ResultDbTable='CqvipResult'
        if  Input is None and SearchMode is None:
            self.Input=Read_buff(file_buff=self.SettingPath,settion=self.SearchName,info='input') # 输入内容
            self.SearchMode=Read_buff(file_buff=self.SettingPath,settion=self.SearchName,info='searchmode') # 模式选择
            self.StartTime=Read_buff(file_buff=self.SettingPath,settion=self.SearchName,info='starttime') # 开始年份
            self.EndTime=Read_buff(file_buff=self.SettingPath,settion=self.SearchName,info='endtime') # 结束年份
            self.StartPage=Read_buff(file_buff=self.SettingPath,settion=self.SearchName,info='startpage') # 开始页数
            self.MaxPage=Read_buff(file_buff=self.SettingPath,settion=self.SearchName,info='maxpage') # 开始页数
        else:
            # Todo
            pass
    def GetMaxPage(self):

        keywordval = str(values[self.SearchMode]) + ':' + str(self.Input)
        index_url = 'http://search.cnki.com.cn/Search.aspx?q=' + quote(keywordval)  # quote方法把汉字转换为encodeuri?
        print(index_url)
        soup = self.GetSoup(url=index_url)
        pagesum_text = soup.find('span', class_='page-sum').get_text()
        print(pagesum_text)
        summarys = math.ceil(int(pagesum_text[7:-1]))
        self.MaxPage=Up_division_int(summarys,int(15))
        Write_buff(file_buff="Config.ini", settion="Cqvip", info="maxpage", state=self.MaxPage)
        return summarys,self.MaxPage
    def GetSoup(self,url=None):
        req = urllib.request.Request(url=url, headers=headers)
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, 'lxml')
        return soup
    def WriteAllUrlIntoDBMain(self):
        summarys,self.MaxPage = self.GetMaxPage()  # 最大页数
        self.StartPage = Read_buff(file_buff=self.SettingPath, settion=self.SearchName, info='startpage')  # 开始页数
        t=time.time()
        Write_buff(file_buff="Config.ini", settion="Cqvip", info="flag_get_all_url", state=0)
        for i in range(int(self.StartPage),self.MaxPage):
            print("共有%s页，当前为%s页，获得文献链接的进度完成%.2f" % (self.MaxPage, i,(int(i)/int(self.MaxPage))*100))
            Write_buff(file_buff="Config.ini", settion="Cqvip", info="startpage", state=i+1)

            keywordval = str(values[self.SearchMode]) + ':' + str(self.Input)
            page_url = 'http://search.cnki.com.cn/Search.aspx?q=%s&p=%s'%(quote(keywordval),(i-1)*15)
            print(page_url)
            threading.Thread(target=self.WriteUrlIntoDB, args=(page_url,i)).start()
            time.sleep(2)
        Write_buff(file_buff="Config.ini",settion="Cqvip",info="flag_get_all_url",state=1)
        print(time.time()-t)
    def WriteUrlIntoDB(self,page_url,page):
        soup = self.GetSoup(url=page_url)
        deff = soup.find_all('div', class_='wz_content')  #
        for k in range(len(deff)):
            Href = deff[k].a['href']
            url = Href
            #_UrlList.append(url)
            sql="INSERT INTO `cqvipcrawler`.`databuff` (`Page`, `PageNum`,`PageIndex`, `Url`) VALUES ('%s', '%s', '%s','%s');\n" % (
                str(page), str(k), str(page) + '-' + str(k), url)
            row = self.db.insert(sql) # 插入
    def GetUrlFromDb(self,num=20):
        sql="select `PageIndex`,`Url` from `databuff` where `State`in (0,-10) ORDER BY `Page` ASC, `PageNum` limit %s "%num
        _rows=self.db.do_sql(sql)
        if _rows:
            if len(_rows)>0:
                _UrlList=[x[1] for x in _rows]
                for i in [x[0] for x in _rows]:
                    self.db.upda_sql("update `databuff` set `State`=10 where `PageIndex`='%s'"%i)
                return _UrlList
        else:
            return ""

def InitDict():
    dir = {'url' :'', 'title' :'','authors':'','unit' :'','publication' :'','keywords' :'','abstract' :'','year' :'','volume' :'','issue' :'','pagecode' :'','doi' :'','sponser' :'','type' :''}
    return dir

def InsetDbbyDict(table,Dict):
    COLstr = ''  # 列的字段
    ROWstr = ''  # 行字段
    for key in Dict.keys():
        COLstr = COLstr + ' ' + '`' + key + '`,'
        ROWstr = (ROWstr + '"%s"' + ',') % (str(Dict[key]).replace('%',">").replace('\n','').replace('\"',"#"))
    sql = "INSERT INTO %s (%s) VALUES (%s);\n" % (
        table,COLstr[:-1], ROWstr[:-1])
    sql_update="Update `databuff` set `State`=20 where `Url`='%s' "%str(Dict['url']).replace('\n','')


    result_dic=db.insert(sql)
    if  result_dic['result']:
        db.upda_sql(sql_update)
    else:
        print(result_dic['err'])
        db.upda_sql("Update `databuff` set `State`=-10 where `Url`='%s' "%str(Dict['url']).replace('\n',''))


class PaperAll(object):
    pass
def CreatUrlBuffTable(TableName):
    CreatDBTableSql = '\
            CREATE TABLE IF NOT EXISTS `%s` (\
            `PageIndex` VARCHAR(50) NULL DEFAULT NULL,\
	        `Page` INT(11) NULL DEFAULT NULL,\
	        `PageNum` INT(11) NULL DEFAULT NULL,\
	        `Url` VARCHAR(200) NULL DEFAULT NULL,\
	        `State` INT(11) NULL DEFAULT \'0\'  COMMENT \'-5 日期不对 -10 出现错误 0 初始 10 处理中 20 处理结束\',\
	        `Datetime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,\
	        UNIQUE INDEX `PageIndex` (`PageIndex`)\
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8; ' % TableName
    dict_result = db.upda_sql(CreatDBTableSql)
    if not dict_result:
        print("创建出现问题")

def CreatResultDBTable(TableName):
    '''
    创建结构数据库表单，如果不存在就创建
    :return:
    '''
    CreatDBTableSql = '\
        CREATE TABLE IF NOT EXISTS `%s` (\
          `id` int(11) unsigned NOT NULL AUTO_INCREMENT,\
          `url` varchar(200) DEFAULT NULL, \
          `title` varchar(200) DEFAULT NULL,\
          `authors` varchar(200) DEFAULT NULL,\
          `unit` varchar(200) DEFAULT NULL,\
          `publication` varchar(200) DEFAULT NULL,\
          `keywords` varchar(200) DEFAULT NULL,\
          `abstract` text DEFAULT NULL,\
          `year` varchar(200) DEFAULT NULL,\
          `volume` varchar(200) DEFAULT NULL,\
          `issue` varchar(200) DEFAULT NULL,\
          `pagecode` varchar(200) DEFAULT NULL,\
          `doi` varchar(200) DEFAULT NULL,\
          `sponser` varchar(200) DEFAULT NULL,\
          `type` varchar(200) DEFAULT NULL,\
          PRIMARY KEY (`id`)\
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8; ' % TableName
    dict_result = db.upda_sql(CreatDBTableSql)
    if not dict_result:
        print("创建出现问题")


class ClockProcess(multiprocessing.Process):
    def __init__(self, interval):
        multiprocessing.Process.__init__(self)
        self.interval = interval

    def run(self):
        _db=HCJ_MySQL()
        _Cqvip = Cqvip_Crawler(db=_db)
        _Cqvip.WriteAllUrlIntoDBMain()
        print("结束")

def PutUrlToList(Cqvip,num):
    UrlList=Cqvip.GetUrlFromDb(num=num)
    if UrlList:
        if len(UrlList)>0:
            for url in UrlList:
                req_list.put(url)
    else:pass
def ShowStatePro():
    sql_count_all="select count(*) from `databuff` where 1"
    num_all=int(db.do_sql_one(sql_count_all)[0])
    sql_count_done="select count(*) from `databuff` where `State`=20"
    num_done = int(db.do_sql_one(sql_count_done)[0])
    if num_all ==0:
        num_all=1
    if int(Read_buff(file_buff="Config.ini", settion="Cqvip", info='flag_get_all_url')) == 1 and num_all == num_done:
        # 完成全部
        Write_buff(file_buff="Config.ini",settion="Cqvip",info="stopflag",state=1)
        print("#############################################目前有%s条数据，其中已处理的有%s，处理完成度为%.2f##############################" % (num_all, num_done, (int(num_done) / int(num_all)) * 100))
        print("爬取结束")
        sys.exit()
    print("#############################################目前有%s条数据，其中已处理的有%s，处理完成度为%.2f##############################"%(num_all,num_done,(int(num_done)/int(num_all))*100))
def main():
    ClockProcess(1).start()
    PutUrlToList(Cqvip, 20)
    LoopTimer(0.5, PutUrlToList, args=(Cqvip, 20,)).start()
    LoopTimer(1, ShowStatePro).start()
    # 生成N个采集线程
    req_thread = []
    for i in range(concurrent):
        t = Crawl(i + 1, req_list, data_list)  # 创造线程
        t.start()
        req_thread.append(t)
    # 生成N个解析线程
    parse_thread = []
    for i in range(conparse):
        t = Parse(i + 1, data_list, req_thread)  # 创造解析线程
        t.start()
        parse_thread.append(t)
    for t in req_thread:
        t.join()
    for t in parse_thread:
        t.join()

def init_main():
    if int(Read_buff(file_buff="Config.ini", settion="Cqvip", info='restart')) == 1:
        CreatResultDBTable("result")
        CreatUrlBuffTable("databuff")
        db.do_sql("TRUNCATE `databuff`;")
        db.do_sql("TRUNCATE `result`;")
        Write_buff(file_buff="Config.ini", settion="Cqvip", info="restart", state=0)
        Write_buff(file_buff="Config.ini", settion="Cqvip", info="startpage", state=1)
        Write_buff(file_buff="Config.ini", settion="Cqvip", info="stopflag", state=0)
        Write_buff(file_buff="Config.ini", settion="Cqvip", info="flag_get_all_url", state=0)

def main1(argv):
    import sys, getopt
    Input = SearchMode= StartTime =  EndTime = StartPage = ""
    try:
      opts, args = getopt.getopt(argv,"hk:m:s:e:",["help", "mode=","end=", "start="])
    except getopt.GetoptError:
      print('main.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('main.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt == "-k":
         Input = arg
      elif opt in ("-m","--mode"):
         SearchMode = arg
      elif opt in( "--start","-s"):
          StartTime = arg

      elif opt in("--end","-e"):
          EndTime = arg
    print('输入关键词为：', Input)
    print('输入模式为：', SearchMode)
    print('输入开始时间为：', StartTime)
    print('输入结束时间为：', EndTime)

def GetSoup(url=None):
    try:
        req = urllib.request.Request(url=url, headers=headers)
        html = urllib.request.urlopen(req,timeout=3).read()
        soup = BeautifulSoup(html, 'lxml')
    except:
        db.upda_sql("update `databuff` set `State`=-15 where `Url`='%s'"%(url))
        print("出现一次连接失败")
        soup=False
    return soup
def parse(url,_soup):
    if _soup is not None:
        _Paper = InitDict()
        _Paper['url'] = url  # 获得【链接】
        _Paper['title'] = _soup.find('div',
                              style="text-align:center; width:740px; font-size: 28px;color: #0000a0; font-weight:bold; font-family:'宋体';").text
        author = _soup.find_all('div', style='text-align:center; width:740px; height:30px;')
        author_buff=""
        for item in author:
            author_buff += item.get_text()
        _Paper['authors'] = author_buff  # 获得【作者】
        abstract = _soup.find('div', style='text-align:left;word-break:break-all')
        abstract_text = abstract.text.replace('\n','').replace('\r','').replace(' ','')# 获得【摘要】
        _Paper['abstract']=abstract_text.split("要】：")[1] if "要】：" in abstract_text else abstract_text
        authorUnitScope = _soup.find('div', style='text-align:left;', class_='xx_font')
        author_unit = ''
        author_unit_text = authorUnitScope.get_text().replace('\n','').replace('\r','').replace(' ','')
        info=author_unit_text.split("：")
        auindex = author_unit_text.split("单位】：")[1].split("【")[0] if "单位】：" in author_unit_text else ""
        _Paper['sponser'] = author_unit_text.split("基金】：")[1].split("【")[0] if "【基金】：" in author_unit_text else ""
        _Paper['unit'] = auindex # 获得【单位】
        publicationScope = _soup.find('div', style='float:left;').text.replace('\n','').replace('\r','').replace(' ','').replace('\t','')
        _Paper['publication']=re.search(r'《.*》', publicationScope).group() if "《" in publicationScope  else ""
        _Paper['year']=re.search(r'\d+年', publicationScope).group() if "年" in publicationScope else ""
        _Paper['year']=_Paper['year'].split("年")[0] if _Paper['year']!="" else _Paper['year']
        _Paper['issue']=re.search(r'\d+期', publicationScope).group() if "期" in publicationScope else ""
        _Paper['issue'] =_Paper['issue'].split("期")[0] if _Paper['issue'] != "" else _Paper['issue']
        InsetDbbyDict("`cqvipcrawler`.`result`", _Paper)
if __name__ == '__main__':
    SearchDBName = 'Cqvip'
    multiprocessing.freeze_support()  # 多进程打包的话必须加上
    db = HCJ_MySQL()
    Cqvip = Cqvip_Crawler(db=db)
    init_main()
    main()
    # url="http://cdmd.cnki.com.cn/Article/CDMD-10286-2003124034.htm"
    # soup=GetSoup(url)
    # parse(url=url,_soup=soup)