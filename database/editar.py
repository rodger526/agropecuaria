from database.conexion import obtener_conexion


_ULTIMO_ERROR = ""


def _guardar_error(error):
    global _ULTIMO_ERROR
    _ULTIMO_ERROR = str(error or "").strip()


def obtener_ultimo_error():
    return _ULTIMO_ERROR


def actualizar_datos_practica(
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
):
    """
    Actualiza solo datos editables.

    No modifica:
    - codigo
    - pdf_url
    - firma_docente
    - firma_comision
    """

    global _ULTIMO_ERROR
    _ULTIMO_ERROR = ""

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE practicas
            SET
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
                evidencias = %s
            WHERE id = %s
            RETURNING id
            """,
            (
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
                id_practica,
            ),
        )

        fila = cursor.fetchone()

        if not fila:
            raise ValueError(
                f"No existe una práctica con id {id_practica}."
            )

        conexion.commit()
        return True

    except Exception as error:
        _guardar_error(error)

        if conexion:
            conexion.rollback()

        print("\nERROR AL ACTUALIZAR PRÁCTICA")
        print(error)
        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def actualizar_con_firma_comision(
    id_practica,
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
    nueva_pdf_url,
    nueva_firma_comision_url,
):
    """
    Actualiza datos, pdf_url y firma_comision en una sola transacción.

    La condición del WHERE impide reemplazar una firma de comisión
    que ya exista.
    """

    global _ULTIMO_ERROR
    _ULTIMO_ERROR = ""

    conexion = None
    cursor = None

    try:
        if not str(nueva_pdf_url or "").startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "La URL del PDF actualizado no es válida."
            )

        if not str(nueva_firma_comision_url or "").startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "La URL de la firma de comisión no es válida."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE practicas
            SET
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
                firma_comision = %s
            WHERE id = %s
              AND (
                    firma_comision IS NULL
                    OR BTRIM(firma_comision) = ''
                  )
            RETURNING id
            """,
            (
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
                nueva_pdf_url,
                nueva_firma_comision_url,
                id_practica,
            ),
        )

        fila = cursor.fetchone()

        if not fila:
            cursor.execute(
                """
                SELECT firma_comision
                FROM practicas
                WHERE id = %s
                """,
                (id_practica,),
            )

            existente = cursor.fetchone()

            if not existente:
                raise ValueError(
                    f"No existe una práctica con id {id_practica}."
                )

            if str(existente[0] or "").strip():
                raise ValueError(
                    "La práctica ya posee una firma de comisión. "
                    "No puede sustituirse."
                )

            raise RuntimeError(
                "PostgreSQL no confirmó la actualización."
            )

        conexion.commit()
        return True

    except Exception as error:
        _guardar_error(error)

        if conexion:
            conexion.rollback()

        print("\nERROR AL ACTUALIZAR PDF Y FIRMA")
        print(error)
        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_estado_firmas(id_practica):
    global _ULTIMO_ERROR
    _ULTIMO_ERROR = ""

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                firma_docente,
                firma_comision,
                pdf_url,
                codigo
            FROM practicas
            WHERE id = %s
            """,
            (id_practica,),
        )

        fila = cursor.fetchone()

        if not fila:
            return {
                "firma_docente": None,
                "firma_comision": None,
                "pdf_url": None,
                "codigo": None,
            }

        return {
            "firma_docente": fila[0],
            "firma_comision": fila[1],
            "pdf_url": fila[2],
            "codigo": fila[3],
        }

    except Exception as error:
        _guardar_error(error)

        return {
            "firma_docente": None,
            "firma_comision": None,
            "pdf_url": None,
            "codigo": None,
        }

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()