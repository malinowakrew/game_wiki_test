from mongoengine import connect, disconnect
disconnect()
connect('wiki', host='mongodb://localhost/wiki')