from peewee import *
import dotenv
import os
import peewee
from playhouse.shortcuts import ReconnectMixin

dotenv.load_dotenv()

database = os.getenv('DB', 'inventory')
db_host = os.getenv('HOST', 'localhost')
db_port = os.getenv('PORT', 3311)
user = os.getenv('USER_NAME', 'root')
password = os.getenv('PW', 'debezium')

class RetryDB(ReconnectMixin, MySQLDatabase):
    pass


db = RetryDB(database, user=user, password=password, host=db_host, port=int(db_port), charset='utf8')


class BaseModel(Model):
    class Meta:
        database = db