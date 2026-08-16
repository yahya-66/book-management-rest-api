from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Buku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(100), nullable=False)
    penulis = db.Column(db.String(100), nullable=False)
    def to_dict(self):
        return{
            "id": self.id,
            "judul": self.judul,
            "penulis": self.penulis
        }