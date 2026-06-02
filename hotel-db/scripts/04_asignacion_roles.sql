-- =========================================================
-- ASIGNACION DE ROLES Y PERMISOS
-- Hotel Database - Best practices for security and least privilege
-- =========================================================

-- ---------------------------------------------------------
-- 1. ELIMINACION DE USUARIOS EXISTENTES (si los hay)
-- ---------------------------------------------------------
DROP USER IF EXISTS cliente_01;
DROP USER IF EXISTS limpieza_01;
DROP USER IF EXISTS recepcion_01;
DROP USER IF EXISTS gerente_hotel;
DROP USER IF EXISTS admin_hotel;

-- ---------------------------------------------------------
-- 2. ELIMINACION DE ROLES EXISTENTES (si los hay)
-- ---------------------------------------------------------
DROP ROLE IF EXISTS cliente_usuario;
DROP ROLE IF EXISTS empleado_limpieza;
DROP ROLE IF EXISTS recepcionista;
DROP ROLE IF EXISTS gerente;
DROP ROLE IF EXISTS administrador;

-- ---------------------------------------------------------
-- 3. CREACION DE ROLES
-- ---------------------------------------------------------

-- Rol de administrador: acceso total al esquema
CREATE ROLE administrador LOGIN
    VALID UNTIL '2099-12-31';

-- Rol de gerente: gestiona empleados, habitaciones y servicios
CREATE ROLE gerente LOGIN
    VALID UNTIL '2099-12-31';

-- Rol de recepcionista: gestiona reservas y clientes
CREATE ROLE recepcionista LOGIN
    VALID UNTIL '2099-12-31';

-- Rol de empleado de limpieza: solo actualiza estado de habitaciones
CREATE ROLE empleado_limpieza LOGIN
    VALID UNTIL '2099-12-31';

-- Rol de cliente usuario: acceso limitado a sus datos
CREATE ROLE cliente_usuario LOGIN
    VALID UNTIL '2099-12-31';

-- ---------------------------------------------------------
-- 4. ASIGNACION DE PERMISOS GENERICOS
-- ---------------------------------------------------------

-- Permiso de conexion a la base de datos
GRANT CONNECT ON DATABASE hotel TO 
    administrador,
    gerente,
    recepcionista,
    empleado_limpieza,
    cliente_usuario;

-- Permiso de uso del esquema
GRANT USAGE ON SCHEMA hotel TO 
    administrador,
    gerente,
    recepcionista,
    empleado_limpieza,
    cliente_usuario;

-- ---------------------------------------------------------
-- 5. PERMISOS POR TABLA - ADMINISTRADOR (acceso total)
-- ---------------------------------------------------------

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hotel TO administrador;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hotel TO administrador;

-- Permisos por defecto para nuevas tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA hotel GRANT ALL PRIVILEGES ON TABLES TO administrador;
ALTER DEFAULT PRIVILEGES IN SCHEMA hotel GRANT ALL PRIVILEGES ON SEQUENCES TO administrador;

-- ---------------------------------------------------------
-- 6. PERMISOS POR TABLA - GERENTE
-- ---------------------------------------------------------

-- Empleados: gestion completa
GRANT ALL PRIVILEGES ON TABLE hotel.empleado TO gerente;

-- Personas: gestion completa (necesario para empleados)
GRANT ALL PRIVILEGES ON TABLE hotel.persona TO gerente;

-- Telefonos: gestion completa
GRANT ALL PRIVILEGES ON TABLE hotel.telefono TO gerente;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hotel TO gerente;

-- Habitaciones: gestion completa
GRANT ALL PRIVILEGES ON TABLE hotel.habitacion TO gerente;

-- Servicios: gestion completa
GRANT ALL PRIVILEGES ON TABLE hotel.servicio TO gerente;

-- Permisos por defecto para nuevas tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA hotel GRANT ALL PRIVILEGES ON TABLES TO gerente;
ALTER DEFAULT PRIVILEGES IN SCHEMA hotel GRANT ALL PRIVILEGES ON SEQUENCES TO gerente;

