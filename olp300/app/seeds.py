import logging

from app.extensions import bcrypt, db
from app.models.libro import EstadoLibro, Libro
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)

_USUARIOS = [
    {
        "usuario": "admin",
        "password": "Admin2024!",
        "nombre": "Administrador",
        "email": "admin@biblioteca.udem.mx",
    },
    {
        "usuario": "ernesto",
        "password": "Ernesto2024!",
        "nombre": "Ernesto Vega",
        "email": "ernesto.vega@udem.edu",
    },
    {
        "usuario": "santiago",
        "password": "Santiago2024!",
        "nombre": "Santiago Pongutá",
        "email": "santiago.ponguta@udem.edu",
    },
]

_LIBROS = [
    # Ficción
    {
        "ISBN": "978-0-06-112008-4",
        "titulo": "Cien años de soledad",
        "autor": "Gabriel García Márquez",
        "editorial": "Harper Perennial",
        "sinopsis": "La saga de la familia Buendía en el pueblo ficticio de Macondo, mezcla de realismo y magia.",
        "anio_publicacion": 1967,
        "numero_paginas": 417,
        "precio": 350.00,
        "ubicacion": "A-01-03",
        "numero_copias": 3,
        "categoria": "Ficción",
        "estado": EstadoLibro.disponible,
    },
    {
        "ISBN": "978-0-14-028329-7",
        "titulo": "El nombre de la rosa",
        "autor": "Umberto Eco",
        "editorial": "Vintage",
        "sinopsis": "Un thriller medieval ambientado en una abadía italiana del siglo XIV donde ocurren misteriosos crímenes.",
        "anio_publicacion": 1980,
        "numero_paginas": 502,
        "precio": 420.00,
        "ubicacion": "A-02-01",
        "numero_copias": 2,
        "categoria": "Ficción",
        "estado": EstadoLibro.prestado,
    },
    {
        "ISBN": "978-84-376-0494-7",
        "titulo": "Don Quijote de la Mancha",
        "autor": "Miguel de Cervantes Saavedra",
        "editorial": "Cátedra",
        "sinopsis": "Las aventuras del ingenioso hidalgo don Quijote y su fiel escudero Sancho Panza.",
        "anio_publicacion": 1605,
        "numero_paginas": 863,
        "precio": 450.00,
        "ubicacion": "A-03-02",
        "numero_copias": 3,
        "categoria": "Ficción",
        "estado": EstadoLibro.mantenimiento,
    },
    {
        "ISBN": "978-0-14-118776-1",
        "titulo": "1984",
        "autor": "George Orwell",
        "editorial": "Penguin Books",
        "sinopsis": "Distopía sobre un régimen totalitario que ejerce vigilancia absoluta sobre sus ciudadanos.",
        "anio_publicacion": 1949,
        "numero_paginas": 328,
        "precio": 250.00,
        "ubicacion": "A-02-03",
        "numero_copias": 4,
        "categoria": "Ficción",
        "estado": EstadoLibro.disponible,
    },
    # Ciencia
    {
        "ISBN": "978-0-06-093546-9",
        "titulo": "Una breve historia del tiempo",
        "autor": "Stephen Hawking",
        "editorial": "Bantam Books",
        "sinopsis": "Explicación accesible de los grandes conceptos de la cosmología y la física moderna.",
        "anio_publicacion": 1988,
        "numero_paginas": 212,
        "precio": 280.00,
        "ubicacion": "B-01-02",
        "numero_copias": 4,
        "categoria": "Ciencia",
        "estado": EstadoLibro.disponible,
    },
    {
        "ISBN": "978-0-14-028038-8",
        "titulo": "El origen de las especies",
        "autor": "Charles Darwin",
        "editorial": "Penguin Classics",
        "sinopsis": "Obra fundacional de la biología evolutiva que presenta la teoría de la selección natural.",
        "anio_publicacion": 1859,
        "numero_paginas": 703,
        "precio": 310.00,
        "ubicacion": "B-02-01",
        "numero_copias": 2,
        "categoria": "Ciencia",
        "estado": EstadoLibro.disponible,
    },
    {
        "ISBN": "978-0-7432-7356-5",
        "titulo": "Cosmos: Una odisea personal",
        "autor": "Carl Sagan",
        "editorial": "Ballantine Books",
        "sinopsis": "Exploración del universo, la ciencia y el lugar de la humanidad en el cosmos.",
        "anio_publicacion": 1980,
        "numero_paginas": 365,
        "precio": 360.00,
        "ubicacion": "B-01-03",
        "numero_copias": 3,
        "categoria": "Ciencia",
        "estado": EstadoLibro.prestado,
    },
    # Historia
    {
        "ISBN": "978-0-679-41714-7",
        "titulo": "Sapiens: De animales a dioses",
        "autor": "Yuval Noah Harari",
        "editorial": "Harper",
        "sinopsis": "Historia de la humanidad desde el Homo sapiens primitivo hasta la era moderna.",
        "anio_publicacion": 2011,
        "numero_paginas": 443,
        "precio": 390.00,
        "ubicacion": "C-01-01",
        "numero_copias": 5,
        "categoria": "Historia",
        "estado": EstadoLibro.disponible,
    },
    {
        "ISBN": "978-0-06-196436-2",
        "titulo": "Homo Deus: Breve historia del mañana",
        "autor": "Yuval Noah Harari",
        "editorial": "Harper",
        "sinopsis": "Exploración del futuro de la humanidad en la era de la inteligencia artificial y la biotecnología.",
        "anio_publicacion": 2015,
        "numero_paginas": 464,
        "precio": 400.00,
        "ubicacion": "C-01-02",
        "numero_copias": 4,
        "categoria": "Historia",
        "estado": EstadoLibro.disponible,
    },
    # Filosofía
    {
        "ISBN": "978-0-14-044913-6",
        "titulo": "La república",
        "autor": "Platón",
        "editorial": "Penguin Classics",
        "sinopsis": "Diálogo sobre la justicia, el orden político y el carácter de la ciudad justa.",
        "anio_publicacion": 1974,
        "numero_paginas": 416,
        "precio": 320.00,
        "ubicacion": "D-01-01",
        "numero_copias": 2,
        "categoria": "Filosofía",
        "estado": EstadoLibro.disponible,
    },
    {
        "ISBN": "978-84-204-8144-0",
        "titulo": "Así habló Zaratustra",
        "autor": "Friedrich Nietzsche",
        "editorial": "Alianza Editorial",
        "sinopsis": "Obra filosófica que introduce conceptos como el superhombre, el eterno retorno y la voluntad de poder.",
        "anio_publicacion": 1883,
        "numero_paginas": 344,
        "precio": 290.00,
        "ubicacion": "D-01-02",
        "numero_copias": 1,
        "categoria": "Filosofía",
        "estado": EstadoLibro.perdido,
    },
    {
        "ISBN": "978-84-450-7289-2",
        "titulo": "Historia de la filosofía occidental",
        "autor": "Bertrand Russell",
        "editorial": "Austral",
        "sinopsis": "Panorama completo del pensamiento filosófico desde los presocráticos hasta el siglo XX.",
        "anio_publicacion": 1945,
        "numero_paginas": 798,
        "precio": 580.00,
        "ubicacion": "D-02-01",
        "numero_copias": 2,
        "categoria": "Filosofía",
        "estado": EstadoLibro.mantenimiento,
    },
    # Tecnología
    {
        "ISBN": "978-0-13-468599-1",
        "titulo": "El lenguaje de programación C",
        "autor": "Brian W. Kernighan, Dennis M. Ritchie",
        "editorial": "Prentice Hall",
        "sinopsis": "El texto de referencia definitivo para el lenguaje C, escrito por sus propios creadores.",
        "anio_publicacion": 1978,
        "numero_paginas": 272,
        "precio": 520.00,
        "ubicacion": "E-01-01",
        "numero_copias": 2,
        "categoria": "Tecnología",
        "estado": EstadoLibro.disponible,
    },
    {
        "ISBN": "978-0-201-63361-0",
        "titulo": "The Pragmatic Programmer",
        "autor": "Andrew Hunt, David Thomas",
        "editorial": "Addison-Wesley",
        "sinopsis": "Guía esencial de prácticas y principios para el desarrollo de software profesional.",
        "anio_publicacion": 1999,
        "numero_paginas": 352,
        "precio": 680.00,
        "ubicacion": "E-01-02",
        "numero_copias": 3,
        "categoria": "Tecnología",
        "estado": EstadoLibro.disponible,
    },
    {
        "ISBN": "978-0-13-235088-4",
        "titulo": "Clean Code",
        "autor": "Robert C. Martin",
        "editorial": "Prentice Hall",
        "sinopsis": "Principios, patrones y prácticas para escribir código limpio, legible y mantenible.",
        "anio_publicacion": 2008,
        "numero_paginas": 431,
        "precio": 750.00,
        "ubicacion": "E-01-03",
        "numero_copias": 2,
        "categoria": "Tecnología",
        "estado": EstadoLibro.disponible,
    },
]


def seed_db() -> None:
    """Inserta datos iniciales solo si la BD está vacía. Idempotente."""
    if db.session.get(Usuario, "admin") is not None:
        return

    logger.info("BD vacía — ejecutando seed inicial")

    for data in _USUARIOS:
        hashed = bcrypt.generate_password_hash(data["password"], rounds=12).decode("utf-8")
        db.session.add(Usuario(
            usuario=data["usuario"],
            contrasena=hashed,
            nombre=data["nombre"],
            email=data["email"],
        ))

    for data in _LIBROS:
        db.session.add(Libro(**data))

    db.session.commit()
    logger.info("Seed completado: %d usuarios, %d libros", len(_USUARIOS), len(_LIBROS))
