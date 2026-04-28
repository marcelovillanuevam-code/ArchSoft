# PROMPTS.md — OLP300 Catálogo de Libros
# Prompts para Claude Code — ejecución secuencial

Cada prompt es autosuficiente: incluye el contexto necesario para que Claude Code
lo ejecute sin haber leído CLAUDE.md ni ARCHITECTURE.md previamente.

Ejecuta los prompts en el orden numerado. No saltes pasos — cada uno asume
que los archivos del paso anterior ya existen en disco.

Antes de ejecutar cualquier prompt: abre Claude Code en la raíz del repo `olp300/`.

---

## FASE 0 — Setup del ambiente y estructura del proyecto

### PROMPT 0.1 — Inicializar repositorio y estructura de carpetas

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Tu única tarea en este prompt es crear la estructura de carpetas y archivos vacíos.
No escribas código Python todavía — solo crea los archivos con contenido mínimo
(un comentario o docstring que indique qué va ahí).

Crea exactamente esta estructura desde la raíz del proyecto:

olp300/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   └── libro.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── libro_service.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   └── libro_controller.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   └── login.html
│   │   └── libros/
│   │       ├── catalogo.html
│   │       └── stub.html
│   └── static/
│       └── css/
│           └── .gitkeep
├── tests/
│   └── __init__.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

Contenido mínimo requerido:
- requirements.txt: debe estar vacío por ahora, solo un comentario # dependencias
- .gitignore: incluir .env, __pycache__, *.pyc, .venv, *.egg-info
- .env.example: exactamente esto:
  FLASK_ENV=development
  SECRET_KEY=cambia-esto-antes-de-demo
  DB_USER=olp300_user
  DB_PASSWORD=cambia-esto
  DB_HOST=localhost
  DB_PORT=3306
  DB_NAME=olp300
- Todos los .py: solo un comentario de una línea indicando qué capa MVC es este archivo
- Todos los .html: solo <!DOCTYPE html><html><body><!-- placeholder --></body></html>

No inicialices git. No instales nada. Solo crea los archivos.
```

---

### PROMPT 0.2 — Escribir requirements.txt e instalar dependencias

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
El proyecto usa Python 3.11, Flask, MariaDB y bcrypt.

Reemplaza el contenido de requirements.txt con exactamente estas dependencias
(sin rangos de versión — usar == para reproducibilidad):

Flask==3.0.3
flask-sqlalchemy==3.1.1
flask-bcrypt==1.0.1
python-dotenv==1.0.1
PyMySQL==1.1.1
cryptography==42.0.8

Después ejecuta en terminal:
  python -m venv .venv
  source .venv/bin/activate   (en Windows: .venv\Scripts\activate)
  pip install -r requirements.txt

Verifica que la instalación fue exitosa ejecutando:
  python -c "import flask; import flask_sqlalchemy; import flask_bcrypt; print('OK')"

Si algún import falla, muéstrame el error completo sin intentar arreglarlo solo.
```

---

### PROMPT 0.3 — Setup de MariaDB: crear base de datos y usuario

```
   Eres el asistente de un proyecto académico Flask llamado OLP300.
   Necesito crear la base de datos en MariaDB local.

   Genera un archivo llamado setup_db.sql en la raíz del proyecto con estos comandos:

   CREATE DATABASE IF NOT EXISTS olp300 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER IF NOT EXISTS 'olp300_user'@'localhost' IDENTIFIED BY 'olp300_pass_dev';
   GRANT ALL PRIVILEGES ON olp300.* TO 'olp300_user'@'localhost';
   FLUSH PRIVILEGES;

   Después muéstrame el comando exacto para ejecutarlo:
   mysql -u root -p < setup_db.sql

   No ejecutes nada tú mismo. Solo genera el archivo y muéstrame el comando.
   El archivo setup_db.sql NO debe commitearse — agrégalo a .gitignore.
```

---

### PROMPT 0.4 — Crear schema.sql y seed.sql

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Tu tarea es generar los archivos SQL de estructura y datos de prueba.
Estás en la rama feat/db-sergio.

Genera schema.sql en la raíz del proyecto con:

1. DROP TABLE IF EXISTS para libros y usuarios (en ese orden para evitar FK issues).
2. CREATE TABLE usuarios:
   - usuario VARCHAR(50) PRIMARY KEY
   - contrasena VARCHAR(255) NOT NULL  (guardará hash bcrypt)
   - nombre VARCHAR(50) NOT NULL UNIQUE
   - email VARCHAR(150) NOT NULL UNIQUE

