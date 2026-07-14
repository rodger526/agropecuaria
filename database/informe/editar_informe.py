from database.conexion import obtener_conexion


def actualizar_informe(informe):
    """
    Actualiza un informe completo.

    También reemplaza las fotografías asociadas.
    """

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE informes_laboratorio
            SET
                titulo=%s,
                autores=%s,
                asignatura=%s,
                carrera=%s,
                semestre=%s,
                docente=%s,
                resumen=%s,
                palabras_clave=%s,
                introduccion=%s,
                objetivo_general=%s,
                objetivos_especificos=%s,
                materiales_reactivos=%s,
                procedimiento_experimental=%s,
                resultados=%s,
                discusion=%s,
                conclusiones=%s,
                recomendaciones=%s,
                bibliografia=%s,
                cuestionario=%s,
                anexos=%s,
                hoja_datos_url=%s,
                pdf_url=%s
            WHERE id=%s
        """, (

            informe.titulo,
            informe.autores,
            informe.asignatura,
            informe.carrera,
            informe.semestre,
            informe.docente,
            informe.resumen,
            informe.palabras_clave,
            informe.introduccion,
            informe.objetivo_general,
            informe.objetivos_especificos,
            informe.materiales_reactivos,
            informe.procedimiento_experimental,
            informe.resultados,
            informe.discusion,
            informe.conclusiones,
            informe.recomendaciones,
            informe.bibliografia,
            informe.cuestionario,
            informe.anexos,
            informe.hoja_datos_url,
            informe.pdf_url,
            informe.id

        ))

        if cursor.rowcount == 0:
            raise Exception("El informe no existe.")

        # ===========================================
        # Eliminar fotografías anteriores
        # ===========================================

        cursor.execute("""
            DELETE FROM informe_laboratorio_fotos
            WHERE informe_id=%s
        """, (
            informe.id,
        ))

        # ===========================================
        # Insertar nuevamente las fotografías
        # ===========================================

        orden = 1

        for foto in informe.fotos or []:

            cursor.execute("""
                INSERT INTO informe_laboratorio_fotos(
                    informe_id,
                    foto_url,
                    descripcion,
                    orden
                )
                VALUES(%s,%s,%s,%s)
            """, (

                informe.id,
                foto.get("foto_url"),
                foto.get("descripcion"),
                orden

            ))

            orden += 1

        conexion.commit()

        print("Informe actualizado correctamente.")

        return True

    except Exception as e:

        print("\n========== ERROR ACTUALIZANDO INFORME ==========")
        print(e)
        print("===============================================\n")

        if conexion:
            conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_pdf_url_informe(id_informe, nueva_url):
    """
    Actualiza únicamente la URL del PDF.
    """

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE informes_laboratorio
            SET pdf_url=%s
            WHERE id=%s
        """, (

            nueva_url,
            id_informe

        ))

        conexion.commit()

        return True

    except Exception as e:

        print("\n===== ERROR ACTUALIZANDO PDF =====")
        print(e)
        print("=================================\n")

        if conexion:
            conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_hoja_datos(id_informe, nueva_url):
    """
    Actualiza la URL de la hoja de datos.
    """

    conexion = None
    cursor = None

    try:

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE informes_laboratorio
            SET hoja_datos_url=%s
            WHERE id=%s
        """, (

            nueva_url,
            id_informe

        ))

        conexion.commit()

        return True

    except Exception as e:

        print("\n===== ERROR ACTUALIZANDO HOJA DE DATOS =====")
        print(e)
        print("===========================================\n")

        if conexion:
            conexion.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()