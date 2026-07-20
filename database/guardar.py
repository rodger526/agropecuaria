from database.conexion import obtener_conexion


def guardar_practica(practica):
    """
    Guarda una práctica en PostgreSQL.

    Solamente almacena los datos de la práctica y la URL pública
    del PDF subido a Supabase Storage.

    Las firmas no se guardan en PostgreSQL. Solo se utilizan
    temporalmente durante la generación del PDF.

    Devuelve:
        True  -> si la práctica fue guardada correctamente.
        False -> si ocurrió algún error.
    """

    conexion = None
    cursor = None

    try:
        if practica is None:
            raise ValueError(
                "El objeto práctica no puede ser None."
            )

        pdf_url = str(
            practica.pdf_url or ""
        ).strip()

        if not pdf_url:
            raise ValueError(
                "La práctica no tiene una URL de PDF asociada."
            )

        if not pdf_url.lower().startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "pdf_url debe contener una URL válida del PDF en línea."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = """
            INSERT INTO practicas (
                fecha_creacion,
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
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s
            )
            RETURNING id
        """

        datos = (
            practica.fecha_creacion,
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
            pdf_url,
        )

        cursor.execute(
            sql,
            datos,
        )

        practica_id = cursor.fetchone()[0]

        practica.id = practica_id

        conexion.commit()

        print(
            "Práctica guardada correctamente. "
            f"ID: {practica_id}"
        )

        return True

    except Exception as error:
        print(
            "\n========== ERROR AL GUARDAR PRÁCTICA =========="
        )
        print(error)
        print(
            "================================================\n"
        )

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()