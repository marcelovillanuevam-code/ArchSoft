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
    def wrapper(*args, **kwargs):
        if not session.get("usuario"):
            return redirect(url_for("auth.login", expired=1))
        return f(*args, **kwargs)
    return wrapper


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si ya esta logeado, mandarlo al catalogo
    if session.get("usuario"):
        return redirect(url_for("libro.catalogo"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")

        if not usuario or not contrasena:
            return render_template("auth/login.html", error="Favor de llenar todos los campos")

        user = autenticar(usuario, contrasena)
        if user is not None:
            session["usuario"] = user.usuario
            session["nombre"] = user.nombre
            session.permanent = False
            return redirect(url_for("libro.catalogo"))

        return render_template("auth/login.html", error="Usuario o contraseña incorrectos")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
