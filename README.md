# High-Dimensional-Image-Processing System

## Prerequisites
- Python 3.x
- Virtualenv
- Redis (for Celery)

## Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/dkkundu/High-Dimensional-Image-Processing.git
    cd High-Dimensional-Image-Processing
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the environment variables:**
    Copy the example `.env` file to the root directory:
    ```sh
    cp example/dot_env .env
    ```

5. **Initialize the database:**
    ```sh
    ./migrate_db.sh
    ```

## Running the Application

1. **Start the Flask application:**
    ```sh
    python run.py
    ```

2. **Access the application:**
    Open your web browser and go to `http://localhost:8001`.

## Running Celery Worker

1. **Start the Celery worker:**
    ```sh
    celery -A app.celery_app.celery worker --loglevel=info
    ```

## Additional Commands

- **Run database migrations:**
    ```sh
    flask db migrate
    flask db upgrade
    ```

- **Create a new admin user:**
    ```sh
    flask create_admin
    ```

- **Run tests:**
    ```sh
    pytest
    ```

## Postman Collection

You can download the Postman collection for this project from the following path:
```
/mnt/backup/Office/python test/example/High-Dimensional Image Processing.postman_collection.json
```

Alternatively, you can download it from the GitHub repository:
[High-Dimensional Image Processing.postman_collection.json](https://github.com/dkkundu/High-Dimensional-Image-Processing/blob/main/example/High-Dimensional%20Image%20Processing.postman_collection.json)

## Note

Make sure Redis is installed on your system.