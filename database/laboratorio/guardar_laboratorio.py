from database.conexion import obtener_conexion


def guardar_laboratorio(laboratorio):
    """
    Guarda un objeto Laboratorio en la tabla `laboratorios` y, si trae
    materiales/reactivos/estudiantes, los inserta en sus tablas
    relacionadas (laboratorio_materiales, laboratorio_reactivos,
    laboratorio_estudiantes) usando el id recién generado como FK.

    Cada dict de materiales/reactivos se espera con las claves
    "nombre" y "cantidad". Cada dict de estudiantes se espera con
    las claves "nombre", "cedula" y opcionalmente "firma_ruta"
    (ruta del PNG de la firma capturada por QR; None si el estudiante
    se ingresó manualmente sin firmar).

    Devuelve True si todo se guardó correctamente, False si hubo error.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # 1) Insertar el laboratorio y recuperar su id con RETURNING
        cursor.execute("""
            INSERT INTO laboratorios (
                codigo,
                laboratorio,
                numero_estudiantes,
                asignatura,
                unidad_academica,
                semestre,
                carrera,
                hora_entrada,
                hora_salida,
                institucion,
                ciudad,
                docente_responsable,
                fecha_practica,
                tema_practica,
                subtema,
                logro_aprendizaje,
                objetivos,
                metodologia,
                resultados,
                conclusiones,
                observaciones,
                pdf_url
            )
            VALUES (
                %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s,
                %s, %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
        """, (
            laboratorio.codigo,
            laboratorio.laboratorio,
            laboratorio.numero_estudiantes,
            laboratorio.asignatura,
            laboratorio.unidad_academica,
            laboratorio.semestre,
            laboratorio.carrera,
            laboratorio.hora_entrada,
            laboratorio.hora_salida,
            laboratorio.institucion,
            laboratorio.ciudad,
            laboratorio.docente_responsable,
            laboratorio.fecha_practica,
            laboratorio.tema_practica,
            laboratorio.subtema,
            laboratorio.logro_aprendizaje,
            laboratorio.objetivos,
            laboratorio.metodologia,
            laboratorio.resultados,
            laboratorio.conclusiones,
            laboratorio.observaciones,
            laboratorio.pdf_url,
        ))

        laboratorio_id = cursor.fetchone()[0]
        laboratorio.id = laboratorio_id

        # 2) Insertar materiales relacionados
        for material in laboratorio.materiales:
            cursor.execute("""
                INSERT INTO laboratorio_materiales (laboratorio_id, nombre, cantidad)
                VALUES (%s, %s, %s)
            """, (
                laboratorio_id,
                material.get("nombre"),
                material.get("cantidad"),
            ))

        # 3) Insertar reactivos relacionados
        for reactivo in laboratorio.reactivos:
            cursor.execute("""
                INSERT INTO laboratorio_reactivos (laboratorio_id, nombre, cantidad)
                VALUES (%s, %s, %s)
            """, (
                laboratorio_id,
                reactivo.get("nombre"),
                reactivo.get("cantidad"),
            ))

        # 4) Insertar estudiantes relacionados (incluye ruta de firma si existe)
        for estudiante in laboratorio.estudiantes:
            cursor.execute("""
                INSERT INTO laboratorio_estudiantes (laboratorio_id, nombre, cedula, firma_ruta)
                VALUES (%s, %s, %s, %s)
            """, (
                laboratorio_id,
                estudiante.get("nombre"),
                estudiante.get("cedula"),
                estudiante.get("firma_ruta"),
            ))

        # Todo OK -> confirmar transacción completa
        conexion.commit()
        return True

    except Exception as e:
        print(e)
        if conexion:
            conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()