# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

# =========================================================
# 1. UTILIDAD DE CONEXIÓN
# =========================================================
class DBConnection:
    def __init__(self):
        self.config = {
            "dbname": "Hotel",
            "user": "postgres",
            "password": "20231020128",
            "host": "localhost",
            "port": "5432",
        }

    def get_connection(self):
        conn = psycopg2.connect(**self.config)
        conn.set_client_encoding('UTF8')
        return conn

db = DBConnection()

# =========================================================
# 2. ENTIDADES (Modelos de Datos)
# =========================================================

@dataclass
class Persona:
    id_persona: int
    primer_nombre: str
    primer_apellido: str
    email: str
    segundo_nombre: Optional[str] = None
    segundo_apellido: Optional[str] = None
    calle: Optional[str] = None
    carrera: Optional[str] = None
    numero: Optional[str] = None

@dataclass
class Telefono:
    id_telefono: Optional[int]
    id_persona: int
    telefono: str

@dataclass
class Cliente:
    id_persona: int

@dataclass
class Empleado:
    id_persona: int
    cargo: str
    area: str

@dataclass
class Habitacion:
    numero_h: int
    tipo: str
    estado: str
    precio_noche: float

@dataclass
class Reserva:
    id_reserva: Optional[int]
    id_cliente: int
    numero_h: int
    fecha_llegada: str
    fecha_salida: str
    valor_reserva: float
    tiempo_maxc: int

@dataclass
class Servicio:
    id_servicio: Optional[int]
    nombre: str
    descripcion: str
    costo: float
    estado: str

@dataclass
class Consumo:
    id_consumo: Optional[int]
    id_reserva: int
    id_servicio: int
    fecha_hora: str

# =========================================================
# 3. DAOs (CON TODAS LAS FUNCIONES: LISTAR, CREAR, ELIMINAR)
# =========================================================

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

    def eliminar(self, id_persona):
        sql = "DELETE FROM hotel.persona WHERE id_persona = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_persona,))
                conn.commit()
                return cur.rowcount

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

    def eliminar(self, id_telefono):
        sql = "DELETE FROM hotel.telefono WHERE id_telefono = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_telefono,))
                conn.commit()
                return cur.rowcount

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

    def eliminar(self, id_persona):
        sql = "DELETE FROM hotel.cliente WHERE id_persona = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_persona,))
                conn.commit()
                return cur.rowcount

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

    def eliminar(self, id_persona):
        sql = "DELETE FROM hotel.empleado WHERE id_persona = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_persona,))
                conn.commit()
                return cur.rowcount

class HabitacionDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.habitacion ORDER BY numero_h;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, h: Habitacion):
        sql = "INSERT INTO hotel.habitacion VALUES (%s, %s, %s, %s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (h.numero_h, h.tipo, h.estado, h.precio_noche))
                conn.commit()

    def eliminar(self, numero_h):
        sql = "DELETE FROM hotel.habitacion WHERE numero_h = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (numero_h,))
                conn.commit()
                return cur.rowcount

class ReservaDAO:
    def listar(self):
        sql = "SELECT * FROM hotel.reserva ORDER BY id_reserva;"
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def crear(self, r: Reserva):
        sql = "INSERT INTO hotel.reserva (id_cliente, numero_h, fecha_llegada, fecha_salida, valor_reserva, tiempo_maxc) VALUES (%s,%s,%s,%s,%s,%s);"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (r.id_cliente, r.numero_h, r.fecha_llegada, r.fecha_salida, r.valor_reserva, r.tiempo_maxc))
                conn.commit()

    def eliminar(self, id_reserva):
        sql = "DELETE FROM hotel.reserva WHERE id_reserva = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_reserva,))
                conn.commit()
                return cur.rowcount

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

    def eliminar(self, id_servicio):
        sql = "DELETE FROM hotel.servicio WHERE id_servicio = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_servicio,))
                conn.commit()
                return cur.rowcount

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

    def eliminar(self, id_consumo):
        sql = "DELETE FROM hotel.consumo WHERE id_consumo = %s;"
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_consumo,))
                conn.commit()
                return cur.rowcount

# =========================================================
# 4. INTERFAZ GRÁFICA (UI)
# =========================================================

