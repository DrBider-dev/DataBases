import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager

# Localizamos la carpeta raíz del proyecto
base_dir = Path(__file__).resolve().parent.parent
# Especificamos tu nombre de archivo personalizado: Raiz.env
env_path = os.path.join(base_dir, 'Raiz.env')

# Cargamos el archivo indicando la ruta exacta
load_dotenv(dotenv_path=env_path)

class DBConnection:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    @contextmanager
    def get_connection(self):
        # Verificación para confirmar que leyó el archivo Raiz.env
        if not self.password:
            print(f"DEBUG: Intentando cargar desde: {env_path}")
            raise ValueError("Error: No se encontró la contraseña en Raiz.env. Verifica los nombres de las variables.")

        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
        conn.set_client_encoding('UTF8')
        try:
            yield conn
        finally:
            conn.close()

db = DBConnection()