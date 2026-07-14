from database.conexion import obtener_conexion


def buscar_por_codigo(codigo):
    """
    Busca una práctica por su código.

    Devuelve una tupla completa o None.
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
            SELECT *
            FROM practicas
            WHERE codigo = %s
        """, (
            codigo,
        ))

        return cursor.fetchone()

    except Exception as e:
        print("\n===== ERROR BUSCANDO PRÁCTICA POR CÓDIGO =====")
        print(e)
        print("===============================================\n")

        return None

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_por_id(id_practica):
    """
    Busca una práctica por id.

    Devuelve una tupla completa o None.
    """

    conexion = None
    cursor = None

    try:
        if id_practica is None:
            return None

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT *
            FROM practicas
            WHERE id = %s
        """, (
            id_practica,
        ))

        return cursor.fetchone()

    except Exception as e:
        print("\n===== ERROR BUSCANDO PRÁCTICA POR ID =====")
        print(e)
        print("==========================================\n")

        return None

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_por_carrera(carrera):
    """
    Busca prácticas por coincidencia parcial de carrera.

    Devuelve una lista de tuplas.
    """

    conexion = None
    cursor = None

    try:
        carrera = str(carrera or "").strip()

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT *
            FROM practicas
            WHERE carrera ILIKE %s
            ORDER BY id DESC
        """, (
            f"%{carrera}%",
        ))

        return cursor.fetchall()

    except Exception as e:
        print("\n===== ERROR BUSCANDO PRÁCTICAS POR CARRERA =====")
        print(e)
        print("================================================\n")

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def buscar_por_asignatura(asignatura):
    """
    Busca prácticas por coincidencia parcial de asignatura.

    Devuelve una lista de tuplas.
    """

    conexion = None
    cursor = None

    try:
        asignatura = str(asignatura or "").strip()

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT *
            FROM practicas
            WHERE asignatura ILIKE %s
            ORDER BY id DESC
        """, (
            f"%{asignatura}%",
        ))

        return cursor.fetchall()

    except Exception as e:
        print(
            "\n===== ERROR BUSCANDO PRÁCTICAS POR ASIGNATURA ====="
        )
        print(e)
        print(
            "===================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def listar_practicas():
    """
    Devuelve únicamente las prácticas que poseen un PDF almacenado
    en línea dentro de Supabase Storage.

    Orden de columnas:
        0: id
        1: fecha_creacion
        2: carrera
        3: asignatura
        4: tema_practica
        5: ingeniero_revisor
        6: pdf_url

    Este orden debe coincidir con los IDX_* definidos en
    views/buscar_practica.py.
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
                carrera,
                asignatura,
                tema_practica,
                ingeniero_revisor,
                pdf_url
            FROM practicas
            WHERE pdf_url IS NOT NULL
              AND TRIM(pdf_url) <> ''
              AND pdf_url LIKE 'https://%'
              AND pdf_url LIKE '%supabase.co/storage/v1/object/%'
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    except Exception as e:
        print("\n========== ERROR LISTANDO PRÁCTICAS ==========")
        print(e)
        print("==============================================\n")

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def total_practicas():
    """
    Devuelve el número de prácticas visibles en la ventana de búsqueda.

    Cuenta únicamente registros cuyo PDF está almacenado en línea.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM practicas
            WHERE pdf_url IS NOT NULL
              AND TRIM(pdf_url) <> ''
              AND pdf_url LIKE 'https://%'
              AND pdf_url LIKE '%supabase.co/storage/v1/object/%'
        """)

        resultado = cursor.fetchone()

        return resultado[0] if resultado else 0

    except Exception as e:
        print("\n========== ERROR CONTANDO PRÁCTICAS ==========")
        print(e)
        print("==============================================\n")

        return 0

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()