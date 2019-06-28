#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:hcj
# @File    : test1.py
# datetime:2019/6/24 11:39
# encoding='utf-8'
# import json
# import time
# import random
# from lxml import etree
# import requests
# import codecs



class CNKI(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    cookies = {
        'Cookie': 'Ecp_ClientId=4181108101501154830; cnkiUserKey=ec1ef785-3872-fac6-cad3-402229207945; UM_distinctid=166f12b44b1654-05e4c1a8d86edc-b79183d-1fa400-166f12b44b2ac8; KEYWORD=%E5%8D%B7%E7%A7%AF%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C%24%E5%8D%B7%E7%A7%AF%20%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C; Ecp_IpLoginFail=1811121.119.135.10; amid=73b0014b-8b61-4e24-a333-8774cb4dd8bd; SID=110105; CNZZDATA1257838113=579682214-1541655561-http%253A%252F%252Fsearch.cnki.net%252F%7C1542070177'}
    param = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept - Encoding': 'gzip, deflate',
        'Accept - Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep - alive',
        'Content - Type': 'application / x - www - form - urlencoded;charset = UTF - 8',
        'Host': 'yuanjian.cnki.net',
        'Origin': 'http: // yuanjian.cnki.net',
        'Referer': 'http: // yuanjian.cnki.net / Search / Result',
        'X - Requested - With': 'XMLHttpRequest'}

    def content(self):
        li = []
        for j in range(274, 275):
            for i in range(j, j + 1):
                url = 'http://yuanjian.cnki.net/Search/Result'
                print('当前页', i)
                time.sleep(random.random() * 3)
                formdata = {'Type': 1,
                            'Order': 1,
                            'Islegal': 'false',
                            'ArticleType': 1,
                            'Theme': '卷积神经网络',
                            'searchType': 'MulityTermsSearch',
                            'ParamIsNullOrEmpty': 'true',
                            'Page': i}
                print(formdata)
                try:
                    r = requests.post(url, data=formdata, headers=self.headers, cookies=self.cookies, params=self.param)
                    r.raise_for_status()
                    r.encoding = r.apparent_encoding
                    data = etree.HTML(r.text)
                    # 链接列表
                    #url_list = data.xpath("//*[@id='article_result']/div/div/p[1]/a[1]/@href")
                    #
                    url_list = data.xpath("//*[@id='article_result']/div/div/p[1]/a[1]/@href")
                    # 关键词列表
                    key_wordlist = []
                    all_items = data.xpath("//*[@id='article_result']/div/div")
                    for i in range(1, len(all_items) + 1):
                        key_word = data.xpath("//*[@id='article_result']/div/div[%s]/div[1]/p[1]/a/text()" % i)

                        key_words = '；'.join(key_word)
                        key_wordlist.append(key_words)
                    # 来源
                    source_items = data.xpath("//*[@id='article_result']/div/div")
                    for j in range(1, len(source_items) + 1):
                        sources = data.xpath("//*[@id='article_result']/div/div/p[3]/a[1]/span/text()")
                    for index, url in enumerate(url_list):
                        items = {}
                        try:
                            print('当前链接：', url)
                            content = requests.get(url, headers=self.headers)
                            contents = etree.HTML(content.text)
                            # 论文题目
                            title = contents.xpath("//h1[@class='xx_title']/text()")[0]
                            items['titleCh'] = title
                            items['titleEn'] = ''
                            print('标题：', title)
                            # 来源
                            source = sources[index]
                            items['source'] = source
                            print('来源：', source)

                            # 关键字
                            each_key_words = key_wordlist[index]
                            print('关键字：', each_key_words)
                            items['keywordsEn'] = ''
                            items['keywordsCh'] = each_key_words
                            # 作者
                            author = contents.xpath("//*[@id='content']/div[2]/div[3]/a/text()")
                            items['authorCh'] = author
                            items['authorEn'] = ''
                            print('作者：', author)
                            # 单位
                            unit = contents.xpath("//*[@id='content']/div[2]/div[5]/a[1]/text()")
                            units = ''.join(unit).strip(';')
                            items['unitCh'] = units
                            items['unitEn'] = ''
                            print('单位：', units)
                            # 分类号
                            classify = contents.xpath("//*[@id='content']/div[2]/div[5]/text()")[-1]
                            c = ''.join(classify).split(';')
                            res = []
                            for name in c:
                                print('当前分类号：', name)
                                try:
                                    if name.find("TP391.41") != -1:
                                        print('改变分类号!')
                                        name = 'TP391.4'
                                    result = requests.get('http://127.0.0.1:5000/%s/' % name)
                                    time.sleep(5)
                                    re_classify1 = result.content
                                    string = str(re_classify1, 'utf-8')
                                    classify_result = eval(string)['classfiy']
                                    # print('文献分类导航:', classify_result)

                                except Exception as e:
                                    print(e)
                                res.append(classify_result)
                                print('文献分类导航:', res)
                            items['classify'] = res

                            # 摘要
                            abstract = contents.xpath("//div[@class='xx_font'][1]/text()")[1].strip()
                            print('摘要：', abstract)
                            items['abstractCh'] = abstract
                            items['abstractEn'] = ''
                            # 相似文献
                            similar = contents.xpath(
                                "//*[@id='xiangsi']/table[2]/tbody/tr[3]/td/table/tbody/tr/td/text()")
                            si = ''.join(similar).replace('\r\n', '').split('期')
                            po = []
                            for i in si:
                                sis = i + '期'
                                if len(sis) > 3:
                                    po.append(sis)

                            items['similar_article'] = po
                            # 参考文献
                            refer_doc = contents.xpath("//*[@id='cankao']/table[2]/tbody/tr[3]/td/table/tbody/tr/td/text()")
                            items['refer_doc'] = refer_doc

                            li.append(items)

                        except Exception as e:
                            print(e)
                        print(len(li))
                except Exception as e:
                    print(e)

        return li


