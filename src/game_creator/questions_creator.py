from src import scraper
from random import randint, shuffle
from datetime import datetime, timedelta
from werkzeug.exceptions import Gone, NotFound


from db.schema import *


class QuestionCreator:
    def __init__(self):
        self.questions_list = []
        self.current_year = datetime.now().year
        self.NUMBER_OF_QUESTIONS = 5

    def read(self) -> None:
        scrapped_questions_list = scraper.data_soup_process()
        chosen_numbers = []

        while self.NUMBER_OF_QUESTIONS > 0:
            question_number = randint(0, len(scrapped_questions_list)-1)

            if question_number not in chosen_numbers:
                chosen_numbers.append(question_number)
                self.questions_list.append(scrapped_questions_list[question_number])
                self.NUMBER_OF_QUESTIONS -= 1

    def dict_maker(self) -> Game:
        game = Game(date=datetime.now(), points=0)

        chosen_questions = []
        for question in self.questions_list:
            year = int(question["year"])
            text = question["text"]

            answers = [year]
            while True:
                random_year_1 = randint(-25, 25)
                random_year_2 = randint(-25, 25)

                while random_year_1 == 0:
                    random_year_1 = randint(-25, 25)

                while random_year_2 == 0:
                    random_year_2 = randint(-25, 25)

                random_year_2 += year
                random_year_1 += year

                if random_year_2 <= self.current_year and random_year_1 <= self.current_year:
                    if random_year_1 != random_year_2:
                        answers.append(random_year_1)
                        answers.append(random_year_2)
                        break
            shuffle(answers)

            q = Question(question_text=text,
                         answer_a=answers[0],
                         answer_b=answers[1],
                         answer_c=answers[2],
                         correct=year,
                         user_answer=None)
            q.save()
            game.questions.append(q)

            chosen_questions.append({"text": text,
                                    "years": {random_year_1: False,
                                              random_year_2: False,
                                              year: True}})
        game.save()
        return game

    def add_game_to_user(self, game, user_identity):
        user = Account.objects(name=user_identity["username"])[0]
        user.update(push__score=game)

    def user_question_reader(self, number, user_identity=None):
        user = Account.objects(name=user_identity["username"])[0]
        games = user.score[-1]
        question = games.questions[number]
        try:
            nic = question.user_answer
            if type(nic) == str:
                raise Gone
        except Gone:
            raise Gone
        except Exception:
            raise ValueError
            #if games.questions[number]#TODO chech if answer exist
        return question

    @staticmethod
    def check_if_today_game_exist(user_identity=None):
        try:
            user = Account.objects(name=user_identity["username"])[0]
            game = user.score[-1]
        except IndexError:
            return True
        last_game_date = game.date.strftime("%m/%d/%Y")
        date = datetime.now().strftime("%m/%d/%Y")

        if last_game_date == date:
            return False
        else:
            return True

    def check_answer(self, user_answer, question, user_identity):
        if user_answer in ["A", "B", "C"]:
            Question.objects(id=question.id).update(set__user_answer=user_answer)

            if question.user_view()[user_answer] == question.correct:
                self.add_point(user_identity['username'])
                return 1
            else:
                return 0
        else:
            raise NotFound

    @staticmethod
    def add_point(user_identity):
        user = Account.objects(name=user_identity)[0]
        game = user.score[-1]
        game.update(inc__points=1)

    @staticmethod
    def return_correct_year(question):
        return question.correct

# """
# if __name__ == "__main__":
#     points = 0
#     q = QuestionCreator()
#     q.read()
#     data = q.dict_maker()
#     lista = q.user_questions_maker(data)
#     print(lista)
#     for nr, i in enumerate(lista):
#         print(data[nr]["text"])
#         print(i)
#         start = datetime.now()
#         odp = input("ODP:").upper()
#         stop = datetime.now()
#         if (data[nr]["years"])[i[odp]]:
#             print("Poprawnie")
#             if stop-start < timedelta(seconds=10):
#                 print("NA czas")
#                 points += 1
#             else:
#                 print("Nie na czas")
#         else:
#             print(list((data[nr]["years"].keys()))[list(data[nr]["years"].values()).index(True)])
#     print("Your points {}".format(points))
# """