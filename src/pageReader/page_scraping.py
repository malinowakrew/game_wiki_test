import requests
from bs4 import BeautifulSoup

from datetime import datetime
import re

"""
Page scrapping depends on date and transform information from it into a dictionary
"""


class Scraper:
    def __init__(self):
        self.date = datetime.now()

    def get_page_url(self) -> str:
        day = self.date.day
        month = self.date.strftime('%B')

        return "https://en.wikipedia.org/wiki/" + month + "_" + str(day)

    def req(self) -> list:
        http = self.get_page_url()
        url = requests.get(http)
        code = BeautifulSoup(url.text, "html.parser")
        return code.findAll("ul")

    def data_soup_process(self) -> list:
        li = self.req()
        lu = li[1].findAll("li")
        data = []
        for row in lu:
            text = row.get_text()
            split_text = text.split(" – ")

            #we don't want to use date before Christ times
            if not re.search("BC", split_text[0]):
                data.append({"year": split_text[0], "text": split_text[1]})

        return data
