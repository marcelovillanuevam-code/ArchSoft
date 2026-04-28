from functools import wraps

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services.auth_service import autenticar

auth_bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("usuario"):
            return redirect(url_for("auth.login", expired=1))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route("/login", methods=["GET"])
def login():
    if session.get("usuario"):
        return redirect("/catalogo")
    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def login_post():
    try:
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")

        user = autenticar(usuario, contrasena)

        if user is not None:
            session["usuario"] = user.usuario
            session["nombre"] = user.nombre
            session.permanent = False
            return redirect("/catalogo")

        return render_template(
            "auth/login.html",
            error="Usuario o contrase\u00f1a incorrectos",
        )

    except Exception:
        return render_template(
            "auth/login.html",
            error="Ocurri\u00f3 un error. Intenta de nuevo.",
        )


@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")
