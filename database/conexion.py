import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():

    try:

        conexion = psycopg2.connect(
            host=os.getenv("SUPABASE_HOST"),
            database=os.getenv("SUPABASE_DB"),
            user=os.getenv("SUPABASE_USER"),
            password=os.getenv("SUPABASE_PASSWORD"),
            port=os.getenv("SUPABASE_PORT"),
            sslmode="require"
        )

        return conexion

    except Exception as e:

        print("ERROR DE CONEXIÓN:")
        print(e)

        raise e