from database.conexion import obtener_conexion


def guardar_laboratorio(laboratorio):
    """
    Guarda un objeto Laboratorio en la tabla `laboratorios`.

    También guarda:
        - materiales;
        - reactivos;
        - estudiantes;
        - encargado del laboratorio;
        - cargo del encargado;
        - firma del encargado;
        - firma del docente;
        - código de sesión.

    Devuelve:
        True si todo se guardó correctamente.
        False si ocurrió algún error.
    """

    conexion = None
    cursor = None

    try:
        if laboratorio is None:
            raise ValueError(
                "El objeto laboratorio no puede ser None."
            )

        if not str(
            laboratorio.codigo or ""
        ).strip():
            raise ValueError(
                "El laboratorio no tiene un código válido."
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
        # 1. Insertar registro principal
        # ============================================================

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
                pdf_url,
                encargado_laboratorio,
                cargo_encargado,
                firma_encargado_ruta,
                firma_docente_ruta,
                codigo_sesion
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
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
            laboratorio.encargado_laboratorio,
            laboratorio.cargo_encargado,
            laboratorio.firma_encargado_ruta,
            laboratorio.firma_docente_ruta,
            laboratorio.codigo_sesion,
        ))

        resultado = cursor.fetchone()

        if not resultado:
            raise RuntimeError(
                "PostgreSQL no devolvió el ID del laboratorio."
            )

        laboratorio_id = resultado[0]
        laboratorio.id = laboratorio_id

        # ============================================================
        # 2. Insertar materiales
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

            cantidad = material.get("cantidad")

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
                laboratorio_id,
                nombre,
                cantidad,
            ))

        # ============================================================
        # 3. Insertar reactivos
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

            cantidad = reactivo.get("cantidad")

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
                laboratorio_id,
                nombre,
                cantidad,
            ))

        # ============================================================
        # 4. Insertar estudiantes
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

            cedula = estudiante.get("cedula")
            firma_ruta = estudiante.get("firma_ruta")

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
                laboratorio_id,
                nombre,
                cedula,
                firma_ruta,
            ))

        conexion.commit()

        print(
            f"Laboratorio guardado correctamente. ID: {laboratorio_id}"
        )

        return True

    except Exception as error:
        print(
            "\n========== ERROR AL GUARDAR LABORATORIO =========="
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