3. CREATE TABLE libros:
   - ISBN VARCHAR(20) PRIMARY KEY
   - titulo VARCHAR(255) NOT NULL  (con INDEX)
   - autor VARCHAR(255) NOT NULL   (con INDEX)
   - editorial VARCHAR(150)
   - sinopsis TEXT
   - anio_publicacion SMALLINT
   - numero_paginas INT
   - precio DECIMAL(10,2)
   - ubicacion VARCHAR(100)
   - numero_copias INT
   - categoria VARCHAR(100)
   - fecha_registro DATETIME DEFAULT NOW()
   - estado ENUM('disponible','prestado','mantenimiento','perdido') DEFAULT 'disponible'

Genera seed.sql en la raíz del proyecto con:

1. 3 usuarios con contraseñas en texto plano temporales claramente marcadas con un
   comentario -- HASH PENDIENTE: esta contraseña debe reemplazarse con hash bcrypt
   antes de la demo. Las contraseñas en texto plano son solo para que el equipo sepa
   qué credenciales probar. Ejemplo: usuario='admin', contrasena='REEMPLAZAR_CON_HASH',
   nombre='Administrador', email='admin@biblioteca.udem.mx'

2. 15 libros con datos realistas y variados: diferentes autores, categorías
   (Ficción, Ciencia, Historia, Filosofía, Tecnología), estados variados
   (no todos 'disponible'), precios entre 200 y 800, entre 150 y 800 páginas.
   ISBNs con formato real: 978-X-XX-XXXXXX-X

Incluye un comentario al inicio de seed.sql explicando que las contraseñas
deben hashearse con bcrypt antes de insertar en producción/demo.
```

---

### PROMPT 0.5 — Generar script Python para hashear contraseñas del seed

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
El archivo seed.sql tiene contraseñas en texto plano marcadas como REEMPLAZAR_CON_HASH.
Estás en la rama feat/db-sergio.

Crea un script llamado hash_seed_passwords.py en la raíz del proyecto.
El script debe:

1. Importar flask_bcrypt (bcrypt standalone, sin necesitar la app Flask).
2. Definir un dict con las contraseñas en texto plano de los 3 usuarios del seed:
   passwords = {
       "admin": "Admin2024!",
       "usuario1": "User2024!",
       "usuario2": "User2024!"
   }
3. Para cada entrada, generar el hash bcrypt con cost factor 12:
   bcrypt.generate_password_hash(pwd, rounds=12).decode('utf-8')
4. Imprimir en pantalla los UPDATE SQL listos para copiar y pegar:
   UPDATE usuarios SET contrasena='<hash>' WHERE usuario='<usuario>';

El script NO modifica seed.sql automáticamente — solo imprime los SQL.
El usuario los copia manualmente a seed.sql.

Agrega hash_seed_passwords.py a .gitignore — no se commitea.

Al final del script imprime un recordatorio:
"RECUERDA: Copia los UPDATE anteriores a seed.sql antes de ejecutarlo en la BD."
```

---

## FASE 1 — Capa Modelo (rama: feat/db)

### PROMPT 1.1 — Implementar extensions.py

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa Modelo. Rama activa: feat/db-sergio.

Contexto de arquitectura:
- El proyecto usa el patrón MVC estricto.
- extensions.py existe para evitar imports circulares: crea las instancias
  de db y bcrypt SIN inicializarlas con la app todavía (patrón Application Factory).
- Ningún archivo en models/ ni services/ puede importar flask, request,
  session ni render_template.

Implementa app/extensions.py con:

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

Eso es todo. No agregues nada más. Este archivo debe ser exactamente eso.
Verifica que el archivo no importa flask directamente.
```

---

### PROMPT 1.2 — Implementar models/usuario.py

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa Modelo. Rama activa: feat/db-sergio.

Archivos que ya existen y puedes importar:
- app/extensions.py exporta: db (SQLAlchemy instance), bcrypt (Bcrypt instance)

Regla crítica de arquitectura: este archivo NO puede importar flask, request,
session, render_template ni ningún símbolo de Flask. Solo SQLAlchemy.

Implementa app/models/usuario.py con la clase Usuario:

- __tablename__ = "usuarios"
- usuario: String(50), primary_key=True
- contrasena: String(255), nullable=False  (guardará el hash bcrypt)
- nombre: String(50), nullable=False, unique=True
- email: String(150), nullable=False, unique=True

Agrega un método __repr__ útil para debugging que NO exponga contrasena.
No agregues métodos de negocio (verificar_password, etc.) — eso va en el service.
```

---

### PROMPT 1.3 — Implementar models/libro.py

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa Modelo. Rama activa: feat/db-sergio.

