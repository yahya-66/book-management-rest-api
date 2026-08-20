from flask import Blueprint, jsonify, request
from database import Buku, db
from services.buku_service import (
    cari_buku,
    tambah_buku as tambah_buku_service,
    hapus_buku as hapus_buku_service,
    update_buku as update_buku_service,
    daftar_buku
)
from flask_jwt_extended import jwt_required, get_jwt
buku_bp = Blueprint("buku", __name__)

def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Akses ditolak. Hanya admin"}), 403
    return None

def validasi_buku(data):
    if not data:
        return {
            "status": "error",
            "message": "Body JSON tidak boleh kosong"
        }, 400
    if "judul" not in data or "penulis" not in data:
        return {
            "status": "error",
            "message": "Judul dan Penulis wajib diisi."
        }, 400
    if not data["judul"].strip() or not data["penulis"].strip():
        return {
            "status": "error",
            "message": "Judul dan penulis tidak boleh kosong."
        }, 400
    if len(data["judul"].strip()) < 3:
        return {
            "status": "error",
            "message": "Nama judul minimal 3 karakter"
        }, 400
    if len(data["penulis"].strip()) < 3:
        return {
            "status": "error",
            "message": "Nama penulis minimal 3 karakter"
        }, 400
    return None

"""
Menampilkan daftar buku
---
tags:
  - Buku
responses:
  200:
    description: Berhasil mengambil data buku
"""
@buku_bp.route("/buku", methods=["GET"])
@jwt_required()
def get_buku():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    judul = request.args.get("judul")
    penulis = request.args.get("penulis")
    semua_buku, total = daftar_buku(
        page=page,
        limit=limit,
        sort=sort,
        order=order,
        judul=judul,
        penulis=penulis
    )
    return jsonify({
        "page": page,
        "limit": limit,
        "total": total,
        "data": [buku.to_dict() for buku in semua_buku]
    }), 200

"""
Mengambil detail buku berdasarkan ID
---
tags:
  - Buku
parameters:
  - name: id
    in: path
    type: integer
    required: true
resposes:
  200:
    description: Berhasil mengambil data buku
  400:
    description: Buku tidak ditemukan
"""
@buku_bp.route("/buku/<int:id>", methods=["GET"])
@jwt_required()
def get_buku_by_id(id):
    id_buku = cari_buku(id)
    if id_buku is None: 
        return jsonify({
            "status": "error",
            "message": "Buku tidak ditemukan"
        }),404
    return jsonify(id_buku.to_dict()), 200

"""
Mengubah data buku
---
tags:
  - Buku
parameters:
  - name: id
    in: path
    type: integer
    requireed: true
  - in: body
    name: body
    required: true
    schema:
      properties:
         judul:
           type: string
         penulis: 
           type: string
responses:
   200:
     description: Buku berhasil diupdate
   404:
     description: Buku tidak ditemukan
"""
@buku_bp.route("/buku/<int:id>", methods=["PUT"])
@jwt_required()
def update_buku(id):
    cek = admin_required()
    if cek:
        return cek
    data = request.get_json()
    if not data:
        return jsonify({
            "status": "error",
            "message": "Data wajib diisi"
        }), 400
    if "judul" not in data or "penulis" not in data:
        return jsonify({
            "status": "error",
            "message": "Judul dan penulis wajib diisi"
        }), 400
    if not data["judul"] or not data["penulis"]:
        return jsonify({
            "status": "error",
            "message": "Judul dan penulis tidak boleh kosong"
        }), 400
    buku = update_buku_service(
        id,
        data["judul"],
        data["penulis"]
    )
    if buku is None:
        return  jsonify({
            "status": "error",
            "message": "Buku tidak ditemukan"
        }), 404
    return jsonify(buku.to_dict())

"""
Menghapus buku
---
tags:
  - Buku
parameters:
  - name: id
    in: path
    type: integer
    required: true
responses:
  200:
    description: Buku berhasil dihapus
  404:
    description: Buku tidak ditemukan
"""
@buku_bp.route("/buku/<int:id>", methods=["DELETE"])
@jwt_required()
def hapus_buku(id):
    cek = admin_required()
    if cek:
        return cek
    buku = hapus_buku_service(id)
    if buku is None:
        return jsonify({
            "status": "error",
            "message": "Buku tidak ditemukan"
        }), 404
    return jsonify({
        "status": "success",
        "message": "Buku berhasil dihapus",
        "data": buku.to_dict()
    }), 200

"""
Menambahkan buku baru
---
tags:
  - Buku
security: 
  - Bearer: []
parameters:
  - in: body
    name: body
    required: true
    schema: 
      properties:
         judul:
           type: string
         penulis:
           type: string
responses:
  201:
    descrption: Buku berhasil ditambahkan
  400:
    description: Data tidak valid
"""
@buku_bp.route("/buku", methods=["POST"])
@jwt_required()
def tambah_buku():
    cek = admin_required()
    if cek:
        return cek
    data = request.get_json()
    error = validasi_buku(data)
    if error:
        return jsonify(error[0]), error[1]
    buku_baru = tambah_buku_service(
        data["judul"],
        data["penulis"]
    )
    return jsonify(buku_baru.to_dict()), 201
