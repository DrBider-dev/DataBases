from util.db import db
from psycopg2.extras import RealDictCursor
from models.entities import Persona, Telefono, Cliente, Empleado, Habitacion, Reserva, Servicio, Consumo

class PersonaDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.persona ORDER BY id_persona;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, p: Persona):
        sql = "INSERT INTO hotel.persona VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (p.id_persona, p.primer_nombre, p.segundo_nombre, p.primer_apellido, 
                                 p.segundo_apellido, p.email, p.calle, p.carrera, p.numero))
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.persona WHERE id_persona = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

class HabitacionDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.habitacion ORDER BY numero_h;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, h: Habitacion):
        sql = "INSERT INTO hotel.habitacion VALUES (%s,%s,%s,%s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (h.numero_h, h.tipo, h.estado, h.precio_noche))
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.habitacion WHERE numero_h = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

class TelefonoDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.telefono ORDER BY id_telefono;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, t: Telefono):
        sql = "INSERT INTO hotel.telefono (id_persona, telefono) VALUES (%s, %s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (t.id_persona, t.telefono))
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.telefono WHERE id_telefono = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

class ClienteDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.cliente;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, c: Cliente):
        sql = "INSERT INTO hotel.cliente VALUES (%s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (c.id_persona,))
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.cliente WHERE id_persona = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

class EmpleadoDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.empleado;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, e: Empleado):
        sql = "INSERT INTO hotel.empleado VALUES (%s, %s, %s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (e.id_persona, e.cargo, e.area))
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.empleado WHERE id_persona = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

class ReservaDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.reserva ORDER BY id_reserva;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, r: Reserva):
        sql = """INSERT INTO hotel.reserva (id_cliente, numero_h, fecha_llegada, fecha_salida, valor_reserva, tiempo_maxc) 
                 VALUES (%s, %s, %s, %s, %s, %s);"""
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (r.id_cliente, r.numero_h, r.fecha_llegada, r.fecha_salida, r.valor_reserva, r.tiempo_maxc))
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.reserva WHERE id_reserva = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

class ServicioDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.servicio ORDER BY id_servicio;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, s: Servicio):
        sql = "INSERT INTO hotel.servicio (nombre, descripcion, costo, estado) VALUES (%s, %s, %s, %s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (s.nombre, s.descripcion, s.costo, s.estado))
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.servicio WHERE id_servicio = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

class ConsumoDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.consumo ORDER BY id_consumo;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, c: Consumo):
        sql = "INSERT INTO hotel.consumo (id_reserva, id_servicio) VALUES (%s, %s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (c.id_reserva, c.id_servicio))
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.consumo WHERE id_consumo = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()