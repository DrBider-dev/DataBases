
-- =========================================================
-- DATOS DE PRUEBA PARA EL SISTEMA HOTEL
-- =========================================================

SET search_path TO hotel;

-- =========================================================
-- PERSONAS
-- =========================================================
INSERT INTO persona (
    id_persona,
    primer_nombre,
    segundo_nombre,
    primer_apellido,
    segundo_apellido,
    email,
    calle,
    carrera,
    numero
)
VALUES
(1, 'Juan', 'Carlos', 'Pérez', 'Gómez', 'juan@email.com', 'Calle 10', 'Carrera 5', '20-15'),
(2, 'María', 'Fernanda', 'López', 'Ruiz', 'maria@email.com', 'Calle 15', 'Carrera 8', '10-20'),
(3, 'Pedro', 'Andrés', 'Ramírez', 'Díaz', 'pedro@email.com', 'Calle 20', 'Carrera 12', '15-30'),
(4, 'Laura', 'Sofía', 'García', 'Martínez', 'laura@email.com', 'Calle 25', 'Carrera 7', '18-12'),
(5, 'Camilo', 'Esteban', 'Torres', 'Moreno', 'camilo@email.com', 'Calle 8', 'Carrera 14', '22-18'),
(6, 'Ana', 'Lucía', 'Castro', 'Vega', 'ana@email.com', 'Calle 3', 'Carrera 2', '11-09'),
(7, 'Luis', 'Fernando', 'Herrera', 'Jiménez', 'luis@email.com', 'Calle 40', 'Carrera 9', '33-44');

-- =========================================================
-- TELEFONOS
-- =========================================================
INSERT INTO telefono (id_persona, telefono)
VALUES
(1, '3001111111'),
(1, '3012222222'),
(2, '3023333333'),
(3, '3034444444'),
(4, '3045555555'),
(5, '3056666666'),
(6, '3067777777'),
(7, '3078888888');

-- =========================================================
-- CLIENTES
-- =========================================================
INSERT INTO cliente (id_cliente, id_persona)
VALUES
(1, 1),
(2, 3),
(3, 4),
(4, 5);

-- =========================================================
-- EMPLEADOS
-- =========================================================
INSERT INTO empleado (
    id_empleado,
    id_persona,
    cargo,
    area
)
VALUES
(1, 2, 'Recepcionista', 'Recepción'),
(2, 6, 'Administrador', 'Administración'),
(3, 7, 'Botones', 'Servicio');

-- =========================================================
-- HABITACIONES
-- =========================================================
INSERT INTO habitacion (
    numero_h,
    tipo,
    estado,
    precio_noche
)
VALUES
(101, 'Sencilla', 'Disponible', 120000),
(102, 'Doble', 'Disponible', 180000),
(103, 'Suite', 'Ocupada', 350000),
(104, 'Sencilla', 'Mantenimiento', 110000),
(105, 'Doble', 'Disponible', 200000),
(106, 'Suite', 'Disponible', 400000);

-- =========================================================
-- RESERVAS
-- =========================================================
INSERT INTO reserva (
    id_reserva,
    id_cliente,
    numero_h,
    fecha_llegada,
    fecha_salida,
    valor_reserva,
    tiempo_maxc
)
VALUES
(1, 1, 101, '2026-05-20', '2026-05-25', 600000, 24),
(2, 2, 102, '2026-05-21', '2026-05-24', 540000, 24),
(3, 3, 103, '2026-05-10', '2026-05-15', 1750000, 24),
(4, 1, 105, '2026-06-01', '2026-06-05', 800000, 24),
(5, 4, 106, '2026-05-28', '2026-06-02', 2000000, 24);

-- =========================================================
-- SERVICIOS
-- =========================================================
INSERT INTO servicio (
    id_servicio,
    nombre,
    descripcion,
    costo,
    estado
)
VALUES
(1, 'Lavandería', 'Lavado y planchado de ropa', 25000, 'Activo'),
(2, 'Spa', 'Masajes y relajación', 80000, 'Activo'),
(3, 'Room Service', 'Servicio a la habitación', 45000, 'Activo'),
(4, 'Transporte', 'Servicio aeropuerto-hotel', 60000, 'Activo'),
(5, 'Gimnasio', 'Acceso al gimnasio', 20000, 'Inactivo');

-- =========================================================
-- CONSUMOS
-- =========================================================
INSERT INTO consumo (
    id_consumo,
    id_reserva,
    id_servicio,
    fecha_hora
)
VALUES
(1, 1, 1, '2026-05-21 10:30:00'),
(2, 1, 3, '2026-05-22 08:15:00'),
(3, 2, 2, '2026-05-22 16:45:00'),
(4, 2, 4, '2026-05-23 09:00:00'),
(5, 3, 3, '2026-05-11 20:10:00'),
(6, 4, 1, '2026-06-02 11:20:00'),
(7, 5, 2, '2026-05-29 14:00:00'),
(8, 5, 3, '2026-05-30 19:40:00');

-- =========================================================
-- VERIFICACIÓN RÁPIDA
-- =========================================================

-- Clientes
SELECT * FROM cliente;

-- Empleados
SELECT * FROM empleado;

-- Habitaciones
SELECT * FROM habitacion;

-- Reservas
SELECT * FROM reserva;

-- Servicios
SELECT * FROM servicio;

-- Consumos
SELECT * FROM consumo;
