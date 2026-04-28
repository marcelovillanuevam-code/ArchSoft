import enum

from app.extensions import db


class EstadoLibro(enum.Enum):
    disponible = "disponible"
    prestado = "prestado"
    mantenimiento = "mantenimiento"
    perdido = "perdido"


class Libro(db.Model):
    __tablename__ = "libros"

    ISBN = db.Column(db.String(20), primary_key=True)
    titulo = db.Column(db.String(255), nullable=False, index=True)
    autor = db.Column(db.String(255), nullable=False, index=True)
    editorial = db.Column(db.String(150), nullable=True)
    sinopsis = db.Column(db.Text, nullable=True)
    anio_publicacion = db.Column(db.SmallInteger, nullable=True)
    numero_paginas = db.Column(db.Integer, nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=True)
    ubicacion = db.Column(db.String(100), nullable=True)
    numero_copias = db.Column(db.Integer, nullable=True)
    categoria = db.Column(db.String(100), nullable=True)
    fecha_registro = db.Column(db.DateTime, server_default=db.func.now())
    estado = db.Column(db.Enum(EstadoLibro), default=EstadoLibro.disponible)

    def __repr__(self):
        return (
            f"<Libro ISBN={self.ISBN!r} titulo={self.titulo!r} "
            f"autor={self.autor!r} estado={self.estado}>"
        )
