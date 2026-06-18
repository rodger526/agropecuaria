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
    """
    Trae solo las columnas que usa la vista VentanaBuscar.
    IMPORTANTE: si agregas o quitas una columna aquí, debes actualizar
    también los índices IDX_* en views/buscar_practica.py para que
    sigan apuntando a la posición correcta.

    'codigo' NO se incluye aquí a propósito: es solo el nombre interno
    con el que se guarda el PDF en disco, no un dato que la vista de
    búsqueda deba mostrar ni filtrar.

    Orden actual (debe coincidir 1 a 1 con los IDX_* de la vista):
        0: id
        1: fecha_creacion
        2: carrera
        3: asignatura
        4: tema_practica
        5: ingeniero_revisor
        6: pdf_url
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            fecha_creacion,
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