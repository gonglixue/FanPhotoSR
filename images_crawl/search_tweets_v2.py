import os
from DriverManager import TwitterImageCrawler

f = open("twitter_address.txt", "r")
all_account = [line.strip() for line in f]

config = {
    "driver_path": "F:\PycharmProject\FanPhotoSR\images_crawl\chromedriver.exe",
    "account":None,
    "start_time": "2019-01-01",
    "end_time": "2019-12-31",
    "save_root": "2019photo",
    "timeout": 600
}


if __name__ == "__main__":
    # init folder
    log = open("crawl_log.txt", "w")
    if not os.path.exists(config["save_root"]):
        os.mkdir(config["save_root"])
    for i in range(1, 13):
        sub_folder = os.path.join(config["save_root"], "%02d"%i)
        if not os.path.exists(sub_folder):
            os.mkdir(sub_folder)

    for account in all_account:
        config["account"] = account
        crawler = TwitterImageCrawler(config, log)
        num = crawler.crawl()
        print("finish account {} with {} images".format(account, num))
        # log.write("{} {}".format(account, num))

    log.close()