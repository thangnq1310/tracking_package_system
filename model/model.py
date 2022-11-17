from peewee import *
from model.base import BaseModel

class Customers(BaseModel):
    id = IntegerField(primary_key=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField()

    class Meta:
        table_name = 'customers'