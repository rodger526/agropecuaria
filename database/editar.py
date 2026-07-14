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
    """
    Actualiza los datos principales de una práctica.

    Las firmas se conservan si firma_docente o firma_comision llegan
    como None, gracias al uso de COALESCE.

    Devuelve:
        True  -> actualización correcta.
        False -> error o práctica inexistente.
    """

    conexion = None
    cursor = None

    try:
        if id_practica is None:
            raise ValueError(
                "El id de la práctica no puede ser None."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE practicas
            SET
                codigo = %s,
                carrera = %s,
                semestre = %s,
                asignatura = %s,
                unidad_silabo = %s,
                tipo_practica = %s,
                ingeniero_revisor = %s,
                lugar_ejecucion = %s,
                semana_planificada = %s,
                tema_practica = %s,
                resultado_aprendizaje = %s,
                articulacion_curricular = %s,
                objetivo_general = %s,
                materiales_equipos = %s,
                descripcion_actividad = %s,
                evidencias = %s,
                pdf_url = %s,
                firma_docente = COALESCE(%s, firma_docente),
                firma_comision = COALESCE(%s, firma_comision)
            WHERE id = %s
        """, (
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
            id_practica,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe una práctica con id {id_practica}."
            )

        conexion.commit()

        print(
            f"Práctica {id_practica} actualizada correctamente."
        )

        return True

    except Exception as e:
        print("\n========== ERROR AL ACTUALIZAR PRÁCTICA ==========")
        print(e)
        print("===================================================\n")

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_firma_comision(id_practica, ruta_firma):
    """
    Actualiza únicamente la firma de la comisión.

    Actualmente ruta_firma puede ser una ruta local. Para que funcione
    desde distintas computadoras, lo recomendable es subir también la
    firma a Supabase Storage y guardar su URL.
    """

    conexion = None
    cursor = None

    try:
        if id_practica is None:
            raise ValueError(
                "El id de la práctica no puede ser None."
            )

        if not ruta_firma:
            raise ValueError(
                "La ruta de la firma no puede estar vacía."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE practicas
            SET firma_comision = %s
            WHERE id = %s
        """, (
            ruta_firma,
            id_practica,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe una práctica con id {id_practica}."
            )

        conexion.commit()

        print(
            f"Firma de comisión actualizada para la práctica {id_practica}."
        )

        return True

    except Exception as e:
        print("\n===== ERROR AL ACTUALIZAR FIRMA DE COMISIÓN =====")
        print(e)
        print("==================================================\n")

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_pdf_url(id_practica, nueva_url):
    """
    Actualiza únicamente el campo pdf_url de una práctica.

    Se usa después de regenerar y subir el PDF a Supabase Storage.
    """

    conexion = None
    cursor = None

    try:
        if id_practica is None:
            raise ValueError(
                "El id de la práctica no puede ser None."
            )

        nueva_url = str(nueva_url or "").strip()

        if not nueva_url:
            raise ValueError(
                "La URL del PDF está vacía."
            )

        if not nueva_url.lower().startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "La URL del PDF no tiene un formato válido."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE practicas
            SET pdf_url = %s
            WHERE id = %s
        """, (
            nueva_url,
            id_practica,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe una práctica con id {id_practica}."
            )

        conexion.commit()

        print(
            f"URL del PDF actualizada para la práctica {id_practica}."
        )

        return True

    except Exception as e:
        print("\n========== ERROR ACTUALIZANDO PDF URL ==========")
        print(e)
        print("=================================================\n")

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()