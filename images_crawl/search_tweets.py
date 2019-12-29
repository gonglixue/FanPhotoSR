#!usr/bin/python3

from bs4 import BeautifulSoup
import time
from csv import DictWriter
import pprint
import datetime
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from urllib import request

# https://twitter.com/search?q=191222%20since%3A2019-01-01%20until%3A2019-01-02&src=typd
# https://twitter.com/search?q=191222%20until%3A2019-01-02%20since%3A2019-01-01&src=typed_query
def init_driver(driver_type):
    if driver_type == 1:
        driver = webdriver.Firefox()
    elif driver_type == 2:
        driver = webdriver.Chrome("F:\PycharmProject\FanPhotoSR\images_crawl\chromedriver.exe")
    elif driver_type == 3:
        driver = webdriver.Ie()
    elif driver_type == 4:
        driver = webdriver.Opera()
    elif driver_type == 5:
        driver = webdriver.PhantomJS()
    driver.wait = WebDriverWait(driver, 5)
    return driver


def scroll(driver, start_date, end_date, words, lang, max_time=20, account=None):
    languages = { 1: 'en', 2: 'it', 3: 'es', 4: 'fr', 5: 'de', 6: 'ru', 7: 'zh'}
    url = "https://twitter.com/search?q="
    for w in words[:-1]:
        url += "{}%20OR".format(w)
    url += "{}".format(words[-1])
    if account is not None:
        url += "(from%3A{})".format(account)
    url += "%20"
    url += "until%3A{}%20since%3A{}&".format(end_date, start_date)
    if lang != 0:
        url += "l={}&".format(languages[lang])
    url += "src=typed_query"
    print("url", url)
    driver.get(url)
    start_time = time.time()  # remember when we started

    last_scrollHeight = driver.execute_script("return document.body.scrollHeight;")  # scroll height before loading
    while (time.time() - start_time) < max_time:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print( str(time.time() - start_time) + " < " + str(max_time) , end='\r')

        current_scrollHeight = driver.execute_script("return document.body.scrollHeight;")
        if current_scrollHeight == last_scrollHeight:
            print("scoll to bottom")
            break
        last_scrollHeight = current_scrollHeight


def scrape_tweets(driver):
    try:
        tweet_divs = driver.page_source
        obj = BeautifulSoup(tweet_divs, "html.parser")
        content = obj.find_all("div", class_="content")
        print(content)

        print("content printed")
        print(len(content))
        for c in content:
            tweets = c.find("p", class_="tweet-text").strings
            tweet_text = "".join(tweets)
            print(tweet_text)
            print("-----------")
            try:
                name = (c.find_all("strong", class_="fullname")[0].string).strip()
            except AttributeError:
                name = "Anonymous"
            date = (c.find_all("span", class_="_timestamp")[0].string).strip()

            datestring = str(c.find_all("span", class_="_timestamp")[0])
            datestring = datestring[datestring.index("data-time")+11:]
            datestring = datestring[:datestring.index("\"")]
            print(datestring)
            print(tweet_text)      

            photo_container = c.find_all("div", class_="AdaptiveMedia-photoContainer")      
            if len(photo_container) > 0:
                print("find {} photo container".format(len(photo_container)))
                for pc in photo_container:
                    img_tags = pc.find_all("img")[0]
                    src = img_tags["src"]
                    img_name = src.split('/')[-1]

                    # request image url
                    print("img url:", src+":large")
                    # req = request.Request(src+":large", headers={
                    #     "authority": "pbs.twimg.com",
                    #     "method": "GET",
                    #     "path":"/media/EMZQzy6UwAEnZZ8.jpg:large",
                    #     "scheme": "https",
                    #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    #     "accept-encoding": "gzip, deflate, br",
                    #     "accept-language": "zh-CN,zh;q=0.9",
                    #     "cache-control": "no-cache",
                    #     "pragma": "no-cache",
                    #     "sec-fetch-mode": "navigate",
                    #     "sec-fetch-site": "none",
                    #     "sec-fetch-user": "?1",
                    #     "upgrade-insecure-requests": "1",
                    #     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
                    # })
                    # data = request.urlopen(req, timeout=30).read()
                    # f = open(img_name, 'wb')
                    # f.write(data)
                    # f.close()

                    # request by driver
                    img_response = driver.get(src+":large")
            else:
                print("no photo")
            # try:
            #     write_csv(datestring,tweet_text,name)
            # except:
            #     print('csv error')

    except Exception as e:
        print("Something went wrong!")
        print(e)
        driver.quit()


