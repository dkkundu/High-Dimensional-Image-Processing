from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from .base import Base  # Updated import

class ImageMetadata(Base):
    __tablename__ = 'image_metadata'
    id = Column(Integer, primary_key=True)
    request_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    dimensions = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_time = Column(String, nullable=False)

class ImageStatistics(Base):
    __tablename__ = 'image_statistics'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, nullable=False)
    channel = Column(Integer, nullable=False)
    mean = Column(Float, nullable=False)
    std = Column(Float, nullable=False)
    min = Column(Float, nullable=False)
    max = Column(Float, nullable=False)

class PCAResults(Base):
    __tablename__ = 'pca_results'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, nullable=False)
    components = Column(Integer, nullable=False)
    explained_variance = Column(JSON, nullable=False)
    file_path = Column(String, nullable=False)
