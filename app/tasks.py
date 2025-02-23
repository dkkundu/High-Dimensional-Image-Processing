from app.celery_app import celery
from datetime import datetime
from app.views.image_processor import ImageProcessor
from app.models import SessionLocal
from app.models.image_process import ImageMetadata, ImageStatistics, PCAResults
from app.views.image_processor import ImageProcessor
import tifffile
import os

UPLOAD_DIR = "uploads"

@celery.task
def upload_image_task(file_path, request_id):
    processor = ImageProcessor(file_path)
    metadata = {
        "request_id": request_id,
        "filename": os.path.basename(file_path),
        "dimensions": str(processor.shape),
        "file_path": file_path,
        "upload_time": datetime.now().isoformat()
    }
    
    db = SessionLocal()
    db.add(ImageMetadata(**metadata))
    db.commit()
    db.close()
    

@celery.task
def analyze_image_task(image_id, components):
    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(image_id)).first()
    db.close()
    
    if not image:
        return {"error": "Image not found"}
    
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
    
    return {"file_path": output_path}

@celery.task
def get_statistics_task(image_id):
    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(image_id)).first()
    db.close()
    
    if not image:
        return {"error": "Image not found"}
    
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
    
    return stats

@celery.task
def example_task():
    print("This is an example task.")
