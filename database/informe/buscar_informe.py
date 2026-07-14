from database.conexion import obtener_conexion


def listar_informes():
    """
    Devuelve únicamente los informes que tienen un PDF en línea.

    Orden de columnas:
        0: id
        1: fecha_creacion
        2: codigo
        3: titulo
        4: asignatura
        5: autores
        6: docente
        7: pdf_url

    Este orden debe coincidir con los índices utilizados en
    views/buscar_informe.py.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                fecha_creacion,
                codigo,
                titulo,
                asignatura,
                autores,
                docente,
                pdf_url
            FROM informes_laboratorio
            WHERE pdf_url IS NOT NULL
              AND TRIM(pdf_url) <> ''
              AND pdf_url LIKE 'https://%'
            ORDER BY id DESC
        """)

        resultados = cursor.fetchall()

        return resultados

    except Exception as e:
        print(
            "\n========== ERROR LISTANDO INFORMES =========="
        )
        print(e)
        print(
            "=============================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_informe_por_id(id_informe):
    """
    Busca un informe por su ID.

    Devuelve una tupla con el siguiente orden:

        0: id
        1: codigo
        2: titulo
        3: autores
        4: asignatura
        5: carrera
        6: semestre
        7: docente
        8: resumen
        9: palabras_clave
        10: introduccion
        11: objetivo_general
        12: objetivos_especificos
        13: materiales_reactivos
        14: procedimiento_experimental
        15: resultados
        16: discusion
        17: conclusiones
        18: recomendaciones
        19: bibliografia
        20: cuestionario
        21: anexos
        22: hoja_datos_url
        23: pdf_url
        24: fecha_creacion

    Este orden debe coincidir con InformeLaboratorio.from_row().
    """

    conexion = None
    cursor = None

    try:
        if not id_informe:
            return None

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                codigo,
                titulo,
                autores,
                asignatura,
                carrera,
                semestre,
                docente,
                resumen,
                palabras_clave,
                introduccion,
                objetivo_general,
                objetivos_especificos,
                materiales_reactivos,
                procedimiento_experimental,
                resultados,
                discusion,
                conclusiones,
                recomendaciones,
                bibliografia,
                cuestionario,
                anexos,
                hoja_datos_url,
                pdf_url,
                fecha_creacion
            FROM informes_laboratorio
            WHERE id = %s
        """, (
            id_informe,
        ))

        resultado = cursor.fetchone()

        return resultado

    except Exception as e:
        print(
            "\n===== ERROR BUSCANDO INFORME POR ID ====="
        )
        print(e)
        print(
            "=========================================\n"
        )

        return None

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_informe_por_codigo(codigo):
    """
    Busca un informe por código.

    Devuelve la fila completa o None.
    """

    conexion = None
    cursor = None

    try:
        codigo = str(
            codigo or ""
        ).strip()

        if not codigo:
            return None

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                codigo,
                titulo,
                autores,
                asignatura,
                carrera,
                semestre,
                docente,
                resumen,
                palabras_clave,
                introduccion,
                objetivo_general,
                objetivos_especificos,
                materiales_reactivos,
                procedimiento_experimental,
                resultados,
                discusion,
                conclusiones,
                recomendaciones,
                bibliografia,
                cuestionario,
                anexos,
                hoja_datos_url,
                pdf_url,
                fecha_creacion
            FROM informes_laboratorio
            WHERE codigo = %s
        """, (
            codigo,
        ))

        return cursor.fetchone()

    except Exception as e:
        print(
            "\n===== ERROR BUSCANDO INFORME POR CÓDIGO ====="
        )
        print(e)
        print(
            "=============================================\n"
        )

        return None

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_informes_por_titulo(titulo):
    """
    Busca informes por coincidencia parcial en el título.

    Devuelve una lista de tuplas resumidas.
    """

    conexion = None
    cursor = None

    try:
        titulo = str(
            titulo or ""
        ).strip()

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                fecha_creacion,
                codigo,
                titulo,
                asignatura,
                autores,
                docente,
                pdf_url
            FROM informes_laboratorio
            WHERE titulo ILIKE %s
              AND pdf_url IS NOT NULL
              AND TRIM(pdf_url) <> ''
              AND pdf_url LIKE 'https://%'
            ORDER BY id DESC
        """, (
            f"%{titulo}%",
        ))

        return cursor.fetchall()

    except Exception as e:
        print(
            "\n===== ERROR BUSCANDO INFORMES POR TÍTULO ====="
        )
        print(e)
        print(
            "==============================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_informes_por_asignatura(asignatura):
    """
    Busca informes por coincidencia parcial en la asignatura.

    Devuelve una lista de tuplas resumidas.
    """

    conexion = None
    cursor = None

    try:
        asignatura = str(
            asignatura or ""
        ).strip()

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                fecha_creacion,
                codigo,
                titulo,
                asignatura,
                autores,
                docente,
                pdf_url
            FROM informes_laboratorio
            WHERE asignatura ILIKE %s
              AND pdf_url IS NOT NULL
              AND TRIM(pdf_url) <> ''
              AND pdf_url LIKE 'https://%'
            ORDER BY id DESC
        """, (
            f"%{asignatura}%",
        ))

        return cursor.fetchall()

    except Exception as e:
        print(
            "\n===== ERROR BUSCANDO INFORMES POR ASIGNATURA ====="
        )
        print(e)
        print(
            "==================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_informes_por_autor(autor):
    """
    Busca informes por coincidencia parcial en autores.

    Devuelve una lista de tuplas resumidas.
    """

    conexion = None
    cursor = None

    try:
        autor = str(
            autor or ""
        ).strip()

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                fecha_creacion,
                codigo,
                titulo,
                asignatura,
                autores,
                docente,
                pdf_url
            FROM informes_laboratorio
            WHERE autores ILIKE %s
              AND pdf_url IS NOT NULL
              AND TRIM(pdf_url) <> ''
              AND pdf_url LIKE 'https://%'
            ORDER BY id DESC
        """, (
            f"%{autor}%",
        ))

        return cursor.fetchall()

    except Exception as e:
        print(
            "\n===== ERROR BUSCANDO INFORMES POR AUTOR ====="
        )
        print(e)
        print(
            "=============================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_fotos_por_informe(id_informe):
    """
    Devuelve las fotografías relacionadas con un informe.

    Formato:

        [
            {
                "id": 1,
                "foto_url": "https://...",
                "descripcion": "...",
                "orden": 1
            }
        ]
    """

    conexion = None
    cursor = None

    try:
        if not id_informe:
            return []

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                foto_url,
                descripcion,
                orden
            FROM informe_laboratorio_fotos
            WHERE informe_id = %s
            ORDER BY orden ASC, id ASC
        """, (
            id_informe,
        ))

        filas = cursor.fetchall()

        return [
            {
                "id": fila[0],
                "foto_url": fila[1],
                "descripcion": fila[2],
                "orden": fila[3],
            }
            for fila in filas
        ]

    except Exception as e:
        print(
            "\n===== ERROR BUSCANDO FOTOS DEL INFORME ====="
        )
        print(e)
        print(
            "============================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def total_informes():
    """
    Devuelve el total de informes con PDF disponible en línea.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM informes_laboratorio
            WHERE pdf_url IS NOT NULL
              AND TRIM(pdf_url) <> ''
              AND pdf_url LIKE 'https://%'
        """)

        resultado = cursor.fetchone()

        return resultado[0] if resultado else 0

    except Exception as e:
        print(
            "\n===== ERROR CONTANDO INFORMES ====="
        )
        print(e)
        print(
            "===================================\n"
        )

        return 0

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()