from database.conexion import obtener_conexion


def actualizar_practica(
    id_practica,
    codigo,
    carrera,
    semestre,
    asignatura,
    unidad_silabo,
    tipo_practica,
    ingeniero_revisor,
    lugar_ejecucion,
    semana_planificada,
    tema_practica,
    resultado_aprendizaje,
    articulacion_curricular,
    objetivo_general,
    materiales_equipos,
    descripcion_actividad,
    evidencias,
    pdf_url,
    firma_docente=None,
    firma_comision=None,
):

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE practicas
            SET
                codigo=%s,
                carrera=%s,
                semestre=%s,
                asignatura=%s,
                unidad_silabo=%s,
                tipo_practica=%s,
                ingeniero_revisor=%s,
                lugar_ejecucion=%s,
                semana_planificada=%s,
                tema_practica=%s,
                resultado_aprendizaje=%s,
                articulacion_curricular=%s,
                objetivo_general=%s,
                materiales_equipos=%s,
                descripcion_actividad=%s,
                evidencias=%s,
                pdf_url=%s,
                firma_docente=COALESCE(%s, firma_docente),
                firma_comision=COALESCE(%s, firma_comision)
            WHERE id=%s
        """,
        (
            codigo,
            carrera,
            semestre,
            asignatura,
            unidad_silabo,
            tipo_practica,
            ingeniero_revisor,
            lugar_ejecucion,
            semana_planificada,
            tema_practica,
            resultado_aprendizaje,
            articulacion_curricular,
            objetivo_general,
            materiales_equipos,
            descripcion_actividad,
            evidencias,
            pdf_url,
            firma_docente,
            firma_comision,
            id_practica
        ))

        conexion.commit()

        return True

    except Exception as e:

        print("ERROR AL ACTUALIZAR:")
        print(e)

        if conexion:
            conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_firma_comision(id_practica, ruta_firma):
    """Actualiza únicamente la firma de comisión, sin tocar el resto de campos.
    Útil cuando la comisión firma después de que ya se creó la práctica."""

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE practicas
            SET firma_comision = %s
            WHERE id = %s
        """, (ruta_firma, id_practica))

        conexion.commit()
        return True

    except Exception as e:
        print("ERROR AL ACTUALIZAR FIRMA COMISIÓN:")
        print(e)
        if conexion:
            conexion.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()