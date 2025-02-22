from app.views.image_reord_api import (
    upload_image, get_metadata, get_slice,
    analyze_image, get_statistics, serve_media
)

def register_routes(app):
    app.add_url_rule("/upload", view_func=upload_image, methods=["POST"])
    app.add_url_rule("/metadata/<reduest_id>", view_func=get_metadata, methods=["GET"])
    app.add_url_rule("/slice/<reduest_id>", view_func=get_slice, methods=["GET"])
    app.add_url_rule("/analyze/<reduest_id>", view_func=analyze_image, methods=["POST"])
    app.add_url_rule("/statistics/<reduest_id>", view_func=get_statistics, methods=["GET"])
    app.add_url_rule("/media/<path:filename>", view_func=serve_media, methods=["GET"])