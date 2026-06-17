from database.conexion import obtener_conexion


def guardar_practica(practica):

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO practicas(
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
        )
        VALUES(
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
        """

        datos = (

            practica.codigo,

            practica.carrera,
            practica.semestre,
            practica.asignatura,
            practica.unidad_silabo,
            practica.tipo_practica,
            practica.ingeniero_revisor,
            practica.lugar_ejecucion,
            practica.semana_planificada,

            practica.tema_practica,
            practica.resultado_aprendizaje,
            practica.articulacion_curricular,

            practica.objetivo_general,
            practica.materiales_equipos,
            practica.descripcion_actividad,
            practica.evidencias,

            practica.pdf_url

        )

        cursor.execute(sql, datos)

        conexion.commit()

        print("Práctica guardada correctamente.")

        return True

    except Exception as e:

        print("\n========== ERROR AL GUARDAR ==========")
        print(str(e))
        print("======================================\n")

        if conexion:
            conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()