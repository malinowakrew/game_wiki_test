import requests
from bs4 import BeautifulSoup

from datetime import datetime

class Scraper():
    def __init__(self):
        self.date = datetime.now()

    def getPageURL(self):
        day = self.date.day
        month = self.date.strftime('%B')

        return "https://en.wikipedia.org/wiki/" + month + "_" + str(day)

    def req(self):
        http = self.getPageURL()
        url = requests.get(http)
        code = BeautifulSoup(url.text, "html.parser")
        return (code.findAll("ul"))

    def dataSoupProccess(self):
        li = self.req()
        lu = li[1].findAll("li")
        data = {}
        for item in lu:
            r = item.get_text()
            ru = r.split(" – ")
            data[ru[0]] = ru[1]

        return data