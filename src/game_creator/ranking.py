import datetime
from db.schema import *


class Ranking:
    def __init__(self, user_identity):
        self.user = Account.objects(name=user_identity)[0]

    def read_users_games(self):
        games = self.user.score
        games_objects = [game for game in games if isinstance(game, Game)]
        return games_objects

    def read_user_answers_from_games(self):
        dict_for_all_ranking = {}
        games_list = self.read_users_games()
        for game in games_list:
            dict_for_one_game = {"points": game.points}
            questions = [question.ranking_view() for question in game.questions]
            dict_for_one_game["questions"] = questions

            dict_for_all_ranking[game.date.strftime("%d-%m-%Y")] = dict_for_one_game

        return dict_for_all_ranking
