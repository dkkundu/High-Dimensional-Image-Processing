from sqlalchemy import Column, Integer, String, Text
from .base import Base  # Updated import

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
