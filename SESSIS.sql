-- Crear base de datos
CREATE DATABASE SESSIS;
GO

USE SESSIS;
GO

-- ==============================
-- TABLA ROLES
-- ==============================
CREATE TABLE Roles (
    id_rol INT PRIMARY KEY IDENTITY(1,1),
    nombre_rol VARCHAR(100) NOT NULL,
    descripcion VARCHAR(250)
);

-- ==============================
-- TABLA UBICACIONES
-- ==============================
CREATE TABLE Ubicaciones (
    id_ubicacion INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(200) NOT NULL, 
    tipo VARCHAR(50),                    
    direccion VARCHAR(250) NOT NULL,
    imagen_url VARCHAR(500) NULL
);

-- ==============================
-- TABLA EMPLEADO
-- ==============================
CREATE TABLE Empleado (
    id_empleado INT PRIMARY KEY IDENTITY(1,1),
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    cedula VARCHAR(50) NOT NULL UNIQUE,
    telefono VARCHAR(50),
    direccion VARCHAR(250),
    fecha_contratacion DATE NOT NULL,
    estado BIT NOT NULL DEFAULT 1
);

-- ==============================
-- TABLA CLIENTES
-- ==============================
CREATE TABLE Clientes (
    id_cliente INT PRIMARY KEY IDENTITY(1,1),
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    cedula VARCHAR(50) NOT NULL UNIQUE,
    telefono VARCHAR(50),
    id_ubicacion INT,
    estado BIT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_ubicacion) REFERENCES Ubicaciones(id_ubicacion)
);

-- ==============================
-- TABLA INVENTARIO
-- ==============================
CREATE TABLE Inventario (
    id_inventario VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion VARCHAR(250),
    estado VARCHAR(50),
    id_ubicacion INT NOT NULL,
    FOREIGN KEY (id_ubicacion) REFERENCES Ubicaciones(id_ubicacion)
);

-- ==============================
-- TABLA USUARIOS
-- ==============================
CREATE TABLE Usuarios (
    id_usuario INT PRIMARY KEY IDENTITY(1,1),
    id_empleado INT NOT NULL,
    id_rol INT NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(150) NOT NULL,
    estado VARCHAR(50),
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado),
    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol)
);

-- ==============================
-- TABLA REPORTE INCIDENTES
-- ==============================
CREATE TABLE dbo.ReporteIncidentes (
    id_reporte     INT IDENTITY(1,1) NOT NULL
                   CONSTRAINT PK_ReporteIncidentes PRIMARY KEY,
    id_empleado    INT NOT NULL,            -- FK a dbo.Empleados(id_empleado)
    categoria      VARCHAR(50) NOT NULL,    -- valores controlados (ver CHECK)
    descripcion    NVARCHAR(1000) NOT NULL,
    fecha_evento   DATE NOT NULL,
    foto           NVARCHAR(400) NULL,      -- ruta relativa en /media (ImageField)
    creado_por     NVARCHAR(150) NULL,
    creado_en      DATETIME2(0) NOT NULL
                   CONSTRAINT DF_ReporteIncidentes_creado_en DEFAULT SYSDATETIME()
);
ADD CONSTRAINT FK_ReporteIncidentes_Empleados
      FOREIGN KEY (id_empleado) REFERENCES dbo.Empleados(id_empleado);

-- CHECK de categorías válidas (ajusta si necesitas más)
  ADD CONSTRAINT CK_ReporteIncidentes_Categoria
      CHECK (categoria IN (
          'accidente-trabajo',
          'fallo-equipamiento',
          'incidente-seguridad',
          'problema-ambiental',
          'otros-eventos'
      ));

-- Índices útiles
CREATE INDEX IX_ReporteIncidentes_Empleado ON dbo.ReporteIncidentes (id_empleado);
CREATE INDEX IX_ReporteIncidentes_Fecha   ON dbo.ReporteIncidentes (fecha_evento DESC);
GO

-- ==============================
-- TABLA ASISTENCIA
-- ==============================
CREATE TABLE Asistencia (
    id_asistencia INT PRIMARY KEY IDENTITY(1,1),
    id_empleado INT NOT NULL,
    turno_ingreso DATETIME NOT NULL,
    turno_salida DATETIME,
    id_ubicacion INT NOT NULL,
    observaciones VARCHAR(250),
    estado VARCHAR(50),
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado),
    FOREIGN KEY (id_ubicacion) REFERENCES Ubicaciones(id_ubicacion)
);

