import logging
import math

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.libro import Libro

logger = logging.getLogger(__name__)

POR_PAGINA = 10


def listar(page: int, filtro_tipo: str | None, filtro_valor: str | None) -> dict:
    if page < 1:
        page = 1

    try:
        query = db.session.query(Libro)

        # Aplicar filtro si hay tipo y valor
        if filtro_tipo and filtro_valor:
            patron = f"%{filtro_valor}%"
            if filtro_tipo == "titulo":
                query = query.filter(Libro.titulo.ilike(patron))
            elif filtro_tipo == "autor":
                query = query.filter(Libro.autor.ilike(patron))
            elif filtro_tipo == "isbn":
                query = query.filter(Libro.ISBN.ilike(patron))

        total = query.count()
        paginas = max(math.ceil(total / POR_PAGINA), 1)
        libros = query.offset((page - 1) * POR_PAGINA).limit(POR_PAGINA).all()

        return {
            "libros": libros,
            "total": total,
            "pagina": page,
            "paginas": paginas,
            "por_pagina": POR_PAGINA,
            "hay_anterior": page > 1,
            "hay_siguiente": page < paginas,
        }
    except SQLAlchemyError:
        logger.exception("Error al listar libros")
        return {
            "libros": [],
            "total": 0,
            "pagina": page,
            "paginas": 1,
            "por_pagina": POR_PAGINA,
            "hay_anterior": False,
            "hay_siguiente": False,
        }
