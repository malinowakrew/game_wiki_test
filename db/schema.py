from mongoengine import *
from mongoengine import connect

from datetime import datetime
from passlib.hash import argon2


class Question(Document):
    question_text = StringField(required=True)
    answer_a = IntField(required=True)
    answer_b = IntField(required=True)
    answer_c = IntField(required=True)
    correct = IntField(required=True)
    user_answer = StringField()

    def user_view(self):
        return{"question": self.question_text,
               "A": self.answer_a,
               "B": self.answer_b,
               "C": self.answer_c}


class Game(Document):
    date = DateTimeField(required=True, default=datetime.utcnow)
    points = IntField(required=True)
    questions = ListField(ReferenceField(Question))


role = ("admin", "user")


class Account(Document):
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

"""
def test():
    connect('wiki', host='mongodb://localhost/wiki')
    user = Account(role="user", name="Adas", email="adam@gmail.com")
    user.passwd = "aleks"
    user.save()
    return user
"""