-- ==============================
-- TABLA HORAS EXTRAS
-- ==============================
CREATE TABLE HorasExtras (
    id_hora_extra INT PRIMARY KEY IDENTITY(1,1),
    id_empleado INT NOT NULL,
    fecha DATE NOT NULL,
    cantidad_horas INT NOT NULL,
    justificacion VARCHAR(250),
    estado VARCHAR(50),
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado)
);

-- ==============================
-- TABLA CITAS
-- ==============================
CREATE TABLE Citas (
    id_cita INT PRIMARY KEY IDENTITY(1,1),
    id_cliente INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_cita DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_finalizacion TIME,
    motivo VARCHAR(200),
    descripcion VARCHAR(250),

    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);
GO

-- ==============================
-- TABLAS DE AUDITORIA
-- ==============================


USE [SESSIS];
GO

CREATE TABLE [dbo].[Clientes_Auditoria_TB](
    [id_auditoria] INT IDENTITY(1,1) NOT NULL,
    [cliente_id] INT NULL,
    [usuario_id] INT NULL,
    [usuario_email] NVARCHAR(255) NULL,
    [accion] NVARCHAR(50) NOT NULL,
    [fecha] DATETIME NULL CONSTRAINT DF_ClientesAuditoria_Fecha DEFAULT (GETDATE()),
    [nombre_completo] NVARCHAR(255) NULL,
    [email] NVARCHAR(150) NULL,
    [cedula] NVARCHAR(50) NULL,
    [telefono] NVARCHAR(50) NULL,
    [residencia] NVARCHAR(255) NULL,

    CONSTRAINT PK_Clientes_Auditoria PRIMARY KEY CLUSTERED (id_auditoria ASC),

    -- FK al cliente
    CONSTRAINT FK_ClientesAuditoria_Cliente 
        FOREIGN KEY ([cliente_id]) 
        REFERENCES [dbo].[Clientes] ([id_cliente])
        ON DELETE SET NULL,

    -- FK al usuario que realiza la acción
    CONSTRAINT FK_ClientesAuditoria_Usuario 
        FOREIGN KEY ([usuario_id]) 
        REFERENCES [dbo].[Usuarios] ([id_usuario])
        ON DELETE SET NULL
);
GO


CREATE TABLE [dbo].[Usuarios_Auditoria_TB](
    [id_auditoria] INT IDENTITY(1,1) NOT NULL,         
    [usuario_afectado_id] INT NULL,
    [usuario_accion_id]   INT NULL,
    [accion] NVARCHAR(50) NOT NULL,                     
    [fecha] DATETIME NOT NULL DEFAULT(GETDATE()),       
    [id_empleado] INT NULL,                              
    [id_rol] INT NULL,
    [email] NVARCHAR(150) NULL,
    [estado] NVARCHAR(50) NULL,

    CONSTRAINT PK_Usuarios_Auditoria PRIMARY KEY CLUSTERED (id_auditoria ASC),

    -- FK: Usuario afectado
    CONSTRAINT FK_UsuariosAuditoria_UsuarioAfectado 
        FOREIGN KEY ([usuario_afectado_id]) 
        REFERENCES [dbo].[Usuarios] ([id_usuario]),

    -- FK: Usuario que realiza la acción
    CONSTRAINT FK_UsuariosAuditoria_UsuarioAccion 
        FOREIGN KEY ([usuario_accion_id]) 
        REFERENCES [dbo].[Usuarios] ([id_usuario])
);
GO


CREATE TABLE dbo.Empleados_Auditoria_TB (
    id_auditoria       INT IDENTITY(1,1) PRIMARY KEY,
    empleado_id        INT NULL,             
    usuario_id         INT NULL,              
    usuario_email      VARCHAR(255) NULL,     
    accion             VARCHAR(50) NOT NULL,  
    fecha              DATETIME NOT NULL CONSTRAINT DF_EMP_AUD_fecha DEFAULT (GETDATE()),

    -- Snapshot de datos del empleado al momento de la acción
    nombre_completo    NVARCHAR(255) NULL,
    email              NVARCHAR(150) NULL,
    cedula             NVARCHAR(50)  NULL,
    telefono           NVARCHAR(50)  NULL,
    direccion          NVARCHAR(255) NULL,
    fecha_contratacion DATE          NULL,

    -- Llave foránea al empleado
    CONSTRAINT FK_EmplAud_Empleado 
        FOREIGN KEY (empleado_id) 
        REFERENCES dbo.Empleado(id_empleado)
        ON DELETE SET NULL,

    -- Llave foránea al usuario
    CONSTRAINT FK_EmplAud_Usuario 
        FOREIGN KEY (usuario_id) 
        REFERENCES dbo.Usuarios(id_usuario)
        ON DELETE SET NULL
);
GO


