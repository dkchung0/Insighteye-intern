### 基本套件
import numpy as np
import pandas as pd
import time

### 爬蟲套件
import re

import requests
from bs4 import BeautifulSoup 

### 資料庫套件
import pymongo
from pymongo import MongoClient

############################################################

t1_start = time.time()

class crawlers_vote_static:

    def __init__(self,url,header,connect):

        self.url = url
        self.database = connect["test"]
        self.users = header

    def get_web_page(self):

        w = requests.get(self.url,headers=self.users)    

        w.encoding = "utf-8"
        
        if w.status_code != 200 :
            print("Invalid url")
            return None
        else :
            return w.text #js檔 轉為字串用正則表達式處理

    def get_rule(self,js_page):

        pattern = re.compile(r'(?<=firAreaID)\S+=(\S+);') # ()內是要的東西

        city=[]
        for i in range(len(pattern.findall(js_page))):
            city.append(pattern.findall(js_page)[i][1:-1])

        area = []

        for i in range(len(pattern.findall(js_page))):
            pattern2 = re.compile(r'(?<=firAreaID\[{}\]\+\'00\'\+padding\(\')\d+'.format(i))
            area.append(pattern2.findall(js_page))

        numbers = []
        n=-1
        for i in city:
            n+=1
            for j in area[n]:
                numbers.append(i+"00"+j)

        return numbers

    def vote_data(self,rule):
    
        url = "https://referendum.2021.nat.gov.tw/pc/zh_TW/01/{}0000000.html".format(rule)
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}

        w = requests.get(url,headers=headers) 
                                                                                                    
        w.encoding = "utf-8"
        
        if w.status_code != 200 :
            print("Invalid url")
        else :
            soup = BeautifulSoup(w.text, "lxml") 

            pattern = re.compile(r'(?<=\xa0-\xa0)\w+')
            Adm = pattern.findall(soup.select('td[valign="bottom"]')[0].text)[0]

            pattern = re.compile(r'(?<=\xa0)\d+')
            vote = int(pattern.findall(soup.select('td[align="right"]')[0].text)[0])

            df = [i.text for i in soup.select('tr.trT td')]

            df.insert(0,Adm)
            df.append(vote)

            return df
    
    def run_data(self,numbers):

        cols=["縣市行政區","同意票數","不同意票數","有效票數","無效票數","投票數","投票權人數","已完成投票所投票率(%)","有效同意票數對投票權人數(%)","已完成投票所"]

        for i in numbers:
            # time.sleep(1)
            if  self.database["vote_oop_static"].find_one({"縣市行政區":self.vote_data(i)[0]}):
                print("'{}'資料已新增".format(self.vote_data(i)[0]))
            else:
                try:
                    self.database["vote_oop_static"].insert_one(dict(zip(cols,self.vote_data(i))))
                except:
                    n = {}
                    for k, v in dict(zip(cols,self.vote_data(i))).items():
                        if isinstance(v, np.int64):
                            v = int(v)
                        n[k]= v

                    self.database["vote_oop_static"].insert_one(n)


###########################################################################

if __name__ == '__main__ '

    url = "https://referendum.2021.nat.gov.tw/pc/zh_TW/js/treeFF.js"
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
    connect = MongoClient('localhost', 27017)

    craw_page = crawlers_vote_static(url,header,connect)
    page = craw_page.get_web_page()
    numbers = craw_page.get_rule(page)
    craw_page.run_data(numbers)

    t1_end = time.time()

    print("Elapsed time during the whole program in seconds:{}".format(t1_end-t1_start)) 