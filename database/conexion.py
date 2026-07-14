import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# Raíz del proyecto:
# agropecuaria/
# ├── .env
# └── database/
#     └── conexion.py
BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_ENV = BASE_DIR / ".env"

load_dotenv(RUTA_ENV)


def obtener_conexion():
    """
    Crea y devuelve una conexión PostgreSQL hacia Supabase.

    Lanza una excepción si faltan variables de entorno o si no se
    puede establecer la conexión.
    """

    variables = {
        "SUPABASE_HOST": os.getenv("SUPABASE_HOST"),
        "SUPABASE_DB": os.getenv("SUPABASE_DB"),
        "SUPABASE_USER": os.getenv("SUPABASE_USER"),
        "SUPABASE_PASSWORD": os.getenv("SUPABASE_PASSWORD"),
        "SUPABASE_PORT": os.getenv("SUPABASE_PORT"),
    }

    faltantes = [
        nombre
        for nombre, valor in variables.items()
        if not valor
    ]

    if faltantes:
        raise RuntimeError(
            "Faltan variables de entorno para PostgreSQL: "
            + ", ".join(faltantes)
        )

    try:
        return psycopg2.connect(
            host=variables["SUPABASE_HOST"],
            database=variables["SUPABASE_DB"],
            user=variables["SUPABASE_USER"],
            password=variables["SUPABASE_PASSWORD"],
            port=int(variables["SUPABASE_PORT"]),
            sslmode="require",
            connect_timeout=15,
        )

    except Exception as e:
        print("\n========== ERROR DE CONEXIÓN ==========")
        print(e)
        print("=======================================\n")

        raise