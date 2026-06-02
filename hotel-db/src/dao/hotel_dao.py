from util.db import db
from psycopg2.extras import RealDictCursor
from models.entities import Persona, Telefono, Cliente, Empleado, Habitacion, Reserva, Servicio, Consumo

def _table_columns(cur, table_name):
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'hotel' AND table_name = %s;
    """, (table_name,))
    return {row["column_name"] if isinstance(row, dict) else row[0] for row in cur.fetchall()}

def _next_id_insert(table_name, id_column, columns):
    select_values = [f"COALESCE(MAX({id_column}), 0) + 1"]
    select_values.extend(["%s"] * len(columns))
    insert_columns = ", ".join([id_column] + columns)
    return (
        f"INSERT INTO hotel.{table_name} ({insert_columns}) "
        f"SELECT {', '.join(select_values)} FROM hotel.{table_name};"
    )

def _cliente_usa_id_interno(cur):
    return "id_cliente" in _table_columns(cur, "cliente")

def _cliente_ids_por_entrada(cur, id_cliente_o_persona):
    if not _cliente_usa_id_interno(cur):
        return [id_cliente_o_persona]

    cur.execute("""
        SELECT id_cliente
        FROM hotel.cliente
        WHERE id_persona = %s OR id_cliente = %s
        ORDER BY CASE WHEN id_persona = %s THEN 0 ELSE 1 END;
    """, (id_cliente_o_persona, id_cliente_o_persona, id_cliente_o_persona))
    return [row[0] for row in cur.fetchall()]

def _cliente_id_para_reserva(cur, id_cliente_o_persona):
    ids = _cliente_ids_por_entrada(cur, id_cliente_o_persona)
    if not ids:
        raise ValueError("No existe un cliente con ese ID.")
    return ids[0]

def _validar_disponibilidad_reserva(cur, r: Reserva):
    cur.execute("SELECT %s::date < %s::date;", (r.fecha_llegada, r.fecha_salida))
    if not cur.fetchone()[0]:
        raise ValueError("La fecha de salida debe ser posterior a la fecha de llegada.")

    cur.execute("""
        SELECT id_reserva, fecha_llegada, fecha_salida
        FROM hotel.reserva
        WHERE numero_h = %s
          AND fecha_llegada < %s::date
          AND %s::date < fecha_salida
        LIMIT 1;
    """, (r.numero_h, r.fecha_salida, r.fecha_llegada))
    reserva_cruzada = cur.fetchone()
    if reserva_cruzada:
        raise ValueError(
            f"La habitación {r.numero_h} ya está reservada "
            f"del {reserva_cruzada[1]} al {reserva_cruzada[2]}."
        )

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
        sql_telefonos = "DELETE FROM hotel.telefono WHERE id_persona = %s;"
        sql_persona = "DELETE FROM hotel.persona WHERE id_persona = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_telefonos, (id,))
                cur.execute(sql_persona, (id,))
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
        sql_consumos = """
            DELETE FROM hotel.consumo
            WHERE id_reserva IN (
                SELECT id_reserva FROM hotel.reserva WHERE numero_h = %s
            );
        """
        sql_reservas = "DELETE FROM hotel.reserva WHERE numero_h = %s;"
        sql = "DELETE FROM hotel.habitacion WHERE numero_h = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_consumos, (id,))
                cur.execute(sql_reservas, (id,))
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
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if _cliente_usa_id_interno(cur):
                    sql = "SELECT * FROM hotel.cliente ORDER BY id_cliente;"
                else:
                    sql = "SELECT * FROM hotel.cliente ORDER BY id_persona;"
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, c: Cliente):
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                if _cliente_usa_id_interno(cur):
                    sql = _next_id_insert("cliente", "id_cliente", ["id_persona"])
                    cur.execute(sql, (c.id_persona,))
                else:
                    sql = "INSERT INTO hotel.cliente (id_persona) VALUES (%s);"
                    cur.execute(sql, (c.id_persona,))
                conn.commit()

    def eliminar(self, id):
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cliente_ids = _cliente_ids_por_entrada(cur, id)
                if cliente_ids:
                    cur.execute("""
                        DELETE FROM hotel.consumo
                        WHERE id_reserva IN (
                            SELECT id_reserva
                            FROM hotel.reserva
                            WHERE id_cliente = ANY(%s)
                        );
                    """, (cliente_ids,))
                    cur.execute("DELETE FROM hotel.reserva WHERE id_cliente = ANY(%s);", (cliente_ids,))

                if _cliente_usa_id_interno(cur):
                    cur.execute("DELETE FROM hotel.cliente WHERE id_persona = %s OR id_cliente = %s;", (id, id))
                else:
                    cur.execute("DELETE FROM hotel.cliente WHERE id_persona = %s;", (id,))
                conn.commit()

class EmpleadoDAO:
    def listar(self):
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                columns = _table_columns(cur, "empleado")
                if "id_empleado" in columns:
                    sql = "SELECT * FROM hotel.empleado ORDER BY id_empleado;"
                else:
                    sql = "SELECT * FROM hotel.empleado ORDER BY id_persona;"
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, e: Empleado):
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                columns = _table_columns(cur, "empleado")
                if "id_empleado" in columns:
                    sql = _next_id_insert("empleado", "id_empleado", ["id_persona", "cargo", "area"])
                    cur.execute(sql, (e.id_persona, e.cargo, e.area))
                else:
                    sql = "INSERT INTO hotel.empleado (id_persona, cargo, area) VALUES (%s, %s, %s);"
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
        sql = _next_id_insert(
            "reserva",
            "id_reserva",
            ["id_cliente", "numero_h", "fecha_llegada", "fecha_salida", "valor_reserva", "tiempo_maxc"]
        )
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("LOCK TABLE hotel.reserva IN SHARE ROW EXCLUSIVE MODE;")
                _validar_disponibilidad_reserva(cur, r)
                id_cliente = _cliente_id_para_reserva(cur, r.id_cliente)
                cur.execute(sql, (id_cliente, r.numero_h, r.fecha_llegada, r.fecha_salida, r.valor_reserva, r.tiempo_maxc))
                conn.commit()

    def eliminar(self, id):
        sql_consumos = "DELETE FROM hotel.consumo WHERE id_reserva = %s;"
        sql_reserva = "DELETE FROM hotel.reserva WHERE id_reserva = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_consumos, (id,))
                cur.execute(sql_reserva, (id,))
                conn.commit()

class ServicioDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.servicio ORDER BY id_servicio;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, s: Servicio):
        sql = _next_id_insert("servicio", "id_servicio", ["nombre", "descripcion", "costo", "estado"])
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (s.nombre, s.descripcion, s.costo, s.estado))
                conn.commit()

    def eliminar(self, id):
        sql_consumos = "DELETE FROM hotel.consumo WHERE id_servicio = %s;"
        sql = "DELETE FROM hotel.servicio WHERE id_servicio = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_consumos, (id,))
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
        sql = _next_id_insert("consumo", "id_consumo", ["id_reserva", "id_servicio"])
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
