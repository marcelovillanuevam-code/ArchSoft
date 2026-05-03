from flask import Blueprint, abort, redirect, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.controllers.auth_controller import login_required
from app.services.libro_service import (
    actualizar,
    crear,
    eliminar,
    listar,
    obtener_por_isbn,
)

libro_bp = Blueprint("libro", __name__)


def _libro_a_dict(libro) -> dict:
    return {
        "ISBN": libro.ISBN,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "editorial": libro.editorial,
        "sinopsis": libro.sinopsis,
        "anio_publicacion": libro.anio_publicacion,
        "numero_paginas": libro.numero_paginas,
        "precio": libro.precio,
        "ubicacion": libro.ubicacion,
        "numero_copias": libro.numero_copias,
        "categoria": libro.categoria,
        "estado": libro.estado.value if libro.estado else "disponible",
    }


@libro_bp.route("/catalogo")
@login_required
def catalogo():
    page = request.args.get("page", 1, type=int)
    filtro_tipo = request.args.get("filtro_tipo", "").strip() or None
    filtro_valor = request.args.get("filtro_valor", "").strip() or None

    try:
        resultado = listar(page, filtro_tipo, filtro_valor)
    except SQLAlchemyError:
        abort(503)

    context = {
        **resultado,
        "usuario": session.get("nombre", ""),
        "filtro_tipo": filtro_tipo or "",
        "filtro_valor": filtro_valor or "",
        "page_anterior": resultado["pagina"] - 1,
        "page_siguiente": resultado["pagina"] + 1,
    }
    return render_template("libros/catalogo.html", **context)


@libro_bp.route("/libros/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    if request.method == "POST":
        datos = request.form.to_dict()
        libro_obj, errores = crear(datos)
        if errores:
            return render_template("libros/form.html", modo="nuevo", libro=datos, errores=errores)
        return redirect(url_for("libro.catalogo"))
    return render_template("libros/form.html", modo="nuevo", libro=None, errores={})


@libro_bp.route("/libros/<isbn>")
@login_required
def detalle(isbn):
    libro = obtener_por_isbn(isbn)
    if libro is None:
        abort(404)
    return render_template("libros/detalles.html", libro=libro)


@libro_bp.route("/libros/<isbn>/editar", methods=["GET", "POST"])
@login_required
def editar(isbn):
    if request.method == "POST":
        datos = request.form.to_dict()
        libro_obj, errores = actualizar(isbn, datos)
        if errores:
            return render_template(
                "libros/form.html",
                modo="editar",
                libro={**datos, "ISBN": isbn},
                errores=errores,
            )
        return redirect(url_for("libro.catalogo"))
    libro = obtener_por_isbn(isbn)
    if libro is None:
        abort(404)
    return render_template("libros/form.html", modo="editar", libro=_libro_a_dict(libro), errores={})


@libro_bp.route("/libros/<isbn>/eliminar", methods=["POST"])
@login_required
def eliminar_libro(isbn):
    eliminar(isbn)
    return redirect(url_for("libro.catalogo"))
