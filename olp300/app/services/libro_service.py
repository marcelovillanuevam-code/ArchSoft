# Capa Servicio — lógica de negocio para operaciones sobre libros
# STUB temporal — Sergio debe reemplazar con la implementación real.
# Contrato: ver CLAUDE.md sección 5 y ARCHITECTURE.md sección 4.4.

import logging
import math

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.libro import Libro

logger = logging.getLogger(__name__)

POR_PAGINA = 10


def listar(page: int, filtro_tipo: str | None, filtro_valor: str | None) -> dict:
    """
    Devuelve:
    {
        "libros":       [Libro, ...],
        "total":        int,
        "pagina":       int,
        "paginas":      int,
        "por_pagina":   int,
        "hay_anterior": bool,
        "hay_siguiente": bool,
    }
    filtro_tipo acepta: "titulo" | "autor" | "isbn" | None
    """
    try:
        if page < 1:
            page = 1

        query = db.session.query(Libro)

        if filtro_tipo and filtro_valor:
            filtro_campo = {
                "titulo": Libro.titulo,
                "autor": Libro.autor,
                "isbn": Libro.ISBN,
            }.get(filtro_tipo)

            if filtro_campo is not None:
                query = query.filter(filtro_campo.ilike(f"%{filtro_valor}%"))

        total = query.count()
        paginas = max(math.ceil(total / POR_PAGINA), 1)

        libros = (
            query
            .offset((page - 1) * POR_PAGINA)
            .limit(POR_PAGINA)
            .all()
        )

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
        logger.exception("Error de BD al listar libros")
        return {
            "libros": [],
            "total": 0,
            "pagina": 1,
            "paginas": 1,
            "por_pagina": POR_PAGINA,
            "hay_anterior": False,
            "hay_siguiente": False,
        }
