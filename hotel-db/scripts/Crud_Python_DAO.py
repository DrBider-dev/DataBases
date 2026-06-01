import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type
from dataclasses import dataclass, asdict, fields
from abc import ABC, abstractmethod
from contextlib import contextmanager
import psycopg2
from psycopg2 import sql

# =========================================================
# 1. ENTIDADES DE DOMINIO (MODELOS)
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
    id_telefono: Optional[int] # Autogenerado
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
    id_reserva: Optional[int] # Autogenerado
    id_cliente: int
    numero_h: int
    fecha_llegada: str
    fecha_salida: str
    valor_reserva: float
    tiempo_maxc: int

@dataclass
class Servicio:
    id_servicio: Optional[int] # Autogenerado
    nombre: str
    descripcion: str
    costo: float
    estado: str

@dataclass
class Consumo:
    id_consumo: Optional[int] # Autogenerado
    id_reserva: int
    id_servicio: int
    fecha_hora: str

T = TypeVar('T')

# =========================================================
# 2. CAPA DAO (CONTRATO Y LÓGICA BASE)
# =========================================================

class BaseDAO(Generic[T], ABC):
    @abstractmethod
    def listar(self) -> List[T]: pass
    @abstractmethod
    def crear(self, entidad: T) -> bool: pass
    @abstractmethod
    def actualizar(self, entidad: T) -> bool: pass
    @abstractmethod
    def eliminar(self, pk: Any) -> bool: pass

class PostgresDAO(BaseDAO[T]):
    def __init__(self, db_config: Dict[str, Any], schema: str, table_name: str, model_class: Type[T], pk_col: str):
        self.config = db_config
        self.schema = schema
        self.table = table_name
        self.model = model_class
        self.pk = pk_col

    @contextmanager
    def _connection(self):
        conn = psycopg2.connect(**self.config)
        try:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema)))
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def listar(self) -> List[T]:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {self.table} ORDER BY {self.pk}")
                return [self.model(*row) for row in cur.fetchall()]

    def crear(self, obj: T) -> bool:
        data = asdict(obj)
        # Filtramos campos autogenerados que sean None (IDs)
        items = {k: v for k, v in data.items() if v is not None}
        cols = items.keys()
        vals = tuple(items.values())
        query = f"INSERT INTO {self.table} ({', '.join(cols)}) VALUES ({', '.join(['%s']*len(vals))})"
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, vals)
        return True

    def actualizar(self, obj: T) -> bool:
        data = asdict(obj)
        pk_val = data.pop(self.pk)
        set_clause = ", ".join([f"{k}=%s" for k in data.keys()])
        query = f"UPDATE {self.table} SET {set_clause} WHERE {self.pk}=%s"
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (*data.values(), pk_val))
                return cur.rowcount > 0

    def eliminar(self, pk: Any) -> bool:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"DELETE FROM {self.table} WHERE {self.pk} = %s", (pk,))
                return cur.rowcount > 0

# =========================================================
# 3. INTERFAZ GRÁFICA (UI)
# =========================================================

