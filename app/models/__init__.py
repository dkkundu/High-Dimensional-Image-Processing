from sqlalchemy.orm import sessionmaker
from .base import Base, engine  # Updated import
from app.models.image_process import ImageMetadata, ImageStatistics, PCAResults  # Import models to register them
from app.models.post import Post  # Import the Post model

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    ImageMetadata, ImageStatistics, PCAResults , Post  # Import models to register them
    Base.metadata.create_all(bind=engine)  # Create all tables
