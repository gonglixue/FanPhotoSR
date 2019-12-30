import datetime
import time
from dateutil.relativedelta import relativedelta
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import requests
from PIL import Image
from io import BytesIO

class DriverManager(object):

    def __init__(self, config, log_file):
        self.account = config["account"]
        self.start_time = config["start_time"]
        self.end_time = config["end_time"]
        self.driver = webdriver.Chrome(config["driver_path"])
        self.save_root = config["save_root"]
        self.timeout = config["timeout"] # s
        self.log_file = log_file

    @staticmethod
    def construct_url(account, start_time, end_time):
        url = "https://twitter.com/search?q=(from%3A{})%20until%3A{}%20since%3A{}&src=typed_query".format(
            account,
            end_time,
            start_time
        )
        return url

    def crawl(self):
        # get all date range by month
        all_dates = self.__get_all_months__()
        total_counts = 0

        for i in range(len(all_dates)-1):
            query_start = all_dates[i]
            query_end = all_dates[i+1]
            url = self.construct_url(self.account, query_start, query_end)
            print("{} - {}: {}".format(query_start, query_end, url))
            

            self.__scroll_to_end__(url)
            query_images_count = self.__parse_page__()
            total_counts += query_images_count

            print("------------------- {}".format(query_images_count))
            self.log_file.write("   {} - {}: {}\n".format(query_start, query_end,query_images_count))

        print("\n\n\n Finish")
        print(total_counts)
        self.log_file.write("[{}]: {} images\n".format(self.account, total_counts))
        self.log_file.write("---------------------------------------------------\n\n\n")
        
        time.sleep(8)
        self.driver.quit()
        return total_counts
            

    def __parse_page__(self):
        images_count = 0
        try:
            tweets_divs = self.driver.page_source
            obj = BeautifulSoup(tweets_divs, "html.parser")
            content = obj.find_all("div", class_='content')
            print("------{} tweets are found".format(len(content)))
            self.log_file.write("   {} tweets found\n".format(len(content)))
            for c in content:
                datestring = str(c.find_all("span", class_="_timestamp")[0])
                datestring = datestring[datestring.index("data-time")+11:]
                datestring = datestring[:datestring.index("\"")]
                tweet_time = time.localtime(int(datestring))
                month = "%02d"%(int(tweet_time.tm_mon))
                day = "%02d"%(int(tweet_time.tm_mday))

                photo_container = c.find_all("div", class_="AdaptiveMedia-photoContainer")      
                if len(photo_container) > 0:
                    print("------------find {} photo container".format(len(photo_container)))
                    images_count += len(photo_container)

                    for pc in photo_container:
                        img_tags = pc.find_all("img")[0]
                        src = img_tags["src"]
                        img_name = src.split('/')[-1]

                        # request image url
                        print("------------img url:", src+":large")
                        response = requests.get(src+":large")
                        image = Image.open(BytesIO(response.content))
                        
                        img_name = "{}-{}-{}-{}".format(month, day, self.account, img_name)
                        image.save(os.path.join(self.save_root, month, img_name))
                        print("------------save image:", img_name)
                        
                else:
                    print("------------no photo")
                    images_count += 0
        except Exception as e:
            print("Something woring in __parse_page__")
            print(e)
            self.driver.quit()
        return images_count

    def __scroll_to_end__(self, url):
        self.driver.get(url)
        last_scorll_height = self.driver.execute_script("return document.body.scrollHeight;")
        
        start_time = time.time()
        # scroll until load all data
        while (time.time() - start_time) < self.timeout:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

            current_scroll_height = self.driver.execute_script("return document.body.scrollHeight;")
            if current_scroll_height == last_scorll_height:
                print("------scroll to bottom")
                break
            last_scorll_height = current_scroll_height
        if (time.time() - start_time) > self.timeout:
            print("------scroll timeout")



    def __get_all_months__(self):
        all_dates = []
        start_date = datetime.datetime.strptime(self.start_time, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(self.end_time, "%Y-%m-%d")
        # step = relativedelta(months=+1)
        step = datetime.timedelta(days=15)
        while start_date <= end_date:
            all_dates.append(str(start_date.date()))
            start_date += step

            if start_date > end_date:
                all_dates.append(str(end_date.date()))

        print("construct dates:", all_dates)
        return all_dates
    

