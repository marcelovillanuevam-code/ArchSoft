# ARCHITECTURE.md — OLP300 Catálogo de Libros

Referencia técnica de arquitectura para Evidencia 10, Arquitectura de Software, UDEM.
Autores: Sergio Ayala #672830 · Santiago Pongutá #584354 · Ernesto Vega #644175 · Marcelo Villanueva #666660

---

## 1. Decisión de stack

### Por qué Flask

Flask es un microframework que no impone estructura propia. Esa característica, que en proyectos grandes es una desventaja, aquí es una ventaja académica: la separación en capas MVC es 100% responsabilidad del equipo y queda explícita en la estructura de carpetas, no oculta detrás de convenciones del framework.

Comparado con FastAPI (opción descartada): FastAPI agrega Pydantic, Uvicorn y un sistema de dependencias que no aportan valor para este alcance y suman complejidad de setup en demo. Flask resuelve exactamente lo que necesitamos con menos piezas.

### Stack final

| Capa | Tecnología | Justificación |
|---|---|---|
| Framework | Flask 3.x | Microframework, sin opinión sobre estructura — MVC queda explícito |
| Templates | Jinja2 (built-in Flask) | Server-side rendering — cumple MVC sin ambigüedad |
| CSS | Tailwind CSS vía CDN | Sin build step en esta entrega |
| Base de datos | MariaDB | Compatible MySQL, gratuito, soporte activo |
| ORM | SQLAlchemy 2.x + flask-sqlalchemy | Queries parametrizadas, previene SQL injection |
| Hash | flask-bcrypt (cost 12) | Estándar para contraseñas, unidireccional |
| Sesiones | flask.session + SECRET_KEY | Built-in Flask, sin dependencias extra |
| Variables de entorno | python-dotenv | Estándar, sin secretos en código |

---

## 2. Por qué Jinja2 server-side cumple MVC

Este punto es deliberado. Si se usara React u otra SPA:

- La Vista correría en un proceso separado, en otro lenguaje (JavaScript).
- El backend se convertiría en una API REST, no en un controlador MVC.
- La separación M-V-C se rompería: habría M y C en Python, y V en JS — dos patrones mezclados.

Con Jinja2 server-side:

```
Request HTTP
    ↓
Flask Blueprint (Controlador)     ← recibe el request
    ↓
Service (Modelo)                  ← aplica lógica de negocio
    ↓
SQLAlchemy (Modelo)               ← accede a MariaDB
    ↓
Controlador arma dict de contexto
    ↓
Jinja2 Template (Vista)           ← recibe contexto, produce HTML
    ↓
Response HTTP al navegador
```

Los tres componentes corren en el mismo proceso Python. La separación es por módulo y por contrato, no por red. Eso es MVC clásico.

---

## 3. Estructura de carpetas y qué hace cada archivo

```
olp300/
├── app/
│   ├── __init__.py          # create_app(): registra blueprints, extensiones, config
│   ├── config.py            # Clase Config — lee .env con python-dotenv
│   ├── extensions.py        # Instancias compartidas: db, bcrypt (sin circular imports)
│   │
│   ├── models/              # ←── MODELO (ORM)
│   │   ├── usuario.py       # clase Usuario: usuario PK, contrasena, nombre, email
│   │   └── libro.py         # clase Libro: ISBN PK, titulo, autor, ... estado ENUM
│   │
│   ├── services/            # ←── MODELO (lógica de negocio)
│   │   ├── auth_service.py  # autenticar() — no toca Flask
│   │   └── libro_service.py # listar() con paginación y filtros — no toca Flask
│   │
│   ├── controllers/         # ←── CONTROLADOR (Blueprints Flask)
│   │   ├── auth_controller.py   # GET /login, POST /login, GET /logout
│   │   └── libro_controller.py  # GET /catalogo + 4 stubs
│   │
│   ├── templates/           # ←── VISTA (Jinja2)
│   │   ├── base.html        # layout: navbar, footer, bloque content
│   │   ├── auth/
│   │   │   └── login.html   # extiende base.html
│   │   └── libros/
│   │       ├── catalogo.html
│   │       └── stub.html    # plantilla genérica para rutas no implementadas
│   │
│   └── static/css/          # Tailwind build (producción)
│
├── tests/
├── schema.sql               # CREATE TABLE libros, CREATE TABLE usuarios
├── seed.sql                 # 3 usuarios + 15 libros de prueba
├── .env.example
├── requirements.txt
└── README.md
```

---

## 4. Capa Modelo

### 4.1 models/usuario.py

```python
from app.extensions import db

class Usuario(db.Model):
    __tablename__ = "usuarios"
    usuario    = db.Column(db.String(50),  primary_key=True)
    contrasena = db.Column(db.String(255), nullable=False)   # bcrypt hash
    nombre     = db.Column(db.String(50),  nullable=False, unique=True)
    email      = db.Column(db.String(150), nullable=False, unique=True)
```

### 4.2 models/libro.py

