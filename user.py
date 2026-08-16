from database import db
from flask import Blueprint, request, jsonify, current_app
from flask import current_app
from werkzeug.utils import secure_filename
import os
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt
user_bp = Blueprint("user", __name__)

ALLOWED_EXTENSTIONS = {"png", "jpg", "jpeg"}
def allowed_file(filename):
    return (
        "." in filename and 
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSTIONS
    )

class User(db.Model):
    __tablename__= "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), default="user")
    def to_dict(self):
        return{
            "id": self.id,
            "username": self.username,
            "role": self.role
        }
    
@user_bp.route("/register", methods=["POST"])
def register():
    """
    Register User
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      201:
        description: Register berhasil
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"message": "Username dan password wajib diisi"}),400
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username sudah digunakan"}),400
    hashed_password = generate_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        role="user"
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()),201

@user_bp.route("/login", methods=["POST"])
def login():
    """
    Login User
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            username:
              type: string
            password:
              type: string
    reaponses:
      201:
        description: Login berhasil
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "Username tidak ditenukan"}), 404
    if not check_password_hash(user.password, password):
        return jsonify({"message": "Password salah"}),  401
    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )
    return jsonify ({
        "message": "Loginn berhasil",
        "token": token
    })
    
@user_bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"message": "File tidak ditemukan"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "Tidak ada file yang dipilih"}), 400
    if not allowed_file(file.filename):
        return jsonify({"message": "Format file tidak didukung"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"], filename
    )
    file.save(filepath)
    return jsonify({
        "message": "Upload berhasil",
        "filename": filename
    }), 201

@user_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    cek = admin_required()
    if cek:
        return cek
    users = User.query.all()
    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "role": user.role 
        }
        for user in users
    ])