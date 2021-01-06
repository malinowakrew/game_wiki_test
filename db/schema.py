"""
schema.py
==========================
Module
"""
from mongoengine import *

from datetime import datetime
from passlib.hash import argon2


class Question(Document):
    """
        About Question schema
        This is schema of mongodb document

    """
    question_text = StringField(required=True)
    answer_a = IntField(required=True)
    answer_b = IntField(required=True)
    answer_c = IntField(required=True)
    correct = IntField(required=True)
    user_answer = StringField()

    def user_view(self):
        return {"question": self.question_text,
               "A": self.answer_a,
               "B": self.answer_b,
               "C": self.answer_c}

    def ranking_view(self):
        return {
            "question-text": self.question_text,
            "year": self.correct
        }

class Game(Document):
    """
        About Question schema
        This is schema of mongodb document

    """
    date = DateTimeField(required=True, default=datetime.utcnow)
    points = IntField(required=True)
    questions = ListField(ReferenceField(Question))

    def ranking_view(self):
        return {
            "nic": ""
        }#TODO:make this game ranking view accurate
role = ("admin", "user")


class Account(Document):
    """
        About Question schema
        This is schema of mongodb document

    """
    role = StringField(required=True, hoices=role)
    name = StringField(required=True, unique=True)
    email = StringField(required=True)  # regex="^@gmail.com"
    score = ListField(ReferenceField(Game))
    __passwd = StringField(required=True, max_length=200)

    @property
    def passwd(self):
        return self.__passwd

    @passwd.setter
    def passwd(self, passwd):
        self.__passwd = argon2.using(salt_size=8).hash(passwd)


# def test():
#     disconnect()
#     connect('wiki-test', host='mongodb://localhost/wiki-test')
#     user = Account(role="user", name="test", email="adam1@gmail.com")
#     user.passwd = "test"
#     user.save()
#     return user
#
# def test_cos():
#     user = Account.objects(name="Ed")[0]
#     user.passwd = "12345"
#     user.save()
