-- schema.sql — OLP300 Catálogo de Libros
-- Ejecutar: mysql -u olp300_user -p olp300 < schema.sql
-- Eliminar primero libros (sin FK salientes) y luego usuarios

DROP TABLE IF EXISTS libros;
DROP TABLE IF EXISTS usuarios;

-- ---------------------------------------------------------------
-- TABLA: usuarios
-- ---------------------------------------------------------------
CREATE TABLE usuarios (
    usuario      VARCHAR(50)  NOT NULL,
    contrasena   VARCHAR(255) NOT NULL,
    nombre       VARCHAR(50)  NOT NULL,
    email        VARCHAR(150) NOT NULL,
    PRIMARY KEY (usuario),
    UNIQUE KEY uq_nombre (nombre),
    UNIQUE KEY uq_email  (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------
-- TABLA: libros
-- ---------------------------------------------------------------
CREATE TABLE libros (
    ISBN               VARCHAR(20)  NOT NULL,
    titulo             VARCHAR(255) NOT NULL,
    autor              VARCHAR(255) NOT NULL,
    editorial          VARCHAR(150),
    sinopsis           TEXT,
    anio_publicacion   SMALLINT,
    numero_paginas     INT,
    precio             DECIMAL(10,2),
    ubicacion          VARCHAR(100),
    numero_copias      INT,
    categoria          VARCHAR(100),
    fecha_registro     DATETIME     NOT NULL DEFAULT NOW(),
    estado             ENUM('disponible','prestado','mantenimiento','perdido')
                           NOT NULL DEFAULT 'disponible',
    PRIMARY KEY (ISBN),
    INDEX idx_titulo (titulo),
    INDEX idx_autor  (autor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
