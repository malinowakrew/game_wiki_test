from mongoengine import *
from mongoengine import connect

from datetime import datetime
from passlib.hash import argon2

class Game(Document):
    date = DateTimeField(required=True, default=datetime.utcnow)
    points = IntField(required=True)


role = ("admin", "user")
class Account(Document):
    role = StringField(required=True, hoices=role)
    name = StringField(required=True)
    email = StringField(required=True, unique=True) #regex="^@gmail.com"
    score = ListField(Game(), default=list)
    __passwd = StringField(required=True, max_length=200)

    @property
    def passwd(self):
        return self.__passwd

    @passwd.setter
    def passwd(self, passwd):
        self.__passwd = argon2.using(salt_size=8).hash(passwd)

    """
    @property
    def name(self):
        return self.name

    @passwd.setter
    def passwd(self, name):
        self.name = name
    """

def test():
    connect('wiki', host='mongodb://localhost/wiki')
    user = Account(role="user", name="Adas", email="adam@gmail.com")
    user.passwd = "aleks"
    user.save()
    return user