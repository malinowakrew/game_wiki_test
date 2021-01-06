from src import scraper


def test_data_soup_proccess():
    assert isinstance(scraper.data_soup_process(), list)