class AppHotel(tk.Tk):
    def __init__(self, mapping):
        super().__init__()
        self.title("Hotel CRUD - Patrón DAO Estricto")
        self.geometry("1100x700")
        self.mapping = mapping
        self.current_key = "persona"
        
        self._setup_ui()
        self.cargar_datos()

    def _setup_ui(self):
        # Selector
        f_top = ttk.Frame(self, padding=10)
        f_top.pack(fill="x")
        ttk.Label(f_top, text="Tabla:").pack(side="left")
        self.combo = ttk.Combobox(f_top, values=list(self.mapping.keys()), state="readonly")
        self.combo.set(self.current_key)
        self.combo.pack(side="left", padx=5)
        self.combo.bind("<<ComboboxSelected>>", self.on_change_table)

        # Paneles
        self.pane = ttk.PanedWindow(self, orient="horizontal")
        self.pane.pack(fill="both", expand=True, padx=10, pady=5)

        self.form_frame = ttk.LabelFrame(self.pane, text="Formulario Nuevo", padding=10)
        self.pane.add(self.form_frame, weight=1)
        self._build_form()

        # Grid
        grid_frame = ttk.Frame(self.pane)
        self.pane.add(grid_frame, weight=3)
        self.tree = ttk.Treeview(grid_frame, show="headings")
        self.tree.pack(fill="both", expand=True)

        # Botones
        f_btns = ttk.Frame(self, padding=10)
        f_btns.pack(fill="x")
        ttk.Button(f_btns, text="Guardar Registro", command=self.guardar).pack(side="left", padx=5)
        ttk.Button(f_btns, text="Eliminar Seleccionado", command=self.eliminar).pack(side="left", padx=5)
        ttk.Button(f_btns, text="Refrescar Lista", command=self.cargar_datos).pack(side="right")

    def _build_form(self):
        for w in self.form_frame.winfo_children(): w.destroy()
        self.inputs = {}
        cls = self.mapping[self.current_key]["class"]
        import dataclasses
        for f in dataclasses.fields(cls):
            # No mostramos campos que suelen ser PK autogeneradas en el form de creación
            if f.name.startswith('id_') and ('Optional' in str(f.type) or f.type == Optional[int]):
                continue
            ttk.Label(self.form_frame, text=f.name.upper()+":").pack(anchor="w")
            e = ttk.Entry(self.form_frame)
            e.pack(fill="x", pady=(0, 5))
            self.inputs[f.name] = e

    def on_change_table(self, _):
        self.current_key = self.combo.get()
        self._build_form()
        self.cargar_datos()

    def cargar_datos(self):
        self.tree.delete(*self.tree.get_children())
        dao = self.mapping[self.current_key]["dao"]
        try:
            datos = dao.listar()
            if not datos: return
            cols = list(datos[0].keys())
            self.tree["columns"] = cols
            for col in cols:
                self.tree.heading(col, text=col.upper())
                self.tree.column(col, width=110)
            for row in datos:
                self.tree.insert("", "end", values=list(row.values()))
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {e}")

    def guardar(self):
        try:
            cls = self.mapping[self.current_key]["class"]
            dao = self.mapping[self.current_key]["dao"]
            data = {k: v.get() for k, v in self.inputs.items()}
            for k,v in data.items():
                if v == "": data[k] = None
            dao.crear(cls(**data))
            self.cargar_datos()
            messagebox.showinfo("OK", "Guardado")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar(self):
        sel = self.tree.selection()
        if not sel: return
        pk = self.tree.item(sel[0], "values")[0]
        dao = self.mapping[self.current_key]["dao"]
        if messagebox.askyesno("Confirmar", f"¿Eliminar registro {pk}?"):
            try:
                dao.eliminar(pk)
                self.cargar_datos()
            except Exception as e:
                messagebox.showerror("Error", f"No se puede eliminar (posible restricción de FK): {e}")

if __name__ == "__main__":
    tablas = {
        "persona": {"dao": PersonaDAO(), "class": Persona},
        "telefono": {"dao": TelefonoDAO(), "class": Telefono},
        "cliente": {"dao": ClienteDAO(), "class": Cliente},
        "empleado": {"dao": EmpleadoDAO(), "class": Empleado},
        "habitacion": {"dao": HabitacionDAO(), "class": Habitacion},
        "reserva": {"dao": ReservaDAO(), "class": Reserva},
        "servicio": {"dao": ServicioDAO(), "class": Servicio},
        "consumo": {"dao": ConsumoDAO(), "class": Consumo},
    }
    app = AppHotel(tablas)
    app.mainloop()