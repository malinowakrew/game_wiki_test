"""
schema.py
==========================
Module
"""
from mongoengine import CASCADE, Document, StringField, IntField, ListField, DateTimeField, ReferenceField

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
    questions = ListField(ReferenceField(Question, reverse_delete_rule=CASCADE))

    def ranking_view(self):
        return {
            "nic": ""
        }#TODO:make this game ranking view accurate


role = ("verify-user", "user")


class Account(Document):
    """
        About Question schema
        This is schema of mongodb document

    """
    role = StringField(required=True, hoices=role)
    name = StringField(required=True, unique=True)
    email = StringField(unique=False)  # regex="^@gmail.com"
    score = ListField(ReferenceField(Game, reverse_delete_rule=CASCADE))
    __passwd = StringField(required=True, max_length=200)

    @property
    def passwd(self):
        return self.__passwd

    @passwd.setter
    def passwd(self, passwd):
        self.__passwd = argon2.using(salt_size=8).hash(passwd)

    def user_view(self):
        return {"name": self.name,
                "role": self.role}
