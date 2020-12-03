from mongoengine import *
from datetime import datetime

class Game(Document):
    date = DateTimeField(required=True, default=datetime.utcnow)
    points = IntField(required=True)


role = ("admin", "user")
class Account(Document):
    role = StringField(required=True, hoices=role)
    name = StringField(required=True)
    email = StringField(required=True, regex="@gmail.com", unique=True)
    score = ListField(Game(), default=list)


def test():
    user = Account(role="user", name="Ed", email="ed@gmail.com")
    return user