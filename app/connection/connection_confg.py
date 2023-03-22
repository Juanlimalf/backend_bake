import sqlalchemy
from sqlalchemy.orm import sessionmaker
from decouple import config

user = config("user")
password = config("password")
host = config("host")
port = config("port")
database = config("database")


class DBconnection:

    def __init__(self):
        self.__connection__string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        self.__engine = self.__creat__engine()
        self.session = None

    def __creat__engine(self):
        engine = sqlalchemy.create_engine(self.__connection__string)
        return engine

    def get_engine(self):
        return self.__engine

    def __enter__(self):
        session_make = sessionmaker(bind=self.__engine)
        self.session = session_make()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def create_tables(self):
        from app.models.schemas import Base
        Base.metadata.create_all(self.__engine)
        