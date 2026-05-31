
-- =========================================================
-- DATOS DE PRUEBA PARA EL SISTEMA HOTEL (ACTUALIZADO)
-- =========================================================

SET search_path TO hotel;

INSERT INTO persona (
    id_persona,primer_nombre,segundo_nombre,primer_apellido,segundo_apellido,email,calle,carrera,numero
)
VALUES
(1012345678,'Juan','Carlos','Pérez','Gómez','juan@email.com','Calle 10','Carrera 5','20-15'),
(1023456789,'María','Fernanda','López','Ruiz','maria@email.com','Calle 15','Carrera 8','10-20'),
(1034567890,'Pedro','Andrés','Ramírez','Díaz','pedro@email.com','Calle 20','Carrera 12','15-30'),
(1045678901,'Laura','Sofía','García','Martínez','laura@email.com','Calle 25','Carrera 7','18-12'),
(1056789012,'Camilo','Esteban','Torres','Moreno','camilo@email.com','Calle 8','Carrera 14','22-18'),
(1067890123,'Ana','Lucía','Castro','Vega','ana@email.com','Calle 3','Carrera 2','11-09'),
(1078901234,'Luis','Fernando','Herrera','Jiménez','luis@email.com','Calle 40','Carrera 9','33-44');

INSERT INTO telefono (id_persona, telefono)
VALUES
(1012345678,'3001111111'),
(1012345678,'3012222222'),
(1023456789,'3023333333'),
(1034567890,'3034444444'),
(1045678901,'3045555555'),
(1056789012,'3056666666'),
(1067890123,'3067777777'),
(1078901234,'3078888888');

INSERT INTO cliente (id_persona)
VALUES
(1012345678),
(1034567890),
(1045678901),
(1056789012);

INSERT INTO empleado (id_persona,cargo,area)
VALUES
(1023456789,'Recepcionista','Recepción'),
(1067890123,'Administrador','Administración'),
(1078901234,'Botones','Servicio');

INSERT INTO habitacion (numero_h,tipo,estado,precio_noche)
VALUES
(101,'Sencilla','Disponible',120000),
(102,'Doble','Disponible',180000),
(103,'Suite','Ocupada',350000),
(104,'Sencilla','Mantenimiento',110000),
(105,'Doble','Disponible',200000),
(106,'Suite','Disponible',400000);

INSERT INTO reserva (
    id_reserva,id_cliente,numero_h,fecha_llegada,fecha_salida,valor_reserva,tiempo_maxc
)
VALUES
(1,1012345678,101,'2026-05-20','2026-05-25',600000,24),
(2,1034567890,102,'2026-05-21','2026-05-24',540000,24),
(3,1045678901,103,'2026-05-10','2026-05-15',1750000,24),
(4,1012345678,105,'2026-06-01','2026-06-05',800000,24),
(5,1056789012,106,'2026-05-28','2026-06-02',2000000,24);

INSERT INTO servicio (
    id_servicio,nombre,descripcion,costo,estado
)
VALUES
(1,'Lavandería','Lavado y planchado de ropa',25000,'Activo'),
(2,'Spa','Masajes y relajación',80000,'Activo'),
(3,'Room Service','Servicio a la habitación',45000,'Activo'),
(4,'Transporte','Servicio aeropuerto-hotel',60000,'Activo'),
(5,'Gimnasio','Acceso al gimnasio',20000,'Inactivo');

INSERT INTO consumo (
    id_consumo,id_reserva,id_servicio,fecha_hora
)
VALUES
(1,1,1,'2026-05-21 10:30:00'),
(2,1,3,'2026-05-22 08:15:00'),
(3,2,2,'2026-05-22 16:45:00'),
(4,2,4,'2026-05-23 09:00:00'),
(5,3,3,'2026-05-11 20:10:00'),
(6,4,1,'2026-06-02 11:20:00'),
(7,5,2,'2026-05-29 14:00:00'),
(8,5,3,'2026-05-30 19:40:00');

SELECT * FROM cliente;
SELECT * FROM empleado;
SELECT * FROM habitacion;
SELECT * FROM reserva;
SELECT * FROM servicio;
SELECT * FROM consumo;
