import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager

base_dir = Path(__file__).resolve().parent.parent
env_path = os.path.join(base_dir, 'Raiz.env')

load_dotenv(dotenv_path=env_path)

class DBConnection:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    @contextmanager
    def get_connection(self, user=None, password=None):
        if not self.password:
            print(f"DEBUG: Intentando cargar desde: {env_path}")
            raise ValueError("Error: No se encontró la contraseña en Raiz.env. Verifica los nombres de las variables.")

        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=user or self.user,
            password=password or self.password
        )
        conn.set_client_encoding('UTF8')
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def get_connection_role(self, username):
        from auth import authenticate_user
        auth_result = authenticate_user(username, os.getenv("DB_PASSWORD", "temp_password"))
        if auth_result:
            with self.get_connection(user=username, password=os.getenv("DB_PASSWORD", "temp_password")) as conn:
                yield conn
        else:
            with self.get_connection() as conn:
                yield conn

db = DBConnection()