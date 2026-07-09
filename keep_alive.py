import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():

    conexion = psycopg2.connect(
        host=os.getenv("SUPABASE_HOST"),
        database=os.getenv("SUPABASE_DB"),
        user=os.getenv("SUPABASE_USER"),
        password=os.getenv("SUPABASE_PASSWORD"),
        port=os.getenv("SUPABASE_PORT"),
        sslmode="require"
    )

    return conexion


def keep_alive():

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("SELECT NOW();")

    resultado = cursor.fetchone()

    print("Supabase activo:", resultado)

    cursor.close()
    conexion.close()


if __name__ == "__main__":
    keep_alive()