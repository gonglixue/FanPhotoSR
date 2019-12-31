import os
import time
from DriverManager import TwitterImageCrawler

f = open("twitter_address.txt", "r")
all_account = [line.strip() for line in f]

config = {
    "driver_path": "F:\PycharmProject\FanPhotoSR\images_crawl\chromedriver.exe",
    "account":None,
    "start_time": "2019-01-01",
    "end_time": "2019-12-31",
    "save_root": "2019photo2",
    "timeout": 600
}

def resume_status(status_log):
    line = ""
    for ll in status_log:
        line = ll.strip()
    if len(line) == 0 or line is None:
        return "", ""
    account, last_date = line.split(",")
    account = account.strip()
    last_date = last_date.strip()
    return account, last_date
    

if __name__ == "__main__":
    mode = "scratch" # "resume"
    resume_account, resume_date = "", ""

    # init folder
    if not os.path.exists("crawl_log.txt") or mode=="scratch":
        log = open("crawl_log.txt", "w")
    else:
        log = open("crawl_log_{}.txt".format(time.strftime("%Y%m%d-%H%M%S", time.localtime()) ), "w")
    if mode == "scratch":
        status_log = open("status_log.txt", "w")
    else:
        status_log = open("status_log.txt", "r")
        resume_account, resume_date = resume_status(status_log)
        status_log.close()
        status_log = open("status_log.txt", "a")

    if not os.path.exists(config["save_root"]):
        os.mkdir(config["save_root"])
    for i in range(0, 13):
        sub_folder = os.path.join(config["save_root"], "%02d"%i)
        if not os.path.exists(sub_folder):
            os.mkdir(sub_folder)

    begin_ind = 0
    if resume_account != "":
        for acc in all_account:
            if acc == resume_account:
                break
            begin_ind += 1
    all_account = all_account[begin_ind: -1]
    print("search {} accounts: ".format(len(all_account)))
    print(all_account)

    resume_flag = True
    for account in all_account:
        config["account"] = account
        crawler = TwitterImageCrawler(config, log, status_log)
        if resume_flag:
            if resume_date == "":
                resume_date = None
            num = crawler.crawl(resume_date)
            resume_flag = False
        else:
            num = crawler.crawl()
        print("finish account {} with {} images".format(account, num))
        # log.write("{} {}".format(account, num))

    log.close()
    status_log.close()