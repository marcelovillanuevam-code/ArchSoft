# CLAUDE.md — OLP300 Catálogo de Libros

Guía operativa para Claude cuando trabaje en este repositorio.
Léelo completo antes de proponer o escribir cualquier código.
Si una instrucción del usuario contradice este archivo, detente y pregunta — no asumas.

---

## 1. Qué es este proyecto

Aplicación web para administrar el catálogo de libros de una biblioteca universitaria.
Trabajo académico — Evidencia 10, materia Arquitectura de Software, UDEM.
El profesor evalúa explícitamente que el patrón **MVC esté visible y respetado**.

### Alcance de esta entrega (Evidencia 10)
- Pantalla de Autenticación (`/login`) — funcional contra la tabla `usuarios`.
- Pantalla de Catálogo de Libros (`/catalogo`) — paginación + filtro por Título / Autor / ISBN.
- Stubs visuales para Nuevo Libro, Detalles, Editar, Eliminar (rutas que no se rompen, templates "en construcción").

### Fuera de alcance ahora — NO implementar sin que el usuario lo pida explícitamente
- Formularios completos de Nuevo Libro, Detalles, Editar, Eliminar.
- Recuperación de contraseña.
- Roles de usuario (admin vs. consulta).

---

## 2. Stack — no cambiar sin discusión explícita

| Componente | Decisión |
|---|---|
| Lenguaje | Python 3.11 |
| Framework web | **Flask** |
| Templates | **Jinja2** vía Flask — server-side. NO React, NO SPA |
| CSS | Tailwind vía CDN (esta entrega) |
| Base de datos | **MariaDB** |
| ORM | **SQLAlchemy 2.x** con `flask-sqlalchemy` |
| Hash contraseñas | **flask-bcrypt** (cost factor 12) |
| Sesiones | `flask.session` + `SECRET_KEY` desde `.env` |
| Variables de entorno | `python-dotenv` |
| Servidor dev | `flask run` (built-in) |

### Por qué Flask y no FastAPI
Flask no impone estructura — eso obliga al equipo a ser explícito con las capas MVC.
Sin Pydantic, sin Uvicorn, sin itsdangerous separado. Menos piezas = menos puntos de falla en demo.

---

## 3. La regla de oro: MVC estricto

La materia evalúa el patrón. Una violación es un bug aunque el código "funcione".

### Contratos por capa

| Capa | Carpeta | Puede | No puede |
|---|---|---|---|
| **Modelo** | `app/models/`, `app/services/` | Definir tablas ORM, ejecutar queries, aplicar reglas de negocio | Importar `flask`, `request`, `session`, `render_template` ni saber que existe HTTP |
| **Vista** | `app/templates/` | Recibir un `dict` de contexto y renderizar HTML | Hacer queries, importar SQLAlchemy, contener lógica de negocio |
| **Controlador** | `app/controllers/` | Recibir request HTTP, llamar al service, elegir template, devolver response | Tener queries SQL directas ni lógica de negocio más allá de orquestar |

### Señales de MVC roto — rechaza estos patrones

```python
# ❌ Query directa en el controlador
@libro_bp.route('/catalogo')
def catalogo():
    libros = db.session.query(Libro).all()  # pertenece al service
    ...

# ✅ Correcto
@libro_bp.route('/catalogo')
def catalogo():
    resultado = libro_service.listar(page=1)
    return render_template('libros/catalogo.html', **resultado)
```

```python
# ❌ Model tocando la sesión de Flask
from flask import session
class AuthService:
    def autenticar(self, u, p):
        session['user'] = u  # esto va en el controlador
```

```jinja2
{# ❌ Lógica de negocio en template #}
{% if libro.precio > 500 and libro.copias < 2 %}

{# ✅ El service manda el resultado calculado #}
{% if libro.alerta_stock %}
```

---

## 4. Estructura de carpetas (autoridad)

```
olp300/
├── app/
│   ├── __init__.py              # Flask app factory: create_app()
│   ├── config.py                # Carga .env, clases Config
│   ├── extensions.py            # db = SQLAlchemy(), bcrypt = Bcrypt()
│   ├── models/                  # MODELO — ORM
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   └── libro.py
│   ├── services/                # MODELO — lógica de negocio
│   │   ├── auth_service.py
│   │   └── libro_service.py
│   ├── controllers/             # CONTROLADOR — Blueprints Flask
│   │   ├── auth_controller.py
│   │   └── libro_controller.py
│   ├── templates/               # VISTA — Jinja2
│   │   ├── base.html
│   │   ├── auth/
│   │   │   └── login.html
│   │   └── libros/
│   │       ├── catalogo.html
│   │       └── stub.html
│   └── static/
│       └── css/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

Si no sabes dónde va un archivo, probablemente va en `services/`. No crear carpetas nuevas sin discutirlo.

---

## 5. Contratos entre capas

Estos contratos los acuerda el equipo el día 1. Cambiarlos requiere notificar a todos.

### auth_service.autenticar

```python
def autenticar(usuario: str, password: str) -> "Usuario | None":
    """
    Devuelve el objeto Usuario si las credenciales son válidas.
    Devuelve None si el usuario no existe O si la contraseña es incorrecta.
    NUNCA distingue entre los dos casos hacia afuera (previene enumeración de usuarios).
    No toca flask.session — eso es trabajo del controlador.
    """