Archivos que ya existen y puedes importar:
- app/extensions.py exporta: db (SQLAlchemy instance)

Regla crítica: este archivo NO puede importar flask, request, session
ni render_template.

Implementa app/models/libro.py con:

1. Enum de Python llamado EstadoLibro con valores:
   disponible, prestado, mantenimiento, perdido

2. Clase Libro (db.Model):
   - __tablename__ = "libros"
   - ISBN: String(20), primary_key=True
   - titulo: String(255), nullable=False, index=True
   - autor: String(255), nullable=False, index=True
   - editorial: String(150), nullable=True
   - sinopsis: Text, nullable=True
   - anio_publicacion: SmallInteger, nullable=True
   - numero_paginas: Integer, nullable=True
   - precio: Numeric(10,2), nullable=True
   - ubicacion: String(100), nullable=True
   - numero_copias: Integer, nullable=True
   - categoria: String(100), nullable=True
   - fecha_registro: DateTime, server_default=db.func.now()
   - estado: Enum(EstadoLibro), default=EstadoLibro.disponible

Agrega __repr__ útil. No agregues lógica de negocio.
```

---

### PROMPT 1.4 — Implementar services/auth_service.py

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa Modelo (subcapa servicios). Rama: feat/db-sergio.

Archivos que ya existen y puedes importar:
- app/extensions.py → db, bcrypt
- app/models/usuario.py → Usuario

Regla crítica: este archivo NO puede importar flask, request, session,
render_template. Solo SQLAlchemy y bcrypt.

Implementa app/services/auth_service.py con una función:

def autenticar(usuario: str, password: str) -> "Usuario | None":

Contrato obligatorio:
1. Busca el usuario en la BD por PK (campo usuario).
2. Si no existe: retorna None.
3. Si existe pero la contraseña no coincide (bcrypt.check_password_hash): retorna None.
4. Si existe y la contraseña es correcta: retorna el objeto Usuario.
5. NUNCA distingue hacia afuera si el fallo fue "usuario no existe" vs
   "contraseña incorrecta" — ambos casos retornan None sin mensaje diferente.
   Esto previene enumeración de usuarios.
6. NO toca flask.session — eso es responsabilidad del controlador.

La función debe capturar cualquier excepción de BD (SQLAlchemyError) y
retornar None en ese caso también, logueando el error con el módulo logging
estándar de Python (no print).
```

---

### PROMPT 1.5 — Implementar services/libro_service.py

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa Modelo (subcapa servicios). Rama: feat/db-sergio.

Archivos que ya existen y puedes importar:
- app/extensions.py → db
- app/models/libro.py → Libro, EstadoLibro

Regla crítica: este archivo NO puede importar flask, request, session,
render_template.

Implementa app/services/libro_service.py con una función:

def listar(page: int, filtro_tipo: str | None, filtro_valor: str | None) -> dict:

Contrato obligatorio:
1. POR_PAGINA = 10 (constante en el módulo).
2. filtro_tipo acepta exactamente: "titulo" | "autor" | "isbn" | None
   - "titulo": filtro con ilike en campo titulo
   - "autor": filtro con ilike en campo autor
   - "isbn": filtro con ilike en campo ISBN
   - None o cualquier otro valor: sin filtro
3. El filtro usa ilike con wildcards: f"%{filtro_valor}%"
4. Paginación con .offset((page - 1) * POR_PAGINA).limit(POR_PAGINA)
5. Calcula total con .count() ANTES de aplicar offset/limit.
6. Retorna exactamente este dict:
   {
       "libros":     [lista de objetos Libro],
       "total":      int,
       "pagina":     int,   (el page recibido)
       "paginas":    int,   (ceil(total / POR_PAGINA), mínimo 1)
       "por_pagina": int,   (siempre 10)
       "hay_anterior": bool,
       "hay_siguiente": bool,
   }
7. Si page < 1, tratar como page = 1.
8. Captura SQLAlchemyError y retorna el dict con listas/valores vacíos,
   logueando el error con logging.

