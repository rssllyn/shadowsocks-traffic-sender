# *_* encoding:utf-8 *_*
import schedule 
import time
import json
import functools
import re
import requests

def sendTrafficToAllUsers(conf, mailtime):
    mailgunSendURL = "{baseurl}/messages".format(baseurl=conf["mailgun-api-base-url"])
    mailgunFrom = conf["mailgun-from"]
    mailgunAPIKey = conf["mailgun-api-key"]
    currenttime = mailtime
    zhdate = time.strftime("%Y年%m月%d日", time.localtime()).decode("utf-8")
    endate = time.strftime("%B %d, %Y", time.localtime()).decode("utf-8")
    sendTime = {
            "en": u"{time} on {date}".format(date=endate, time=currenttime),
            "zh": u"{date}{time}".format(date=zhdate, time=currenttime)
    }
    auth=("api", mailgunAPIKey)
    print auth
    with open("sstraffic") as traffic:
        for line in traffic:
            parts = line.split()
            if parts[0] =="#" or parts[0] == "Total":
                continue
            port = int(parts[0])

            limitTraffic = parts[1]
            m = re.match(r"(.*)\((.*)\)", limitTraffic)
            limitBytes = int(m.groups()[0])
            limitForDisplay = m.groups()[1]

            usedTraffic = parts[2]
            m = re.match(r"(.*)\((.*)\)", usedTraffic)
            usedBytes = int(m.groups()[0])
            usedForDisplay = m.groups()[1]

            remainingTraffic = parts[3]
            m = re.match(r"(.*)\((.*)\)", remainingTraffic)
            remainingBytes = int(m.groups()[0])
            remainingForDisplay = m.groups()[1]


            for u in conf["users"]:
                if u["port"] == port:
                    user = u

                    if ("mail" not in user) or len(user["mail"]) == 0:
                        print "没有为端口号{port}对应的用户设置邮箱地址，请修改traffic-sender.conf进行配置".format(port=port)
                        continue
                            
                    if remainingBytes > 0:
                        textTemplate = conf["mailgun-text-{}".format(user["language"])]
                        text = textTemplate.format(time=sendTime[user["language"]], limit=limitForDisplay, used=usedForDisplay, remaining=remainingForDisplay, port=port, name=user["name"])
                        subjectTemplate = conf["mailgun-subject-{}".format(user["language"])]
                        subject = subjectTemplate.format(time=sendTime[user["language"]], limit=limitForDisplay, used=usedForDisplay, remaining=remainingForDisplay, port=port, name=user["name"])
                        data = {
                            "from": mailgunFrom,
                            "to": user["mail"],
                            "subject": subject,
                            "text": text
                        }
                        print data
                        r = requests.post(mailgunSendURL, auth=auth, data=data)
                        print r.text
                    else:
                        print "you are out of traffic"
            

def sendEmailEveryDay():
    with open("traffic-sender.conf") as configFile:
        conf = json.load(configFile)
        mailtime = conf["mailtime"].split()
        for t in mailtime:
            print "will send email every day at", t
            schedule.every().day.at(t).do(functools.partial(sendTrafficToAllUsers, conf, t))
            # schedule.every(10).seconds.do(functools.partial(sendTrafficToAllUsers, conf))

if __name__ == "__main__":
    sendEmailEveryDay()
    while True:
        schedule.run_pending()
        time.sleep(1)
