"""
Flask API: app instance and entry point. Run the server with:

    python app.py

Serves at http://localhost:5000 by default.
"""
from flask import Flask
from flask_cors import CORS

from blueprints.images_bp import images_bp

app = Flask(__name__)
CORS(app)  # CORS on all routes and responses; handles OPTIONS preflight
app.register_blueprint(images_bp, url_prefix="/api")


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=False)
