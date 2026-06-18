from database.conexion import obtener_conexion


def actualizar_laboratorio(laboratorio):
    """
    Actualiza el registro de `laboratorios` cuyo id coincide con
    laboratorio.id, y reemplaza sus materiales/reactivos/estudiantes
    en las tablas relacionadas (DELETE + INSERT en la misma transacción).

    Recibe un objeto Laboratorio ya modificado desde la vista.
    Devuelve True si todo se actualizó correctamente, False si hubo error.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # 1) Actualizar la fila principal en laboratorios
        cursor.execute("""
            UPDATE laboratorios
            SET
                laboratorio        = %s,
                numero_estudiantes = %s,
                asignatura         = %s,
                unidad_academica   = %s,
                semestre           = %s,
                carrera            = %s,
                hora_entrada       = %s,
                hora_salida        = %s,
                institucion        = %s,
                ciudad             = %s,
                docente_responsable= %s,
                fecha_practica     = %s,
                tema_practica      = %s,
                subtema            = %s,
                logro_aprendizaje  = %s,
                objetivos          = %s,
                metodologia        = %s,
                resultados         = %s,
                conclusiones       = %s,
                observaciones      = %s,
                pdf_url            = %s
            WHERE id = %s
        """, (
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
            laboratorio.id,
        ))

        # 2) Reemplazar materiales (DELETE + INSERT)
        cursor.execute("""
            DELETE FROM laboratorio_materiales WHERE laboratorio_id = %s
        """, (laboratorio.id,))

        for material in laboratorio.materiales:
            cursor.execute("""
                INSERT INTO laboratorio_materiales (laboratorio_id, nombre, cantidad)
                VALUES (%s, %s, %s)
            """, (laboratorio.id, material.get("nombre"), material.get("cantidad")))

        # 3) Reemplazar reactivos (DELETE + INSERT)
        cursor.execute("""
            DELETE FROM laboratorio_reactivos WHERE laboratorio_id = %s
        """, (laboratorio.id,))

        for reactivo in laboratorio.reactivos:
            cursor.execute("""
                INSERT INTO laboratorio_reactivos (laboratorio_id, nombre, cantidad)
                VALUES (%s, %s, %s)
            """, (laboratorio.id, reactivo.get("nombre"), reactivo.get("cantidad")))

        # 4) Reemplazar estudiantes (DELETE + INSERT)
        cursor.execute("""
            DELETE FROM laboratorio_estudiantes WHERE laboratorio_id = %s
        """, (laboratorio.id,))

        for estudiante in laboratorio.estudiantes:
            cursor.execute("""
                INSERT INTO laboratorio_estudiantes (laboratorio_id, nombre, cedula)
                VALUES (%s, %s, %s)
            """, (laboratorio.id, estudiante.get("nombre"), estudiante.get("cedula")))

        conexion.commit()
        return True

    except Exception as e:
        print("ERROR AL ACTUALIZAR LABORATORIO")
        print(e)
        if conexion:
            conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()