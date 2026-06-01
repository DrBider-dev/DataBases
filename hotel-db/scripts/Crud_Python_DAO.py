import os
import tkinter as tk
from contextlib import contextmanager
from tkinter import ttk, messagebox
from typing import Any, Dict, List, Optional, Tuple

try:
    import psycopg2
    from psycopg2 import sql
except ImportError as exc:
    raise SystemExit(
        "Falta instalar psycopg2-binary. Ejecuta: pip install psycopg2-binary"
    ) from exc


# =========================================================
# CONFIGURACIÓN DE CONEXIÓN
# =========================================================
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "Hotel"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "20231020128"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

SCHEMA_NAME = "hotel"


# =========================================================
# METADATOS DE LAS TABLAS
# =========================================================
TABLES: Dict[str, Dict[str, Any]] = {
    "persona": {
        "label": "Persona",
        "pk": "id_persona",
        "columns": [
            {"name": "id_persona", "label": "ID Persona", "type": "bigint", "required": True, "pk": True},
            {"name": "primer_nombre", "label": "Primer nombre", "type": "text", "required": True},
            {"name": "segundo_nombre", "label": "Segundo nombre", "type": "text", "required": False},
            {"name": "primer_apellido", "label": "Primer apellido", "type": "text", "required": True},
            {"name": "segundo_apellido", "label": "Segundo apellido", "type": "text", "required": False},
            {"name": "email", "label": "Email", "type": "text", "required": True},
            {"name": "calle", "label": "Calle", "type": "text", "required": False},
            {"name": "carrera", "label": "Carrera", "type": "text", "required": False},
            {"name": "numero", "label": "Número", "type": "text", "required": False},
        ],
    },
    "telefono": {
        "label": "Teléfono",
        "pk": "id_telefono",
        "columns": [
            {"name": "id_telefono", "label": "ID Teléfono", "type": "int", "required": False, "pk": True, "auto": True},
            {"name": "id_persona", "label": "Persona", "type": "fk", "required": True, "fk": "persona"},
            {"name": "telefono", "label": "Teléfono", "type": "text", "required": True},
        ],
    },
    "cliente": {
        "label": "Cliente",
        "pk": "id_persona",
        "columns": [
            {"name": "id_persona", "label": "Persona", "type": "fk", "required": True, "pk": True, "fk": "persona"},
        ],
    },
    "empleado": {
        "label": "Empleado",
        "pk": "id_persona",
        "columns": [
            {"name": "id_persona", "label": "Persona", "type": "fk", "required": True, "pk": True, "fk": "persona"},
            {"name": "cargo", "label": "Cargo", "type": "text", "required": True},
            {"name": "area", "label": "Área", "type": "text", "required": True},
        ],
    },
    "habitacion": {
        "label": "Habitación",
        "pk": "numero_h",
        "columns": [
            {"name": "numero_h", "label": "Número habitación", "type": "int", "required": True, "pk": True},
            {"name": "tipo", "label": "Tipo", "type": "choice", "required": True, "choices": ["Sencilla", "Doble", "Suite"]},
            {"name": "estado", "label": "Estado", "type": "choice", "required": True, "choices": ["Disponible", "Ocupada", "Mantenimiento"]},
            {"name": "precio_noche", "label": "Precio noche", "type": "numeric", "required": True},
        ],
    },
    "reserva": {
        "label": "Reserva",
        "pk": "id_reserva",
        "columns": [
            {"name": "id_reserva", "label": "ID Reserva", "type": "int", "required": False, "pk": True, "auto": True},
            {"name": "id_cliente", "label": "Cliente", "type": "fk", "required": True, "fk": "cliente"},
            {"name": "numero_h", "label": "Habitación", "type": "fk", "required": True, "fk": "habitacion"},
            {"name": "fecha_llegada", "label": "Fecha llegada", "type": "date", "required": True},
            {"name": "fecha_salida", "label": "Fecha salida", "type": "date", "required": True},
            {"name": "valor_reserva", "label": "Valor reserva", "type": "numeric", "required": True},
            {"name": "tiempo_maxc", "label": "Tiempo máximo", "type": "int", "required": True},
        ],
    },
    "servicio": {
        "label": "Servicio",
        "pk": "id_servicio",
        "columns": [
            {"name": "id_servicio", "label": "ID Servicio", "type": "int", "required": False, "pk": True, "auto": True},
            {"name": "nombre", "label": "Nombre", "type": "text", "required": True},
            {"name": "descripcion", "label": "Descripción", "type": "text", "required": False},
            {"name": "costo", "label": "Costo", "type": "numeric", "required": True},
            {"name": "estado", "label": "Estado", "type": "choice", "required": True, "choices": ["Activo", "Inactivo"]},
        ],
    },
    "consumo": {
        "label": "Consumo",
        "pk": "id_consumo",
        "columns": [
            {"name": "id_consumo", "label": "ID Consumo", "type": "int", "required": False, "pk": True, "auto": True},
            {"name": "id_reserva", "label": "Reserva", "type": "fk", "required": True, "fk": "reserva"},
            {"name": "id_servicio", "label": "Servicio", "type": "fk", "required": True, "fk": "servicio"},
            {"name": "fecha_hora", "label": "Fecha y hora", "type": "datetime", "required": False},
        ],
    },
}