```python
import enum
from app.extensions import db

class EstadoLibro(enum.Enum):
    disponible    = "disponible"
    prestado      = "prestado"
    mantenimiento = "mantenimiento"
    perdido       = "perdido"

class Libro(db.Model):
    __tablename__ = "libros"
    ISBN              = db.Column(db.String(20),   primary_key=True)
    titulo            = db.Column(db.String(255),  nullable=False, index=True)
    autor             = db.Column(db.String(255),  nullable=False, index=True)
    editorial         = db.Column(db.String(150))
    sinopsis          = db.Column(db.Text)
    anio_publicacion  = db.Column(db.SmallInteger)
    numero_paginas    = db.Column(db.Integer)
    precio            = db.Column(db.Numeric(10, 2))
    ubicacion         = db.Column(db.String(100))
    numero_copias     = db.Column(db.Integer)
    categoria         = db.Column(db.String(100))
    fecha_registro    = db.Column(db.DateTime,     server_default=db.func.now())
    estado            = db.Column(db.Enum(EstadoLibro), default=EstadoLibro.disponible)
```

**Regla:** ningún archivo en `models/` ni `services/` importa `flask`, `request`, `session` ni `render_template`.

### 4.3 services/auth_service.py — responsabilidades

- Buscar el usuario por PK.
- Verificar el hash con `bcrypt.check_password_hash`.
- Devolver `Usuario` si es válido, `None` en cualquier caso de fallo.
- **No** tocar `flask.session` — esa responsabilidad es del controlador.
- **No** distinguir "usuario no existe" de "contraseña incorrecta" en el valor de retorno (previene enumeración).

### 4.4 services/libro_service.py — responsabilidades

- Aplicar el filtro con `ilike` según `filtro_tipo`.
- Paginar con SQLAlchemy `.offset()` / `.limit()`.
- Devolver el dict de contexto acordado (ver CLAUDE.md sección 5).
- **No** saber qué template va a usar el controlador.

---

## 5. Capa Controlador

### 5.1 auth_controller.py

| Ruta | Método | Acción |
|---|---|---|
| `/login` | GET | Renderiza `auth/login.html` |
| `/login` | POST | Llama `auth_service.autenticar()`, si válido guarda sesión y redirige a `/catalogo`, si no re-renderiza login con error genérico |
| `/logout` | GET | `session.clear()` → redirect `/login` |

Protección de sesión expirada: si el usuario llega a `/catalogo` con cookie vencida, el decorador `@login_required` redirige a `/login?expired=1`. El template muestra el aviso.

### 5.2 libro_controller.py

| Ruta | Método | Implementado en E10 | Acción |
|---|---|---|---|
| `/catalogo` | GET | Sí | Recibe `page`, `filtro_tipo`, `filtro_valor` como query params. Llama `libro_service.listar()`. Renderiza `libros/catalogo.html`. |
| `/libros/nuevo` | GET | Stub | Renderiza `libros/stub.html` |
| `/libros/<isbn>` | GET | Stub | Renderiza `libros/stub.html` |
| `/libros/<isbn>/editar` | GET | Stub | Renderiza `libros/stub.html` |
| `/libros/<isbn>/eliminar` | POST | Stub | Renderiza `libros/stub.html` |

Los stubs devuelven HTTP 200 y mantienen la navegación visible. No rompen el DET.

---

## 6. Capa Vista

### 6.1 base.html

- Carga Tailwind CSS vía CDN.
- Define bloques: `{% block title %}`, `{% block content %}`.
- Incluye navbar con nombre de usuario en sesión y botón Cerrar Sesión.
- Todos los demás templates lo extienden con `{% extends "base.html" %}`.

### 6.2 auth/login.html

- Formulario con campos `usuario` y `contrasena`.
- Botón X para "salir" (T04 del DET — cierra la pestaña o redirige a una URL de salida).
- Área de error: `{% if error %}` muestra el mensaje genérico.
- Aviso de sesión expirada: `{% if request.args.get('expired') %}`.

### 6.3 libros/catalogo.html

Recibe el contexto definido en CLAUDE.md sección 5.3. Debe renderizar:

- Dropdown de filtro (Título / Autor / ISBN) + campo de texto + botón buscar.
- Botón "Nuevo Libro" → `GET /libros/nuevo`.
- Tabla: columnas ISBN, Título, Autor, Estado, Copias, Acciones.
- Por cada fila: botón Ver → `/libros/<isbn>`, ícono Editar → `/libros/<isbn>/editar`, ícono Eliminar → form POST a `/libros/<isbn>/eliminar`.
- Paginador: botones Anterior / Siguiente, indicador "Página X de Y".

**Regla:** el template no hace cálculos. Si necesita saber si hay página siguiente, el controlador manda `"hay_siguiente": bool`.

---

## 7. Modelo de datos

### Tabla `libros`

