import uuid
import os
import tifffile
from flask import app, request, jsonify, send_file, abort
from datetime import datetime
from .image_processor import ImageProcessor
from app.models import SessionLocal
from app.models.image_process import ImageMetadata, ImageStatistics, PCAResults  # Import models to register them
from app.tasks import (
    upload_image_task,
)



def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if not file.filename.endswith(('.tif', '.tiff')):
        return jsonify({"error": "Invalid file format"}), 400

    reduest_id = str(uuid.uuid4())
    file_path = os.path.join("media", f"{reduest_id}_{file.filename}")
    file.save(file_path)

    task = upload_image_task.delay(file_path, reduest_id)

    return jsonify(
        {
            "status": "201",
            "task_id": task.id, 
            "reduest_id": reduest_id,
            "message": "File upload request successfully processed"
            }
        ), 202

def get_metadata(reduest_id):
    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(reduest_id)).first()
    db.close()
    
    if not image:
        return {"error": "Image not found"}, 404
    
    metadata_response = {
        "dimensions": image.dimensions,
        "upload_time": image.upload_time,
        "filename": image.filename
    }
    
    try:
        with tifffile.TiffFile(image.file_path) as tif:
            metadata_response["tiff_metadata"] = str(tif.pages[0].tags)
            
            if tif.ome_metadata:
                metadata_response["ome_metadata"] = tif.ome_metadata
            
            extra_metadata = tif.imagej_metadata or tif.micromanager_metadata or tif.scn_metadata
            if extra_metadata:
                metadata_response["extra_metadata"] = extra_metadata
            
            metadata_response["pages_metadata"] = {
                f"Page {i}": str(page.tags) for i, page in enumerate(tif.pages)
            }
    except Exception as e:
        metadata_response["error"] = str(e)
    
    return jsonify({
        "status": "200",
        "messages": "Metadata successfully retrieved",
        "reduest_id": reduest_id,
        "data": metadata_response
    }), 200

def get_slice(reduest_id):
    time = request.args.get('time', type=int)
    z = request.args.get('z', type=int)
    channel = request.args.get('channel', type=int)

    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(reduest_id)).first()
    db.close()
    
    if not image:
        return jsonify({
            "status": "404",
            "messages": "Image not found",
            "reduest_id": reduest_id,
            "error": ""
        }), 404
    
    processor = ImageProcessor(image.file_path)
    
    try:
        slice_data = processor.get_slice(time, z, channel)
    except IndexError as e:
        return jsonify({
            "status": "404",
            "messages": str(e),
            "reduest_id": reduest_id,
            "error": ""
        }), 404
    
    output_filename = f"slice_{reduest_id}.tif"
    output_path = os.path.join("media", output_filename)
    tifffile.imwrite(output_path, slice_data)
    
    file_url = request.url_root + 'media/' + output_filename
    
    return jsonify({
        "status": "200",
        "messages": "Slice successfully retrieved",
        "reduest_id": reduest_id,
        "data": {"url": file_url}
    }), 200

def analyze_image(request_id):
    if request.content_type != 'application/json':
        return jsonify({"error": "Unsupported Media Type"}), 415

    data = request.get_json()
    components = data.get('components', 3)

    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(request_id)).first()
    db.close()
    
    if not image:
        return {"error": "Image not found"}
    
    processor = ImageProcessor(image.file_path)
    pca_result = processor.perform_pca(components)
    
    output_path = os.path.join("media", f"pca_{request_id}.tif")
    tifffile.imwrite(output_path, pca_result)
    
    db = SessionLocal()
    pca_record = PCAResults(
        image_id=image.id,
        components=components,
        file_path=output_path,
        explained_variance=[]
    )
    db.add(pca_record)
    db.commit()
    db.refresh(pca_record)
    db.close()
    
    file_url = request.url_root + 'media/' + os.path.basename(output_path)

    return jsonify(
    {
        "status": "201",
        "request_id": request_id,
        "message": "File upload request successfully processed",
        "data": {
            "image_id": image.id,
            "pca_result": list(pca_result.shape),
            "components": pca_record.components,
            "explained_variance": pca_record.explained_variance,
            "file_url": file_url
        }
    }
    ), 200

def get_statistics(request_id):
    db = SessionLocal()
    image = db.query(ImageMetadata).filter(ImageMetadata.file_path.contains(request_id)).first()
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
