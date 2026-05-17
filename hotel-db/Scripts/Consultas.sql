-- =========================================================
-- CONSULTAS / OPERACIONES SOLICITADAS
-- =========================================================

-- 1) Gestiona información de clientes y reservas (insertar, actualizar, consultar)

-- Insertar cliente (ejemplo)
INSERT INTO persona (
    primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, calle, carrera, numero
) VALUES (
    'Juan', 'Carlos', 'Pérez', 'Gómez', 'juan.perez@email.com', 'Calle 10', 'Carrera 5', '20-15'
)
ON CONFLICT (email) DO NOTHING;

INSERT INTO cliente (id_persona)
SELECT id_persona
FROM persona
WHERE email = 'juan.perez@email.com'
ON CONFLICT (id_persona) DO NOTHING;

INSERT INTO telefono (id_persona, telefono)
SELECT id_persona, '3001234567'
FROM persona
WHERE email = 'juan.perez@email.com'
ON CONFLICT DO NOTHING;

-- Consultar clientes con sus datos
SELECT
    c.id_cliente,
    p.id_persona,
    TRIM(CONCAT_WS(' ', p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido)) AS nombre_completo,
    p.email,
    p.calle,
    p.carrera,
    p.numero
FROM cliente c
JOIN persona p ON p.id_persona = c.id_persona;

-- Consultar cliente con teléfonos
SELECT
    c.id_cliente,
    p.id_persona,
    TRIM(CONCAT_WS(' ', p.primer_nombre, p.primer_apellido)) AS cliente,
    t.telefono
FROM cliente c
JOIN persona p ON p.id_persona = c.id_persona
LEFT JOIN telefono t ON t.id_persona = p.id_persona
ORDER BY c.id_cliente;

-- Actualizar datos de un cliente
UPDATE persona p
SET email = 'nuevo.correo@email.com',
    calle = 'Calle 20',
    carrera = 'Carrera 8',
    numero = '30-22'
FROM cliente c
WHERE c.id_persona = p.id_persona
  AND c.id_cliente = 1;

-- Insertar una reserva
INSERT INTO reserva (
    id_cliente, numero_h, fecha_llegada, fecha_salida, valor_reserva, tiempo_maxc
) VALUES (
    1, 101, '2026-05-20', '2026-05-25', 750000, 24
);

-- Consultar reservas de un cliente
SELECT
    r.id_reserva,
    r.fecha_llegada,
    r.fecha_salida,
    r.valor_reserva,
    r.tiempo_maxc,
    h.numero_h,
    h.tipo,
    h.estado
FROM reserva r
JOIN habitacion h ON h.numero_h = r.numero_h
WHERE r.id_cliente = 1
ORDER BY r.fecha_llegada DESC;

-- 2) Consulta disponibilidad y estado de habitaciones

-- Habitaciones disponibles para un rango de fechas
-- Cambia las fechas según necesites
SELECT
    h.numero_h,
    h.tipo,
    h.estado,
    h.precio_noche
FROM habitacion h
WHERE h.estado = 'Disponible'
  AND NOT EXISTS (
      SELECT 1
      FROM reserva r
      WHERE r.numero_h = h.numero_h
        AND r.fecha_llegada <= DATE '2026-05-25'
        AND r.fecha_salida  >= DATE '2026-05-20'
  )
ORDER BY h.numero_h;

-- Consultar estado actual de todas las habitaciones
SELECT
    numero_h,
    tipo,
    estado,
    precio_noche
FROM habitacion
ORDER BY numero_h;

-- Actualizar estado de una habitación
UPDATE habitacion
SET estado = 'Mantenimiento'
WHERE numero_h = 101;

-- Marcar habitación como ocupada
UPDATE habitacion
SET estado = 'Ocupada'
WHERE numero_h = 101;

-- 3) Consulta y actualiza el estado de las habitaciones asignadas

-- Ver habitaciones asignadas a reservas activas
SELECT
    r.id_reserva,
    r.id_cliente,
    r.numero_h,
    r.fecha_llegada,
    r.fecha_salida,
    h.estado
FROM reserva r
JOIN habitacion h ON h.numero_h = r.numero_h
WHERE CURRENT_DATE BETWEEN r.fecha_llegada AND r.fecha_salida;

-- Liberar una habitación al finalizar la reserva
UPDATE habitacion
SET estado = 'Disponible'
WHERE numero_h = 101;

-- Consulta habitaciones con reserva vencida y estado aún ocupado
SELECT
    r.id_reserva,
    r.numero_h,
    r.fecha_salida,
    h.estado
FROM reserva r
JOIN habitacion h ON h.numero_h = r.numero_h
WHERE r.fecha_salida < CURRENT_DATE
  AND h.estado = 'Ocupada';

-- 4) Registrar consumos adicionales de los huéspedes

-- Registrar consumo
INSERT INTO consumo (id_reserva, id_servicio, fecha_hora)
VALUES (1, 1, NOW());

-- Consultar consumos de una reserva
SELECT
    co.id_consumo,
    co.fecha_hora,
    s.nombre AS servicio,
    s.costo
FROM consumo co
JOIN servicio s ON s.id_servicio = co.id_servicio
WHERE co.id_reserva = 1
ORDER BY co.fecha_hora DESC;

-- Total de consumos por reserva
SELECT
    co.id_reserva,
    SUM(s.costo) AS total_consumos
FROM consumo co
JOIN servicio s ON s.id_servicio = co.id_servicio
GROUP BY co.id_reserva;

-- 5) Gestiona información de empleados (insertar, actualizar, eliminar, consultar)

