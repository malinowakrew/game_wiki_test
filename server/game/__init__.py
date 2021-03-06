from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
)
from flask import jsonify, request, redirect, url_for, Blueprint

from werkzeug.exceptions import BadRequest, NotFound

from src.game_creator.questions_creator import QuestionCreator

bp = Blueprint('game', __name__, url_prefix='/game')


@bp.route('/start', methods=['GET'])
@jwt_required
def start_game():
    return redirect(url_for('game.scrap'), code=302)


@bp.route('/scraper', methods=['GET'])
@jwt_required
def scrap():
    current_user = get_jwt_identity()

    game_questions = QuestionCreator()
    if game_questions.check_if_today_game_exist(current_user):

        game_questions.read()
        data = game_questions.dict_maker()
        game_questions.add_game_to_user(data, current_user)
        return jsonify({"game-created": True,
                        "next-page": url_for("game.wiki_test", number=0)}), 200
    else:
        return jsonify({"game-created": False,
                        "explanation": "Existing game with today date on this account"}), 401


@bp.route('/question/<int:number>', methods=['GET'])
@jwt_required
def show_question(number):
    if number > 4:
        raise NotFound
    if request.method == 'GET':
        game_questions = QuestionCreator()
        current_user = get_jwt_identity()
        current_user = current_user
        quest = game_questions.user_question_reader(number, current_user)
        return jsonify({"question": quest.user_view(),
                        "next-page": url_for("game.answer_question", number=number)}), 200


@bp.route('/answer/<int:number>/<answer>', methods=['GET'])
@jwt_required
def check_user_answer(number, answer):
    current_user = get_jwt_identity()
    if 0 <= number > 4:
        raise NotFound
    if number == 4:
        next_page = url_for("accounts.show_games_ranking", name=current_user["username"])
    else:
        next_page = url_for("game.wiki_test", number=number + 1)

    game_questions = QuestionCreator()
    question_in_database = game_questions.user_question_reader(number, current_user)
    point = game_questions.check_answer(answer, question_in_database, current_user)
    if point:
        return jsonify({"point": point,
                        "next-page": next_page}), 200
    else:
        correct_answer = game_questions.return_correct_year(question_in_database)

        return jsonify({"point": point,
                        "correct": correct_answer,
                        "next-page": next_page}), 200


@bp.route('/test/<int:number>', methods=['GET', 'POST'])
def wiki_test(number):
    if request.method == "GET":
        return redirect(url_for("game.show_question", number=number), code=302)
    if request.method == "POST":
        try:
            answer = request.json.get("answer", None)
            return redirect(url_for("game.check_user_answer", number=number, answer=answer), code=302)
        except Exception:
            raise BadRequest


@bp.route('/answer/<int:number>', methods=['POST'])
def answer_question(number):
    answer = request.json.get("answer", None)
    return redirect(url_for("game.check_user_answer", number=number, answer=answer), code=302)


@bp.errorhandler(IndexError)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "Game was not created",
                    "text": str(error)}), 400


@bp.errorhandler(BadRequest)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "Posted json is not correct",
                    "text": str(error)}), 400

