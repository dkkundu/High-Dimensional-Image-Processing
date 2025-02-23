import os
from dotenv import load_dotenv
from app import create_app

PORT_SET = int(os.getenv('PORT', 5000))
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT_SET)
