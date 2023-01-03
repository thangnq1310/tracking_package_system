from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dotenv
import os

dotenv.load_dotenv()

database = os.getenv('DB', 'logistic')
db_host = os.getenv('HOST', 'mysql_kafka')
db_port = os.getenv('PORT', 3306)
user = os.getenv('USER_NAME', 'root')
password = os.getenv('PW', 'It235711')

engine = create_engine(
    f'mysql+pymysql://{user}:{password}@{db_host}:{db_port}/{database}'
)
Session = sessionmaker(bind=engine)
session = Session()
