#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : Cqvip_main.py
# datetime:2019/6/19 9:43

import threading
from configparser import ConfigParser
from urllib.parse import quote
from HCJ_py_timer import LoopTimer
import socket
import os
import math
import urllib.request
from bs4 import BeautifulSoup
import time
import re
from HCJ_Buff_Control import Read_buff,Write_buff
#构造不同条件的关键词搜索
from HCJ_DB_Helper import HCJ_MySQL


values = {
           '1': 'k', # 标题
           '2': 'w', # 作者
           '3': 'k', # 关键词
           '4': 'o', # 单位

    }

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
def Up_division_int(A, B):
    '''
     向上整除
    :param A:
    :param B:
    :return:
    '''
    return int((A + B - 1) / B)
class Cqvip_Crawler:
    def __init__(self,Input=None,SearchMode=None,StartTime=None,EndTime=None,StartPage=None,SettingPath='./Config.ini'):
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
        index_url = "http://www.cqvip.com/data/main/search.aspx?action=so&curpage=1&perpage=%s&%s=%s"%(str(self._Perpage),str(values[self.SearchMode]),quote(str(self.Input)))
        soup = self.GetSoup(url=index_url)
        deff = soup.select('p')[0].text
        summarys = int(deff.split('\r\n')[1].split('"recordcount":')[1].split(',')[0].strip())
        print("查询到共%s相关文献"%summarys)
        self.MaxPage=Up_division_int(summarys,int(self._Perpage))

        cf = ConfigParser()
        cf.read("Config.ini", encoding='utf-8')
        cf.set(self.SearchName, 'maxpage', str(self.MaxPage))
        cf.write(open('Config.ini', 'w', encoding='utf-8'))
        return self.MaxPage
    def GetSoup(self,url=None):
        req = urllib.request.Request(url=url, headers=headers)
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, 'lxml')
        return soup
    def WriteAllUrl(self):
        self.MaxPage = self.GetMaxPage()  # 最大页数
        self.StartPage = Read_buff(file_buff=self.SettingPath, settion=self.SearchName, info='startpage')  # 开始页数
        _UrlList=[]
        t=time.time()
        Write_buff(file_buff="Config.ini", settion="Cqvip", info="flag_get_all_url", state=0)
        for i in range(int(self.StartPage),self.MaxPage):
            print("共有%s页，当前为%s页" % (self.MaxPage, i))
            page_url = "http://www.cqvip.com/data/main/search.aspx?action=so&curpage=%s&perpage=20&%s=%s" % (
                str(i), str(values[self.SearchMode]), quote(str(self.Input)))
            threading.Thread(target=self.WriteUrlIntoDB, args=( page_url,i)).start()
            time.sleep(0.1)
            # print(_UrlList)
        Write_buff(file_buff="Config.ini",settion="Cqvip",info="flag_get_all_url",state=1)
        print(time.time()-t)
        return _UrlList
    def WriteUrlIntoDB(self,page_url,page):
        soup = self.GetSoup(url=page_url)
        deff = soup.find_all('th')
        for k in range(len(deff)):
            Href = deff[k].a['href']
            if 'http' not in Href or 'www' not in Href:
                Href = deff[k].a['href'].replace('\\', '')
                url = "http://www.cqvip.com/" + quote(Href)
                #_UrlList.append(url)
                sql="INSERT INTO `cqvipcrawler`.`databuff` (`Page`, `PageNum`,`PageIndex`, `Url`) VALUES ('%s', '%s', '%s','%s');\n" % (
                    str(page), str(k), str(page) + '-' + str(k), url)
                row = db.insert(sql) # 插入
    def GetDicPaper(self,_soup=None,_url=None):
        _Paper = InitDict()
        deff = _soup.find('span', class_="detailtitle")
        _Paper['url'] = _url  # 获得【链接】
        _Paper['title'] = deff.find('h1').text  # 获得【标题】
        str1 = deff.find('strong').text.split('\xa0\xa0')
        _Paper['unit'] = str1[0].split('|')[0]  # 获得【单位】
        _Paper['authors'] = str1[0].split('|')[1]  # 获得【作者】
        _Paper['publication'] = str1[1]  # 获得【出版社】
        deff2 = _soup.select('table', class_="datainfo f14")
        _Paper['abstract'] = deff2[0].text.replace('\n', '').split('：', 1)[1]  # 获得【摘要】
        p = deff2[1].text
        _Paper['type'] = deff2[1].text.split('【分　类】', 1)[1].split('【关键词】')[0].replace('\n', '')  # 获得【分类】
        _Paper['keywords'] = deff2[1].text.split('【关键词】', 1)[1].split('【出　处】')[0].replace('\n', '')  # 获得【关键词】
        StrComeFrom = deff2[1].text.split('【出　处】', 1)[1].split('【收　录】')[0].replace('\n', '')
        Strlist = re.split(r"[;,\s]\s*", StrComeFrom)
        t = 0
        for st in Strlist:
            if st:
                if "年" in st:
                    if '》' in st:
                        _Paper['year'] = st.split('》')[1]  # 获得【出版年份】
                    else:
                        _Paper['year'] = st
                if "共" not in st and "页" in st:
                    _Paper['pagecode'] = st  # 获得【页码】
                if "期" in st:
                    _Paper['issue'] = st  # 获得【期】
        return _Paper
    def GetUrlFromDb(self,num=20):
        sql="select `PageIndex`,`Url` from `databuff` where `State`=0 ORDER BY `Page` ASC, `PageNum` limit %s "%num
        _rows=db.do_sql(sql)
        if _rows:
            if len(_rows)>0:
                _UrlList=[x[1] for x in _rows]
                for i in [x[0] for x in _rows]:
                    db.upda_sql("update `databuff` set `State`=10 where `PageIndex`='%s'"%i)
                return _UrlList
        else:
            return ""
    def CqvipMain(self):
        # LoopTimer(0.1, self.WriteAllUrl).start()
        LoopTimer(0.1, self.GetPaperResultFromUrl).start()
    def GetPaperResultFromUrl(self):
        '''
        通过GetUrlFromDb获得20个链接，然后进行爬取，爬取后写入数据库
        :return:
        '''
        UrlList = self.GetUrlFromDb(num=20)  # 获取20个
        threading.Thread(target=self.ThreadGetAndWrite, args=(UrlList,)).start()

    def ThreadGetAndWrite(self,UrlList):
        print("线程开始")
        if   len(UrlList)>0:
            startTime = time.time()
            for i in range(len(UrlList)):
                try:
                    soup = self.GetSoup(url=UrlList[i])
                    Paper = self.GetDicPaper(_soup=soup, _url=UrlList[i])
                    InsetDbbyDict("`cqvipcrawler`.`result`", Paper)
                except:
                    print("失败")
                    pass
            print("成功插入%s,耗时%s"%(len(UrlList),(time.time() - startTime)))
            time.sleep(0.05)
        else:
            pass
