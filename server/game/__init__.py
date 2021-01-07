from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
)
from flask import Flask, jsonify, request, redirect, url_for

import werkzeug
from flask import (
    Blueprint
)


from src.game_creator.questions_creator import QuestionCreator

bp = Blueprint('game', __name__, url_prefix='/game')


@bp.route('/start', methods=['POST'])
def redirection():
    ok = request.json.get('crate-new-game', True)
    if ok:
        return redirect(url_for('game.scrap'), code=302)
    else:
        return jsonify({"redirected": False}), 200


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
                        "explanation": "Existing game with today date on this account"}), 200


@bp.route('/question/<int:number>', methods=['GET'])
@jwt_required
def show_question(number):
    if number > 4:
        raise werkzeug.exceptions.NotFound
    if request.method == 'GET':
        game_questions = QuestionCreator()
        current_user = get_jwt_identity()
        current_user = current_user["username"]
        quest = game_questions.user_question_reader(number, current_user)
        return jsonify({"question": quest.user_view(),
                        "next-page": url_for("game.answer_question", number=number)}), 200


@bp.route('/answer/<int:number>/<answer>', methods=['GET'])
@jwt_required
def question_ident(number, answer):
    if 0 <= number > 4:
        raise werkzeug.exceptions.NotFound
    if number == 4:
        next_page = url_for("users.show_games_ranking")
    else:
        next_page = url_for("game.wiki_test", number=number + 1)
    current_user = get_jwt_identity()["username"]
    game_questions = QuestionCreator()
    quest = game_questions.user_question_reader(number, current_user)
    point = game_questions.check_answer(answer, quest, current_user)
    if point:
        return jsonify({"point": point,
                        "next-page": next_page}), 200
    else:
        correct_answer = game_questions.return_correct_year(quest)

        return jsonify({"point": point,
                        "correct": correct_answer,
                        "next-page": next_page}), 200


@bp.route('/test/<int:number>', methods=['GET', 'POST'])
def wiki_test(number):
    if request.method == "GET":
        return redirect(url_for("game.show_question", number=number), code=302)
    if request.method == "POST":
        answer = request.json.get("answer", None)
        return redirect(url_for("game.question_ident", number=number, answer=answer), code=302)


@bp.route('/answer/<int:number>', methods=['POST'])
def answer_question(number):
    answer = request.json.get("answer", None)
    return redirect(url_for("question_ident", number=number, answer=answer), code=302)


@bp.errorhandler(werkzeug.exceptions.NotFound)
def handle_bad_request(error):
    return jsonify({"route": False,
                    "error-type": "NotFound",
                    "text": str(error)}), 404