NO sabe qué template va a usar el controlador.
```

---

## FASE 2 — Capa Controlador (rama: feat/back-ernesto)

### PROMPT 2.1 — Implementar app/config.py

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa de configuración. Rama: feat/back-ernesto.

Archivos que ya existen:
- .env.example (muestra las variables necesarias)
- requirements.txt (python-dotenv está instalado)

Implementa app/config.py con:

1. Carga el .env con load_dotenv() al inicio del módulo.
2. Clase Config con atributos de clase:
   - SECRET_KEY = os.environ.get("SECRET_KEY", "dev-inseguro-cambiar")
   - SQLALCHEMY_DATABASE_URI construida desde DB_USER, DB_PASSWORD, DB_HOST,
     DB_PORT, DB_NAME usando el driver mysql+pymysql
   - SQLALCHEMY_TRACK_MODIFICATIONS = False
   - SESSION_COOKIE_HTTPONLY = True
   - SESSION_COOKIE_SAMESITE = "Lax"
   - SESSION_COOKIE_SECURE = False  (True solo en producción)
3. Clase DevelopmentConfig(Config):
   - DEBUG = True
   - SQLALCHEMY_ECHO = False  (poner True solo si se necesita debug de queries)
4. config_by_name dict: {"development": DevelopmentConfig, "default": DevelopmentConfig}

Asegúrate de que SQLALCHEMY_DATABASE_URI no quede con valores None si
falta alguna variable de entorno — en ese caso usar defaults seguros
que hagan fallar la conexión de forma obvia (no silenciosa).
```

---

### PROMPT 2.2 — Implementar app/__init__.py (Application Factory)

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando el Application Factory. Rama: feat/back-ernesto.

Archivos que ya existen y debes usar:
- app/config.py → config_by_name
- app/extensions.py → db, bcrypt
- app/models/usuario.py → Usuario (importar para que db.create_all() lo registre)
- app/models/libro.py → Libro (ídem)
- app/controllers/auth_controller.py → auth_bp (Blueprint) — aún no existe,
  pero lo crearás en el siguiente prompt. Por ahora pon el import con un
  comentario # TODO: descomentar cuando exista el blueprint
- app/controllers/libro_controller.py → libro_bp — igual, comentado por ahora

Implementa app/__init__.py con la función create_app(config_name="default"):

1. Crea la instancia Flask con __name__.
2. Carga la config desde config_by_name[config_name].
3. Inicializa extensiones: db.init_app(app), bcrypt.init_app(app).
4. Dentro de un app.app_context(): ejecuta db.create_all().
5. Registra blueprints (cuando estén descomentados):
   - auth_bp con url_prefix="/"
   - libro_bp con url_prefix="/"
6. Define una ruta raíz GET / que redirija a /catalogo si hay sesión activa,
   o a /login si no la hay.
7. Retorna app.

Al final del archivo, fuera de create_app, agrega:
if __name__ == "__main__":
    app = create_app()
    app.run()
```

---

### PROMPT 2.3 — Implementar controllers/auth_controller.py

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa Controlador. Rama: feat/back-ernesto.

Archivos que ya existen y puedes importar:
- app/extensions.py → bcrypt (no necesario aquí, el service lo usa)
- app/services/auth_service.py → autenticar(usuario, password)

Regla crítica de MVC: este archivo PUEDE importar flask (request, session,
redirect, url_for, render_template). NO puede hacer queries SQL directas.
Toda lógica de negocio va en auth_service.

Implementa app/controllers/auth_controller.py con un Blueprint llamado auth_bp:

1. GET /login:
   - Si ya hay sesión activa (session.get("usuario")), redirige a /catalogo.
   - Si no, renderiza auth/login.html sin contexto de error.

2. POST /login:
   - Lee request.form["usuario"] y request.form["contrasena"].
   - Llama autenticar(usuario, contrasena).
   - Si retorna un objeto Usuario:
     * session["usuario"] = usuario_obj.usuario
     * session["nombre"] = usuario_obj.nombre
     * session.permanent = False
     * redirect a /catalogo
   - Si retorna None:
     * re-renderiza auth/login.html con error="Usuario o contraseña incorrectos"
     * NUNCA detalla si el fallo fue usuario o contraseña
   - Captura cualquier excepción inesperada y re-renderiza login con error genérico.

3. GET /logout:
   - session.clear()
   - redirect a /login

4. Decorador login_required como función en este mismo archivo:
   from functools import wraps
   def login_required(f):
       ...redirige a /login?expired=1 si no hay session["usuario"]

   Exporta login_required para que libro_controller lo importe.
```

---

### PROMPT 2.4 — Implementar controllers/libro_controller.py

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa Controlador. Rama: feat/back-ernesto.

Archivos que ya existen y puedes importar:
- app/services/libro_service.py → listar(page, filtro_tipo, filtro_valor)
- app/controllers/auth_controller.py → login_required

El servicio listar() retorna:
{
    "libros": [...], "total": int, "pagina": int,
    "paginas": int, "por_pagina": int,
    "hay_anterior": bool, "hay_siguiente": bool
}

Regla MVC: no queries SQL directas. No lógica de negocio.

