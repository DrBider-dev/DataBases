import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

# Importación de DAOs y Entidades
from dao.hotel_dao import (
    PersonaDAO, TelefonoDAO, ClienteDAO, EmpleadoDAO, 
    HabitacionDAO, ReservaDAO, ServicioDAO, ConsumoDAO
)
from models.entities import (
    Persona, Telefono, Cliente, Empleado, 
    Habitacion, Reserva, Servicio, Consumo
)

# Forzamos la carga desde Raiz.env
load_dotenv(dotenv_path='Raiz.env')

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "proyectohotel_secret_key")

# Instanciación de todos los DAOs
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

# -----------------------------------------------------
# INICIO
# -----------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------------------------------------
# PERSONAS
# -----------------------------------------------------
@app.route('/personas')
def personas():
    return render_template('personas.html', lista=p_dao.listar())

@app.route('/personas/guardar', methods=['POST'])
def guardar_persona():
    try:
        p = Persona(
            id_persona=validar_entero_no_negativo('id_persona', 'El ID de la persona'),
            primer_nombre=request.form['primer_nombre'],
            primer_apellido=request.form['primer_apellido'],
            email=request.form['email'],
            segundo_nombre=request.form.get('segundo_nombre'),
            segundo_apellido=request.form.get('segundo_apellido'),
            calle=request.form.get('calle'),
            carrera=request.form.get('carrera'),
            numero=request.form.get('numero')
        )
        p_dao.crear(p)
        flash("Persona registrada correctamente", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('personas'))

@app.route('/eliminar/persona/<int:id>')
def eliminar_persona(id):
    try:
        p_dao.eliminar(id)
        flash("Persona eliminada", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('personas'))

# -----------------------------------------------------
# TELÉFONOS
# -----------------------------------------------------
@app.route('/telefonos')
def telefonos():
    return render_template('telefonos.html', lista=t_dao.listar())

@app.route('/telefonos/guardar', methods=['POST'])
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

@app.route('/eliminar/telefono/<int:id>')
def eliminar_telefono(id):
    try:
        t_dao.eliminar(id)
        flash("Teléfono eliminado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('telefonos'))

# -----------------------------------------------------
# CLIENTES
# -----------------------------------------------------
@app.route('/clientes')
def clientes():
    return render_template('clientes.html', lista=c_dao.listar())

@app.route('/clientes/guardar', methods=['POST'])
def guardar_cliente():
    try:
        c = Cliente(id_persona=validar_entero_no_negativo('id_persona', 'El ID de la persona'))
        c_dao.crear(c)
        flash("Cliente registrado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('clientes'))

@app.route('/eliminar/cliente/<int:id>')
def eliminar_cliente(id):
    try:
        c_dao.eliminar(id)
        flash("Cliente eliminado", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('clientes'))

# -----------------------------------------------------
# EMPLEADOS
# -----------------------------------------------------
@app.route('/empleados')
def empleados():
    return render_template('empleados.html', lista=e_dao.listar())

@app.route('/empleados/guardar', methods=['POST'])
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

@app.route('/eliminar/empleado/<int:id>')
def eliminar_empleado(id):
    try:
        e_dao.eliminar(id)
        flash("Empleado eliminado", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('empleados'))

# -----------------------------------------------------
# HABITACIONES
# -----------------------------------------------------
@app.route('/habitaciones')
def habitaciones():
    return render_template('habitaciones.html', lista=h_dao.listar())

@app.route('/habitaciones/guardar', methods=['POST'])
def guardar_habitacion():
    try:
        h = Habitacion(
            numero_h=validar_entero_no_negativo('numero_h', 'El número de habitación'),
            tipo=request.form['tipo'],
            estado=request.form['estado'],
            precio_noche=float(request.form['precio_noche'])
        )
        h_dao.crear(h)
        flash("Habitación creada", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('habitaciones'))

@app.route('/eliminar/habitacion/<int:id>')
def eliminar_habitacion(id):
    try:
        h_dao.eliminar(id)
        flash("Habitación eliminada", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('habitaciones'))

# -----------------------------------------------------
# RESERVAS
# -----------------------------------------------------
@app.route('/reservas')
def reservas():
    return render_template('reservas.html', lista=r_dao.listar())

@app.route('/reservas/guardar', methods=['POST'])
def guardar_reserva():
    try:
        res = Reserva(
            id_reserva=None,
            id_cliente=validar_entero_no_negativo('id_cliente', 'El ID del cliente'),
            numero_h=validar_entero_no_negativo('numero_h', 'El número de habitación'),
            fecha_llegada=request.form['fecha_llegada'],
            fecha_salida=request.form['fecha_salida'],
            valor_reserva=float(request.form['valor_reserva']),
            tiempo_maxc=int(request.form['tiempo_maxc'])
        )
        r_dao.crear(res)
        flash("Reserva exitosa", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('reservas'))

@app.route('/eliminar/reserva/<int:id>')
def eliminar_reserva(id):
    try:
        r_dao.eliminar(id)
        flash("Reserva eliminada", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('reservas'))

# -----------------------------------------------------
# SERVICIOS
# -----------------------------------------------------
@app.route('/servicios')
def servicios():
    return render_template('servicios.html', lista=s_dao.listar())

@app.route('/servicios/guardar', methods=['POST'])
def guardar_servicio():
    try:
        ser = Servicio(
            id_servicio=None,
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            costo=float(request.form['costo']),
            estado=request.form['estado']
        )
        s_dao.crear(ser)
        flash("Servicio creado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('servicios'))

@app.route('/eliminar/servicio/<int:id>')
def eliminar_servicio(id):
    try:
        s_dao.eliminar(id)
        flash("Servicio eliminado", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('servicios'))

# -----------------------------------------------------
# CONSUMOS
# -----------------------------------------------------
@app.route('/consumos')
def consumos():
    return render_template('consumos.html', lista=co_dao.listar())

@app.route('/consumos/guardar', methods=['POST'])
def guardar_consumo():
    try:
        con = Consumo(
            id_consumo=None,
            id_reserva=validar_entero_no_negativo('id_reserva', 'El ID de la reserva'),
            id_servicio=validar_entero_no_negativo('id_servicio', 'El ID del servicio')
        )
        co_dao.crear(con)
        flash("Consumo cargado", "success")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('consumos'))

@app.route('/eliminar/consumo/<int:id>')
def eliminar_consumo(id):
    try:
        co_dao.eliminar(id)
        flash("Consumo eliminado", "warning")
    except Exception as err:
        flash(f"Error: {err}", "danger")
    return redirect(url_for('consumos'))

# -----------------------------------------------------
# EJECUCIÓN
# -----------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