def write_csv_header():
    with open("twitterData.csv", "w+") as csv_file:
        fieldnames = ['Date', 'Name', 'Tweets','Tags']
        writer = DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

def write_csv(date,tweet,name):
    with open("twitterData.csv", "a+") as csv_file:
        fieldnames = ['Date', 'Name', 'Tweets','Tags']
        writer = DictWriter(csv_file, fieldnames=fieldnames)
        #writer.writeheader()
        writer.writerow({'Date': date,'Name': name,'Tweets': tweet})



def make_csv(data):
    l = len(data['date'])
    print("count: %d" % l)
    with open("twitterData.csv", "a+") as file:
        fieldnames = ['Date', 'Name', 'Tweets']
        writer = DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(l):
            writer.writerow({'Date': data['date'][i],
                            'Name': data['name'][i],
                            'Tweets': data['tweet'][i],
                            })


def get_all_dates(start_date, end_date):
    dates = []
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    step = timedelta(days=1)
    while start_date <= end_date:
        dates.append(str(start_date.date()))
        start_date += step

    return dates


def main():
    # driver_type = int(input("1) Firefox | 2) Chrome | 3) IE | 4) Opera | 5) PhantomJS\nEnter the driver you want to use: "))
    # wordsToSearch = input("Enter the words: ").split(',')
    # for w in wordsToSearch:
    #     w = w.strip()
    # start_date = input("Enter the start date in (YYYY-MM-DD): ")
    # end_date = input("Enter the end date in (YYYY-MM-DD): ")
    # account = input("Enter account(without @): ")
    # lang = int(input("0) All Languages 1) English | 2) Italian | 3) Spanish | 4) French | 5) German | 6) Russian | 7) Chinese\nEnter the language you want to use: "))

    driver_type = 2
    wordsToSearch = ["191222"]
    start_date = "2019-12-21"
    end_date = "2019-12-23"
    account = "yeoreum110"
    lang = 0

    write_csv_header()

    driver = init_driver(driver_type)

    driver.get("https://pbs.twimg.com/media/EMZQzy6UwAEnZZ8.jpg:large")
    js_script = '''window.downloadImageToBase64 = function (url) {
    // Put these constants out of the function to avoid creation of objects.
    var STATE_DONE = 4;
    var HTTP_OK = 200;
    var xhr = new XMLHttpRequest();

    function stateChange() {
        // Wait for valid response
        if (xhr.readyState == STATE_DONE && xhr.status == HTTP_OK) {
            var blob = new Blob([xhr.response], {
                type: xhr.getResponseHeader("Content-Type")
            });
            // Create file reader and convert blob array to Base64 string
            var reader = new window.FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = function () {
                var base64data = reader.result;
                console.log(base64data);
            }

        }
    };
   //  xhr.responseType = "arraybuffer";
    // Load async
    xhr.open("GET", url, false); // sync request
    xhr.send(null);

    //console.log(xhr.readyState)
    //console.log(xhr.status)
    // stateChange();
    //console.log(xhr.response)
   if (xhr.status == HTTP_OK && xhr.readyState==STATE_DONE)
   {
       return xhr.response;
   }
   else{
       return "-1";
   }
};'''
    driver.execute_script(js_script)
    bdata = driver.execute_script('return window.downloadImageToBase64("https://pbs.twimg.com/media/EMZQzy6UwAEnZZ8.jpg:large");')
    # print(bdata.encode('unicode'))
    import base64
    bdata = bytearray(bdata, 'utf-16')
    # base64.b64decode(data)
    # print(bdata)
    with open("bdata.jpg", "wb") as f:
        f.write(bdata)
        f.close()

    # scroll(driver, start_date, end_date, wordsToSearch, lang, account=account)
    # scrape_tweets(driver)
    # time.sleep(5)
    print("finish!")
    driver.quit()


if __name__ == "__main__":
    main()