Implementa app/controllers/libro_controller.py con Blueprint libro_bp:

1. GET /catalogo — decorado con @login_required:
   - Lee query params:
     * page = request.args.get("page", 1, type=int)
     * filtro_tipo = request.args.get("filtro_tipo", "").strip() or None
     * filtro_valor = request.args.get("filtro_valor", "").strip() or None
   - Llama libro_service.listar(page, filtro_tipo, filtro_valor).
   - Construye context con TODO lo del dict del service MÁS:
     * "usuario": session.get("nombre", "")
     * "filtro_tipo": filtro_tipo or ""
     * "filtro_valor": filtro_valor or ""
   - Captura SQLAlchemyError → abort(503).
   - Renderiza libros/catalogo.html con **context.

2. Stubs — todos decorados con @login_required, todos retornan HTTP 200:
   - GET /libros/nuevo → render_template("libros/stub.html", pantalla="Nuevo Libro")
   - GET /libros/<isbn> → render_template("libros/stub.html", pantalla="Detalles del Libro")
   - GET /libros/<isbn>/editar → render_template("libros/stub.html", pantalla="Editar Libro")
   - POST /libros/<isbn>/eliminar → render_template("libros/stub.html", pantalla="Eliminar Libro")

3. Al final, descomenta los imports de blueprints en app/__init__.py
   y verifica que la app arranca sin errores con: flask run
```

---

## FASE 3 — Capa Vista (rama: feat/front-santiago)

### PROMPT 3.1 — Implementar templates/base.html

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la capa Vista con Jinja2 + Tailwind CSS vía CDN.
Rama: feat/front-santiago.

Contexto de la app: biblioteca universitaria. La referencia visual del profesor
usa colores dorado/amarillo UDEM y blanco. El layout es full-screen.

Implementa app/templates/base.html con:

1. DOCTYPE html, lang="es", charset UTF-8, viewport meta.
2. Tailwind CSS vía CDN:
   <script src="https://cdn.tailwindcss.com"></script>
3. Bloque {% block title %}OLP300{% endblock %} en <title>.
4. Navbar fijo en la parte superior con:
   - Logo/nombre "Biblioteca UDEM" a la izquierda (texto, no imagen).
   - Color de fondo: dorado/amarillo (#B8960C o similar UDEM).
   - Texto blanco.
   - A la derecha: "Bienvenido, {{ session.get('nombre', '') }}" y un
     botón/link "Cerrar sesión" que apunta a /logout.
   - El navbar SOLO se muestra si session.get("usuario") existe.
     Usa {% if session.get("usuario") %}...{% endif %}
5. Contenedor principal: <main class="..."> con {% block content %}{% endblock %}.
6. Sin footer por ahora.

Regla de Vista: este template no hace cálculos. Solo renderiza variables
que recibe en el contexto.
```

---

### PROMPT 3.2 — Implementar templates/auth/login.html

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la Vista de autenticación. Rama: feat/front-santiago.

El template base.html ya existe en templates/base.html.

Variables de contexto que recibe este template:
- error: string con mensaje de error, o None/ausente si no hay error
- request.args.get("expired"): presente si la sesión expiró

Implementa app/templates/auth/login.html:

1. {% extends "base.html" %}
2. El navbar NO debe mostrarse en login (ya está controlado en base.html
   con la condición de sesión).
3. Layout centrado en pantalla (full screen, centrado vertical y horizontal).
4. Encabezado: "Librería de la Universidad" y subtítulo con nombre de la institución.
5. Tarjeta/card blanca con:
   - Título "Iniciar sesión"
   - Campo "Usuario (Matrícula/Nómina)" con name="usuario", placeholder
   - Campo "Contraseña" con name="contrasena", type="password", placeholder
   - Link/texto pequeño "¿Olvidaste tu contraseña?" (no funcional — solo visual)
   - Botón "Iniciar sesión" tipo submit, color dorado/azul UDEM
6. Botón X en la esquina superior derecha de la pantalla para "salir"
   (T04 del DET). Implementar como: window.close() con onclick, o un link
   a una URL de salida. Poner un comentario en el HTML explicando que
   corresponde a T04 del DET.
7. Área de mensajes:
   - {% if error %}: div con fondo rojo claro, texto "{{ error }}"
   - {% if request.args.get('expired') %}: div con fondo amarillo,
     texto "Tu sesión ha expirado. Por favor inicia sesión nuevamente."
