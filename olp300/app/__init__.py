from flask import Flask, redirect, session, url_for

from app.config import config_by_name
from app.extensions import bcrypt, db


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    bcrypt.init_app(app)

    # Import modelos para que db.create_all() los registre
    with app.app_context():
        from app.models.libro import Libro  # noqa: F401
        from app.models.usuario import Usuario  # noqa: F401
        db.create_all()

    from app.controllers.auth_controller import auth_bp
    from app.controllers.libro_controller import libro_bp

    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(libro_bp, url_prefix="/")

    @app.route("/")
    def index():
        if session.get("usuario"):
            return redirect(url_for("libro.catalogo"))
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
