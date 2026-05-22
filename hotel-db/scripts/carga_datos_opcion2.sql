SET search_path TO Hotel;

-- PERSONAS
COPY persona (id_persona, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, calle, carrera, numero)
FROM '/ruta/a/tus/archivos/persona.csv'
DELIMITER ','
CSV HEADER;

-- TELEFONOS
COPY telefono (id_persona, telefono)
FROM '/ruta/a/tus/archivos/telefono.csv'
DELIMITER ','
CSV HEADER;

-- CLIENTES
COPY cliente (id_cliente, id_persona)
FROM '/ruta/a/tus/archivos/cliente.csv'
DELIMITER ','
CSV HEADER;

-- EMPLEADOS
COPY empleado (id_empleado, id_persona, cargo, area)
FROM '/ruta/a/tus/archivos/empleado.csv'
DELIMITER ','
CSV HEADER;

-- HABITACIONES
COPY habitacion (numero_h, tipo, estado, precio_noche)
FROM '/ruta/a/tus/archivos/habitacion.csv'
DELIMITER ','
CSV HEADER;

-- RESERVAS
COPY reserva (id_reserva, id_cliente, numero_h, fecha_llegada, fecha_salida, valor_reserva, tiempo_maxc)
FROM '/ruta/a/tus/archivos/reserva.csv'
DELIMITER ','
CSV HEADER;

-- SERVICIOS
COPY servicio (id_servicio, nombre, descripcion, costo, estado)
FROM '/ruta/a/tus/archivos/servicio.csv'
DELIMITER ','
CSV HEADER;

-- CONSUMOS
COPY consumo (id_consumo, id_reserva, id_servicio, fecha_hora)
FROM '/ruta/a/tus/archivos/consumo.csv'
DELIMITER ','
CSV HEADER;
