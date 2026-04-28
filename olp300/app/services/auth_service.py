import logging

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import bcrypt, db
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)


def autenticar(usuario: str, password: str) -> "Usuario | None":
    try:
        obj = db.session.get(Usuario, usuario)
        if obj is None:
            return None
        if not bcrypt.check_password_hash(obj.contrasena, password):
            return None
        return obj
    except SQLAlchemyError:
        logger.exception("Error de BD al autenticar usuario '%s'", usuario)
        return None
