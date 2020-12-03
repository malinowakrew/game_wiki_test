from flask import Flask
from flask import Flask, jsonify, abort, request, make_response, render_template
from db.db import *

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@app.route('/')
def hello_world():
    user = test()
    print(user.role)
    print(user.name)
    return "Nic"

@app.route('/task', methods=['GET'])
def get_tasks():
    return jsonify(tasks[0])


if __name__ == '__main__':
    app.run()

