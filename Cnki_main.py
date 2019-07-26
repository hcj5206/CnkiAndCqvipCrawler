#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : Cqvip_main.py
# datetime:2019/6/19 9:43
import queue
import random
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
SearchDBName="Cnki"

from PublicDef import *
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

concurrent=int(Read_buff(file_buff="./Config.ini",settion='Setting',info='Cnki_CollectNum').replace(' ',''))
conparse=int(Read_buff(file_buff="./Config.ini",settion='Setting',info='Cnki_parsenum').replace(' ',''))
interval=int(Read_buff(file_buff="./Config.ini",settion='Setting',info='Cnki_interval').replace(' ',''))
# 生成请求队列
req_list = queue.Queue()
# 生成数据队列 ，请求以后，响应内容放到数据队列里
data_list = queue.Queue()
class Cnki_Crawler:
    def __init__(self,db,Input=None,SearchMode=None,StartTime=None,EndTime=None,StartPage=None,SettingPath='./Config.ini'):
        self.db=db
       
        self.SettingPath=SettingPath # 配置文件地址
        if  Input is None and SearchMode is None:
            self.StartTime=Read_buff(file_buff=self.SettingPath,settion=SearchDBName,info='starttime') # 开始年份
            self.EndTime=Read_buff(file_buff=self.SettingPath,settion=SearchDBName,info='endtime') # 结束年份
            self.StartPage=Read_buff(file_buff=self.SettingPath,settion=SearchDBName,info='startpage') # 开始页数
            self.MaxPage=Read_buff(file_buff=self.SettingPath,settion=SearchDBName,info='maxpage') # 开始页数
            self.title = Read_buff(file_buff=self.SettingPath, settion=SearchDBName, info='title')
            self.authors = Read_buff(file_buff=self.SettingPath, settion=SearchDBName, info='authors')
            self.keywords = Read_buff(file_buff=self.SettingPath, settion=SearchDBName, info='keywords')
            self.unit = Read_buff(file_buff=self.SettingPath, settion=SearchDBName,info='unit')
            self.BaseKeyword=""
            if RemoveSpecialCharacter(self.title) !="":
                self.BaseKeyword=self.BaseKeyword+" title:"+self.title
            if RemoveSpecialCharacter(self.authors) !="":
                self.BaseKeyword=self.BaseKeyword+" author:"+self.authors
            if RemoveSpecialCharacter(self.keywords) !="":
                self.BaseKeyword=self.BaseKeyword+" qw:"+self.keywords
            if RemoveSpecialCharacter(self.unit) !="":
                self.BaseKeyword=self.BaseKeyword+" 作者单位:"+self.unit
        else:
            # Todo
            pass
    def GetMaxPage(self):

        index_url = 'http://search.cnki.com.cn/Search.aspx?q=%s' % quote(self.BaseKeyword)  # quote方法把汉字转换为encodeuri?
        try:
            print("GetMaxPage",index_url)
            soup = GetSoup(url=index_url)
            pagesum_text = soup.find('span', class_='page-sum').get_text()
            summarys = math.ceil(int(pagesum_text[7:-1]))
            self.MaxPage=Up_division_int(summarys,int(15))
            Write_buff(file_buff="Config.ini", settion=SearchDBName, info="maxpage", state=self.MaxPage)
        except:
            print(index_url,"获得最大出错")
        return summarys,self.MaxPage
    def WriteAllUrlIntoDBMain(self):
        summarys,self.MaxPage = self.GetMaxPage()  # 最大页数
        self.StartPage = Read_buff(file_buff=self.SettingPath, settion=SearchDBName, info='startpage')  # 开始页数
        t=time.time()
        Write_buff(file_buff="Config.ini", settion=SearchDBName, info="flag_get_all_url", state=0)
        for i in range(int(self.StartPage),self.MaxPage):
            print("Cnki：共有%s页，当前为%s页，获得文献链接的进度完成%.2f" % (self.MaxPage, i,(int(i)/int(self.MaxPage))*100))
            Write_buff(file_buff="Config.ini", settion=SearchDBName, info="startpage", state=i+1)
            keywordval = self.BaseKeyword
            page_url = 'http://search.cnki.com.cn/Search.aspx?q=%s&p=%s'%(quote(keywordval),(i-1)*15)
            threading.Thread(target=self.WriteUrlIntoDB, args=(page_url,i)).start()
            time.sleep(1)
        Write_buff(file_buff="Config.ini",settion=SearchDBName,info="flag_get_all_url",state=1)
        print(time.time()-t)
        sys.exit(0)
    def WriteUrlIntoDB(self,page_url,page):

        soup = GetSoup(url=page_url)
        if soup:
            deff = soup.find_all('div', class_='wz_content')  #
            for k in range(len(deff)):
                Href = deff[k].a['href']
                url = Href
                #_UrlList.append(url)
                sql="INSERT INTO `crawler`.`%s` ( `Url`,`Source`) VALUES ('%s','%s');\n" % (DbDatabuff,
                     url,SearchDBName)
                row = self.db.insert(sql) # 插入


    def GetUrlFromDb(self,num=10):
        sql="select `Index`,`Url` from `%s` where `State`in (0,-10) and `Source`='%s'  limit %s "%(DbDatabuff,SearchDBName,num)
        _rows=self.db.do_sql(sql)
        if _rows:
            if len(_rows)>0:
                _UrlList=[x[1] for x in _rows]
                for i in [x[0] for x in _rows]:
                    self.db.upda_sql("update `%s` set `State`=10 where `Index`='%s'"%(DbDatabuff,i))
                return _UrlList
        else:
            return ""
