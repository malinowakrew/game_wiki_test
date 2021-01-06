import requests
from bs4 import BeautifulSoup

from datetime import datetime
import re

"""
page_scrapping
=====================
Page scrapping depends on date and transform information from it into a dictionary.
Using:
*re 
*bs4
*requests
"""


class Scraper:
    """
    The main aim of this class is collecting data from wikipedia and give it to other classes and functions.
    """
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

        problematic_data = '1/01'
        problematic_data = datetime.strptime(problematic_data, '%m/%d')
        if self.date.day == problematic_data.day and self.date.month == problematic_data.month:
            lu = li[5].findAll("li")
        else:
            lu = li[1].findAll("li")

        data = []
        for row in lu:
            text = row.get_text()
            split_text = text.split(" – ")

            #we don't want to use date before Christ times
            if not re.search("BC", split_text[0]) or re.search("AD", split_text[0]):
                data.append({
                    "year": split_text[0],
                    "text": re.sub("\[[0-9]{1,2}\]", "", split_text[1])
                })

        return data

if __name__ == "__main__":
    sc = Scraper()
    n = sc.data_soup_process()