-- ---------------------------------------------------------
-- 7. PERMISOS POR TABLA - RECEPCIONISTA
-- ---------------------------------------------------------

-- Clientes: gestion completa
GRANT ALL PRIVILEGES ON TABLE hotel.cliente TO recepcionista;

-- Personas: solo insercion y actualizacion (para crear/editar clientes)
GRANT SELECT, INSERT, UPDATE ON TABLE hotel.persona TO recepcionista;

-- Telefonos: gestion completa
GRANT ALL PRIVILEGES ON TABLE hotel.telefono TO recepcionista;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hotel TO recepcionista;

-- Habitaciones: solo seleccion y actualizacion de estado
GRANT SELECT, UPDATE ON TABLE hotel.habitacion TO recepcionista;

-- Reservas: gestion completa
GRANT ALL PRIVILEGES ON TABLE hotel.reserva TO recepcionista;

-- Servicios: solo lectura (para informacion a clientes)
GRANT SELECT ON TABLE hotel.servicio TO recepcionista;

-- Consumos: gestion completa
GRANT ALL PRIVILEGES ON TABLE hotel.consumo TO recepcionista;

-- Permisos por defecto
ALTER DEFAULT PRIVILEGES IN SCHEMA hotel GRANT SELECT, INSERT, UPDATE ON TABLES TO recepcionista;

-- ---------------------------------------------------------
-- 8. PERMISOS POR TABLA - EMPLEADO DE LIMPIEZA
-- ---------------------------------------------------------

-- Habitaciones: solo ver y actualizar estado
GRANT SELECT, UPDATE ON TABLE hotel.habitacion TO empleado_limpieza;

-- Personas: solo lectura (para identificacion basica)
GRANT SELECT ON TABLE hotel.persona TO empleado_limpieza;

-- Permisos por defecto para nuevas tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA hotel GRANT SELECT ON TABLES TO empleado_limpieza;

-- ---------------------------------------------------------
-- 9. PERMISOS POR TABLA - CLIENTE USUARIO
-- ---------------------------------------------------------

-- Personas: solo lectura de datos propios (se complementa con RLS)
GRANT SELECT ON TABLE hotel.persona TO cliente_usuario;

-- Clientes: solo lectura de datos propios
GRANT SELECT ON TABLE hotel.cliente TO cliente_usuario;

-- Habitaciones: solo lectura (para ver disponibilidad)
GRANT SELECT ON TABLE hotel.habitacion TO cliente_usuario;

-- Reservas: solo lectura
GRANT SELECT ON TABLE hotel.reserva TO cliente_usuario;

-- Servicios: solo lectura
GRANT SELECT ON TABLE hotel.servicio TO cliente_usuario;

-- Consumos: solo lectura
GRANT SELECT ON TABLE hotel.consumo TO cliente_usuario;

-- Permisos por defecto
ALTER DEFAULT PRIVILEGES IN SCHEMA hotel GRANT SELECT ON TABLES TO cliente_usuario;

-- ---------------------------------------------------------
-- 10. FUNCION AUXILIAR PARA RLS
-- DEBE crearse ANTES de los CREATE POLICY que la referencian
-- ---------------------------------------------------------

-- Funcion para obtener el id_persona del usuario PostgreSQL actual
-- Busca en la tabla persona un registro cuyo email coincida con CURRENT_USER
CREATE OR REPLACE FUNCTION hotel.current_user_id()
RETURNS BIGINT AS $$
DECLARE
    v_user_id BIGINT;
BEGIN
    -- Mapeo entre usuario de PostgreSQL y id_persona via email
    -- En produccion se puede usar una tabla de sesiones o JWT claims
    SELECT id_persona INTO v_user_id
    FROM hotel.persona
    WHERE email = CURRENT_USER;

    RETURN v_user_id;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION hotel.current_user_id() TO
    cliente_usuario,
    recepcionista,
    gerente;

