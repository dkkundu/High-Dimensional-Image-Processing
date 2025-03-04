from app.views.image_reord_api import (
    upload_image, get_metadata, get_slice,
    analyze_image, get_statistics
)

def register_routes(app):
    app.add_url_rule("/upload", view_func=upload_image, methods=["POST"])
    app.add_url_rule("/metadata/<request_id>", view_func=get_metadata, methods=["GET"])
    app.add_url_rule("/slice/<request_id>", view_func=get_slice, methods=["GET"])
    app.add_url_rule("/analyze/<request_id>", view_func=analyze_image, methods=["POST"])
    app.add_url_rule("/statistics/<request_id>", view_func=get_statistics, methods=["GET"])