8. El formulario hace POST a /login con method="post".
```

---

### PROMPT 3.3 — Implementar templates/libros/stub.html

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la Vista stub para pantallas no implementadas.
Rama: feat/front-santiago.

Variables de contexto que recibe:
- pantalla: string con el nombre de la pantalla (ej: "Nuevo Libro")

Implementa app/templates/libros/stub.html:

1. {% extends "base.html" %}
2. Contenido centrado con:
   - Ícono o emoji grande (ej: 🚧)
   - Título "{{ pantalla }}"
   - Texto: "Esta pantalla está en construcción y estará disponible próximamente."
   - Botón "← Volver al Catálogo" que apunta a /catalogo
3. Estilo limpio con Tailwind. No debe verse como un error — debe verse
   como una pantalla "en construcción" intencional.
```

---

### PROMPT 3.4 — Implementar templates/libros/catalogo.html

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás implementando la Vista principal del catálogo. Rama: feat/front-santiago.

Este es el template más complejo. Lee el contrato de contexto completo antes
de escribir una sola línea de Jinja2.

Variables de contexto que recibe (contrato fijo — no asumas nada más):
{
    "libros":        [lista de objetos Libro con atributos: ISBN, titulo, autor,
                      estado (EstadoLibro enum), numero_copias, categoria],
    "total":         int,
    "pagina":        int,
    "paginas":       int,
    "por_pagina":    int,
    "hay_anterior":  bool,
    "hay_siguiente": bool,
    "filtro_tipo":   str,   ("titulo" | "autor" | "isbn" | "")
    "filtro_valor":  str,   (valor del filtro | "")
    "usuario":       str,
}

Implementa app/templates/libros/catalogo.html con {% extends "base.html" %}:

SECCIÓN 1 — Encabezado:
- Título "Libros" (h1 grande)
- Subtítulo: "Pestaña para administrar los libros que se encuentran en el sistema"
- Botón "Nuevo Libro +" alineado a la derecha → href="/libros/nuevo"
  Color azul o dorado UDEM.
- Botón X para cerrar sesión visible (T09 del DET) → href="/logout"

SECCIÓN 2 — Barra de filtros:
- Form GET a /catalogo (no POST — los filtros van en la URL para que sean
  compartibles y el botón atrás funcione).
- Select con name="filtro_tipo" y opciones:
  <option value="">-- Filtrar por --</option>
  <option value="titulo">Título</option>
  <option value="autor">Autor</option>
  <option value="isbn">ISBN</option>
  El option del filtro_tipo actual debe tener selected.
- Input text con name="filtro_valor", value="{{ filtro_valor }}"
- Botón submit "Buscar"
- Si filtro_valor no está vacío: mostrar un link "✕ Limpiar filtro" → /catalogo

SECCIÓN 3 — Tabla de libros:
- Columnas: Título | Autor(es) | ISBN | Estado | Copias | Acciones
- Por cada libro en libros:
  * Estado como badge/pill de color:
    - disponible → verde
    - prestado → azul
    - mantenimiento → amarillo
    - perdido → rojo
  * Acciones:
    - Botón "Ver detalles" → /libros/{{ libro.ISBN }}
    - Ícono editar (lápiz) → /libros/{{ libro.ISBN }}/editar
    - Ícono eliminar (bote de basura) → form POST a /libros/{{ libro.ISBN }}/eliminar
      El form de eliminar debe tener un confirm() en onsubmit para prevenir
      eliminaciones accidentales.
- Si libros está vacío:
  Mostrar fila con colspan que diga "No se encontraron libros."

SECCIÓN 4 — Paginador:
- Botón "← Anterior": deshabilitado si NOT hay_anterior.
  Link a /catalogo?page={{ pagina - 1 }}&filtro_tipo={{ filtro_tipo }}&filtro_valor={{ filtro_valor }}
- Texto "Página {{ pagina }} de {{ paginas }}"
- Botón "Siguiente →": deshabilitado si NOT hay_siguiente.
  Link a /catalogo?page={{ pagina + 1 }}&filtro_tipo={{ filtro_tipo }}&filtro_valor={{ filtro_valor }}
- Total de registros: "{{ total }} libro(s) encontrado(s)"

REGLA: este template no hace ningún cálculo. Usa solo las variables del contexto.
No uses expresiones como (pagina - 1) en Jinja2 — eso es lógica. Si necesitas
algo calculado, pídeme que lo agregue al controlador.

