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


def _buscar_en_tabla(table_name, columns, order_by, termino):
    filtro = " OR ".join([f"CAST({column} AS TEXT) ILIKE %s" for column in columns])
    params = [f"%{termino}%"] * len(columns)
    sql = f"SELECT * FROM hotel.{table_name} WHERE {filtro} ORDER BY {order_by};"
    with db.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def _obtener_por_id(table_name, id_column, id_value):
    sql = f"SELECT * FROM hotel.{table_name} WHERE {id_column} = %s;"
    with db.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (id_value,))
            return cur.fetchone()


def _validar_actualizado(cur, mensaje="No se encontró el registro a actualizar."):
    if cur.rowcount == 0:
        raise ValueError(mensaje)


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


def _cliente_registro_por_entrada(cur, id_cliente_o_persona):
    if _cliente_usa_id_interno(cur):
        cur.execute("""
            SELECT id_cliente
            FROM hotel.cliente
            WHERE id_persona = %s OR id_cliente = %s
            ORDER BY CASE WHEN id_persona = %s THEN 0 ELSE 1 END
            LIMIT 1;
        """, (id_cliente_o_persona, id_cliente_o_persona, id_cliente_o_persona))
        row = cur.fetchone()
        return row[0] if row else None

    cur.execute("SELECT id_persona FROM hotel.cliente WHERE id_persona = %s;", (id_cliente_o_persona,))
    row = cur.fetchone()
    return row[0] if row else None


def _empleado_usa_id_interno(cur):
    return "id_empleado" in _table_columns(cur, "empleado")


def _empleado_registro_por_entrada(cur, id_empleado_o_persona):
    if _empleado_usa_id_interno(cur):
        cur.execute("""
            SELECT id_empleado
            FROM hotel.empleado
            WHERE id_persona = %s OR id_empleado = %s
            ORDER BY CASE WHEN id_persona = %s THEN 0 ELSE 1 END
            LIMIT 1;
        """, (id_empleado_o_persona, id_empleado_o_persona, id_empleado_o_persona))
        row = cur.fetchone()
        return row[0] if row else None

    cur.execute("SELECT id_persona FROM hotel.empleado WHERE id_persona = %s;", (id_empleado_o_persona,))
    row = cur.fetchone()
    return row[0] if row else None


