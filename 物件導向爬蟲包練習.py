### 基本套件
import numpy as np
import pandas as pd

from time import process_time
from tqdm.auto import tqdm

### 爬蟲套件
import re

import requests
from bs4 import BeautifulSoup 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

### 資料庫套件
import pymongo
from pymongo import MongoClient

################################################################################################################################

class crawlers_vote:
    
    def __init__(self,url,path,client):
        
        self.url = url
        self.path = path
        self.database = client["test"]


    def votepage_rule(self):


        driver = webdriver.Chrome(path)
        driver.get(self.url)
        driver.find_element_by_name("nodeIcon2").click()

        html = BeautifulSoup(driver.page_source, 'html.parser')

        number = []
        for i in html.select('div[id="domRoot"] div[id]'):
            number.append(i.attrs["id"])

        pattern = re.compile(r'(?<=folder)\d+')

        city_num = [int(pattern.findall(i)[0]) for i in number[3:25]]

        numbers=[]

        for j in range(len(city_num)-1): # 最後一個嘉義市另外看
            numbers.append([city_num[j]+i+1 for i in range(city_num[j+1]-city_num[j]-1)]) 

        numbers.append([391,392])

        return city_num , numbers

    def vote_data(self,city,adms):

        driver = webdriver.Chrome(path)    
        driver.get(self.url)

        driver.find_element_by_name("nodeIcon2").click()
        driver.find_element_by_name("nodeIcon{}".format(city)).click()
        driver.find_element_by_id("itemTextLink{}".format(adms)).click()

        html = BeautifulSoup(driver.page_source, 'html.parser')


        pattern = re.compile(r'(?<=\xa0-\xa0)\w+')
        Adm = pattern.findall(html.select('td[valign="bottom"]')[0].text)[0]

        pattern = re.compile(r'(?<=\xa0)\d+')
        vote = int(pattern.findall(html.select('td[align="right"]')[0].text)[0])

        df = [i.text for i in html.select('tr.trT td')]

        df.insert(0,Adm)
        df.append(vote)

        return df
    
    def run(self,citynum,numbers):

        cols=["縣市行政區","同意票數","不同意票數","有效票數","無效票數","投票數","投票權人數","已完成投票所投票率(%)","有效同意票數對投票權人數(%)","已完成投票所"]

        k=-1
        for i in citynum:
            k+=1
            for j in numbers[k]:
                if  self.database["vote_oop"].find_one({"縣市行政區":self.vote_data(i,j)[0]}):
                    print("'{}'資料已新增".format(self.vote_data(i,j)[0]))
                else:
                    try:
                        self.database["vote_oop"].insert_one(dict(zip(cols,self.vote_data(i,j))))
                    except:
                        n = {}
                        for k, v in dict(zip(cols,self.vote_data(i,j))).items():
                            if isinstance(v, np.int64):
                                v = int(v)
                            n[k]= v

                        self.database["vote_oop"].insert_one(n)

###########################################################################################################

url = "https://referendum.2021.nat.gov.tw/pc/zh_TW/IDX/indexFF.html"
path = os.getcwd() + "\chromedriver.exe'
connect = MongoClient('localhost', 27017)

c_page = crawlers_vote(url,path,connect)
citynumbers , allnumbers = c_page.votepage_rule()

c_page.run(citynumbers,allnumbers)