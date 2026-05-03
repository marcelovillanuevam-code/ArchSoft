from flask import Blueprint, abort, render_template, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.controllers.auth_controller import login_required
from app.services.libro_service import listar

libro_bp = Blueprint("libro", __name__)


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


# --- Stubs: se implementan en el Proyecto Final ---

@libro_bp.route("/libros/nuevo")
@login_required
def nuevo():
    return render_template("libros/stub.html", pantalla="Nuevo Libro")


@libro_bp.route("/libros/<isbn>")
@login_required
def detalle(isbn):
    return render_template("libros/stub.html", pantalla="Detalles del Libro")


@libro_bp.route("/libros/<isbn>/editar")
@login_required
def editar(isbn):
    return render_template("libros/stub.html", pantalla="Editar Libro")


@libro_bp.route("/libros/<isbn>/eliminar", methods=["POST"])
@login_required
def eliminar(isbn):
    return render_template("libros/stub.html", pantalla="Eliminar Libro")
