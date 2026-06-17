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
    pdf_url
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
                pdf_url=%s
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