```

### libro_service.listar

```python
def listar(page: int, filtro_tipo: str | None, filtro_valor: str | None) -> dict:
    """
    Devuelve:
    {
        "libros":      [Libro, ...],
        "total":       int,       # total de registros que coinciden
        "pagina":      int,       # página actual (1-based)
        "paginas":     int,       # total de páginas
        "por_pagina":  int        # constante: 10
    }
    filtro_tipo acepta: "titulo" | "autor" | "isbn" | None
    """
```

### Contexto de catalogo.html — acuerdo Santiago ↔ Ernesto

```python
# libro_controller.py manda exactamente esto:
context = {
    "libros":       [...],   # lista de objetos Libro
    "total":        int,
    "pagina":       int,
    "paginas":      int,
    "filtro_tipo":  str,     # "titulo" | "autor" | "isbn" | ""
    "filtro_valor": str,     # valor del filtro | ""
    "usuario":      str,     # nombre del usuario en sesión
}
```

Santiago puede trabajar con este dict como mock desde el día 1 sin esperar a Ernesto.

### Stubs — comportamiento mínimo obligatorio

Cada stub responde HTTP 200 y renderiza `libros/stub.html` con `{"pantalla": "Nombre"}`.

| Ruta | Pantalla |
|---|---|
| `GET /libros/nuevo` | Nuevo Libro |
| `GET /libros/<isbn>` | Detalles del Libro |
| `GET /libros/<isbn>/editar` | Editar Libro |
| `POST /libros/<isbn>/eliminar` | Eliminar Libro |

---

## 6. Base de datos

- Motor: MariaDB. Connection string: `mysql+pymysql://user:pass@host/db`.
- Contraseñas: bcrypt hash en `contrasena` — nunca texto plano.
- Queries: siempre vía ORM, nunca f-strings con input del usuario.
- Migraciones: `db.create_all()` en `create_app()` es suficiente para esta entrega.

### .env.example

```
FLASK_ENV=development
SECRET_KEY=cambia-esto-antes-de-demo
DB_USER=olp300_user
DB_PASSWORD=cambia-esto
DB_HOST=localhost
DB_PORT=3306
DB_NAME=olp300
```

Nunca versionar el `.env` real. Solo `.env.example`.

---

## 7. Seguridad — checklist antes de marcar una feature como lista

- [ ] Contraseñas hasheadas con bcrypt (abrir la tabla y verificar).
- [ ] `SECRET_KEY` viene de `.env`, no hardcodeada.
- [ ] `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = "Lax"`.
- [ ] Mensaje de error de login es genérico — nunca revelar qué falló.
- [ ] Todas las rutas excepto `/login` redirigen si no hay sesión activa.
- [ ] Queries usan ORM (parametrizadas).

---

## 8. División de responsabilidades

| Integrante | Capa | Archivos |
|---|---|---|
| Sergio Ayala | Modelo / BD | `models/usuario.py`, `models/libro.py`, `services/auth_service.py`, `services/libro_service.py`, `schema.sql`, `seed.sql` |
| Ernesto Vega | Controlador | `controllers/auth_controller.py`, `controllers/libro_controller.py`, `app/__init__.py`, `extensions.py` |
| Santiago Pongutá | Vista | `templates/base.html`, `templates/auth/login.html`, `templates/libros/catalogo.html`, `templates/libros/stub.html` |
| Marcelo Villanueva | Integración / DevOps | `config.py`, `.env.example`, `requirements.txt`, `README.md`, flujo Auth E2E, coordinación de PRs |

Ramas: `feat/db-sergio`, `feat/back-ernesto`, `feat/front-santiago`, `feat/integracion-marcelo`.
Merge a `main` solo vía Pull Request aprobado por Marcelo.

---

## 9. Lo que NO hacer

- No instalar librerías sin agregarlas a `requirements.txt`.
- No crear tablas adicionales — solo `libros` y `usuarios`.
- No implementar nada del Proyecto Final sin pedido explícito.
- No poner lógica de negocio en templates ni queries en controladores.
- No hardcodear credenciales ni commitear `.env`.
- No merges directos a `main` sin PR.
