from database.conexion import obtener_conexion


def guardar_informe(informe):
    """
    Guarda el informe principal y sus fotografías relacionadas
    dentro de una sola transacción.

    El objeto informe debe contener:

        informe.fotos = [
            {
                "foto_url": "...",
                "descripcion": "...",
                "orden": 1
            }
        ]

    Devuelve:
        True si se guardó correctamente.
        False si ocurrió algún error.
    """

    conexion = None
    cursor = None

    try:
        if informe is None:
            raise ValueError(
                "El objeto informe no puede ser None."
            )

        if not str(
            informe.codigo or ""
        ).strip():
            raise ValueError(
                "El informe no tiene un código válido."
            )

        if not str(
            informe.titulo or ""
        ).strip():
            raise ValueError(
                "El informe no tiene título."
            )

        if not str(
            informe.autores or ""
        ).strip():
            raise ValueError(
                "Debe ingresar los autores del informe."
            )

        if not str(
            informe.asignatura or ""
        ).strip():
            raise ValueError(
                "Debe ingresar la asignatura."
            )

        pdf_url = str(
            informe.pdf_url or ""
        ).strip()

        if not pdf_url:
            raise ValueError(
                "El informe no tiene una URL de PDF."
            )

        if not pdf_url.lower().startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "La URL del PDF no tiene un formato válido."
            )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # ============================================================
        # 1. Insertar informe principal
        # ============================================================

        cursor.execute("""
            INSERT INTO informes_laboratorio (
                codigo,
                titulo,
                autores,
                asignatura,
                carrera,
                semestre,
                docente,
                resumen,
                palabras_clave,
                introduccion,
                objetivo_general,
                objetivos_especificos,
                materiales_reactivos,
                procedimiento_experimental,
                resultados,
                discusion,
                conclusiones,
                recomendaciones,
                bibliografia,
                cuestionario,
                anexos,
                hoja_datos_url,
                pdf_url,
                fecha_creacion
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            RETURNING id
        """, (
            informe.codigo,
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
            pdf_url,
            informe.fecha_creacion,
        ))

        resultado = cursor.fetchone()

        if not resultado:
            raise RuntimeError(
                "PostgreSQL no devolvió el ID del informe."
            )

        informe_id = resultado[0]
        informe.id = informe_id

        # ============================================================
        # 2. Insertar fotografías relacionadas
        # ============================================================

        for indice, foto in enumerate(
            informe.fotos or [],
            start=1,
        ):
            if not isinstance(
                foto,
                dict,
            ):
                continue

            foto_url = str(
                foto.get(
                    "foto_url"
                )
                or ""
            ).strip()

            if not foto_url:
                continue

            if not foto_url.lower().startswith(
                ("http://", "https://")
            ):
                continue

            descripcion = str(
                foto.get(
                    "descripcion"
                )
                or ""
            ).strip()

            try:
                orden = int(
                    foto.get(
                        "orden",
                        indice,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                orden = indice

            cursor.execute("""
                INSERT INTO informe_laboratorio_fotos (
                    informe_id,
                    foto_url,
                    descripcion,
                    orden
                )
                VALUES (%s, %s, %s, %s)
            """, (
                informe_id,
                foto_url,
                descripcion,
                orden,
            ))

        conexion.commit()

        print(
            f"Informe guardado correctamente. ID: {informe_id}"
        )

        return True

    except Exception as e:
        print(
            "\n========== ERROR AL GUARDAR INFORME =========="
        )
        print(e)
        print(
            "==============================================\n"
        )

        if conexion:
            conexion.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()