class Parse(threading.Thread):
    # 初始化属性
    def __init__(self, number, data_list, req_thread):
        super(Parse, self).__init__()
        self.number = number  # 线程编号
        self.data_list = data_list  # 数据队列
        self.req_thread = req_thread  # 请求队列，为了判断采集线程存活状态
        self.is_parse = True  # 判断是否从数据队列里提取数据

    def run(self):
        print('Cnki：启动%d号解析线程' % self.number)
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

            if self.is_parse or '0'in (Read_buff(file_buff="Config.ini", settion=SearchDBName,info='stopflag')):  # 解析
                try:
                    url,data = self.data_list.get(timeout=3)  # 从数据队列里提取一个数据
                except Exception as e:  # 超时以后进入异常
                    data = None
                # 如果成功拿到数据，则调用解析方法
                if data is not None:
                    parse(url,data)  # 调用解析方法
            else:

                break  # 结束while 无限循环

        print('Cnki：退出%d号解析线程' % self.number)
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
        print("Cnki：启动采集线程%d号" % self.number)
        # 如果请求队列不为空，则无限循环，从请求队列里拿请求url
        while self.req_list.qsize() > 0 or '0' in str(Read_buff(file_buff="Config.ini", settion=SearchDBName,info='stopflag')):
            # 从请求队列里提取url
            url = self.req_list.get()
            # print('Cnki：%d号线程采集：%s' % (self.number, url))
            # 防止请求频率过快，随机设置阻塞时间
            time.sleep(random.randint(interval*10,(interval+2)*10)/10)
            # 发起http请求，获取响应内容，追加到数据队列里，等待解析
            response = GetSoup(url)
            # print(url)
            if response: #存在
                self.data_list.put([url,response])  # 向数据队列里追加
class ClockProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
    def run(self):
        _db=HCJ_MySQL()
        _Cqvip = Cnki_Crawler(db=_db)
        _Cqvip.WriteAllUrlIntoDBMain()
        print("Cnki：获取全部url结束")

def Up_division_int(A, B):
    '''
     向上整除
    :param A:
    :param B:
    :return:
    '''
    return int((A + B - 1) / B)
def InitDict():
    dir = {'url' :'', 'title' :'','authors':'','unit' :'','publication' :'','keywords' :'','abstract' :'','year' :'','volume' :'','issue' :'','pagecode' :'','doi' :'','sponser' :'','type' :''}
    return dir

