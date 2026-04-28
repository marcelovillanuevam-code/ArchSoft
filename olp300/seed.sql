-- seed.sql — OLP300 Catálogo de Libros
-- Ejecutar: mysql -u olp300_user -p olp300 < seed.sql
--
-- ⚠️  IMPORTANTE — CONTRASEÑAS EN TEXTO PLANO
-- Los valores de `contrasena` a continuación son marcadores de posición.
-- Antes de la demo o de cualquier despliegue, Sergio debe ejecutar el script
-- de hashing (scripts/hash_passwords.py o equivalente) para reemplazar cada
-- 'REEMPLAZAR_CON_HASH' con el hash bcrypt correspondiente (cost factor 12).
-- NUNCA insertar contraseñas en texto plano en producción.
-- ---------------------------------------------------------------

-- ---------------------------------------------------------------
-- USUARIOS
-- Credenciales de prueba (solo para el equipo):
--   admin        / Admin2024!
--   ernesto      / Ernesto2024!
--   santiago     / Santiago2024!
-- ---------------------------------------------------------------
INSERT INTO usuarios (usuario, contrasena, nombre, email) VALUES
(
    'admin',
    '$2b$12$/yyWVI8VEtPGfklVjqAQIu32Yvn.5yN7T7aISJ7YWlUkD9vT0I6Hi', -- bcrypt cost=12
    'Administrador',
    'admin@biblioteca.udem.mx'
),
(
    'ernesto',
    '$2b$12$.M9.o9aJEtTrfFINK5hAsee85.DXFmSyT4d.L7479lO6hmE7KwIWy', -- bcrypt cost=12
    'Ernesto Vega',
    'ernesto.vega@udem.edu'
),
(
    'santiago',
    '$2b$12$cZyX2086OhIbvxm1j0HS5.quCJcWCd91US4c2ZOM4GLbadsEN6lba', -- bcrypt cost=12
    'Santiago Pongutá',
    'santiago.ponguta@udem.edu'
);

-- ---------------------------------------------------------------
-- LIBROS — 15 registros con categorías y estados variados
-- ---------------------------------------------------------------
INSERT INTO libros
    (ISBN, titulo, autor, editorial, sinopsis,
     anio_publicacion, numero_paginas, precio,
     ubicacion, numero_copias, categoria, estado)
VALUES

-- Ficción (4)
(
    '978-0-06-112008-4',
    'Cien años de soledad',
    'Gabriel García Márquez',
    'Harper Perennial',
    'La saga de la familia Buendía en el pueblo ficticio de Macondo, mezcla de realismo y magia.',
    1967, 417, 350.00, 'A-01-03', 3, 'Ficción', 'disponible'
),
(
    '978-0-14-028329-7',
    'El nombre de la rosa',
    'Umberto Eco',
    'Vintage',
    'Un thriller medieval ambientado en una abadía italiana del siglo XIV donde ocurren misteriosos crímenes.',
    1980, 502, 420.00, 'A-02-01', 2, 'Ficción', 'prestado'
),
(
    '978-84-376-0494-7',
    'Don Quijote de la Mancha',
    'Miguel de Cervantes Saavedra',
    'Cátedra',
    'Las aventuras del ingenioso hidalgo don Quijote y su fiel escudero Sancho Panza.',
    1605, 863, 450.00, 'A-03-02', 3, 'Ficción', 'mantenimiento'
),
(
    '978-0-14-118776-1',
    '1984',
    'George Orwell',
    'Penguin Books',
    'Distopía sobre un régimen totalitario que ejerce vigilancia absoluta sobre sus ciudadanos.',
    1949, 328, 250.00, 'A-02-03', 4, 'Ficción', 'disponible'
),

-- Ciencia (3)
(
    '978-0-06-093546-9',
    'Una breve historia del tiempo',
    'Stephen Hawking',
    'Bantam Books',
    'Explicación accesible de los grandes conceptos de la cosmología y la física moderna.',
    1988, 212, 280.00, 'B-01-02', 4, 'Ciencia', 'disponible'
),
(
    '978-0-14-028038-8',
    'El origen de las especies',
    'Charles Darwin',
    'Penguin Classics',
    'Obra fundacional de la biología evolutiva que presenta la teoría de la selección natural.',
    1859, 703, 310.00, 'B-02-01', 2, 'Ciencia', 'disponible'
),
(
    '978-0-7432-7356-5',
    'Cosmos: Una odisea personal',
    'Carl Sagan',
    'Ballantine Books',
    'Exploración del universo, la ciencia y el lugar de la humanidad en el cosmos.',
    1980, 365, 360.00, 'B-01-03', 3, 'Ciencia', 'prestado'
),

-- Historia (2)
(
    '978-0-679-41714-7',
    'Sapiens: De animales a dioses',
    'Yuval Noah Harari',
    'Harper',
    'Historia de la humanidad desde el Homo sapiens primitivo hasta la era moderna.',
    2011, 443, 390.00, 'C-01-01', 5, 'Historia', 'disponible'
),
(
    '978-0-06-196436-2',
    'Homo Deus: Breve historia del mañana',
    'Yuval Noah Harari',
    'Harper',
    'Exploración del futuro de la humanidad en la era de la inteligencia artificial y la biotecnología.',
    2015, 464, 400.00, 'C-01-02', 4, 'Historia', 'disponible'
),

-- Filosofía (3)
(
    '978-0-14-044913-6',
    'La república',
    'Platón',
    'Penguin Classics',
    'Diálogo sobre la justicia, el orden político y el carácter de la ciudad justa.',
    1974, 416, 320.00, 'D-01-01', 2, 'Filosofía', 'disponible'
),
(
    '978-84-204-8144-0',
    'Así habló Zaratustra',
    'Friedrich Nietzsche',
    'Alianza Editorial',
    'Obra filosófica que introduce conceptos como el superhombre, el eterno retorno y la voluntad de poder.',
    1883, 344, 290.00, 'D-01-02', 1, 'Filosofía', 'perdido'
),
(
    '978-84-450-7289-2',
    'Historia de la filosofía occidental',
    'Bertrand Russell',
    'Austral',
    'Panorama completo del pensamiento filosófico desde los presocráticos hasta el siglo XX.',
    1945, 798, 580.00, 'D-02-01', 2, 'Filosofía', 'mantenimiento'
),

-- Tecnología (3)
(
    '978-0-13-468599-1',
    'El lenguaje de programación C',
    'Brian W. Kernighan, Dennis M. Ritchie',
    'Prentice Hall',
    'El texto de referencia definitivo para el lenguaje C, escrito por sus propios creadores.',
    1978, 272, 520.00, 'E-01-01', 2, 'Tecnología', 'disponible'
),
(
    '978-0-201-63361-0',
    'The Pragmatic Programmer',
    'Andrew Hunt, David Thomas',
    'Addison-Wesley',
    'Guía esencial de prácticas y principios para el desarrollo de software profesional.',
    1999, 352, 680.00, 'E-01-02', 3, 'Tecnología', 'disponible'
),
(
    '978-0-13-235088-4',
    'Clean Code',
    'Robert C. Martin',
    'Prentice Hall',
    'Principios, patrones y prácticas para escribir código limpio, legible y mantenible.',
    2008, 431, 750.00, 'E-01-03', 2, 'Tecnología', 'disponible'
);