EXCEPCIÓN PERMITIDA: los links de paginación SÍ pueden hacer pagina - 1 y pagina + 1
porque son construcciones de URL simples, no lógica de negocio.
```

---

## FASE 4 — Integración (rama: feat/integracion-marcelo)

### PROMPT 4.1 — Conectar todo: desbloquear __init__.py y verificar arranque

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás en la fase de integración. Rama: feat/integracion-marcelo.
Esta rama tiene merges de feat/db-sergio, feat/back-ernesto y feat/front-santiago.

Tarea: verificar que todos los imports estén conectados y la app arranque.

1. Abre app/__init__.py y descomenta los imports de blueprints:
   from app.controllers.auth_controller import auth_bp
   from app.controllers.libro_controller import libro_bp

2. Verifica que app.register_blueprint(auth_bp) y app.register_blueprint(libro_bp)
   estén presentes.

3. Crea el archivo run.py en la raíz:
   from app import create_app
   app = create_app("development")
   if __name__ == "__main__":
       app.run(debug=True, host="0.0.0.0", port=5000)

4. Crea o actualiza .env con los valores reales (copia de .env.example con
   las credenciales de la BD local creada en PROMPT 0.3).

5. Ejecuta: python run.py

6. Reporta exactamente qué sucede:
   - Si arranca: confirmar que http://localhost:5000 redirige a /login.
   - Si falla: mostrar el traceback completo sin intentar arreglarlo solo —
     esperar instrucción.
```

---

### PROMPT 4.2 — Aplicar schema y seed a la base de datos

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás en la fase de integración. Rama: feat/integracion-marcelo.

Prerequisitos que deben cumplirse antes de este prompt:
- MariaDB levantada localmente.
- Usuario olp300_user creado (PROMPT 0.3 ejecutado).
- schema.sql y seed.sql generados (PROMPT 0.4).
- Contraseñas del seed hasheadas (PROMPT 0.5 ejecutado, UPDATEs aplicados a seed.sql).

Ejecuta en orden:
1. mysql -u olp300_user -p olp300 < schema.sql
2. python hash_seed_passwords.py   (copia los UPDATEs al seed.sql si no lo has hecho)
3. mysql -u olp300_user -p olp300 < seed.sql

Después verifica desde Python que los datos existen:
  python -c "
  from app import create_app
  from app.models.usuario import Usuario
  from app.models.libro import Libro
  app = create_app()
  with app.app_context():
      print('Usuarios:', Usuario.query.count())
      print('Libros:', Libro.query.count())
  "

Resultado esperado: Usuarios: 3, Libros: 15
Si el resultado es diferente, muéstrame el output sin intentar arreglarlo solo.
```

---

### PROMPT 4.3 — Prueba E2E del flujo de autenticación

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás verificando el flujo de autenticación end-to-end. Rama: feat/integracion-marcelo.

La app debe estar corriendo (python run.py).

Escribe un script llamado test_auth_e2e.py en tests/ que use el cliente
de pruebas de Flask (no requests externo, sino app.test_client()):

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

Ejecuta: python tests/test_auth_e2e.py
Reporta el resultado completo.
```

---

### PROMPT 4.4 — Prueba E2E del catálogo: filtros y paginación

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Estás verificando el catálogo end-to-end. Rama: feat/integracion-marcelo.

Escribe tests/test_catalogo_e2e.py:

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

Ejecuta: python tests/test_catalogo_e2e.py
```

---

### PROMPT 4.5 — Verificación final de MVC: auditoría de imports

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Esta es la verificación final antes de la entrega. Rama: feat/integracion-marcelo.

El profesor evalúa explícitamente que el patrón MVC esté respetado.
Necesito que hagas una auditoría de imports ejecutando los siguientes comandos
y reportando el resultado:

1. Verifica que ningún archivo en models/ ni services/ importa Flask:
   grep -rn "from flask" app/models/ app/services/
   grep -rn "import flask" app/models/ app/services/
   ESPERADO: sin resultados. Si hay alguno, es una violación MVC — reportarlo.

2. Verifica que ningún template tiene lógica de negocio (comparaciones de negocio):
   grep -n "\.precio\|\.copias\|>.*and\|and.*<" app/templates/
   ESPERADO: sin resultados relevantes de lógica de negocio.

3. Verifica que los controladores no tienen queries directas:
   grep -rn "db.session.query\|db.session.execute\|\.filter_by\|\.filter(" app/controllers/
   ESPERADO: sin resultados. Queries solo en services/.

4. Verifica que requirements.txt tiene todas las dependencias:
   pip freeze | grep -E "Flask|SQLAlchemy|bcrypt|dotenv|PyMySQL"

5. Ejecuta la app una última vez y navega manualmente:
   - /login → debe mostrar formulario
   - Login con credenciales del seed → debe llegar a /catalogo
   - /catalogo con filtro por título → debe filtrar
   - /libros/nuevo → debe mostrar stub
   - /logout → debe regresar a /login

Reporta el resultado de cada punto. Si algo falla, muéstrame el output exacto.
```

