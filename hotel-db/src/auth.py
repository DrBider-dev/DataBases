import os
from functools import wraps
from flask import session, redirect, url_for, flash, request
from util.db import DBConnection

db = DBConnection()

ROLES_PERMISOS = {
    'administrador': ['personas', 'telefonos', 'clientes', 'empleados', 'habitaciones', 'reservas', 'servicios', 'consumos', 'usuarios'],
    'gerente': ['empleados', 'habitaciones', 'servicios', 'personas'],
    'recepcionista': ['clientes', 'reservas', 'consumos', 'habitaciones', 'personas'],
    'empleado_limpieza': ['habitaciones'],
    'cliente_usuario': ['mis_reservas']
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debe iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('login'))
            
            user_role = session.get('user_role')
            if user_role not in roles_permitidos and user_role != 'administrador':
                flash('No tiene permisos para acceder a esta sección', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def authenticate_user(username, password):
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT u.usename, r.rolname 
                    FROM pg_user u
                    JOIN pg_auth_members m ON u.usesysid = m.member
                    JOIN pg_roles r ON m.roleid = r.oid
                    WHERE u.usename = %s
                """, (username,))
                result = cur.fetchone()
                if result:
                    return {'username': result[0], 'role': result[1]}
                
                cur.execute("""
                    SELECT rolname 
                    FROM pg_roles 
                    WHERE rolname = %s AND rolcanlogin = true
                """, (username,))
                result = cur.fetchone()
                if result:
                    return {'username': username, 'role': result[0]}
                
                if os.getenv('DB_USER') == username and os.getenv('DB_PASSWORD') == password:
                    return {'username': username, 'role': 'administrador'}
    except Exception as e:
        print(f"Error en autenticación: {e}")
    return None

def get_user_id_from_role():
    """Get the numeric user ID. For cliente_usuario role, resolves the PostgreSQL username to id_persona."""
    if session.get('user_role') == 'cliente_usuario':
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Map PostgreSQL username to persona.id_persona via email
                    # The persona email should match the PostgreSQL username for client users
                    cur.execute("""
                        SELECT DISTINCT r.id_cliente
                        FROM hotel.reserva r
                        WHERE EXISTS (
                            SELECT 1 FROM hotel.persona p 
                            WHERE p.id_persona = r.id_cliente 
                            AND p.email = CURRENT_USER
                        )
                        LIMIT 1;
                    """)
                    result = cur.fetchone()
                    if result:
                        return result[0]
                    # Fallback: try direct client lookup via persona
                    cur.execute("""
                        SELECT c.id_persona as id_cliente
                        FROM hotel.cliente c
                        JOIN hotel.persona p ON c.id_persona = p.id_persona
                        WHERE p.email = CURRENT_USER;
                    """)
                    result = cur.fetchone()
                    return result[0] if result else None
        except Exception:
            return None
    return session.get('user_id')