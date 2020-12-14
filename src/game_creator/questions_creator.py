from src import scraper
from random import randint

NUMBER_OF_QUESTIONS = 5


class Question:
    def __init__(self, text, a, b, c):
        self.question_text = text
        self.answer_a = a
        self.answer_b = b
        self.answer_c = c


class QuestionCreator:
    def __init__(self):
        self.questions_list = []

    def read(self) -> None:
        scrapped_questions_list = scraper.data_soup_process()
        chosen_numbers = []
        #chosen_numbers = [number for number in generator(NUMBER_OF_QUESTIONS)]
        for _ in range(0, NUMBER_OF_QUESTIONS):
            question_number = randint(0, len(scrapped_questions_list))

            if question_number not in chosen_numbers:
                chosen_numbers.append(question_number)
                self.questions_list.append(scrapped_questions_list[question_number])

    def dict_maker(self) -> list:
        chosen_questions = []
        for question in self.questions_list:
            year = int(question["year"])
            text = question["text"]

            # mogą być jeszcze równe ze sobą ale to trzeba jakoś ładnie tak napisać
            random_year_1 = randint(-25, 25)
            random_year_2 = randint(-25, 25)
            while random_year_1 == 0:
                random_year_1 = randint(-25, 25)

            while random_year_2 == 0:
                random_year_2 = randint(-25, 25)

            random_year_2 += year
            random_year_1 += year

            chosen_questions.append({"text": text,
                                    "years": {random_year_1: False,
                                              random_year_2: False,
                                              year: True}})
        return chosen_questions

