# OLP300 — Catálogo de Libros
## Evidencia 10 — Arquitectura de Software, UDEM

---

### Equipo

| Nombre | Matrícula | Capa | Rama |
|---|---|---|---|
| Sergio Ayala | — | Modelo / BD | `feat/db-sergio` |
| Ernesto Vega | — | Controlador | `feat/back-ernesto` |
| Santiago Pongutá | — | Vista | `feat/front-santiago` |
| Marcelo Villanueva | — | Integración / DevOps | `feat/integracion-marcelo` |

---

### Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Framework web | Flask 3.x |
| Templates | Jinja2 (server-side) |
| CSS | Tailwind CSS vía CDN |
| Base de datos | MariaDB 10.x |
| ORM | SQLAlchemy 2.x + Flask-SQLAlchemy |
| Hash contraseñas | Flask-Bcrypt (cost factor 12) |
| Sesiones | `flask.session` + `SECRET_KEY` desde `.env` |
| Variables de entorno | python-dotenv |
| Servidor de desarrollo | `flask run` / `python run.py` |

---

### Requisitos previos

**Con Docker (recomendado):**
- Docker Desktop

**Sin Docker:**
- Python 3.11
- MariaDB 10.x o superior
- pip

---

### Setup del ambiente

#### Opción A — Docker (recomendado, cero configuración manual)

> Solo necesitas Docker Desktop instalado.

1. **Clonar el repositorio**

   ```bash
   git clone <url-del-repo>
   cd olp300
   ```

2. **Configurar las variables de entorno**

   ```bash
   cp .env.example .env
   ```

   Editar `.env` y ajustar `SECRET_KEY`. Las credenciales de BD ya están preconfiguradas para el entorno Docker.

3. **Levantar los contenedores**

   ```bash
   docker compose up --build
   ```

   Docker levanta MariaDB, espera a que esté lista y luego inicia Flask. Al primer arranque, la app crea las tablas y carga los 15 libros y 3 usuarios de prueba automáticamente.

   La aplicación queda disponible en `http://localhost:5000`.

4. **Detener**

   ```bash
   docker compose down          # detiene contenedores, conserva datos
   docker compose down -v       # detiene contenedores y borra la BD
   ```

---

#### Opción B — Local sin Docker

1. **Clonar el repositorio**

   ```bash
   git clone <url-del-repo>
   cd olp300
   ```

2. **Crear y activar el entorno virtual**

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Crear la base de datos en MariaDB**

   Ejecutar como usuario `root` (única vez):

   ```bash
   mysql -u root -p < setup_db.sql
   ```

5. **Configurar las variables de entorno**

   ```bash
   cp .env.example .env
   ```

   Editar `.env` y ajustar `DB_PASSWORD` y `SECRET_KEY`.

6. **Iniciar el servidor**

   ```bash
   python run.py
   ```

   Al primer arranque la app crea las tablas e inserta automáticamente los usuarios y los 15 libros de prueba.

   La aplicación queda disponible en `http://localhost:5000`.

---

### Credenciales de prueba

| Usuario | Contraseña | Nombre completo |
|---|---|---|
| `admin` | `Admin2024!` | Administrador |
| `ernesto` | `Ernesto2024!` | Ernesto Vega |
| `santiago` | `Santiago2024!` | Santiago Pongutá |

> Las contraseñas se almacenan como hash bcrypt (cost factor 12). Nunca se guardan en texto plano.

---

### Estructura del proyecto

```
olp300/
├── app/
│   ├── __init__.py          # App factory: create_app()
│   ├── config.py            # Carga .env, clases Config
│   ├── extensions.py        # Instancias compartidas: db, bcrypt
│   │
│   ├── models/              # MODELO — definición de tablas ORM
│   │   ├── usuario.py       # Tabla `usuarios`
│   │   └── libro.py         # Tabla `libros`
│   │
│   ├── services/            # MODELO — lógica de negocio
│   │   ├── auth_service.py  # Autenticación con bcrypt
│   │   └── libro_service.py # Paginación y filtros del catálogo
│   │
│   ├── controllers/         # CONTROLADOR — Blueprints Flask
│   │   ├── auth_controller.py   # Rutas /login, /logout + decorador login_required
│   │   └── libro_controller.py  # Rutas /catalogo y stubs de libros
│   │
│   ├── templates/           # VISTA — Jinja2
│   │   ├── base.html            # Layout base con Tailwind
│   │   ├── auth/
│   │   │   └── login.html       # Pantalla de inicio de sesión
│   │   └── libros/
│   │       ├── catalogo.html    # Catálogo con paginación y filtros
│   │       └── stub.html        # Pantalla genérica "en construcción"
│   │
│   └── static/
│       └── css/
│
├── tests/
│   ├── test_auth_e2e.py     # Tests E2E de autenticación
│   └── test_catalogo_e2e.py # Tests E2E del catálogo
│
├── .env.example             # Plantilla de variables de entorno
├── .dockerignore            # Archivos excluidos de la imagen Docker
├── Dockerfile               # Imagen de la aplicación Flask
├── docker-compose.yml       # Orquestación Flask + MariaDB
├── requirements.txt         # Dependencias Python
├── run.py                   # Punto de entrada del servidor
├── schema.sql               # DDL — creación de tablas (referencia)
├── seed.sql                 # Datos de prueba (referencia, ya no necesario ejecutar)
└── setup_db.sql             # Creación de BD y usuario MariaDB (solo opción sin Docker)
```

---

### Patrón MVC — cómo está implementado

La aplicación sigue el patrón Modelo-Vista-Controlador de forma estricta, con fronteras explícitas entre capas.

**Modelo** (`app/models/`, `app/services/`): define las tablas ORM (`Usuario`, `Libro`) y encapsula toda la lógica de negocio en los servicios (`auth_service`, `libro_service`). Ningún archivo de esta capa importa Flask, conoce HTTP ni toca `request` o `session`.

**Vista** (`app/templates/`): plantillas Jinja2 que reciben un diccionario de contexto del controlador y solo se encargan de renderizar HTML. No contienen lógica de negocio ni acceden directamente a la base de datos.

**Controlador** (`app/controllers/`): Blueprints Flask que reciben la petición HTTP, delegan el procesamiento al servicio correspondiente, agregan al contexto los datos de sesión necesarios y devuelven la respuesta renderizando el template adecuado. No contienen queries SQL directas.

---

### Rutas implementadas

| URL | Método | Descripción | Estado |
|---|---|---|---|
| `/` | GET | Redirige a `/catalogo` si hay sesión activa, o a `/login` | Implementado |
| `/login` | GET | Muestra el formulario de inicio de sesión | Implementado |
| `/login` | POST | Valida credenciales y crea sesión | Implementado |
| `/logout` | GET | Destruye la sesión y redirige a `/login` | Implementado |
| `/catalogo` | GET | Lista libros con paginación (10 por página) y filtro por título, autor o ISBN | Implementado |
| `/libros/nuevo` | GET | Formulario de alta de libro | Stub |
| `/libros/<isbn>` | GET | Detalles de un libro | Stub |
| `/libros/<isbn>/editar` | GET | Formulario de edición de libro | Stub |
| `/libros/<isbn>/eliminar` | POST | Elimina un libro | Stub |

> Las rutas marcadas como **Stub** responden HTTP 200 y muestran una pantalla "en construcción". Se implementarán en el Proyecto Final.