class CRUDApp(tk.Tk):
    def __init__(self, db_config: Dict[str, Any], mapping: Dict[str, Dict]):
        super().__init__()
        self.title("Sistema Hotel - Estándar DAO")
        self.geometry("1100x750")
        self.mapping = mapping
        self.current_key = "persona"
        self.inputs = {}
        self._setup_ui()
        self.refresh_grid()

    def _setup_ui(self):
        # Header
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="TABLA:").pack(side="left")
        self.combo = ttk.Combobox(top, values=list(self.mapping.keys()), state="readonly")
        self.combo.set(self.current_key)
        self.combo.pack(side="left", padx=5)
        self.combo.bind("<<ComboboxSelected>>", self._change_table)

        # Paneles
        pane = ttk.PanedWindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True, padx=10, pady=5)

        self.form_container = ttk.LabelFrame(pane, text="Formulario", padding=10)
        pane.add(self.form_container, weight=1)
        self._draw_form()

        self.tree_frame = ttk.Frame(pane)
        pane.add(self.tree_frame, weight=3)
        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Botones
        btns = ttk.Frame(self, padding=10)
        btns.pack(fill="x")
        ttk.Button(btns, text="Limpiar", command=self._clear).pack(side="left", padx=2)
        ttk.Button(btns, text="Crear", command=self._create).pack(side="left", padx=2)
        ttk.Button(btns, text="Actualizar", command=self._update).pack(side="left", padx=2)
        ttk.Button(btns, text="Eliminar", command=self._delete).pack(side="left", padx=2)

    def _draw_form(self):
        for w in self.form_container.winfo_children(): w.destroy()
        self.inputs = {}
        cls = self.mapping[self.current_key]["class"]
        for f in fields(cls):
            ttk.Label(self.form_container, text=f"{f.name.upper()}:").pack(anchor="w")
            ent = ttk.Entry(self.form_container)
            ent.pack(fill="x", pady=(0, 5))
            self.inputs[f.name] = ent

    def _change_table(self, _):
        self.current_key = self.combo.get()
        self._draw_form()
        self.refresh_grid()

    def refresh_grid(self):
        dao = self.mapping[self.current_key]["dao"]
        try:
            data = dao.listar()
            self.tree.delete(*self.tree.get_children())
            if not data: return
            cols = [f.name for f in fields(data[0])]
            self.tree["columns"] = cols
            for c in cols:
                self.tree.heading(c, text=c.title())
                self.tree.column(c, width=100)
            for item in data:
                self.tree.insert("", "end", values=tuple(asdict(item).values()))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_select(self, _):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            for i, key in enumerate(self.inputs.keys()):
                self.inputs[key].delete(0, tk.END)
                if vals[i] != "None": self.inputs[key].insert(0, vals[i])

    def _get_obj(self):
        cls = self.mapping[self.current_key]["class"]
        raw = {k: v.get() for k, v in self.inputs.items()}
        for f in fields(cls):
            if raw[f.name] == "": raw[f.name] = None
            elif f.type == int or f.type == Optional[int]: 
                raw[f.name] = int(raw[f.name]) if raw[f.name] is not None else None
            elif f.type == float: raw[f.name] = float(raw[f.name])
        return cls(**raw)

    def _create(self):
        try:
            self.mapping[self.current_key]["dao"].crear(self._get_obj())
            self.refresh_grid()
            messagebox.showinfo("OK", "Registro creado")
        except Exception as e: messagebox.showerror("Error", str(e))

    def _update(self):
        try:
            self.mapping[self.current_key]["dao"].actualizar(self._get_obj())
            self.refresh_grid()
            messagebox.showinfo("OK", "Actualizado")
        except Exception as e: messagebox.showerror("Error", str(e))

    def _delete(self):
        sel = self.tree.selection()
        if not sel: return
        pk = self.tree.item(sel[0], "values")[0]
        if messagebox.askyesno("?", "¿Eliminar registro?"):
            self.mapping[self.current_key]["dao"].eliminar(pk)
            self.refresh_grid()

    def _clear(self):
        for e in self.inputs.values(): e.delete(0, tk.END)

# =========================================================
# CONFIGURACIÓN
# =========================================================

DB_CONFIG = {
    "dbname": "Hotel",
    "user": "postgres",
    "password": "20231020128",
    "host": "localhost",
    "port": "5432",
}

if __name__ == "__main__":
    schema = "hotel"
    # Mapeo exclusivo de tus tablas SQL
    mapping = {
        "persona": {"dao": PostgresDAO(DB_CONFIG, schema, "persona", Persona, "id_persona"), "class": Persona},
        "telefono": {"dao": PostgresDAO(DB_CONFIG, schema, "telefono", Telefono, "id_telefono"), "class": Telefono},
        "cliente": {"dao": PostgresDAO(DB_CONFIG, schema, "cliente", Cliente, "id_persona"), "class": Cliente},
        "empleado": {"dao": PostgresDAO(DB_CONFIG, schema, "empleado", Empleado, "id_persona"), "class": Empleado},
        "habitacion": {"dao": PostgresDAO(DB_CONFIG, schema, "habitacion", Habitacion, "numero_h"), "class": Habitacion},
        "reserva": {"dao": PostgresDAO(DB_CONFIG, schema, "reserva", Reserva, "id_reserva"), "class": Reserva},
        "servicio": {"dao": PostgresDAO(DB_CONFIG, schema, "servicio", Servicio, "id_servicio"), "class": Servicio},
        "consumo": {"dao": PostgresDAO(DB_CONFIG, schema, "consumo", Consumo, "id_consumo"), "class": Consumo},
    }
    
    app = CRUDApp(DB_CONFIG, mapping)
    app.mainloop()