| Campo | Tipo | Notas |
|---|---|---|
| ISBN | VARCHAR(20) | PK |
| titulo | VARCHAR(255) | Índice |
| autor | VARCHAR(255) | Índice |
| editorial | VARCHAR(150) | |
| sinopsis | TEXT | |
| anio_publicacion | SMALLINT (YEAR) | |
| numero_paginas | INT | |
| precio | DECIMAL(10,2) | |
| ubicacion | VARCHAR(100) | |
| numero_copias | INT | |
| categoria | VARCHAR(100) | |
| fecha_registro | DATETIME | DEFAULT NOW() |
| estado | ENUM | 'disponible' (default), 'prestado', 'mantenimiento', 'perdido' |

### Tabla `usuarios`

| Campo | Tipo | Notas |
|---|---|---|
| usuario | VARCHAR(50) | PK |
| contrasena | VARCHAR(255) | Hash bcrypt — nunca texto plano |
| nombre | VARCHAR(50) | UNIQUE |
| email | VARCHAR(150) | UNIQUE |

### Decisión: bcrypt en lugar de cifrado reversible

La especificación dice "valor cifrado". El equipo lo implementa como hash bcrypt porque las contraseñas no necesitan descifrarse, solo verificarse. Si la BD es comprometida, los hashes no son reversibles. El cifrado reversible (AES, etc.) no aporta seguridad real para contraseñas.

---

## 8. Flujos del DET mapeados a código

| Transición DET | Acción | Ruta / método | Service |
|---|---|---|---|
| T01 | Mostrar login | GET /login | — |
| T02 | Credencial inválida | POST /login (falla) | auth_service.autenticar() |
| T03 | Login exitoso | POST /login → redirect /catalogo | auth_service.autenticar() |
| T04 | Salir desde login | Click X | — |
| T05 | Ir a Nuevo Libro | GET /libros/nuevo | stub |
| T06 | Ver detalles | GET /libros/\<isbn\> | stub |
| T07 | Editar | GET /libros/\<isbn\>/editar | stub |
| T08 | Intentar eliminar | POST /libros/\<isbn\>/eliminar | stub |
| T09 | Salir del catálogo | GET /logout | session.clear() |
| T10–T19 | Validaciones alta/edición | Proyecto Final | — |

---

## 9. Casos no cubiertos en el DET

### Contraseña incorrecta vs. usuario inexistente
El DET solo modela "usuario no encontrado". Internamente el service distingue ambos casos, pero por seguridad el controlador muestra siempre: **"Usuario o contraseña incorrectos"**.

### Sesión expirada
Si la cookie caduca, cualquier ruta protegida redirige a `/login?expired=1`. El template muestra aviso.

### Filtro y paginación
El DET no los modela. Se implementan como query params: `/catalogo?page=2&filtro_tipo=titulo&filtro_valor=quijote`. Página por defecto: 1. Registros por página: 10.

### Error de conexión a BD
El controlador captura `SQLAlchemyError` y devuelve HTTP 503 con un template de error — nunca un stacktrace al usuario.

---

## 10. Estrategia de seguridad

| Riesgo | Mitigación |
|---|---|
| Contraseña filtrada desde BD | bcrypt hash unidireccional (cost 12) |
| Session hijacking | Cookie `HttpOnly`, `SameSite=Lax` |
| Credenciales en código | `SECRET_KEY` y `DB_PASSWORD` en `.env` fuera del repo |
| SQL injection | Queries ORM parametrizadas — nunca f-strings con input |
| XSS | Jinja2 escapa variables por defecto |
| CSRF en formularios POST | Token CSRF en login y futuros formularios |
| Enumeración de usuarios | Mensaje de error genérico en login |

---

## 11. Riesgos identificados

| Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|
| Schema de Sergio atrasa a Ernesto | Media | Alto | Schema + seed publicados antes del miércoles. Ernesto trabaja con BD local. |
| Desacuerdo en contexto Jinja2 | Alta | Medio | El contrato se acuerda el día 1 y vive en CLAUDE.md y ARCHITECTURE.md. |
| Conflictos de merge en main | Alta | Medio | Ramas por persona. PRs pequeños y diarios. Marcelo resuelve conflictos. |
| Profesor cuestiona MVC con Flask | Media | Alto | Sección 2 de este documento defiende la decisión. Jinja2 server-side elimina ambigüedad. |
| Demo falla por MariaDB no levantada | Media | Alto | `README.md` incluye guía de levantamiento. Marcelo prueba con DB limpia el viernes. |
| Marcelo es cuello de botella (PR approval + integración + E2E) | Alta | Alto | Si Marcelo se bloquea, Sergio hace backup de aprobación de PRs. Comunicarlo en el standup. |
| Tailwind CDN no disponible en demo | Baja | Medio | Compilar Tailwind a CSS estático como paso previo a la entrega. |

---

## 12. Referencias

- Especificación Técnica Evidencia 09-10. UDEM — Dr. Felipe de Jesús Rodríguez García.
- Evidencia 09 del equipo: Diagrama de Estado-Transición del Catálogo de Libros.
- Documentación oficial de Flask. https://flask.palletsprojects.com
- Documentación oficial de Jinja2. https://jinja.palletsprojects.com
- Documentación oficial de SQLAlchemy 2.x. https://docs.sqlalchemy.org
- OWASP Authentication Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
