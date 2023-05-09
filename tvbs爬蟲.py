import numpy as np
import pandas as pd
import re
import arrow
import time

import requests
from bs4 import BeautifulSoup 

import pymongo
from pymongo import MongoClient


class tvbs_crawler:
    def __init__(self,date,header,connect,table) :
        self.date = date
        self.users = header
        self.database = connect["test"]
        self.table = table

    def get_web_page(self,url):

        w = requests.get(url,headers=self.users)                                                      
        w.encoding = "utf-8"
        
        if w.status_code != 200 :
            print("Invalid url")
            return None
        else :
            soup = BeautifulSoup(w.text,"html.parser")
            return soup

    def rule_page(self):

        url = "https://news.tvbs.com.tw/realtime/news/" + self.date

        news = self.get_web_page(url)

        realtime_url = []
        for i in range(len(news.select("div.news_list div.list a"))):
            if i%2 != 0 :
                continue
            realtime_url.append(news.select("div.news_list div.list a")[i].attrs["href"])

        return realtime_url
    
    def news_page(self,news):
    
        data = news
        
        insert_time = arrow.now()
        insert_time = insert_time.datetime

        field = "news"

        website = data.select("meta[property='dable:author']")[0].attrs["content"]

        url = data.select("meta[property='og:url']")[0]["content"]

        pattern = re.compile(r'(?<=發佈時間：)(\d+)/(\d+)/(\d+) (\d+):(\d+)')
        t = data.select("div.author")[0].text
        p = pattern.search(t)
        release_time = arrow.get(int(p.group(1)),int(p.group(2)),int(p.group(3)),int(p.group(4)),int(p.group(5)))
        release_time = release_time.datetime
        
        category = data.select("div.bread a")[-1].text

        #domain

        title = data.select("h1.title")[0].text

        try:
            author = data.select("div.author a")[0].text
        except:
            author = ""

        content = news.select("div#news_detail_div")[0].text
        content = re.sub("\n◤FUN心出遊\u3000精緻享受◢👉食尚玩家人氣飯店快閃團只有5天👉高質感精品飯店免費升等超划算👉用國旅券！賺星巴克電子飲料券👉全台唯一卡通頻道聯名主題房👉經典主題飯店帶你遨遊海洋世界👉訂房加購高鐵票還有75折優惠 ","",content)
        content = re.sub("最HOT話題在這！想跟上時事，快點我加入TVBS新聞LINE好友！","",content)
        content = re.sub("掌握即時路況！閃過國道塞車地雷路段","",content)
        content = re.sub("\n","",content)
        content = re.sub("\t","",content)
        content = re.sub("\xa0","",content)

        #click_resp_cnt

        #resp_list
        
        #resp_cnt
        
        #volume
        
        tag = news.select("div.article_keyword")[0].text
        pattern = re.compile(r'(?<=\#)\w+')
        tag = pattern.findall(tag)


        return insert_time , field , website , url , release_time , category , title , author , content , tag

    def run_data(self):
        
        t1_start = time.time()

        realtime_url = self.rule_page()

        try:
            for i in realtime_url :
                url_ = "https://news.tvbs.com.tw" +  i
                news = self.get_web_page(url_)
                insert_time , field , website , url , release_time , category , title , author , content , tag =  self.news_page(news)
                self.database[self.table].insert_one({"insert_time":insert_time,
                                                      "field":field,
                                                      "website":website,
                                                      "url":url,
                                                      "time":release_time,
                                                      "category":category,
                                                      "domain":"",
                                                      "title":title,
                                                      "author":author,
                                                      "content":content,
                                                      "click_resp_cnt":0,
                                                      "resp_list":[],
                                                      "resp_cnt":0,
                                                      "volume":0,
                                                      "tag":[tag]})
        except:
            print(url_)


        t1_end = time.time()

        print("Elapsed time during the whole program in seconds:{}".format(t1_end-t1_start)) 


###################################################################################  2月1日 ~ 2月24日 (data)


for i in range(24):

    i+=1

    if i<10:
        date = "2022-02-0{}".format(i)
        table = "tvbs_2022-02-0{}".format(i)
    else :
        date = "2022-02-{}".format(i)
        table = "tvbs_2022-02-{}".format(i)

    header = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
    connect = MongoClient('localhost', 27017)


    crawler_ = tvbs_crawler(date,header,connect,table)
    crawler_.run_data()
                    