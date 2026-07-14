from database.conexion import obtener_conexion


def actualizar_laboratorio(laboratorio):
    """
    Actualiza completamente un registro de laboratorio.

    También reemplaza:
        - materiales;
        - reactivos;
        - estudiantes.

    Actualiza además:
        - encargado del laboratorio;
        - cargo del encargado;
        - firma del encargado;
        - firma del docente;
        - código de sesión;
        - URL del PDF.

    Todo se ejecuta dentro de una sola transacción.

    Devuelve:
        True si se actualizó correctamente.
        False si ocurrió algún error.
    """

    conexion = None
    cursor = None

    try:
        if laboratorio is None:
            raise ValueError(
                "El objeto laboratorio no puede ser None."
            )

        if not getattr(
            laboratorio,
            "id",
            None,
        ):
            raise ValueError(
                "El laboratorio no tiene un ID válido."
            )

        if not str(
            laboratorio.laboratorio or ""
        ).strip():
            raise ValueError(
                "Debe seleccionar un laboratorio."
            )

        if not str(
            laboratorio.docente_responsable or ""
        ).strip():
            raise ValueError(
                "Debe ingresar el docente responsable."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # ============================================================
        # 1. Actualizar registro principal
        # ============================================================

        cursor.execute("""
            UPDATE laboratorios
            SET
                codigo                  = %s,
                laboratorio             = %s,
                numero_estudiantes      = %s,
                asignatura              = %s,
                unidad_academica        = %s,
                semestre                = %s,
                carrera                 = %s,
                hora_entrada            = %s,
                hora_salida             = %s,
                institucion             = %s,
                ciudad                  = %s,
                docente_responsable     = %s,
                fecha_practica          = %s,
                tema_practica           = %s,
                subtema                 = %s,
                logro_aprendizaje       = %s,
                objetivos               = %s,
                metodologia             = %s,
                resultados              = %s,
                conclusiones            = %s,
                observaciones           = %s,
                pdf_url                 = %s,
                encargado_laboratorio   = %s,
                cargo_encargado         = %s,
                firma_encargado_ruta    = %s,
                firma_docente_ruta      = %s,
                codigo_sesion           = %s
            WHERE id = %s
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
            laboratorio.encargado_laboratorio,
            laboratorio.cargo_encargado,
            laboratorio.firma_encargado_ruta,
            laboratorio.firma_docente_ruta,
            laboratorio.codigo_sesion,
            laboratorio.id,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe un laboratorio con ID {laboratorio.id}."
            )

        # ============================================================
        # 2. Eliminar materiales anteriores
        # ============================================================

        cursor.execute("""
            DELETE FROM laboratorio_materiales
            WHERE laboratorio_id = %s
        """, (
            laboratorio.id,
        ))

        # ============================================================
        # 3. Insertar materiales actuales
        # ============================================================

        for material in laboratorio.materiales or []:
            if not isinstance(
                material,
                dict,
            ):
                continue

            nombre = str(
                material.get("nombre") or ""
            ).strip()

            cantidad = material.get(
                "cantidad"
            )

            if not nombre:
                continue

            cursor.execute("""
                INSERT INTO laboratorio_materiales (
                    laboratorio_id,
                    nombre,
                    cantidad
                )
                VALUES (%s, %s, %s)
            """, (
                laboratorio.id,
                nombre,
                cantidad,
            ))

        # ============================================================
        # 4. Eliminar reactivos anteriores
        # ============================================================

        cursor.execute("""
            DELETE FROM laboratorio_reactivos
            WHERE laboratorio_id = %s
        """, (
            laboratorio.id,
        ))

        # ============================================================
        # 5. Insertar reactivos actuales
        # ============================================================

        for reactivo in laboratorio.reactivos or []:
            if not isinstance(
                reactivo,
                dict,
            ):
                continue

            nombre = str(
                reactivo.get("nombre") or ""
            ).strip()

            cantidad = reactivo.get(
                "cantidad"
            )

            if not nombre:
                continue

            cursor.execute("""
                INSERT INTO laboratorio_reactivos (
                    laboratorio_id,
                    nombre,
                    cantidad
                )
                VALUES (%s, %s, %s)
            """, (
                laboratorio.id,
                nombre,
                cantidad,
            ))

        # ============================================================
        # 6. Eliminar estudiantes anteriores
        # ============================================================

        cursor.execute("""
            DELETE FROM laboratorio_estudiantes
            WHERE laboratorio_id = %s
        """, (
            laboratorio.id,
        ))

        # ============================================================
        # 7. Insertar estudiantes actuales
        # ============================================================

        for estudiante in laboratorio.estudiantes or []:
            if not isinstance(
                estudiante,
                dict,
            ):
                continue

            nombre = str(
                estudiante.get("nombre") or ""
            ).strip()

            cedula = estudiante.get(
                "cedula"
            )

            firma_ruta = estudiante.get(
                "firma_ruta"
            )

            if not nombre:
                continue

            cursor.execute("""
                INSERT INTO laboratorio_estudiantes (
                    laboratorio_id,
                    nombre,
                    cedula,
                    firma_ruta
                )
                VALUES (%s, %s, %s, %s)
            """, (
                laboratorio.id,
                nombre,
                cedula,
                firma_ruta,
            ))

        conexion.commit()

        print(
            f"Laboratorio {laboratorio.id} "
            "actualizado correctamente."
        )

        return True

    except Exception as error:
        print(
            "\n========== ERROR AL ACTUALIZAR LABORATORIO =========="
        )
        print(error)
        print(
            "=====================================================\n"
        )

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_pdf_url_laboratorio(
    id_laboratorio,
    nueva_url,
):
    """
    Actualiza únicamente la URL del PDF del laboratorio.

    Se utiliza después de:
        - regenerar el PDF;
        - subirlo nuevamente a Supabase Storage.
    """

    conexion = None
    cursor = None

    try:
        if not id_laboratorio:
            raise ValueError(
                "El ID del laboratorio no es válido."
            )

        nueva_url = str(
            nueva_url or ""
        ).strip()

        if not nueva_url:
            raise ValueError(
                "La URL del PDF está vacía."
            )

        if not nueva_url.lower().startswith(
            (
                "http://",
                "https://",
            )
        ):
            raise ValueError(
                "La URL del PDF no tiene un formato válido."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE laboratorios
            SET pdf_url = %s
            WHERE id = %s
        """, (
            nueva_url,
            id_laboratorio,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe un laboratorio con ID {id_laboratorio}."
            )

        conexion.commit()

        print(
            "URL del PDF del laboratorio "
            "actualizada correctamente."
        )

        return True

    except Exception as error:
        print(
            "\n===== ERROR ACTUALIZANDO PDF DEL LABORATORIO ====="
        )
        print(error)
        print(
            "==================================================\n"
        )

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_firmas_laboratorio(
    id_laboratorio,
    firma_encargado_ruta=None,
    firma_docente_ruta=None,
):
    """
    Actualiza únicamente las firmas responsables del laboratorio.

    Permite actualizar:
        - firma del encargado;
        - firma del docente.

    Si una ruta llega como None, conserva la firma existente.
    """

    conexion = None
    cursor = None

    try:
        if not id_laboratorio:
            raise ValueError(
                "El ID del laboratorio no es válido."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE laboratorios
            SET
                firma_encargado_ruta = COALESCE(
                    %s,
                    firma_encargado_ruta
                ),
                firma_docente_ruta = COALESCE(
                    %s,
                    firma_docente_ruta
                )
            WHERE id = %s
        """, (
            firma_encargado_ruta,
            firma_docente_ruta,
            id_laboratorio,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe un laboratorio con ID {id_laboratorio}."
            )

        conexion.commit()

        print(
            "Firmas responsables actualizadas correctamente."
        )

        return True

    except Exception as error:
        print(
            "\n===== ERROR ACTUALIZANDO FIRMAS ====="
        )
        print(error)
        print(
            "=====================================\n"
        )

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_responsable_laboratorio(
    id_laboratorio,
    encargado_laboratorio,
    cargo_encargado,
):
    """
    Actualiza únicamente el nombre y cargo del encargado
    almacenado en el registro del laboratorio.
    """

    conexion = None
    cursor = None

    try:
        if not id_laboratorio:
            raise ValueError(
                "El ID del laboratorio no es válido."
            )

        encargado_laboratorio = str(
            encargado_laboratorio or ""
        ).strip()

        cargo_encargado = str(
            cargo_encargado or ""
        ).strip()

        if not encargado_laboratorio:
            raise ValueError(
                "El nombre del encargado está vacío."
            )

        if not cargo_encargado:
            raise ValueError(
                "El cargo del encargado está vacío."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE laboratorios
            SET
                encargado_laboratorio = %s,
                cargo_encargado = %s
            WHERE id = %s
        """, (
            encargado_laboratorio,
            cargo_encargado,
            id_laboratorio,
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                f"No existe un laboratorio con ID {id_laboratorio}."
            )

        conexion.commit()

        print(
            "Responsable del laboratorio actualizado correctamente."
        )

        return True

    except Exception as error:
        print(
            "\n===== ERROR ACTUALIZANDO RESPONSABLE ====="
        )
        print(error)
        print(
            "==========================================\n"
        )

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()