def InitDict():
    dir = {'url' :'', 'title' :'','authors':'','unit' :'','publication' :'','keywords' :'','abstract' :'','year' :'','volume' :'','issue' :'','pagecode' :'','doi' :'','string' :'','sponser' :'','type' :''}
    return dir

def InsetDbbyDict(table,Dict):
    COLstr = ''  # 列的字段
    ROWstr = ''  # 行字段
    for key in Dict.keys():
        COLstr = COLstr + ' ' + '`' + key + '`,'

        ROWstr = (ROWstr + '"%s"' + ',') % (str(Dict[key]).replace('%','#').replace('\n',''))
    sql = "INSERT INTO %s (%s) VALUES (%s);\n" % (
        table,COLstr[:-1], ROWstr[:-1])
    db.insert(sql)

class PaperAll(object):
    pass

def CreatResultDBTable(TableName):
    '''
    创建结构数据库表单，如果不存在就创建
    :return:
    '''
    str = ""
    Dict=InitDict()
    for key in Dict.keys():
        str+="`%s` varchar(200) DEFAULT NULL,"%key
    CreatDBTableSql='\
        CREATE TABLE IF NOT EXISTS `%s` (\
          `id` int(11) unsigned NOT NULL AUTO_INCREMENT,\
          `url` varchar(200) DEFAULT NULL, \
          `title` varchar(200) DEFAULT NULL,\
          `authors` varchar(200) DEFAULT NULL,\
          `unit` varchar(200) DEFAULT NULL,\
          `publication` varchar(200) DEFAULT NULL,\
          `keywords` varchar(200) DEFAULT NULL,\
          `abstract` varchar(200) DEFAULT NULL,\
          `year` varchar(200) DEFAULT NULL,\
          `volume` varchar(200) DEFAULT NULL,\
          `issue` varchar(200) DEFAULT NULL,\
          `pagecode` varchar(200) DEFAULT NULL,\
          `doi` varchar(200) DEFAULT NULL,\
          `string` varchar(200) DEFAULT NULL,\
          `sponser` varchar(200) DEFAULT NULL,\
          `type` varchar(200) DEFAULT NULL,\
          PRIMARY KEY (`id`)\
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1; '%TableName
    dict_result= db.upda_sql(CreatDBTableSql)
    if  not dict_result:
        print("创建出现问题")

    # if dict_result['result'] is True:
    #     print("创建表成功")
    # else:
    #     print(dict_result['err'])

# `Url` varchar(200) DEFAULT NULL,
#   `State` varchar(200) DEFAULT NULL,
#     str=""
#     for i in range(len(list)):
#         str+="`%s` varchar(200) DEFAULT NULL,"%list[i]
#     print(str)
#     p='CREATE TABLE `Result` (\
#   `id` int(11) unsigned NOT NULL AUTO_INCREMENT,%s\
#   PRIMARY KEY (`id`)\
# ) ENGINE=InnoDB DEFAULT CHARSET=latin1;'%str
#     print(p)
if __name__ == '__main__':
    db = HCJ_MySQL()
    Cqvip = Cqvip_Crawler()
    Cqvip.CqvipMain()


