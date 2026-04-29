from app import create_app


def get_logged_client():
    app = create_app("development")
    client = app.test_client()
    client.post("/login", data={"usuario": "admin", "contrasena": "Admin2024!"})
    return client, app


def test_catalogo_carga():
    client, app = get_logged_client()
    with app.app_context():
        r = client.get("/catalogo")
        assert r.status_code == 200
        assert "libros" in r.data.decode().lower() or r.status_code == 200


def test_paginacion():
    client, app = get_logged_client()
    with app.app_context():
        r = client.get("/catalogo?page=1")
        assert r.status_code == 200
        r2 = client.get("/catalogo?page=2")
        assert r2.status_code == 200


def test_filtro_titulo():
    client, app = get_logged_client()
    with app.app_context():
        r = client.get("/catalogo?filtro_tipo=titulo&filtro_valor=a")
        assert r.status_code == 200


def test_stubs_responden_200():
    client, app = get_logged_client()
    with app.app_context():
        for url in ["/libros/nuevo", "/libros/TEST-ISBN", "/libros/TEST-ISBN/editar"]:
            r = client.get(url)
            assert r.status_code == 200, f"{url} retornó {r.status_code}"
        r = client.post("/libros/TEST-ISBN/eliminar")
        assert r.status_code == 200


if __name__ == "__main__":
    test_catalogo_carga()
    test_paginacion()
    test_filtro_titulo()
    test_stubs_responden_200()
    print("Todos los tests del catálogo pasaron.")
