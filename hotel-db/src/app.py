import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from auth import login_required, role_required, authenticate_user
from util.db import db

load_dotenv(dotenv_path='Raiz.env')

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "proyectohotel_secret_key")

from dao.hotel_dao import (
    PersonaDAO, TelefonoDAO, ClienteDAO, EmpleadoDAO,
    HabitacionDAO, ReservaDAO, ServicioDAO, ConsumoDAO
)
from models.entities import (
    Persona, Telefono, Cliente, Empleado,
    Habitacion, Reserva, Servicio, Consumo
)

p_dao = PersonaDAO()
t_dao = TelefonoDAO()
c_dao = ClienteDAO()
e_dao = EmpleadoDAO()
h_dao = HabitacionDAO()
r_dao = ReservaDAO()
s_dao = ServicioDAO()
co_dao = ConsumoDAO()


def validar_entero_no_negativo(nombre_campo, etiqueta):
    try:
        valor = int(request.form[nombre_campo])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"{etiqueta} debe ser un número entero.")
    if valor < 0:
        raise ValueError(f"{etiqueta} no puede ser negativo.")
    return valor


def validar_decimal_no_negativo(nombre_campo, etiqueta):
    try:
        valor = float(request.form[nombre_campo])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"{etiqueta} debe ser un número.")
    if valor < 0:
        raise ValueError(f"{etiqueta} no puede ser negativo.")
    return valor


def valor_opcional(nombre_campo):
    valor = request.form.get(nombre_campo)
    return valor.strip() if valor and valor.strip() else None


def termino_busqueda():
    return request.args.get('q', '').strip()


def listar_o_buscar(dao, q):
    return dao.buscar(q) if q else dao.listar()


def render_crud(template, dao, **contexto):
    q = termino_busqueda()
    return render_template(template, lista=listar_o_buscar(dao, q), q=q, **contexto)


def obtener_o_redirigir(dao, id, endpoint, mensaje):
    registro = dao.obtener(id)
    if not registro:
        flash(mensaje, "warning")
        return None
    return registro


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        auth = authenticate_user(username, password)
        if auth:
            session['user_id'] = username
            session['user_role'] = auth['role']
            flash(f'Bienvenido, {username}', 'success')
            return redirect(url_for('index'))
        flash('Credenciales inválidas', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))


# -----------------------------------------------------
# INICIO
# -----------------------------------------------------
@app.route('/')
@login_required
def index():
    return render_template('index.html')


# -----------------------------------------------------
# PERSONAS - Solo administrador
# -----------------------------------------------------
@app.route('/personas')
@login_required
def personas():
    return render_crud('personas.html', p_dao, persona_editar=None)


@app.route('/personas/guardar', methods=['POST'])
@login_required
def guardar_persona():
    try:
        p = Persona(
            id_persona=validar_entero_no_negativo('id_persona', 'El ID de la persona'),
            primer_nombre=request.form['primer_nombre'],
            primer_apellido=request.form['primer_apellido'],
            email=request.form['email'],
            segundo_nombre=valor_opcional('segundo_nombre'),
            segundo_apellido=valor_opcional('segundo_apellido'),
            calle=valor_opcional('calle'),
            carrera=valor_opcional('carrera'),
            numero=valor_opcional('numero')
        )
        p_dao.crear(p)
        flash("Persona registrada correctamente", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('personas'))


@app.route('/personas/buscar/<int:id>')
@login_required
def buscar_persona(id):
    persona = obtener_o_redirigir(p_dao, id, 'personas', "No se encontró la persona.")
    if not persona:
        return redirect(url_for('personas'))
    return render_template('personas.html', lista=p_dao.listar(), q='', persona_detalle=persona)


@app.route('/personas/editar/<int:id>')
@login_required
def editar_persona(id):
    persona = obtener_o_redirigir(p_dao, id, 'personas', "No se encontró la persona.")
    if not persona:
        return redirect(url_for('personas'))
    return render_template('personas.html', lista=p_dao.listar(), q='', persona_editar=persona)


