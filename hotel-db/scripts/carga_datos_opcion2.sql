-- =========================================================
-- CARGA DE DATOS USANDO RUTAS RELATIVAS (\copy)
-- =========================================================
SET search_path TO hotel;

-- PERSONAS
\copy persona(id_persona, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, calle, carrera, numero) FROM '../data/persona.csv' DELIMITER ',' CSV HEADER;

-- TELEFONOS
\copy telefono(id_telefono, id_persona, telefono) FROM '../data/telefono.csv' DELIMITER ',' CSV HEADER;

-- CLIENTES
\copy cliente(id_persona) FROM '../data/cliente.csv' DELIMITER ',' CSV HEADER;

-- EMPLEADOS
\copy empleado(id_persona, cargo, area) FROM '../data/empleado.csv' DELIMITER ',' CSV HEADER;

-- HABITACIONES
\copy habitacion(numero_h, tipo, estado, precio_noche) FROM '../data/habitacion.csv' DELIMITER ',' CSV HEADER;

-- RESERVAS
\copy reserva(id_reserva, id_cliente, numero_h, fecha_llegada, fecha_salida, valor_reserva, tiempo_maxc) FROM '../data/reserva.csv' DELIMITER ',' CSV HEADER;

-- SERVICIOS
\copy servicio(id_servicio, nombre, descripcion, costo, estado) FROM '../data/servicio.csv' DELIMITER ',' CSV HEADER;

-- CONSUMOS
\copy consumo(id_consumo, id_reserva, id_servicio, fecha_hora) FROM '../data/consumo.csv' DELIMITER ',' CSV HEADER;