def _validar_disponibilidad_reserva(cur, r: Reserva, id_reserva_actual=None):
    cur.execute("SELECT %s::date < %s::date;", (r.fecha_llegada, r.fecha_salida))
    if not cur.fetchone()[0]:
        raise ValueError("La fecha de salida debe ser posterior a la fecha de llegada.")

    if id_reserva_actual is None:
        cur.execute("""
            SELECT id_reserva, fecha_llegada, fecha_salida
            FROM hotel.reserva
            WHERE numero_h = %s
              AND fecha_llegada < %s::date
              AND %s::date < fecha_salida
            LIMIT 1;
        """, (r.numero_h, r.fecha_salida, r.fecha_llegada))
    else:
        cur.execute("""
            SELECT id_reserva, fecha_llegada, fecha_salida
            FROM hotel.reserva
            WHERE numero_h = %s
              AND id_reserva <> %s
              AND fecha_llegada < %s::date
              AND %s::date < fecha_salida
            LIMIT 1;
        """, (r.numero_h, id_reserva_actual, r.fecha_salida, r.fecha_llegada))

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

    def buscar(self, termino):
        return _buscar_en_tabla(
            "persona",
            [
                "id_persona", "primer_nombre", "segundo_nombre", "primer_apellido",
                "segundo_apellido", "email", "calle", "carrera", "numero"
            ],
            "id_persona",
            termino
        )

    def obtener(self, id):
        return _obtener_por_id("persona", "id_persona", id)

    def crear(self, p: Persona):
        sql = "INSERT INTO hotel.persona VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (p.id_persona, p.primer_nombre, p.segundo_nombre, p.primer_apellido,
                                  p.segundo_apellido, p.email, p.calle, p.carrera, p.numero))
                conn.commit()

    def actualizar(self, id, p: Persona):
        sql = """
            UPDATE hotel.persona
            SET primer_nombre = %s,
                segundo_nombre = %s,
                primer_apellido = %s,
                segundo_apellido = %s,
                email = %s,
                calle = %s,
                carrera = %s,
                numero = %s
            WHERE id_persona = %s;
        """
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido,
                    p.email, p.calle, p.carrera, p.numero, id
                ))
                _validar_actualizado(cur, "No existe una persona con ese ID.")
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

    def buscar(self, termino):
        return _buscar_en_tabla(
            "habitacion",
            ["numero_h", "tipo", "estado", "precio_noche"],
            "numero_h",
            termino
        )

    def obtener(self, id):
        return _obtener_por_id("habitacion", "numero_h", id)

    def crear(self, h: Habitacion):
        sql = "INSERT INTO hotel.habitacion VALUES (%s,%s,%s,%s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (h.numero_h, h.tipo, h.estado, h.precio_noche))
                conn.commit()

    def actualizar(self, id, h: Habitacion):
        sql = """
            UPDATE hotel.habitacion
            SET tipo = %s,
                estado = %s,
                precio_noche = %s
            WHERE numero_h = %s;
        """
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (h.tipo, h.estado, h.precio_noche, id))
                _validar_actualizado(cur, "No existe una habitación con ese número.")
                conn.commit()

    def actualizar_estado(self, numero_h, nuevo_estado):
        sql = "UPDATE hotel.habitacion SET estado = %s WHERE numero_h = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (nuevo_estado, numero_h))
                _validar_actualizado(cur, "No existe una habitación con ese número.")
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

    def buscar(self, termino):
        return _buscar_en_tabla(
            "telefono",
            ["id_telefono", "id_persona", "telefono"],
            "id_telefono",
            termino
        )

    def obtener(self, id):
        return _obtener_por_id("telefono", "id_telefono", id)

    def crear(self, t: Telefono):
        sql = "INSERT INTO hotel.telefono (id_persona, telefono) VALUES (%s, %s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (t.id_persona, t.telefono))
                conn.commit()

    def actualizar(self, id, t: Telefono):
        sql = """
            UPDATE hotel.telefono
            SET id_persona = %s,
                telefono = %s
            WHERE id_telefono = %s;
        """
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (t.id_persona, t.telefono, id))
                _validar_actualizado(cur, "No existe un teléfono con ese ID.")
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

    def buscar(self, termino):
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if _cliente_usa_id_interno(cur):
                    columns = ["id_cliente", "id_persona"]
                    order_by = "id_cliente"
                else:
                    columns = ["id_persona"]
                    order_by = "id_persona"
                filtro = " OR ".join([f"CAST({column} AS TEXT) ILIKE %s" for column in columns])
                cur.execute(
                    f"SELECT * FROM hotel.cliente WHERE {filtro} ORDER BY {order_by};",
                    [f"%{termino}%"] * len(columns)
                )
                return cur.fetchall()

    def obtener(self, id):
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if _cliente_usa_id_interno(cur):
                    cur.execute("""
                        SELECT c.*, p.primer_nombre, p.primer_apellido
                        FROM hotel.cliente c
                        JOIN hotel.persona p ON c.id_persona = p.id_persona
                        WHERE c.id_persona = %s OR c.id_cliente = %s
                        ORDER BY CASE WHEN c.id_persona = %s THEN 0 ELSE 1 END
                        LIMIT 1;
                    """, (id, id, id))
                else:
                    cur.execute("""
                        SELECT c.*, p.primer_nombre, p.primer_apellido
                        FROM hotel.cliente c
                        JOIN hotel.persona p ON c.id_persona = p.id_persona
                        WHERE c.id_persona = %s;
                    """, (id,))
                return cur.fetchone()

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

    def actualizar(self, id, c: Cliente):
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                id_registro = _cliente_registro_por_entrada(cur, id)
                if id_registro is None:
                    raise ValueError("No existe un cliente con ese ID.")

                if _cliente_usa_id_interno(cur):
                    cur.execute(
                        "UPDATE hotel.cliente SET id_persona = %s WHERE id_cliente = %s;",
                        (c.id_persona, id_registro)
                    )
                else:
                    cur.execute(
                        "UPDATE hotel.cliente SET id_persona = %s WHERE id_persona = %s;",
                        (c.id_persona, id_registro)
                    )
                _validar_actualizado(cur, "No existe un cliente con ese ID.")
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

    def buscar(self, termino):
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                columns = _table_columns(cur, "empleado")
                if "id_empleado" in columns:
                    search_columns = ["id_empleado", "id_persona", "cargo", "area"]
                    order_by = "id_empleado"
                else:
                    search_columns = ["id_persona", "cargo", "area"]
                    order_by = "id_persona"
                filtro = " OR ".join([f"CAST({column} AS TEXT) ILIKE %s" for column in search_columns])
                cur.execute(
                    f"SELECT * FROM hotel.empleado WHERE {filtro} ORDER BY {order_by};",
                    [f"%{termino}%"] * len(search_columns)
                )
                return cur.fetchall()

    def obtener(self, id):
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if _empleado_usa_id_interno(cur):
                    cur.execute("""
                        SELECT e.*, p.primer_nombre, p.primer_apellido
                        FROM hotel.empleado e
                        JOIN hotel.persona p ON e.id_persona = p.id_persona
                        WHERE e.id_persona = %s OR e.id_empleado = %s
                        ORDER BY CASE WHEN e.id_persona = %s THEN 0 ELSE 1 END
                        LIMIT 1;
                    """, (id, id, id))
                else:
                    cur.execute("""
                        SELECT e.*, p.primer_nombre, p.primer_apellido
                        FROM hotel.empleado e
                        JOIN hotel.persona p ON e.id_persona = p.id_persona
                        WHERE e.id_persona = %s;
                    """, (id,))
                return cur.fetchone()

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

    def actualizar(self, id, e: Empleado):
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                id_registro = _empleado_registro_por_entrada(cur, id)
                if id_registro is None:
                    raise ValueError("No existe un empleado con ese ID.")

                if _empleado_usa_id_interno(cur):
                    cur.execute("""
                        UPDATE hotel.empleado
                        SET id_persona = %s,
                            cargo = %s,
                            area = %s
                        WHERE id_empleado = %s;
                    """, (e.id_persona, e.cargo, e.area, id_registro))
                else:
                    cur.execute("""
                        UPDATE hotel.empleado
                        SET id_persona = %s,
                            cargo = %s,
                            area = %s
                        WHERE id_persona = %s;
                    """, (e.id_persona, e.cargo, e.area, id_registro))
                _validar_actualizado(cur, "No existe un empleado con ese ID.")
                conn.commit()

    def eliminar(self, id):
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                id_registro = _empleado_registro_por_entrada(cur, id)
                if id_registro is None:
                    raise ValueError("No existe un empleado con ese ID.")

                if _empleado_usa_id_interno(cur):
                    cur.execute("DELETE FROM hotel.empleado WHERE id_empleado = %s;", (id_registro,))
                else:
                    cur.execute("DELETE FROM hotel.empleado WHERE id_persona = %s;", (id_registro,))
                conn.commit()


class ReservaDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.reserva ORDER BY id_reserva;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def buscar(self, termino):
        return _buscar_en_tabla(
            "reserva",
            ["id_reserva", "id_cliente", "numero_h", "fecha_llegada", "fecha_salida", "valor_reserva", "tiempo_maxc"],
            "id_reserva",
            termino
        )

    def obtener(self, id):
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if _cliente_usa_id_interno(cur):
                    cur.execute("""
                        SELECT r.*, c.id_cliente, p.primer_nombre, p.primer_apellido
                        FROM hotel.reserva r
                        JOIN hotel.cliente c ON r.id_cliente = c.id_persona
                        JOIN hotel.persona p ON c.id_persona = p.id_persona
                        WHERE r.id_reserva = %s;
                    """, (id,))
                else:
                    cur.execute("""
                        SELECT r.*, p.primer_nombre, p.primer_apellido
                        FROM hotel.reserva r
                        JOIN hotel.persona p ON r.id_cliente = p.id_persona
                        WHERE r.id_reserva = %s;
                    """, (id,))
                return cur.fetchone()

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
                cur.execute(sql, (
                    id_cliente, r.numero_h, r.fecha_llegada, r.fecha_salida,
                    r.valor_reserva, r.tiempo_maxc
                ))
                conn.commit()

    def actualizar(self, id, r: Reserva):
        sql = """
            UPDATE hotel.reserva
            SET id_cliente = %s,
                numero_h = %s,
                fecha_llegada = %s,
                fecha_salida = %s,
                valor_reserva = %s,
                tiempo_maxc = %s
            WHERE id_reserva = %s;
        """
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("LOCK TABLE hotel.reserva IN SHARE ROW EXCLUSIVE MODE;")
                _validar_disponibilidad_reserva(cur, r, id)
                id_cliente = _cliente_id_para_reserva(cur, r.id_cliente)
                cur.execute(sql, (
                    id_cliente, r.numero_h, r.fecha_llegada, r.fecha_salida,
                    r.valor_reserva, r.tiempo_maxc, id
                ))
                _validar_actualizado(cur, "No existe una reserva con ese ID.")
                conn.commit()

    def eliminar(self, id):
        sql_consumos = "DELETE FROM hotel.consumo WHERE id_reserva = %s;"
        sql_reserva = "DELETE FROM hotel.reserva WHERE id_reserva = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_consumos, (id,))
                cur.execute(sql_reserva, (id,))
                conn.commit()

    def buscar_por_cliente(self, id_cliente):
        sql = """
            SELECT r.*, p.primer_nombre, p.primer_apellido
            FROM hotel.reserva r
            JOIN hotel.persona p ON r.id_cliente = p.id_persona
            WHERE r.id_cliente = %s
            ORDER BY r.fecha_llegada DESC;
        """
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (id_cliente,))
                return cur.fetchall()


class ServicioDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.servicio ORDER BY id_servicio;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def buscar(self, termino):
        return _buscar_en_tabla(
            "servicio",
            ["id_servicio", "nombre", "descripcion", "costo", "estado"],
            "id_servicio",
            termino
        )

    def obtener(self, id):
        return _obtener_por_id("servicio", "id_servicio", id)

    def crear(self, s: Servicio):
        sql = _next_id_insert("servicio", "id_servicio", ["nombre", "descripcion", "costo", "estado"])
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (s.nombre, s.descripcion, s.costo, s.estado))
                conn.commit()

    def actualizar(self, id, s: Servicio):
        sql = """
            UPDATE hotel.servicio
            SET nombre = %s,
                descripcion = %s,
                costo = %s,
                estado = %s
            WHERE id_servicio = %s;
        """
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (s.nombre, s.descripcion, s.costo, s.estado, id))
                _validar_actualizado(cur, "No existe un servicio con ese ID.")
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

    def buscar(self, termino):
        return _buscar_en_tabla(
            "consumo",
            ["id_consumo", "id_reserva", "id_servicio", "fecha_hora"],
            "id_consumo",
            termino
        )

    def obtener(self, id):
        return _obtener_por_id("consumo", "id_consumo", id)

    def crear(self, c: Consumo):
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                if c.fecha_hora:
                    sql = _next_id_insert("consumo", "id_consumo", ["id_reserva", "id_servicio", "fecha_hora"])
                    cur.execute(sql, (c.id_reserva, c.id_servicio, c.fecha_hora))
                else:
                    sql = _next_id_insert("consumo", "id_consumo", ["id_reserva", "id_servicio"])
                    cur.execute(sql, (c.id_reserva, c.id_servicio))
                conn.commit()

    def actualizar(self, id, c: Consumo):
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                if c.fecha_hora:
                    cur.execute("""
                        UPDATE hotel.consumo
                        SET id_reserva = %s,
                            id_servicio = %s,
                            fecha_hora = %s
                        WHERE id_consumo = %s;
                    """, (c.id_reserva, c.id_servicio, c.fecha_hora, id))
                else:
                    cur.execute("""
                        UPDATE hotel.consumo
                        SET id_reserva = %s,
                            id_servicio = %s
                        WHERE id_consumo = %s;
                    """, (c.id_reserva, c.id_servicio, id))
                _validar_actualizado(cur, "No existe un consumo con ese ID.")
                conn.commit()

    def eliminar(self, id):
        sql = "DELETE FROM hotel.consumo WHERE id_consumo = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

    def buscar_por_cliente(self, id_cliente):
        sql = """
            SELECT co.*, s.nombre as servicio_nombre
            FROM hotel.consumo co
            JOIN hotel.reserva r ON co.id_reserva = r.id_reserva
            JOIN hotel.servicio s ON co.id_servicio = s.id_servicio
            WHERE r.id_cliente = %s
            ORDER BY co.fecha_hora DESC;
        """
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (id_cliente,))
                return cur.fetchall()