from app.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    usuario = db.Column(db.String(50), primary_key=True)
    contrasena = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)

    def __repr__(self):
        return f"<Usuario usuario={self.usuario!r} nombre={self.nombre!r}>"
