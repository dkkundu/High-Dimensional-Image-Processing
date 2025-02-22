# core.py - Image processing core
import numpy as np
import tifffile
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from skimage.filters import threshold_otsu

class ImageProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = tifffile.memmap(file_path)
        self.shape = self.image.shape
        self.ndim = self.image.ndim
        
    def get_slice(self, time=None, z=None, channel=None):
        slice_idx = [slice(None)] * self.ndim
        dims = {0: 'Time', 1: 'Z', 2: 'Channel', 3: 'Y', 4: 'X'}
        
        if time is not None:
            slice_idx[0] = time
        if z is not None:
            slice_idx[1] = z
        if channel is not None:
            slice_idx[2] = channel
            
        return self.image[tuple(slice_idx)]
    
    def calculate_statistics(self):
        stats = []
        for ch in range(self.shape[2]):
            channel_data = self.image[:, :, ch, :, :].ravel()
            stats.append({
                "channel": ch,
                "mean": float(np.mean(channel_data)),
                "std": float(np.std(channel_data)),
                "min": float(np.min(channel_data)),
                "max": float(np.max(channel_data))
            })
        return stats
    
    def perform_pca(self, n_components=3):
        original_shape = self.image.shape
        data = self.image.reshape(-1, original_shape[2])
        pca = PCA(n_components=n_components)
        reduced = pca.fit_transform(data)
        return reduced.reshape(original_shape[0], original_shape[1], n_components, original_shape[3], original_shape[4])
    
    def segment_channel(self, channel, method='otsu'):
        channel_data = self.image[:, :, channel, :, :]
        if method == 'otsu':
            threshold = threshold_otsu(channel_data)
            return (channel_data > threshold).astype(np.uint8)
        elif method == 'kmeans':
            kmeans = KMeans(n_clusters=2)
            flattened = channel_data.reshape(-1, 1)
            return kmeans.fit_predict(flattened).reshape(channel_data.shape)
        return None

# database.py - Database models
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ImageMetadata(Base):
    __tablename__ = 'image_metadata'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    dimensions = Column(String)
    file_path = Column(String)
    upload_time = Column(String)

class ImageStatistics(Base):
    __tablename__ = 'image_statistics'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer)
    channel = Column(Integer)
    mean = Column(Float)
    std = Column(Float)
    min = Column(Float)
    max = Column(Float)

class PCAResults(Base):
    __tablename__ = 'pca_results'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer)
    components = Column(Integer)
    explained_variance = Column(JSON)
    file_path = Column(String)

engine = create_engine('sqlite:///./image_data.db')
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# main.py - FastAPI application
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import uuid
import os

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.filename.endswith(('.tif', '.tiff')):
        raise HTTPException(400, "Invalid file format")
    
    file_uuid = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_uuid + ".tif")
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    processor = ImageProcessor(file_path)
    metadata = {
        "filename": file.filename,
        "dimensions": str(processor.shape),
        "file_path": file_path,
        "upload_time": datetime.now().isoformat()
    }
    
    db = SessionLocal()
    db.add(ImageMetadata(**metadata))
    db.commit()
    db.close()
    
    return {"id": file_uuid, "message": "File uploaded successfully"}

@app.get("/metadata/{image_id}")
def get_metadata(image_id: str):
    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(image_id)).first()
    db.close()
    
    if not image:
        raise HTTPException(404, "Image not found")
    
    return {
        "dimensions": image.dimensions,
        "upload_time": image.upload_time,
        "filename": image.filename
    }

@app.get("/slice/{image_id}")
def get_slice(image_id: str, time: int = None, z: int = None, channel: int = None):
    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(image_id)).first()
    db.close()
    
    if not image:
        raise HTTPException(404, "Image not found")
    
    processor = ImageProcessor(image.file_path)
    try:
        slice_data = processor.get_slice(time, z, channel)
    except IndexError:
        raise HTTPException(400, "Invalid slice parameters")
    
    output_path = os.path.join(UPLOAD_DIR, f"slice_{image_id}.tif")
    tifffile.imwrite(output_path, slice_data)
    return FileResponse(output_path)

@app.post("/analyze/{image_id}")
async def analyze_image(image_id: str, components: int = 3):
    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(image_id)).first()
    db.close()
    
    if not image:
        raise HTTPException(404, "Image not found")
    
    processor = ImageProcessor(image.file_path)
    pca_result = processor.perform_pca(components)
    
    output_path = os.path.join(UPLOAD_DIR, f"pca_{image_id}.tif")
    tifffile.imwrite(output_path, pca_result)
    
    db = SessionLocal()
    db.add(PCAResults(
        image_id=image.id,
        components=components,
        file_path=output_path,
        explained_variance=[]
    ))
    db.commit()
    db.close()
    
    return FileResponse(output_path)

@app.get("/statistics/{image_id}")
def get_statistics(image_id: str):
    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(image_id)).first()
    db.close()
    
    if not image:
        raise HTTPException(404, "Image not found")
    
    processor = ImageProcessor(image.file_path)
    stats = processor.calculate_statistics()
    
    db = SessionLocal()
    for stat in stats:
        db.add(ImageStatistics(
            image_id=image.id,
            channel=stat['channel'],
            mean=stat['mean'],
            std=stat['std'],
            min=stat['min'],
            max=stat['max']
        ))
    db.commit()
    db.close()
    
    return JSONResponse(content=stats)

# tasks.py - Celery tasks
from celery import Celery

celery = Celery(
    __name__,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery.task
def async_pca(image_path, components):
    processor = ImageProcessor(image_path)
    return processor.perform_pca(components)

# Use in main.py with:
# task = async_pca.delay(image.file_path, components)