from src import scraper

# def test_get_page_url():
#     assert False
#
#
# def test_req():
#     assert False



def test_data_soup_proccess():
    assert isinstance(scraper.data_soup_process(), list)
