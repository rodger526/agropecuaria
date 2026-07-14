from database.conexion import obtener_conexion


def listar_laboratorios():
    """
    Devuelve únicamente laboratorios con PDF en línea.

    Orden:
        0: id
        1: fecha_practica
        2: carrera
        3: laboratorio
        4: asignatura
        5: docente_responsable
        6: tema_practica
        7: pdf_url
        8: encargado_laboratorio
        9: cargo_encargado
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
                pdf_url,
                encargado_laboratorio,
                cargo_encargado
            FROM laboratorios
            WHERE pdf_url IS NOT NULL
              AND TRIM(pdf_url) <> ''
              AND pdf_url LIKE 'https://%'
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    except Exception as error:
        print("\n========== ERROR LISTANDO LABORATORIOS ==========")
        print(error)
        print("=================================================\n")
        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_laboratorio_por_id(id_laboratorio):
    """
    Devuelve una fila en el orden esperado por Laboratorio.from_row().
    """

    conexion = None
    cursor = None

    try:
        if not id_laboratorio:
            return None

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
                pdf_url,
                encargado_laboratorio,
                cargo_encargado,
                firma_encargado_ruta,
                firma_docente_ruta,
                codigo_sesion
            FROM laboratorios
            WHERE id = %s
        """, (
            id_laboratorio,
        ))

        return cursor.fetchone()

    except Exception as error:
        print("\n===== ERROR BUSCANDO LABORATORIO POR ID =====")
        print(error)
        print("=============================================\n")
        return None

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_materiales_por_laboratorio(id_laboratorio):
    """
    Devuelve una lista de materiales.
    """

    conexion = None
    cursor = None

    try:
        if not id_laboratorio:
            return []

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                nombre,
                cantidad
            FROM laboratorio_materiales
            WHERE laboratorio_id = %s
            ORDER BY id
        """, (
            id_laboratorio,
        ))

        filas = cursor.fetchall()

        return [
            {
                "nombre": fila[0],
                "cantidad": fila[1],
            }
            for fila in filas
        ]

    except Exception as error:
        print("\n===== ERROR BUSCANDO MATERIALES =====")
        print(error)
        print("=====================================\n")
        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_reactivos_por_laboratorio(id_laboratorio):
    """
    Devuelve una lista de reactivos.
    """

    conexion = None
    cursor = None

    try:
        if not id_laboratorio:
            return []

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                nombre,
                cantidad
            FROM laboratorio_reactivos
            WHERE laboratorio_id = %s
            ORDER BY id
        """, (
            id_laboratorio,
        ))

        filas = cursor.fetchall()

        return [
            {
                "nombre": fila[0],
                "cantidad": fila[1],
            }
            for fila in filas
        ]

    except Exception as error:
        print("\n===== ERROR BUSCANDO REACTIVOS =====")
        print(error)
        print("====================================\n")
        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_estudiantes_por_laboratorio(id_laboratorio):
    """
    Devuelve una lista de estudiantes con su firma.

    Formato:
        [
            {
                "nombre": "...",
                "cedula": "...",
                "firma_ruta": "..."
            }
        ]
    """

    conexion = None
    cursor = None

    try:
        if not id_laboratorio:
            return []

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                nombre,
                cedula,
                firma_ruta
            FROM laboratorio_estudiantes
            WHERE laboratorio_id = %s
            ORDER BY id
        """, (
            id_laboratorio,
        ))

        filas = cursor.fetchall()

        return [
            {
                "nombre": fila[0],
                "cedula": fila[1],
                "firma_ruta": fila[2],
            }
            for fila in filas
        ]

    except Exception as error:
        print("\n===== ERROR BUSCANDO ESTUDIANTES =====")
        print(error)
        print("======================================\n")
        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_por_codigo(codigo):
    """
    Busca un laboratorio por su código.
    """

    conexion = None
    cursor = None

    try:
        codigo = str(codigo or "").strip()

        if not codigo:
            return None

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
                pdf_url,
                encargado_laboratorio,
                cargo_encargado,
                firma_encargado_ruta,
                firma_docente_ruta,
                codigo_sesion
            FROM laboratorios
            WHERE codigo = %s
        """, (
            codigo,
        ))

        return cursor.fetchone()

    except Exception as error:
        print("\n===== ERROR BUSCANDO LABORATORIO POR CÓDIGO =====")
        print(error)
        print("=================================================\n")
        return None

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()