-- Insertar empleado (ejemplo)
INSERT INTO persona (
    primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, calle, carrera, numero
) VALUES (
    'María', 'Fernanda', 'López', 'Ruiz', 'maria.lopez@email.com', 'Calle 15', 'Carrera 12', '10-30'
)
ON CONFLICT (email) DO NOTHING;

INSERT INTO empleado (id_persona, cargo, area)
SELECT id_persona, 'Recepcionista', 'Recepción'
FROM persona
WHERE email = 'maria.lopez@email.com'
ON CONFLICT (id_persona) DO NOTHING;

-- Consultar empleados
SELECT
    e.id_empleado,
    p.id_persona,
    TRIM(CONCAT_WS(' ', p.primer_nombre, p.primer_apellido)) AS nombre_empleado,
    e.cargo,
    e.area,
    p.email
FROM empleado e
JOIN persona p ON p.id_persona = e.id_persona
ORDER BY e.id_empleado;

-- Actualizar empleado
UPDATE empleado
SET cargo = 'Supervisor',
    area = 'Administración'
WHERE id_empleado = 1;

-- Actualizar datos personales del empleado
UPDATE persona p
SET email = 'nuevo.empleado@email.com',
    calle = 'Avenida 3'
FROM empleado e
WHERE e.id_persona = p.id_persona
  AND e.id_empleado = 1;

-- Eliminar empleado
DELETE FROM empleado
WHERE id_empleado = 1;

-- 6) Administra información relacionada con los servicios ofrecidos por el hotel

-- Insertar servicio
INSERT INTO servicio (nombre, descripcion, costo, estado)
VALUES ('Lavandería', 'Servicio de lavado y planchado', 25000, 'Activo');

-- Consultar servicios
SELECT
    id_servicio,
    nombre,
    descripcion,
    costo,
    estado
FROM servicio
ORDER BY nombre;

-- Actualizar servicio
UPDATE servicio
SET descripcion = 'Lavado, planchado y doblado',
    costo = 30000
WHERE id_servicio = 1;

-- Cambiar estado del servicio
UPDATE servicio
SET estado = 'Inactivo'
WHERE id_servicio = 1;

-- Eliminar servicio
DELETE FROM servicio
WHERE id_servicio = 1;

-- 7) Consultas generales sobre clientes, reservas y consumos para análisis administrativo

-- Total de reservas por cliente
SELECT
    c.id_cliente,
    TRIM(CONCAT_WS(' ', p.primer_nombre, p.primer_apellido)) AS cliente,
    COUNT(r.id_reserva) AS total_reservas
FROM cliente c
JOIN persona p ON p.id_persona = c.id_persona
LEFT JOIN reserva r ON r.id_cliente = c.id_cliente
GROUP BY c.id_cliente, p.primer_nombre, p.primer_apellido
ORDER BY total_reservas DESC;

-- Total facturado por reservas
SELECT
    COALESCE(SUM(valor_reserva), 0) AS total_facturado_reservas
FROM reserva;

-- Total facturado por consumos adicionales
SELECT
    COALESCE(SUM(s.costo), 0) AS total_facturado_consumos
FROM consumo co
JOIN servicio s ON s.id_servicio = co.id_servicio;

-- Resumen por cliente: reservas y consumos
SELECT
    c.id_cliente,
    TRIM(CONCAT_WS(' ', p.primer_nombre, p.primer_apellido)) AS cliente,
    COUNT(DISTINCT r.id_reserva) AS reservas,
    COUNT(co.id_consumo) AS consumos,
    COALESCE(SUM(r.valor_reserva), 0) AS valor_reservas,
    COALESCE(SUM(s.costo), 0) AS valor_consumos
FROM cliente c
JOIN persona p ON p.id_persona = c.id_persona
LEFT JOIN reserva r ON r.id_cliente = c.id_cliente
LEFT JOIN consumo co ON co.id_reserva = r.id_reserva
LEFT JOIN servicio s ON s.id_servicio = co.id_servicio
GROUP BY c.id_cliente, p.primer_nombre, p.primer_apellido
ORDER BY (COALESCE(SUM(r.valor_reserva), 0) + COALESCE(SUM(s.costo), 0)) DESC;

-- Reservas activas en una fecha dada
SELECT
    r.id_reserva,
    TRIM(CONCAT_WS(' ', p.primer_nombre, p.primer_apellido)) AS cliente,
    r.numero_h,
    r.fecha_llegada,
    r.fecha_salida
FROM reserva r
JOIN cliente c ON c.id_cliente = r.id_cliente
JOIN persona p ON p.id_persona = c.id_persona
WHERE CURRENT_DATE BETWEEN r.fecha_llegada AND r.fecha_salida
ORDER BY r.fecha_llegada;

-- Consumos por rango de fechas
SELECT
    co.id_consumo,
    co.fecha_hora,
    r.id_reserva,
    s.nombre AS servicio,
    s.costo
FROM consumo co
JOIN reserva r ON r.id_reserva = co.id_reserva
JOIN servicio s ON s.id_servicio = co.id_servicio
WHERE co.fecha_hora BETWEEN TIMESTAMP '2026-05-01 00:00:00' AND TIMESTAMP '2026-05-31 23:59:59'
ORDER BY co.fecha_hora;

-- Habitaciones con más reservas
SELECT
    h.numero_h,
    h.tipo,
    COUNT(r.id_reserva) AS total_reservas
FROM habitacion h
LEFT JOIN reserva r ON r.numero_h = h.numero_h
GROUP BY h.numero_h, h.tipo
ORDER BY total_reservas DESC;