---

### PROMPT 4.6 — Generar README.md final

```
Eres el asistente de un proyecto académico Flask llamado OLP300.
Genera README.md en la raíz del proyecto. Rama: feat/integracion-marcelo.

El README debe incluir exactamente estas secciones, en este orden:

# OLP300 — Catálogo de Libros
## Evidencia 10 — Arquitectura de Software, UDEM

### Equipo
[tabla con nombre, matrícula, capa, rama]

### Stack
[tabla del stack]

### Requisitos previos
- Python 3.11
- MariaDB 10.x o superior
- pip

### Setup del ambiente (paso a paso)
1. Clonar el repositorio
2. Crear y activar virtualenv
3. pip install -r requirements.txt
4. Crear la BD en MariaDB (comando mysql con setup_db.sql)
5. Copiar .env.example a .env y ajustar credenciales
6. Ejecutar schema.sql y seed.sql
7. python run.py

### Credenciales de prueba
[tabla con los 3 usuarios del seed: usuario y contraseña en texto plano]

### Estructura del proyecto
[árbol de carpetas con descripción de cada capa MVC]

### Patrón MVC — cómo está implementado
[párrafo breve explicando que Modelo está en models/ y services/,
Controlador en controllers/, Vista en templates/]

### Rutas implementadas
[tabla de rutas: URL, método, descripción, estado (implementado/stub)]
```

---

## REFERENCIA RÁPIDA — Orden de ejecución

| # | Prompt | Rama | Archivos creados |
|---|--------|------|-----------------|
| 0.1 | Estructura de carpetas | main | Todos los archivos vacíos |
| 0.2 | requirements.txt + install | main | requirements.txt, .venv |
| 0.3 | Setup MariaDB | main | setup_db.sql |
| 0.4 | schema.sql + seed.sql | feat/db-sergio | schema.sql, seed.sql |
| 0.5 | Hash passwords script | feat/db-sergio | hash_seed_passwords.py |
| 1.1 | extensions.py | feat/db-sergio | app/extensions.py |
| 1.2 | models/usuario.py | feat/db-sergio | app/models/usuario.py |
| 1.3 | models/libro.py | feat/db-sergio | app/models/libro.py |
| 1.4 | services/auth_service.py | feat/db-sergio | app/services/auth_service.py |
| 1.5 | services/libro_service.py | feat/db-sergio | app/services/libro_service.py |
| 2.1 | config.py | feat/back-ernesto | app/config.py |
| 2.2 | app/__init__.py | feat/back-ernesto | app/__init__.py |
| 2.3 | auth_controller.py | feat/back-ernesto | app/controllers/auth_controller.py |
| 2.4 | libro_controller.py | feat/back-ernesto | app/controllers/libro_controller.py |
| 3.1 | base.html | feat/front-santiago | app/templates/base.html |
| 3.2 | login.html | feat/front-santiago | app/templates/auth/login.html |
| 3.3 | stub.html | feat/front-santiago | app/templates/libros/stub.html |
| 3.4 | catalogo.html | feat/front-santiago | app/templates/libros/catalogo.html |
| 4.1 | Conectar + arranque | feat/integracion-marcelo | run.py |
| 4.2 | Aplicar BD | feat/integracion-marcelo | — (solo comandos) |
| 4.3 | Test E2E auth | feat/integracion-marcelo | tests/test_auth_e2e.py |
| 4.4 | Test E2E catálogo | feat/integracion-marcelo | tests/test_catalogo_e2e.py |
| 4.5 | Auditoría MVC | feat/integracion-marcelo | — (solo verificación) |
| 4.6 | README.md final | feat/integracion-marcelo | README.md |

---

## NOTAS DE USO

- **Cada prompt es independiente.** Puedes copiar y pegar directo en Claude Code.
- **Si Claude Code propone algo que contradice CLAUDE.md** (por ejemplo, poner
  una query en el controlador), rechaza la sugerencia y cita la sección violada.
- **Si un prompt falla**, no avances al siguiente. Pega el error en Claude Code
  como mensaje de seguimiento en la misma sesión.
- **Los prompts de Fase 0 y Fase 4** se ejecutan en `main` o en
  `feat/integracion-marcelo`. Las Fases 1, 2 y 3 tienen rama explícita.
- **El orden dentro de cada fase importa.** extensions.py debe existir antes
  que los models. Los models deben existir antes que los services.
  Los services antes que los controllers.
