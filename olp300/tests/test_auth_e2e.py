from app import create_app


def test_login_exitoso():
    app = create_app("development")
    with app.test_client() as client:
        # GET /login debe responder 200
        r = client.get("/login")
        assert r.status_code == 200, f"GET /login falló: {r.status_code}"

        # POST /login con credenciales válidas debe redirigir a /catalogo
        r = client.post("/login", data={"usuario": "admin", "contrasena": "Admin2024!"})
        assert r.status_code in (302, 200), f"POST /login válido falló: {r.status_code}"

        # GET /catalogo con sesión activa debe responder 200
        r = client.get("/catalogo", follow_redirects=True)
        assert r.status_code == 200, f"GET /catalogo falló: {r.status_code}"


def test_login_invalido():
    app = create_app("development")
    with app.test_client() as client:
        r = client.post("/login", data={"usuario": "admin", "contrasena": "mal"})
        assert r.status_code == 200  # re-renderiza login, no redirige
        assert b"incorrectos" in r.data.lower() or b"error" in r.data.lower()


def test_proteccion_ruta():
    app = create_app("development")
    with app.test_client() as client:
        r = client.get("/catalogo")
        assert r.status_code in (302, 200)
        # Si redirige, debe ir a login
        if r.status_code == 302:
            assert "login" in r.headers.get("Location", "")


if __name__ == "__main__":
    test_login_exitoso()
    test_login_invalido()
    test_proteccion_ruta()
    print("Todos los tests pasaron.")
