import logging
import math
from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.libro import EstadoLibro, Libro

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


def obtener_por_isbn(isbn: str) -> "Libro | None":
    """Devuelve el Libro o None. No lanza por 'no encontrado'."""
    return db.session.get(Libro, isbn)


def existe_isbn(isbn: str) -> bool:
    """True si ya existe un libro con ese ISBN."""
    return db.session.get(Libro, isbn) is not None


def validar_libro(datos: dict, isbn_actual: str | None = None) -> dict[str, str]:
    """
    Devuelve dict {campo: mensaje}. Vacío si todo ok.
    isbn_actual=None significa alta. Con valor significa edición.
    """
    errores: dict[str, str] = {}
    año_actual = date.today().year

    for campo in ("titulo", "autor", "editorial", "sinopsis", "ubicacion", "categoria"):
        if not str(datos.get(campo, "")).strip():
            errores[campo] = "Datos requeridos"

    isbn = str(datos.get("ISBN", "")).strip()
    if isbn_actual is None:
        if not isbn:
            errores["ISBN"] = "Datos requeridos"
        elif existe_isbn(isbn):
            errores["ISBN"] = "Libro ya existe"

    raw_anio = str(datos.get("anio_publicacion", "")).strip()
    if not raw_anio:
        errores["anio_publicacion"] = "Datos requeridos"
    else:
        try:
            anio = int(raw_anio)
            if anio < 1000 or anio > año_actual:
                errores["anio_publicacion"] = f"Debe estar entre 1000 y {año_actual}"
        except (ValueError, TypeError):
            errores["anio_publicacion"] = "Datos requeridos"

    raw_paginas = str(datos.get("numero_paginas", "")).strip()
    if not raw_paginas:
        errores["numero_paginas"] = "Datos requeridos"
    else:
        try:
            paginas = int(raw_paginas)
            if paginas <= 0:
                errores["numero_paginas"] = "Debe ser mayor a 0"
        except (ValueError, TypeError):
            errores["numero_paginas"] = "Datos requeridos"

    raw_precio = str(datos.get("precio", "")).strip()
    if not raw_precio:
        errores["precio"] = "Datos requeridos"
    else:
        try:
            precio = float(raw_precio)
            if precio < 0:
                errores["precio"] = "No puede ser negativo"
        except (ValueError, TypeError):
            errores["precio"] = "Datos requeridos"

    raw_copias = str(datos.get("numero_copias", "")).strip()
    if not raw_copias:
        errores["numero_copias"] = "Datos requeridos"
    else:
        try:
            copias = int(raw_copias)
            if copias < 0:
                errores["numero_copias"] = "No puede ser negativo"
        except (ValueError, TypeError):
            errores["numero_copias"] = "Datos requeridos"

    if isbn_actual is not None:
        raw_estado = str(datos.get("estado", "")).strip()
        if raw_estado not in {e.value for e in EstadoLibro}:
            errores["estado"] = "Datos requeridos"

    return errores


def crear(datos: dict) -> "tuple[Libro | None, dict[str, str]]":
    """
    Devuelve (libro, errores).
    Si errores no vacío: libro es None, nada persistido.
    Si errores vacío: libro es el objeto persistido.
    """
    errores = validar_libro(datos, isbn_actual=None)
    if errores:
        return None, errores

    try:
        libro = Libro(
            ISBN=str(datos["ISBN"]).strip(),
            titulo=str(datos["titulo"]).strip(),
            autor=str(datos["autor"]).strip(),
            editorial=str(datos["editorial"]).strip(),
            sinopsis=str(datos["sinopsis"]).strip(),
            anio_publicacion=int(datos["anio_publicacion"]),
            numero_paginas=int(datos["numero_paginas"]),
            precio=float(datos["precio"]),
            ubicacion=str(datos["ubicacion"]).strip(),
            numero_copias=int(datos["numero_copias"]),
            categoria=str(datos["categoria"]).strip(),
            estado=EstadoLibro.disponible,
        )
        db.session.add(libro)
        db.session.commit()
        return libro, {}
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Error al crear libro")
        return None, {"_general": "Error de BD"}


def actualizar(isbn: str, datos: dict) -> "tuple[Libro | None, dict[str, str]]":
    """
    Mismo contrato que crear.
    No permite cambiar ISBN aunque venga en datos.
    """
    libro = db.session.get(Libro, isbn)
    if libro is None:
        return None, {"_general": "Libro no encontrado"}

    errores = validar_libro(datos, isbn_actual=isbn)
    if errores:
        return None, errores

    try:
        libro.titulo = str(datos["titulo"]).strip()
        libro.autor = str(datos["autor"]).strip()
        libro.editorial = str(datos["editorial"]).strip()
        libro.sinopsis = str(datos["sinopsis"]).strip()
        libro.anio_publicacion = int(datos["anio_publicacion"])
        libro.numero_paginas = int(datos["numero_paginas"])
        libro.precio = float(datos["precio"])
        libro.ubicacion = str(datos["ubicacion"]).strip()
        libro.numero_copias = int(datos["numero_copias"])
        libro.categoria = str(datos["categoria"]).strip()
        libro.estado = EstadoLibro(str(datos["estado"]).strip())
        db.session.commit()
        return libro, {}
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Error al actualizar libro")
        return None, {"_general": "Error de BD"}


def eliminar(isbn: str) -> bool:
    """True si lo eliminó. False si no existía o si SQLAlchemyError."""
    libro = db.session.get(Libro, isbn)
    if libro is None:
        return False
    try:
        db.session.delete(libro)
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Error al eliminar libro")
        return False
