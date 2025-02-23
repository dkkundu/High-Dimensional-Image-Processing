import pytest
import io
from app import create_app, db
from app.models.image_process import ImageMetadata

@pytest.fixture
def app():
    app, _ = create_app()
    app.config.update({
        "TESTING": True,
    })

    with app.app_context():
        db.create_all()
        # Insert test data
        test_image = ImageMetadata(
            request_id="request_id",
            filename="test.tif",
            dimensions="512x512",
            file_path="media/test_request_id_test.tif",
            upload_time="2025-02-23 22:53:10"
        )
        db.session.add(test_image)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Home" in response.data

def test_upload_image(client):
    response = client.post('/upload', data={'file': (io.BytesIO(b"fake image data"), 'test.tif')})
    assert response.status_code == 202
    assert b"request_id" in response.data

def test_get_metadata(client):
    response = client.get('/metadata/request_id')
    assert response.status_code == 200
    assert b"metadata" in response.data

def test_get_slice(client):
    response = client.get('/slice/request_id')
    assert response.status_code == 200
    assert b"slice" in response.data

def test_analyze_image(client):
    response = client.post('/analyze/request_id', json={'components': 3})
    assert response.status_code == 200
    assert b"analysis" in response.data

def test_get_statistics(client):
    response = client.get('/statistics/request_id')
    assert response.status_code == 200
    assert b"statistics" in response.data