@app.route('/personas/actualizar/<int:id>', methods=['POST'])
@login_required
def actualizar_persona(id):
    try:
        p = Persona(
            id_persona=id,
            primer_nombre=request.form['primer_nombre'],
            primer_apellido=request.form['primer_apellido'],
            email=request.form['email'],
            segundo_nombre=valor_opcional('segundo_nombre'),
            segundo_apellido=valor_opcional('segundo_apellido'),
            calle=valor_opcional('calle'),
            carrera=valor_opcional('carrera'),
            numero=valor_opcional('numero')
        )
        p_dao.actualizar(id, p)
        flash("Persona actualizada correctamente", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('personas'))


@app.route('/eliminar/persona/<int:id>')
@login_required
def eliminar_persona(id):
    try:
        p_dao.eliminar(id)
        flash("Persona eliminada", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('personas'))


# -----------------------------------------------------
# TELÉFONOS - Solo administrador
# -----------------------------------------------------
@app.route('/telefonos')
@login_required
def telefonos():
    return render_crud('telefonos.html', t_dao, telefono_editar=None)


@app.route('/telefonos/guardar', methods=['POST'])
@login_required
def guardar_telefono():
    try:
        t = Telefono(
            id_telefono=None,
            id_persona=validar_entero_no_negativo('id_persona', 'El ID de la persona'),
            telefono=request.form['telefono']
        )
        t_dao.crear(t)
        flash("Teléfono guardado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('telefonos'))


@app.route('/telefonos/buscar/<int:id>')
@login_required
def buscar_telefono(id):
    telefono = obtener_o_redirigir(t_dao, id, 'telefonos', "No se encontró el teléfono.")
    if not telefono:
        return redirect(url_for('telefonos'))
    return render_template('telefonos.html', lista=t_dao.listar(), q='', telefono_detalle=telefono)


@app.route('/telefonos/editar/<int:id>')
@login_required
def editar_telefono(id):
    telefono = obtener_o_redirigir(t_dao, id, 'telefonos', "No se encontró el teléfono.")
    if not telefono:
        return redirect(url_for('telefonos'))
    return render_template('telefonos.html', lista=t_dao.listar(), q='', telefono_editar=telefono)


@app.route('/telefonos/actualizar/<int:id>', methods=['POST'])
@login_required
def actualizar_telefono(id):
    try:
        t = Telefono(
            id_telefono=id,
            id_persona=validar_entero_no_negativo('id_persona', 'El ID de la persona'),
            telefono=request.form['telefono']
        )
        t_dao.actualizar(id, t)
        flash("Teléfono actualizado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('telefonos'))


@app.route('/eliminar/telefono/<int:id>')
@login_required
def eliminar_telefono(id):
    try:
        t_dao.eliminar(id)
        flash("Teléfono eliminado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('telefonos'))


# -----------------------------------------------------
# CLIENTES - Gerente y Recepcionista
# -----------------------------------------------------
@app.route('/clientes')
@login_required
@role_required('gerente', 'recepcionista')
def clientes():
    return render_crud('clientes.html', c_dao)


@app.route('/clientes/guardar', methods=['POST'])
@login_required
@role_required('gerente', 'recepcionista')
def guardar_cliente():
    try:
        c = Cliente(id_persona=validar_entero_no_negativo('id_persona', 'El ID de la persona'))
        c_dao.crear(c)
        flash("Cliente registrado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('clientes'))


@app.route('/clientes/buscar/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def buscar_cliente(id):
    cliente = obtener_o_redirigir(c_dao, id, 'clientes', "No se encontró el cliente.")
    if not cliente:
        return redirect(url_for('clientes'))
    return render_template('clientes.html', lista=c_dao.listar(), q='', cliente_detalle=cliente)


@app.route('/eliminar/cliente/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def eliminar_cliente(id):
    try:
        c_dao.eliminar(id)
        flash("Cliente eliminado", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('clientes'))


# -----------------------------------------------------
# EMPLEADOS - Solo Gerente
# -----------------------------------------------------
@app.route('/empleados')
@login_required
@role_required('gerente')
def empleados():
    return render_crud('empleados.html', e_dao, empleado_editar=None)


@app.route('/empleados/guardar', methods=['POST'])
@login_required
@role_required('gerente')
def guardar_empleado():
    try:
        emp = Empleado(
            id_persona=validar_entero_no_negativo('id_persona', 'El ID de la persona'),
            cargo=request.form['cargo'],
            area=request.form['area']
        )
        e_dao.crear(emp)
        flash("Empleado registrado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('empleados'))


@app.route('/empleados/buscar/<int:id>')
@login_required
@role_required('gerente')
def buscar_empleado(id):
    empleado = obtener_o_redirigir(e_dao, id, 'empleados', "No se encontró el empleado.")
    if not empleado:
        return redirect(url_for('empleados'))
    return render_template('empleados.html', lista=e_dao.listar(), q='', empleado_detalle=empleado)


@app.route('/empleados/editar/<int:id>')
@login_required
@role_required('gerente')
def editar_empleado(id):
    empleado = obtener_o_redirigir(e_dao, id, 'empleados', "No se encontró el empleado.")
    if not empleado:
        return redirect(url_for('empleados'))
    return render_template('empleados.html', lista=e_dao.listar(), q='', empleado_editar=empleado)


@app.route('/empleados/actualizar/<int:id>', methods=['POST'])
@login_required
@role_required('gerente')
def actualizar_empleado(id):
    try:
        emp = Empleado(
            id_persona=validar_entero_no_negativo('id_persona', 'El ID de la persona'),
            cargo=request.form['cargo'],
            area=request.form['area']
        )
        e_dao.actualizar(id, emp)
        flash("Empleado actualizado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('empleados'))


@app.route('/eliminar/empleado/<int:id>')
@login_required
@role_required('gerente')
def eliminar_empleado(id):
    try:
        e_dao.eliminar(id)
        flash("Empleado eliminado", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('empleados'))


# -----------------------------------------------------
# HABITACIONES - Gerente, Recepcionista, Empleado limpieza
# -----------------------------------------------------
@app.route('/habitaciones')
@login_required
def habitaciones():
    user_role = session.get('user_role')
    if user_role == 'empleado_limpieza':
        lista = h_dao.listar()
        return render_template('habitaciones_limpieza.html', lista=lista, q='')
    return render_crud('habitaciones.html', h_dao, habitacion_editar=None)


@app.route('/habitaciones/guardar', methods=['POST'])
@login_required
@role_required('gerente', 'recepcionista')
def guardar_habitacion():
    try:
        h = Habitacion(
            numero_h=validar_entero_no_negativo('numero_h', 'El número de habitación'),
            tipo=request.form['tipo'],
            estado=request.form['estado'],
            precio_noche=validar_decimal_no_negativo('precio_noche', 'El precio por noche')
        )
        h_dao.crear(h)
        flash("Habitación creada", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('habitaciones'))


@app.route('/habitaciones/buscar/<int:id>')
@login_required
def habitacion_detalle(id):
    habitacion = obtener_o_redirigir(h_dao, id, 'habitaciones', "No se encontró la habitación.")
    if not habitacion:
        return redirect(url_for('habitaciones'))
    template = 'habitaciones_limpieza.html' if session.get('user_role') == 'empleado_limpieza' else 'habitaciones.html'
    return render_template(template, lista=h_dao.listar(), q='', habitacion_detalle=habitacion)


@app.route('/habitaciones/editar/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def editar_habitacion(id):
    habitacion = obtener_o_redirigir(h_dao, id, 'habitaciones', "No se encontró la habitación.")
    if not habitacion:
        return redirect(url_for('habitaciones'))
    return render_template('habitaciones.html', lista=h_dao.listar(), q='', habitacion_editar=habitacion)


@app.route('/habitaciones/actualizar/<int:id>', methods=['POST'])
@login_required
def actualizar_habitacion(id):
    user_role = session.get('user_role')
    try:
        if user_role == 'empleado_limpieza':
            h_dao.actualizar_estado(id, request.form['estado'])
            flash("Estado de habitación actualizado", "success")
        else:
            h = Habitacion(
                numero_h=id,
                tipo=request.form['tipo'],
                estado=request.form['estado'],
                precio_noche=validar_decimal_no_negativo('precio_noche', 'El precio por noche')
            )
            h_dao.actualizar(id, h)
            flash("Habitación actualizada", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('habitaciones'))


@app.route('/eliminar/habitacion/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def eliminar_habitacion(id):
    try:
        h_dao.eliminar(id)
        flash("Habitación eliminada", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('habitaciones'))


# -----------------------------------------------------
# RESERVAS - Gerente y Recepcionista
# -----------------------------------------------------
@app.route('/reservas')
@login_required
@role_required('gerente', 'recepcionista')
def reservas():
    return render_crud('reservas.html', r_dao, reserva_editar=None)


@app.route('/reservas/guardar', methods=['POST'])
@login_required
@role_required('gerente', 'recepcionista')
def guardar_reserva():
    try:
        res = Reserva(
            id_reserva=None,
            id_cliente=validar_entero_no_negativo('id_cliente', 'El ID del cliente'),
            numero_h=validar_entero_no_negativo('numero_h', 'El número de habitación'),
            fecha_llegada=request.form['fecha_llegada'],
            fecha_salida=request.form['fecha_salida'],
            valor_reserva=validar_decimal_no_negativo('valor_reserva', 'El valor de la reserva'),
            tiempo_maxc=validar_entero_no_negativo('tiempo_maxc', 'El tiempo máximo')
        )
        r_dao.crear(res)
        flash("Reserva exitosa", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('reservas'))


@app.route('/reservas/buscar/<int:id>')
@login_required
@role_required('gerente', 'recepcionista', 'cliente_usuario')
def buscar_reserva(id):
    reserva = obtener_o_redirigir(r_dao, id, 'reservas', "No se encontró la reserva.")
    if not reserva:
        return redirect(url_for('reservas'))
    return render_template('reservas.html', lista=r_dao.listar(), q='', reserva_detalle=reserva)


@app.route('/reservas/editar/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def editar_reserva(id):
    reserva = obtener_o_redirigir(r_dao, id, 'reservas', "No se encontró la reserva.")
    if not reserva:
        return redirect(url_for('reservas'))
    return render_template('reservas.html', lista=r_dao.listar(), q='', reserva_editar=reserva)


@app.route('/reservas/actualizar/<int:id>', methods=['POST'])
@login_required
@role_required('gerente', 'recepcionista')
def actualizar_reserva(id):
    try:
        res = Reserva(
            id_reserva=id,
            id_cliente=validar_entero_no_negativo('id_cliente', 'El ID del cliente'),
            numero_h=validar_entero_no_negativo('numero_h', 'El número de habitación'),
            fecha_llegada=request.form['fecha_llegada'],
            fecha_salida=request.form['fecha_salida'],
            valor_reserva=validar_decimal_no_negativo('valor_reserva', 'El valor de la reserva'),
            tiempo_maxc=validar_entero_no_negativo('tiempo_maxc', 'El tiempo máximo')
        )
        r_dao.actualizar(id, res)
        flash("Reserva actualizada", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('reservas'))


@app.route('/eliminar/reserva/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def eliminar_reserva(id):
    try:
        r_dao.eliminar(id)
        flash("Reserva eliminada", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('reservas'))


# -----------------------------------------------------
# MIS RESERVAS - Cliente usuario
# -----------------------------------------------------
@app.route('/mis/reservas')
@login_required
@role_required('cliente_usuario')
def mis_reservas():
    user_id = session.get('user_id')
    lista = r_dao.buscar_por_cliente(user_id) if user_id else []
    return render_template('mis_reservas.html', lista=lista, q='')


# -----------------------------------------------------
# SERVICIOS - Solo Gerente
# -----------------------------------------------------
@app.route('/servicios')
@login_required
@role_required('gerente')
def servicios():
    return render_crud('servicios.html', s_dao, servicio_editar=None)


@app.route('/servicios/guardar', methods=['POST'])
@login_required
@role_required('gerente')
def guardar_servicio():
    try:
        ser = Servicio(
            id_servicio=None,
            nombre=request.form['nombre'],
            descripcion=valor_opcional('descripcion'),
            costo=validar_decimal_no_negativo('costo', 'El costo'),
            estado=request.form['estado']
        )
        s_dao.crear(ser)
        flash("Servicio creado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('servicios'))


@app.route('/servicios/buscar/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def buscar_servicio(id):
    servicio = obtener_o_redirigir(s_dao, id, 'servicios', "No se encontró el servicio.")
    if not servicio:
        return redirect(url_for('servicios'))
    return render_template('servicios.html', lista=s_dao.listar(), q='', servicio_detalle=servicio)


@app.route('/servicios/editar/<int:id>')
@login_required
@role_required('gerente')
def editar_servicio(id):
    servicio = obtener_o_redirigir(s_dao, id, 'servicios', "No se encontró el servicio.")
    if not servicio:
        return redirect(url_for('servicios'))
    return render_template('servicios.html', lista=s_dao.listar(), q='', servicio_editar=servicio)


@app.route('/servicios/actualizar/<int:id>', methods=['POST'])
@login_required
@role_required('gerente')
def actualizar_servicio(id):
    try:
        ser = Servicio(
            id_servicio=id,
            nombre=request.form['nombre'],
            descripcion=valor_opcional('descripcion'),
            costo=validar_decimal_no_negativo('costo', 'El costo'),
            estado=request.form['estado']
        )
        s_dao.actualizar(id, ser)
        flash("Servicio actualizado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('servicios'))


@app.route('/eliminar/servicio/<int:id>')
@login_required
@role_required('gerente')
def eliminar_servicio(id):
    try:
        s_dao.eliminar(id)
        flash("Servicio eliminado", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('servicios'))


# -----------------------------------------------------
# CONSUMOS - Gerente y Recepcionista
# -----------------------------------------------------
@app.route('/consumos')
@login_required
@role_required('gerente', 'recepcionista')
def consumos():
    return render_crud('consumos.html', co_dao, consumo_editar=None)


@app.route('/consumos/guardar', methods=['POST'])
@login_required
@role_required('gerente', 'recepcionista')
def guardar_consumo():
    try:
        con = Consumo(
            id_consumo=None,
            id_reserva=validar_entero_no_negativo('id_reserva', 'El ID de la reserva'),
            id_servicio=validar_entero_no_negativo('id_servicio', 'El ID del servicio'),
            fecha_hora=valor_opcional('fecha_hora')
        )
        co_dao.crear(con)
        flash("Consumo cargado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('consumos'))


@app.route('/consumos/buscar/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def buscar_consumo(id):
    consumo = obtener_o_redirigir(co_dao, id, 'consumos', "No se encontró el consumo.")
    if not consumo:
        return redirect(url_for('consumos'))
    return render_template('consumos.html', lista=co_dao.listar(), q='', consumo_detalle=consumo)


@app.route('/consumos/editar/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def editar_consumo(id):
    consumo = obtener_o_redirigir(co_dao, id, 'consumos', "No se encontró el consumo.")
    if not consumo:
        return redirect(url_for('consumos'))
    return render_template('consumos.html', lista=co_dao.listar(), q='', consumo_editar=consumo)


@app.route('/consumos/actualizar/<int:id>', methods=['POST'])
@login_required
@role_required('gerente', 'recepcionista')
def actualizar_consumo(id):
    try:
        con = Consumo(
            id_consumo=id,
            id_reserva=validar_entero_no_negativo('id_reserva', 'El ID de la reserva'),
            id_servicio=validar_entero_no_negativo('id_servicio', 'El ID del servicio'),
            fecha_hora=valor_opcional('fecha_hora')
        )
        co_dao.actualizar(id, con)
        flash("Consumo actualizado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('consumos'))


@app.route('/eliminar/consumo/<int:id>')
@login_required
@role_required('gerente', 'recepcionista')
def eliminar_consumo(id):
    try:
        co_dao.eliminar(id)
        flash("Consumo eliminado", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('consumos'))


@app.route('/mis/consumos')
@login_required
@role_required('cliente_usuario')
def mis_consumos():
    user_id = session.get('user_id')
    lista = co_dao.buscar_por_cliente(user_id) if user_id else []
    return render_template('mis_consumos.html', lista=lista, q='')


if __name__ == '__main__':
    app.run(debug=True)