class HotelDAO:
    """
    DAO genérico para las tablas del esquema hotel.

    La interfaz gráfica no ejecuta SQL directamente: solo llama a este DAO.
    """

    def __init__(self, config: Dict[str, Any], schema_name: str, tables: Dict[str, Dict[str, Any]]):
        self.config = config
        self.schema_name = schema_name
        self.tables = tables

    @contextmanager
    def _connection(self):
        conn = psycopg2.connect(**self.config)
        conn.autocommit = False
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema_name))
                )
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_meta(self, table_name: str) -> Dict[str, Any]:
        return self.tables[table_name]

    def get_pk(self, table_name: str) -> str:
        return self.tables[table_name]["pk"]

    def get_column_meta(self, table_name: str, column_name: str) -> Dict[str, Any]:
        for col in self.tables[table_name]["columns"]:
            if col["name"] == column_name:
                return col
        raise KeyError(column_name)

    def _table_columns(self, table_name: str) -> List[str]:
        return [col["name"] for col in self.tables[table_name]["columns"]]

    def listar(self, table_name: str) -> List[Tuple[Any, ...]]:
        columns = self._table_columns(table_name)
        meta = self.get_meta(table_name)
        query = sql.SQL("SELECT {} FROM {}.{} ORDER BY {}").format(
            sql.SQL(", ").join(sql.Identifier(c) for c in columns),
            sql.Identifier(self.schema_name),
            sql.Identifier(table_name),
            sql.Identifier(meta["pk"]),
        )

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def obtener_por_pk(self, table_name: str, pk_value: Any) -> Optional[Tuple[Any, ...]]:
        meta = self.get_meta(table_name)
        columns = self._table_columns(table_name)
        query = sql.SQL("SELECT {} FROM {}.{} WHERE {} = %s").format(
            sql.SQL(", ").join(sql.Identifier(c) for c in columns),
            sql.Identifier(self.schema_name),
            sql.Identifier(table_name),
            sql.Identifier(meta["pk"]),
        )

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (pk_value,))
                return cur.fetchone()

    def crear(self, table_name: str, data: Dict[str, Any]) -> int:
        meta = self.get_meta(table_name)
        insert_cols: List[str] = []
        insert_vals: List[Any] = []

        for col in meta["columns"]:
            name = col["name"]
            auto = col.get("auto", False)
            if auto and name not in data:
                continue
            if name in data:
                insert_cols.append(name)
                insert_vals.append(data[name])

        if not insert_cols:
            raise ValueError("No hay datos válidos para insertar.")

        query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
            sql.Identifier(self.schema_name),
            sql.Identifier(table_name),
            sql.SQL(", ").join(sql.Identifier(c) for c in insert_cols),
            sql.SQL(", ").join(sql.Placeholder() for _ in insert_cols),
        )

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, insert_vals)
            return 1

    def actualizar(self, table_name: str, data: Dict[str, Any], pk_value: Any = None) -> int:
        meta = self.get_meta(table_name)
        pk = meta["pk"]
        effective_pk = data.get(pk, pk_value)

        if effective_pk is None:
            raise ValueError("No se encontró el valor de la clave primaria.")

        update_cols: List[str] = []
        update_vals: List[Any] = []

        for col in meta["columns"]:
            name = col["name"]
            if name == pk or col.get("auto", False):
                continue
            if name in data:
                update_cols.append(name)
                update_vals.append(data[name])

        if not update_cols:
            raise ValueError("No hay campos para actualizar.")

        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder())
            for col in update_cols
        )
        query = sql.SQL("UPDATE {}.{} SET {} WHERE {} = {}").format(
            sql.Identifier(self.schema_name),
            sql.Identifier(table_name),
            set_clause,
            sql.Identifier(pk),
            sql.Placeholder(),
        )

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, update_vals + [effective_pk])
                return cur.rowcount

    def eliminar(self, table_name: str, pk_value: Any) -> int:
        meta = self.get_meta(table_name)
        query = sql.SQL("DELETE FROM {}.{} WHERE {} = {}").format(
            sql.Identifier(self.schema_name),
            sql.Identifier(table_name),
            sql.Identifier(meta["pk"]),
            sql.Placeholder(),
        )

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (pk_value,))
                return cur.rowcount

    def fk_options(self, ref_table: str) -> List[Tuple[Any, str]]:
        with self._connection() as conn:
            with conn.cursor() as cur:
                if ref_table == "persona":
                    q = """
                        SELECT id_persona,
                               TRIM(CONCAT_WS(' ', primer_nombre, segundo_nombre, primer_apellido, segundo_apellido)) AS label
                        FROM persona
                        ORDER BY id_persona
                    """
                elif ref_table == "cliente":
                    q = """
                        SELECT c.id_persona,
                               TRIM(CONCAT_WS(' ', p.primer_nombre, p.primer_apellido)) AS label
                        FROM cliente c
                        JOIN persona p ON p.id_persona = c.id_persona
                        ORDER BY c.id_persona
                    """
                elif ref_table == "empleado":
                    q = """
                        SELECT e.id_persona,
                               TRIM(CONCAT_WS(' ', p.primer_nombre, p.primer_apellido)) || ' - ' || e.cargo AS label
                        FROM empleado e
                        JOIN persona p ON p.id_persona = e.id_persona
                        ORDER BY e.id_persona
                    """
                elif ref_table == "habitacion":
                    q = """
                        SELECT numero_h,
                               numero_h::text || ' - ' || tipo || ' - ' || estado AS label
                        FROM habitacion
                        ORDER BY numero_h
                    """
                elif ref_table == "reserva":
                    q = """
                        SELECT r.id_reserva,
                               'Res ' || r.id_reserva::text || ' | Cliente ' || r.id_cliente::text || ' | Hab ' || r.numero_h::text AS label
                        FROM reserva r
                        ORDER BY r.id_reserva
                    """
                elif ref_table == "servicio":
                    q = """
                        SELECT id_servicio,
                               id_servicio::text || ' - ' || nombre AS label
                        FROM servicio
                        ORDER BY id_servicio
                    """
                else:
                    raise ValueError(f"Tabla referenciada no soportada: {ref_table}")

                cur.execute(q)
                return cur.fetchall()

    def crear_tabla(self, table_name: str) -> None:
        """
        Método de conveniencia para mantener una estructura parecida al ejemplo DAO.
        En este proyecto la base de datos ya está creada, así que no se usa desde la GUI.
        """
        raise NotImplementedError(
            "La creación de tablas no está implementada en este refactor porque "
            "la base de datos ya existe."
        )


class CRUDApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CRUD Hotel - PostgreSQL")
        self.geometry("1280x760")
        self.minsize(1100, 700)

        self.dao = HotelDAO(DB_CONFIG, SCHEMA_NAME, TABLES)

        try:
            # Verificación rápida de conexión.
            self.dao.listar("persona")
        except Exception as exc:
            messagebox.showerror(
                "Error de conexión",
                "No se pudo conectar a PostgreSQL.\n\n"
                f"Revisa tus credenciales y la base de datos.\n\nDetalle: {exc}",
            )
            raise

        self.current_table = tk.StringVar(value="persona")
        self.field_widgets: Dict[str, Any] = {}
        self.selected_pk_value = None

        self._build_style()
        self._build_ui()
        self._load_table_names()
        self._refresh_table()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------
    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=26)
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=3)
        style.configure("TEntry", padding=4)
        style.configure("TCombobox", padding=4)

    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Tabla:").pack(side="left")
        self.table_combo = ttk.Combobox(
            top,
            textvariable=self.current_table,
            state="readonly",
            width=30,
        )
        self.table_combo.pack(side="left", padx=8)
        self.table_combo.bind("<<ComboboxSelected>>", self.on_table_change)

        ttk.Button(top, text="Refrescar", command=self._refresh_table).pack(side="left", padx=5)
        ttk.Button(top, text="Limpiar formulario", command=self.clear_form).pack(side="left", padx=5)

        main = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.Frame(main, padding=8)
        right = ttk.Frame(main, padding=8)
        main.add(left, weight=3)
        main.add(right, weight=2)

        tree_frame = ttk.LabelFrame(left, text="Registros", padding=8)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, show="headings")
        self.tree.pack(fill="both", expand=True, side="left")

        yscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        yscroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        form_frame = ttk.LabelFrame(right, text="Formulario", padding=8)
        form_frame.pack(fill="both", expand=True)

        self.form_canvas = tk.Canvas(form_frame, highlightthickness=0)
        self.form_canvas.pack(side="left", fill="both", expand=True)

        form_scroll = ttk.Scrollbar(form_frame, orient="vertical", command=self.form_canvas.yview)
        form_scroll.pack(side="right", fill="y")
        self.form_canvas.configure(yscrollcommand=form_scroll.set)

        self.form_inner = ttk.Frame(self.form_canvas)
        self.form_window = self.form_canvas.create_window((0, 0), window=self.form_inner, anchor="nw")
        self.form_inner.bind("<Configure>", self._on_form_configure)
        self.form_canvas.bind("<Configure>", self._on_canvas_configure)

        btns = ttk.Frame(right, padding=(0, 10, 0, 0))
        btns.pack(fill="x")

        ttk.Button(btns, text="Crear", command=self.create_record).pack(side="left", padx=4)
        ttk.Button(btns, text="Actualizar", command=self.update_record).pack(side="left", padx=4)
        ttk.Button(btns, text="Eliminar", command=self.delete_record).pack(side="left", padx=4)
        ttk.Button(btns, text="Buscar por PK", command=self.search_by_pk).pack(side="left", padx=4)

    def _on_form_configure(self, _event) -> None:
        self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self.form_canvas.itemconfigure(self.form_window, width=event.width)

    def _load_table_names(self) -> None:
        tables = list(TABLES.keys())
        self.table_combo["values"] = tables
        self.table_combo.set(self.current_table.get())

    # -----------------------------------------------------
    # Metadatos y combos
    # -----------------------------------------------------
    def get_meta(self, table_name: str) -> Dict[str, Any]:
        return self.dao.get_meta(table_name)

    def get_pk_column(self, table_name: str) -> str:
        return self.dao.get_pk(table_name)

    def get_column_meta(self, table_name: str, column_name: str) -> Dict[str, Any]:
        return self.dao.get_column_meta(table_name, column_name)

    def fk_options(self, ref_table: str) -> List[Tuple[Any, str]]:
        return self.dao.fk_options(ref_table)

    # -----------------------------------------------------
    # Construcción del formulario
    # -----------------------------------------------------
    def rebuild_form(self) -> None:
        for widget in self.form_inner.winfo_children():
            widget.destroy()
        self.field_widgets.clear()
        self.selected_pk_value = None

        table_name = self.current_table.get()
        meta = self.get_meta(table_name)

        row = 0
        for col in meta["columns"]:
            name = col["name"]
            label = col["label"]
            required = col.get("required", False)
            is_pk = col.get("pk", False)
            auto = col.get("auto", False)
            col_type = col.get("type", "text")

            ttk.Label(self.form_inner, text=label + (":" if not required else " *:")).grid(
                row=row, column=0, sticky="w", padx=4, pady=5
            )

            if col_type == "choice":
                widget = ttk.Combobox(self.form_inner, state="readonly", width=30, values=col["choices"])
            elif col_type == "fk":
                widget = ttk.Combobox(self.form_inner, state="readonly", width=30)
                opts = self.fk_options(col["fk"])
                widget["values"] = [f"{pk} | {label}" for pk, label in opts]
            else:
                widget = ttk.Entry(self.form_inner, width=34)

            widget.grid(row=row, column=1, sticky="ew", padx=4, pady=5)

            if is_pk and auto:
                try:
                    widget.configure(state="disabled")
                except tk.TclError:
                    pass

            self.field_widgets[name] = widget
            row += 1

        self.form_inner.columnconfigure(1, weight=1)

    def clear_form(self) -> None:
        for col in self.get_meta(self.current_table.get())["columns"]:
            w = self.field_widgets.get(col["name"])
            if w is None:
                continue
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                state = str(w.cget("state"))
                if state == "disabled":
                    w.configure(state="normal")
                    w.delete(0, tk.END)
                    w.configure(state="disabled")
                else:
                    w.delete(0, tk.END)
        self.selected_pk_value = None
        self.tree.selection_remove(self.tree.selection())

    # -----------------------------------------------------
    # Carga de datos
    # -----------------------------------------------------
    def _refresh_table(self) -> None:
        self.rebuild_form()
        self.load_data()

    def on_table_change(self, _event=None) -> None:
        self._refresh_table()

    def load_data(self) -> None:
        table_name = self.current_table.get()
        meta = self.get_meta(table_name)
        columns = [col["name"] for col in meta["columns"]]

        self.tree["columns"] = columns
        for c in self.tree["columns"]:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")

        try:
            rows = self.dao.listar(table_name)
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{exc}")
            return

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    # -----------------------------------------------------
    # Helpers de formulario
    # -----------------------------------------------------
    def parse_value(self, value: str, col_meta: Dict[str, Any]) -> Any:
        if value == "":
            return None
        col_type = col_meta.get("type", "text")

        if col_type in ("int", "bigint"):
            return int(value)
        if col_type == "numeric":
            return float(value)
        if col_type == "date":
            return value
        if col_type == "datetime":
            return value
        if col_type == "fk":
            return int(value.split("|", 1)[0].strip())
        return value

    def get_form_data(self) -> Dict[str, Any]:
        table_name = self.current_table.get()
        meta = self.get_meta(table_name)
        data: Dict[str, Any] = {}

        for col in meta["columns"]:
            name = col["name"]
            auto = col.get("auto", False)
            widget = self.field_widgets[name]
            raw = widget.get().strip() if hasattr(widget, "get") else ""

            if auto and raw == "":
                continue
            if raw == "" and not col.get("required", False):
                data[name] = None
                continue
            if raw == "" and col.get("required", False):
                raise ValueError(f"El campo '{col['label']}' es obligatorio.")

            data[name] = self.parse_value(raw, col)

        return data

    def fill_form_from_row(self, values: Tuple[Any, ...]) -> None:
        table_name = self.current_table.get()
        meta = self.get_meta(table_name)
        self.clear_form()

        for col, value in zip(meta["columns"], values):
            name = col["name"]
            widget = self.field_widgets[name]
            if value is None:
                display = ""
            elif col.get("type") == "fk":
                display = self._format_fk_value(col["fk"], value)
            else:
                display = str(value)

            if isinstance(widget, ttk.Combobox):
                widget.set(display)
            else:
                if str(widget.cget("state")) == "disabled":
                    widget.configure(state="normal")
                    widget.delete(0, tk.END)
                    widget.insert(0, display)
                    widget.configure(state="disabled")
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, display)

        pk_name = meta["pk"]
        self.selected_pk_value = values[[c["name"] for c in meta["columns"]].index(pk_name)]

    def _format_fk_value(self, ref_table: str, pk_value: Any) -> str:
        options = self.fk_options(ref_table)
        for pk, label in options:
            if str(pk) == str(pk_value):
                return f"{pk} | {label}"
        return str(pk_value)

    # -----------------------------------------------------
    # CRUD
    # -----------------------------------------------------
    def create_record(self) -> None:
        table_name = self.current_table.get()

        try:
            data = self.get_form_data()
            self.dao.crear(table_name, data)
            messagebox.showinfo("Éxito", "Registro creado correctamente.")
            self._refresh_table()
            self.clear_form()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo crear el registro:\n{exc}")

    def update_record(self) -> None:
        table_name = self.current_table.get()
        meta = self.get_meta(table_name)
        pk = meta["pk"]

        try:
            data = self.get_form_data()
            if pk not in data and self.selected_pk_value is None:
                raise ValueError("Selecciona un registro o escribe la clave primaria.")

            pk_value = data.get(pk, self.selected_pk_value)
            if pk_value is None:
                raise ValueError("No se encontró el valor de la clave primaria.")

            filas = self.dao.actualizar(table_name, data, pk_value=pk_value)
            if filas == 0:
                messagebox.showwarning("Aviso", "No se actualizó ningún registro.")
                return

            messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
            self._refresh_table()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo actualizar el registro:\n{exc}")

    def delete_record(self) -> None:
        table_name = self.current_table.get()
        meta = self.get_meta(table_name)
        pk = meta["pk"]

        pk_value = self.selected_pk_value
        if pk_value is None:
            widget = self.field_widgets.get(pk)
            if widget is not None:
                raw = widget.get().strip()
                if raw:
                    try:
                        pk_value = self.parse_value(raw, self.get_column_meta(table_name, pk))
                    except Exception:
                        pk_value = raw

        if pk_value is None:
            messagebox.showwarning("Aviso", "Selecciona un registro para eliminar.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar el registro con {pk} = {pk_value}?"):
            return

        try:
            filas = self.dao.eliminar(table_name, pk_value)
            if filas == 0:
                messagebox.showwarning("Aviso", "No se encontró el registro a eliminar.")
                return
            messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
            self._refresh_table()
            self.clear_form()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo eliminar el registro:\n{exc}")

    def search_by_pk(self) -> None:
        table_name = self.current_table.get()
        meta = self.get_meta(table_name)
        pk = meta["pk"]

        pk_widget = self.field_widgets.get(pk)
        if pk_widget is None:
            return

        raw = pk_widget.get().strip()
        if not raw:
            messagebox.showwarning("Aviso", "Escribe el valor de la clave primaria en el formulario.")
            return

        try:
            pk_value = self.parse_value(raw, self.get_column_meta(table_name, pk))
            row = self.dao.obtener_por_pk(table_name, pk_value)
            if row is None:
                messagebox.showinfo("Resultado", "No se encontró el registro.")
                return
            self.fill_form_from_row(row)
            self.highlight_row_by_pk(pk_value)
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo buscar el registro:\n{exc}")

    def highlight_row_by_pk(self, pk_value: Any) -> None:
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values and str(values[0]) == str(pk_value):
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                break

    def on_row_select(self, _event=None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.tree.item(item, "values")
        if values:
            self.fill_form_from_row(values)

    # -----------------------------------------------------
    # Cierre
    # -----------------------------------------------------
    def on_close(self) -> None:
        self.destroy()


def main() -> None:
    app = CRUDApp()
    app.mainloop()


if __name__ == "__main__":
    main()
