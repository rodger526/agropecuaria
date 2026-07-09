from database.conexion import obtener_conexion


def listar_laboratorios():
    """
    Devuelve un listado resumido de laboratorios (para tablas/listas en la UI).
    Columnas: id, fecha_practica, carrera, laboratorio, asignatura,
              docente_responsable, tema_practica, pdf_url
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                fecha_practica,
                carrera,
                laboratorio,
                asignatura,
                docente_responsable,
                tema_practica,
                pdf_url
            FROM laboratorios
            ORDER BY id DESC
        """)

        resultados = cursor.fetchall()
        return resultados

    except Exception as e:
        print(e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def buscar_laboratorio_por_id(id_laboratorio):
    """
    Devuelve una tupla con todas las columnas de `laboratorios` en el
    mismo orden que espera Laboratorio.from_row():
    (id, codigo, laboratorio, asignatura, carrera, semestre,
     unidad_academica, institucion, ciudad, docente_responsable,
     fecha_practica, hora_entrada, hora_salida, numero_estudiantes,
     tema_practica, subtema, logro_aprendizaje, objetivos,
     metodologia, resultados, conclusiones, observaciones, pdf_url)

    Devuelve None si no existe el id.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                codigo,
                laboratorio,
                asignatura,
                carrera,
                semestre,
                unidad_academica,
                institucion,
                ciudad,
                docente_responsable,
                fecha_practica,
                hora_entrada,
                hora_salida,
                numero_estudiantes,
                tema_practica,
                subtema,
                logro_aprendizaje,
                objetivos,
                metodologia,
                resultados,
                conclusiones,
                observaciones,
                pdf_url
            FROM laboratorios
            WHERE id = %s
        """, (id_laboratorio,))

        resultado = cursor.fetchone()
        return resultado

    except Exception as e:
        print(e)
        return None

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def buscar_materiales_por_laboratorio(id_laboratorio):
    """Devuelve lista de dicts [{'nombre': ..., 'cantidad': ...}, ...]."""

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT nombre, cantidad
            FROM laboratorio_materiales
            WHERE laboratorio_id = %s
            ORDER BY id
        """, (id_laboratorio,))

        filas = cursor.fetchall()
        return [{"nombre": fila[0], "cantidad": fila[1]} for fila in filas]

    except Exception as e:
        print(e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def buscar_reactivos_por_laboratorio(id_laboratorio):
    """Devuelve lista de dicts [{'nombre': ..., 'cantidad': ...}, ...]."""

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT nombre, cantidad
            FROM laboratorio_reactivos
            WHERE laboratorio_id = %s
            ORDER BY id
        """, (id_laboratorio,))

        filas = cursor.fetchall()
        return [{"nombre": fila[0], "cantidad": fila[1]} for fila in filas]

    except Exception as e:
        print(e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def buscar_estudiantes_por_laboratorio(id_laboratorio):
    """Devuelve lista de dicts [{'nombre': ..., 'cedula': ...}, ...]."""

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT nombre, cedula
            FROM laboratorio_estudiantes
            WHERE laboratorio_id = %s
            ORDER BY id
        """, (id_laboratorio,))

        filas = cursor.fetchall()
        return [{"nombre": fila[0], "cedula": fila[1]} for fila in filas]

    except Exception as e:
        print(e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()