CREATE TABLE dbo.HorasExtras_Auditoria_TB
(
    id_auditoria      INT IDENTITY(1,1) PRIMARY KEY,
    hora_extra_id     INT            NULL,
    empleado_id       INT            NULL,
    usuario_email     VARCHAR(255)   NULL,
    accion            VARCHAR(50)    NOT NULL,      -- CREAR / MODIFICAR / ELIMINAR
    fecha             DATETIME2(0)   NOT NULL DEFAULT SYSUTCDATETIME(),
    -- snapshot
    empleado_nombre   VARCHAR(255)   NULL,
    empleado_cedula   VARCHAR(50)    NULL,
    fecha_registro    DATE           NULL,
    cantidad_horas    DECIMAL(5,2)   NULL,
    justificacion     VARCHAR(MAX)   NULL,
    estado            VARCHAR(50)    NULL,

    -- Foreign Keys
    CONSTRAINT FK_HX_AUD_HX  FOREIGN KEY (hora_extra_id) REFERENCES dbo.HorasExtras(id_hora_extra),
    CONSTRAINT FK_HX_AUD_EMP FOREIGN KEY (empleado_id)   REFERENCES dbo.Empleado(id_empleado)
);
GO


-- ==========================================
-- INSERTS PARA EMPLEADO
-- ==========================================
INSERT INTO Empleado (nombre_completo, email, cedula, telefono, direccion, fecha_contratacion)
VALUES ('Juan Pablo Solis Benamburg', 'juanpablops04@outlook.com', '118330293', '84433060', 'Fidelitas', CAST(GETDATE() AS DATE));

INSERT INTO Empleado (nombre_completo, email, cedula, telefono, direccion, fecha_contratacion)
VALUES ('Luis Anthony Rodriguez Jimenez', 'anthorj76@gmail.com', '119224578', '55556666', 'Fidelitas', CAST(GETDATE() AS DATE));

INSERT INTO Empleado (nombre_completo, email, cedula, telefono, direccion, fecha_contratacion)
VALUES ('Stwart Jafet Guerrero Fernandez', 'sgf.oficial08@gmail.com', '120224158', '66665555', 'Fidelitas', CAST(GETDATE() AS DATE));

-- Empleado inventado
INSERT INTO Empleado (nombre_completo, email, cedula, telefono, direccion, fecha_contratacion)
VALUES ('Carolina Mendez Chavarria', 'carolinamc@example.com', '121558899', '77774444', 'San José Centro', CAST(GETDATE() AS DATE));


-- ==========================================
-- INSERTS PARA ROLES
-- ==========================================
INSERT INTO Roles (nombre_rol, descripcion)
VALUES ('Administrador', 'Acceso total al sistema, incluyendo gestión de usuarios, roles y configuraciones.');

INSERT INTO Roles (nombre_rol, descripcion)
VALUES ('Oficial', 'Acceso restringido, puede registrar asistencia, incidentes y reportes.');


-- ==========================================
-- INSERTS PARA USUARIOS
-- (Relaciona cada empleado con su rol)
-- ==========================================
-- NOTA: Aquí supongo que los IDs se generan con IDENTITY en Empleado y Roles.
--       Debes revisar los IDs reales después de insertar, o usar SELECT SCOPE_IDENTITY().

-- Los primeros 3 empleados con rol Administrador
INSERT INTO Usuarios (id_empleado, id_rol, email, password, estado)
VALUES (1, 1, 'juanpablops04@outlook.com', '123', 'Activo');

INSERT INTO Usuarios (id_empleado, id_rol, email, password, estado)
VALUES (2, 1, 'anthorj76@gmail.com', '123', 'Activo');

INSERT INTO Usuarios (id_empleado, id_rol, email, password, estado)
VALUES (3, 1, 'sgf.oficial08@gmail.com', '123', 'Activo');

-- El empleado inventado con rol Oficial
INSERT INTO Usuarios (id_empleado, id_rol, email, password, estado)
VALUES (4, 2, 'carolinamc@example.com', 'securePass2024!', 'Activo');