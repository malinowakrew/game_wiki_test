import pytest
from src.pageReader.page_scraping import Scraper
import datetime
import random

@pytest.fixture
def scraper():
    return Scraper()


def random_date():
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2020, 12, 31)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random.seed(1929283)
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)


def test_scraper(scraper):
    for _ in range(1, 10):
        scraper.date = random_date()
        data = scraper.data_soup_process()
        assert isinstance(data, list)
        assert len(data) > 0

