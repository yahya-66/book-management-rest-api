from database import Buku, db

def semua_buku():
    return Buku.query.all()

def cari_buku(id):
    return Buku.query.get(id)

def tambah_buku(judul, penulis):
    buku = Buku(
        judul=judul,
        penulis=penulis
    )
    db.session.add(buku)
    db.session.commit()
    return buku

def hapus_buku(id):
    buku = Buku.query.get(id)
    if buku is None:
        return None
    db.session.delete(buku)
    db.session.commit()
    return buku

def update_buku(id, judul, penulis):
    buku = Buku.query.get(id)
    if buku is None:
        return None
    buku.judul = judul
    buku.penulis = penulis
    db.session.commit()
    return buku

def daftar_buku(page=1, limit=5, sort="id", order="asc", judul=None, penulis=None):
    query = Buku.query
    if judul:
        query = query.filter(
            Buku.judul.like(f"%{judul}%")
        )
    if penulis:
        query = query.filter(
            Buku.penulis.like(f"%{penulis}%")
        )
    total = query.count()
    if hasattr(Buku, sort):
        kolom = getattr(Buku, sort)
        if order == "desc":
            query = query.order_by(kolom.desc())
        else:
            query = query.order_by(kolom.asc())
            semua_buku = query.offset(
                (page - 1) * limit
            ).limit(limit).all()
            return semua_buku, total