-- ---------------------------------------------------------
-- 11. ROW LEVEL SECURITY (RLS) - Politicas de aislamiento
-- Se define DESPUES de la funcion current_user_id()
-- ---------------------------------------------------------

-- Habilitar RLS en tablas sensibles
ALTER TABLE hotel.cliente ENABLE ROW LEVEL SECURITY;
ALTER TABLE hotel.reserva ENABLE ROW LEVEL SECURITY;
ALTER TABLE hotel.consumo ENABLE ROW LEVEL SECURITY;
ALTER TABLE hotel.persona ENABLE ROW LEVEL SECURITY;

-- Politica: Los clientes solo ven su propio registro
CREATE POLICY cliente_own_data_policy ON hotel.cliente
    FOR ALL TO cliente_usuario
    USING (id_persona = hotel.current_user_id());

-- Politica: Los clientes solo ven sus propias reservas
CREATE POLICY cliente_reservas_policy ON hotel.reserva
    FOR ALL TO cliente_usuario
    USING (id_cliente = hotel.current_user_id());

-- Politica: Los clientes solo ven consumos de sus reservas
CREATE POLICY cliente_consumos_policy ON hotel.consumo
    FOR ALL TO cliente_usuario
    USING (id_reserva IN (
        SELECT id_reserva FROM hotel.reserva
        WHERE id_cliente = hotel.current_user_id()
    ));

-- Politica: Los clientes solo ven su propia persona
CREATE POLICY cliente_persona_policy ON hotel.persona
    FOR SELECT TO cliente_usuario
    USING (id_persona = hotel.current_user_id());

-- Politica bypass para roles administrativos (ven todas las filas)
CREATE POLICY admin_bypass_cliente  ON hotel.cliente  FOR ALL TO administrador, gerente, recepcionista USING (true);
CREATE POLICY admin_bypass_reserva  ON hotel.reserva  FOR ALL TO administrador, gerente, recepcionista USING (true);
CREATE POLICY admin_bypass_consumo  ON hotel.consumo  FOR ALL TO administrador, gerente, recepcionista USING (true);
CREATE POLICY admin_bypass_persona  ON hotel.persona  FOR ALL TO administrador, gerente, recepcionista USING (true);

-- ---------------------------------------------------------
-- 12. CREACION DE USUARIOS DE EJEMPLO
-- ---------------------------------------------------------

-- Administrador principal
CREATE USER admin_hotel WITH LOGIN PASSWORD 'temp_password_admin';
GRANT administrador TO admin_hotel;

-- Gerente de hotel
CREATE USER gerente_hotel WITH LOGIN PASSWORD 'temp_password_gerente';
GRANT gerente TO gerente_hotel;

-- Recepcionista
CREATE USER recepcion_01 WITH LOGIN PASSWORD 'temp_password_recepcion';
GRANT recepcionista TO recepcion_01;

-- Empleado de limpieza
CREATE USER limpieza_01 WITH LOGIN PASSWORD 'temp_password_limpieza';
GRANT empleado_limpieza TO limpieza_01;

-- Cliente ejemplo
CREATE USER cliente_01 WITH LOGIN PASSWORD 'temp_password_cliente';
GRANT cliente_usuario TO cliente_01;

-- ---------------------------------------------------------
-- 13. COMENTARIOS DE SEGURIDAD
-- ---------------------------------------------------------

COMMENT ON ROLE administrador IS 'Rol con acceso total al esquema hotel - Usar con precaucion';
COMMENT ON ROLE gerente IS 'Rol para gestion de empleados, habitaciones y servicios';
COMMENT ON ROLE recepcionista IS 'Rol para gestion de reservas, clientes y consumos';
COMMENT ON ROLE empleado_limpieza IS 'Rol con acceso limitado solo a actualizacion de estados de habitaciones';
COMMENT ON ROLE cliente_usuario IS 'Rol con acceso de solo lectura a sus propios datos';

-- NOTA: Cambiar los passwords temporales antes de usar en produccion
-- RECOMENDACION: Usar SSL para conexiones y autenticacion segura