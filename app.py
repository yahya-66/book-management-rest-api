from flask import Flask, jsonify, request
from database import db
from models.buku import buku_bp
from models.user import User
from models.user import user_bp
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
load_dotenv()
from flasgger import Swagger
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)
Swagger(app)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
jwt = JWTManager(app)
app.config["SQLALCHEMY_DATABASE_URI"] = (
	f"postgresql+psycopg2://"
	f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
	f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
app.register_blueprint(buku_bp)
app.register_blueprint(user_bp)


@app.route("/")
def home():
	return jsonify({
		"status": "success",
		"message": "REST API",
		"version": "1.0"
	})

if __name__== "__main__":
	with app.app_context():
		db.create_all()
	app.run(debug=True)