def PutUrlToList(Cnki,num):
    UrlList=Cnki.GetUrlFromDb(num=num)
    if UrlList:
        if len(UrlList)>0:
            for url in UrlList:
                req_list.put(url)
    else:pass

def GetSoup(url=None):
    try:
        req = urllib.request.Request(url=url, headers=headers)
        request = urllib.request.urlopen(req,timeout=8)
        html=request.read()
        soup = BeautifulSoup(html, 'lxml')
    except Exception as e:
        db.upda_sql("update `%s` set `State`=-15 where `Url`='%s'"%(DbDatabuff,url))
        print("Cnki：无效链接",str(e),url)
        soup=False
    return soup
def parse(url,_soup):
    if _soup is not None:
        _Paper = InitDict()
        _Paper['url'] = url  # 获得【链接】
        try:
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
            publicationScope=changeChineseNumToArab(publicationScope)
            _Paper['publication']=re.search(r'《.*》', publicationScope).group() if "《" in publicationScope  else ""
            _Paper['year']=re.search(r'\d+年', publicationScope).group() if "年" in publicationScope else ""
            _Paper['year']=_Paper['year'].split("年")[0] if _Paper['year']!="" else _Paper['year']
            _Paper['issue']=re.search(r'\d+期', publicationScope).group() if "期" in publicationScope else ""
            _Paper['issue'] =_Paper['issue'].split("期")[0] if _Paper['issue'] != "" else _Paper['issue']
            InsetDbbyDict("`crawler`.`%s`"%Dbresult, _Paper,db,DbDatabuff,Dbresult)
        except:
            db.upda_sql("update `%s` set `State`=-15 where `Url`='%s'" % (DbDatabuff,_Paper['url']))
            print(_Paper['url'],"goup解析出现错误")
def main():
    multiprocessing.freeze_support()
    ClockProcess().start()
    PutUrlToList(Cnki, 20)
    LoopTimer(0.5, PutUrlToList, args=(Cnki, 20,)).start()
    LoopTimer(1, ShowStatePro,args=(db,SearchDBName,DbDatabuff,Dbresult,)).start()
    # 生成N个采集线程
    time.sleep(1)
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
    if '1' in str(Read_buff(file_buff="Config.ini", settion=SearchDBName, info='restart')):
        CreatResultDBTable(db, Dbresult)
        CreatUrlBuffTable(db, DbDatabuff)
        time.sleep(0.02)
        Write_buff(file_buff="Config.ini", settion=SearchDBName, info="restart", state=0)
        Write_buff(file_buff="Config.ini", settion=SearchDBName, info="startpage", state=1)
        Write_buff(file_buff="Config.ini", settion=SearchDBName, info="stopflag", state=0)
        Write_buff(file_buff="Config.ini", settion=SearchDBName, info="flag_get_all_url", state=0)
    if '0' in str(Read_buff(file_buff="Config.ini", settion=SearchDBName, info='restart')):
        db.upda_sql("Update `%s` set `State`=0 where `State`=10" % DbDatabuff)
    time.sleep(1)

ex_dbname = Read_buff(file_buff="Config.ini", settion=SearchDBName, info='ex_dbname')
DbDatabuff="databuff"+str(ex_dbname)
Dbresult="result"+str(ex_dbname)
def ProcessMain():
    global db, Cnki
    db = HCJ_MySQL()
    Cnki = Cnki_Crawler(db=db)
    multiprocessing.freeze_support()  # 多进程打包的话必须加上
    init_main()
    if '0'in str(Read_buff(file_buff="Config.ini", settion=SearchDBName, info='stopflag')) :
        main()


if __name__ == '__main__':
    # db = HCJ_MySQL()
    # Cnki = Cnki_Crawler(db=db)
    # url="http://www.cnki.com.cn/Article/CJFDTOTAL-ZNGY201106065.htm"
    # g=GetSoup(url)
    # parse(url,g)
    ProcessMain()