if __name__ == '__main__':
    # con = CNKI()
    # items = con.content()
    # print(items)
    # try:
    #     with codecs.open('./cnki_data.json', 'a+', encoding="utf-8") as fp:
    #         for i in items:
    #             fp.write(json.dumps(i, ensure_ascii=False) + ",\n")
    #
    # except IOError as err:
    #     print('error' + str(err))
    # finally:
    #     fp.close()


    str1=""
    Dict={'url': 'http://www.cqvip.com/%22/QK/94832X/200901/28998296.html%22', 'title': '移动自组网软件平台的研究与设计', 'authors': ' 何庆 邱静怡 许德兴 许骏 ', 'unit': '华南师范大学教育信息技术学院 广州510631 广州无线电研究所 广州510500 \n', 'publication': '《计算机应用》', 'keywords': ' 无线自组网 普适终端设备 AODV MAODV 移动计算   ', 'abstract': '终端设备的独有特性包括它们的移动性、个性化和位置感知，形成了新型的无线应用，能满足普遍存在的移动计算需求。展示一种在移动自组网环境下的无线终端设备。终端设备选择在Linux嵌入式平台进行开发。在该设备上，实现了AODV、MAODV路由算法并在NS-2上进行了路由协议性能的比较和分析。最后给出了终端设备原型的实现，并且提出了未来的改进方向和应用场景。\r\t\t\t\t', 'year': '2009', 'volume': '', 'issue': '1', 'pagecode': '340-343', 'doi': '', 'sponser': '', 'type': '【工业技术】 > 自动化技术、计算机技术 > 计算技术、计算机技术 > 计算机的应用 > 计算机网络 '}
    for key in list(Dict.keys()):
        if str(Dict[key])=="":
            del Dict[key]
        else:
            Dict[key] = Dict[key].replace('\n','').replace('\"',"#").replace('\t',"").replace('\r',"").replace('\xa0',"").replace('%', ">")
    print(Dict)
    for key in list(Dict.keys()):
        if str(Dict[key]) != "":
            col=key
            row=Dict[key]
            str1=str1+"`%s`=(case when `%s`='' then '%s' else `%s` end ),"%(col,col,row,col)
    print(str1[:-1])
    sql_update="update `result` set `url`=concat(`url`,';%s'),%s where `title`='%s' and `publication`='%s'"%(Dict['url'],str1[:-1],(Dict['title']),(Dict['publication']))
    print(sql_update)