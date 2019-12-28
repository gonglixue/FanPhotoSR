import json, re, datetime, sys, random, http.cookiejar
import urllib.request, urllib.parse, urllib.error
import requests
from pyquery import PyQuery
from bs4 import BeautifulSoup

def get_this_page_tweets(soup):
    tweets_list = list()
    tweets = soup.find_all("li", {"data-item-type": "tweet"})
    for tweet in tweets:
        tweet_data = None
        try:
            tweet_data = get_tweet_text(tweet)
        except Exception as e:
            continue
            #ignore if there is any loading or tweet error

        if tweet_data:
            tweets_list.append(tweet_data)
            print(".", end="")
            sys.stdout.flush()

    return tweets_list


def get_tweets_data(username, soup):
    tweets_list = list()
    tweets_list.extend(get_this_page_tweets(soup))

def get_tweet_text(tweet):
    tweet_text_box = tweet.find("p", {"class": "TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"})
    images_in_tweet_tag = tweet_text_box.find_all("a", {"class": "twitter-timeline-link u-hidden"})
    tweet_text = tweet_text_box.text
    for image_in_tweet_tag in images_in_tweet_tag:
        tweet_text = tweet_text.replace(image_in_tweet_tag.text, '')

    return tweet_text

LOG_CONSOLE = True

config = {
    "account": "yeoreum110",
    "since": "2019-01-01",
    "until": "2019-12-28"
}
query_format = "https://twitter.com/search?q=(from%3A{account})%20until%3A{until}%20since%3A{since}&src=typed_query"
url = query_format.format(**config)


user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:62.0) Gecko/20100101 Firefox/62.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
]

headers = {
    'Host': "twitter.com",
    'User-Agent': user_agents[0],
    'Accept': "application/json, text/javascript, */*; q=0.01",
    'Accept-Language': "en-US,en;q=0.5",
    'X-Requested-With': "XMLHttpRequest",
    'Referer': url,
    'Connection': "keep-alive"
}

cookieJar = http.cookiejar.CookieJar()
# no proxy
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
opener.addheaders = headers

if LOG_CONSOLE:
    print('**************** request info **********')
    print(url)
    print('\n'.join(h[0] + ": " + h[1] for h in headers))
    print('****************************************')

response = requests.get(url, headers=headers)
soup = BeautifulSoup("https://twitter.com/yeoreum110", 'lxml')
if soup.find("div", {"class": "errorpage-topbar"}):
    print("\n\n Error: Invalid request.")

tweets = get_tweets_data(config["account"], soup)
print(tweets)
# try:
#     response = opener.open(url)
#     jsonResponse = response.read()
# except Exception as e:
#     print("An error occured during an HTTP request:", str(e))
#     print("Try to open in browser: ", url)
#     sys.exit()

# try:
#     # print(jsonResponse)
#     # print("--------------------")
#     s_json = jsonResponse.decode()
#     print(s_json)
#     # print("--------------------")
#     # dataJson = json.loads(s_json)
#     # print(dataJson)
# except:
#     print("Invalid response from Twitter")
#     sys.exit()



