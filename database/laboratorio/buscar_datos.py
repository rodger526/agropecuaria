from database.conexion import obtener_conexion


def obtener_laboratorios_tipo():
    """
    Devuelve todos los tipos de laboratorio junto con el
    encargado y el cargo correspondiente.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                nombre,
                encargado,
                cargo_encargado
            FROM laboratorios_tipo
            ORDER BY nombre
        """)

        filas = cursor.fetchall()

        return [
            {
                "id": fila[0],
                "nombre": fila[1],
                "encargado": fila[2],
                "cargo": fila[3],
            }
            for fila in filas
        ]

    except Exception as e:
        print(
            "[buscar_datos] Error obteniendo laboratorios:",
            e
        )
        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_laboratorio_por_nombre(nombre):
    """
    Devuelve toda la información de un laboratorio
    a partir de su nombre.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                nombre,
                encargado,
                cargo_encargado
            FROM laboratorios_tipo
            WHERE nombre=%s
        """, (nombre,))

        fila = cursor.fetchone()

        if fila is None:
            return None

        return {
            "id": fila[0],
            "nombre": fila[1],
            "encargado": fila[2],
            "cargo": fila[3],
        }

    except Exception as e:
        print(
            "[buscar_datos] Error:",
            e
        )
        return None

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_equipos_por_tipo(
    laboratorio_tipo_id,
    texto=""
):
    """
    Devuelve los materiales/reactivos
    registrados para un laboratorio.
    """

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        patron = f"%{texto.strip()}%"

        if laboratorio_tipo_id:

            cursor.execute("""
                SELECT
                    nombre,
                    cantidad
                FROM laboratorio_tipo_equipos
                WHERE laboratorio_tipo_id=%s
                AND nombre ILIKE %s
                ORDER BY nombre
                LIMIT 8
            """, (
                laboratorio_tipo_id,
                patron,
            ))

        else:

            cursor.execute("""
                SELECT
                    nombre,
                    cantidad
                FROM laboratorio_tipo_equipos
                WHERE nombre ILIKE %s
                ORDER BY nombre
                LIMIT 8
            """, (
                patron,
            ))

        filas = cursor.fetchall()

        return [
            {
                "nombre": fila[0],
                "cantidad": fila[1],
            }
            for fila in filas
        ]

    except Exception as e:

        print(
            "[buscar_datos] Error buscando equipos:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()