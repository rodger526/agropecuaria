from database.conexion import obtener_conexion


def buscar_por_codigo(codigo):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM practicas
        WHERE codigo = %s
    """, (codigo,))

    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    return resultado


def buscar_por_id(id_practica):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM practicas
        WHERE id = %s
    """, (id_practica,))

    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    return resultado


def buscar_por_carrera(carrera):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM practicas
        WHERE carrera ILIKE %s
        ORDER BY id DESC
    """, (f"%{carrera}%",))

    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultados


def buscar_por_asignatura(asignatura):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM practicas
        WHERE asignatura ILIKE %s
        ORDER BY id DESC
    """, (f"%{asignatura}%",))

    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultados


def listar_practicas():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            codigo,
            carrera,
            asignatura,
            tema_practica,
            ingeniero_revisor,
            pdf_url
        FROM practicas
        ORDER BY id DESC
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultados


def total_practicas():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM practicas
    """)

    total = cursor.fetchone()[0]

    cursor.close()
    conexion.close()

    return total