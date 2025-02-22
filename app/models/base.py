from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from config import Config

Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
