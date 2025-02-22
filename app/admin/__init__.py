from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import scoped_session
from app.models import SessionLocal  # Corrected import statement
from app.models.image_process import ImageMetadata, ImageStatistics, PCAResults

def setup_admin(app):
    admin = Admin(app, name="Image Database Admin", template_mode="bootstrap4")
    
    # Database session
    db_session = scoped_session(SessionLocal)

    # Register models with Flask-Admin
    admin.add_view(ModelView(ImageMetadata, db_session, category="Models"))
    admin.add_view(ModelView(ImageStatistics, db_session, category="Models"))
    admin.add_view(ModelView(PCAResults, db_session, category="Models"))
