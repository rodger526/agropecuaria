from database.conexion import obtener_conexion


def guardar_laboratorio(laboratorio):
    """
    Guarda un objeto Laboratorio en PostgreSQL.

    También guarda:
        - materiales;
        - reactivos;
        - estudiantes;
        - encargado del laboratorio;
        - cargo del encargado;
        - firma del encargado;
        - firma del docente;
        - código de sesión;
        - URL del PDF.

    Todo se ejecuta dentro de una sola transacción.

    Devuelve:
        True si se guardó correctamente.
        False si ocurrió algún error.
    """

    conexion = None
    cursor = None

    try:
        # ============================================================
        # Validar objeto recibido
        # ============================================================

        if laboratorio is None:
            raise ValueError(
                "El objeto laboratorio no puede ser None."
            )

        codigo = str(
            getattr(
                laboratorio,
                "codigo",
                "",
            )
            or ""
        ).strip()

        nombre_laboratorio = str(
            getattr(
                laboratorio,
                "laboratorio",
                "",
            )
            or ""
        ).strip()

        docente_responsable = str(
            getattr(
                laboratorio,
                "docente_responsable",
                "",
            )
            or ""
        ).strip()

        if not codigo:
            raise ValueError(
                "El laboratorio no tiene un código válido."
            )

        if not nombre_laboratorio:
            raise ValueError(
                "Debe seleccionar un laboratorio."
            )

        if not docente_responsable:
            raise ValueError(
                "Debe ingresar el docente responsable."
            )

        # ============================================================
        # Abrir conexión
        # ============================================================

        conexion = obtener_conexion()

        if conexion is None:
            raise ConnectionError(
                "No se pudo establecer conexión con PostgreSQL."
            )

        cursor = conexion.cursor()

        # ============================================================
        # 1. Insertar registro principal
        # ============================================================

        cursor.execute(
            """
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
            """,
            (
                codigo,
                nombre_laboratorio,
                getattr(
                    laboratorio,
                    "numero_estudiantes",
                    None,
                ),
                getattr(
                    laboratorio,
                    "asignatura",
                    None,
                ),
                getattr(
                    laboratorio,
                    "unidad_academica",
                    None,
                ),
                getattr(
                    laboratorio,
                    "semestre",
                    None,
                ),
                getattr(
                    laboratorio,
                    "carrera",
                    None,
                ),
                getattr(
                    laboratorio,
                    "hora_entrada",
                    None,
                ),
                getattr(
                    laboratorio,
                    "hora_salida",
                    None,
                ),
                getattr(
                    laboratorio,
                    "institucion",
                    None,
                ),
                getattr(
                    laboratorio,
                    "ciudad",
                    None,
                ),
                docente_responsable,
                getattr(
                    laboratorio,
                    "fecha_practica",
                    None,
                ),
                getattr(
                    laboratorio,
                    "tema_practica",
                    None,
                ),
                getattr(
                    laboratorio,
                    "subtema",
                    None,
                ),
                getattr(
                    laboratorio,
                    "logro_aprendizaje",
                    None,
                ),
                getattr(
                    laboratorio,
                    "objetivos",
                    None,
                ),
                getattr(
                    laboratorio,
                    "metodologia",
                    None,
                ),
                getattr(
                    laboratorio,
                    "resultados",
                    None,
                ),
                getattr(
                    laboratorio,
                    "conclusiones",
                    None,
                ),
                getattr(
                    laboratorio,
                    "observaciones",
                    None,
                ),
                getattr(
                    laboratorio,
                    "pdf_url",
                    None,
                ),
                getattr(
                    laboratorio,
                    "encargado_laboratorio",
                    None,
                ),
                getattr(
                    laboratorio,
                    "cargo_encargado",
                    None,
                ),
                getattr(
                    laboratorio,
                    "firma_encargado_ruta",
                    None,
                ),
                getattr(
                    laboratorio,
                    "firma_docente_ruta",
                    None,
                ),
                getattr(
                    laboratorio,
                    "codigo_sesion",
                    None,
                ),
            ),
        )

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

        materiales = getattr(
            laboratorio,
            "materiales",
            None,
        ) or []

        for material in materiales:
            if not isinstance(
                material,
                dict,
            ):
                continue

            nombre = str(
                material.get(
                    "nombre"
                )
                or ""
            ).strip()

            cantidad = material.get(
                "cantidad"
            )

            if not nombre:
                continue

            cursor.execute(
                """
                INSERT INTO laboratorio_materiales (
                    laboratorio_id,
                    nombre,
                    cantidad
                )
                VALUES (%s, %s, %s)
                """,
                (
                    laboratorio_id,
                    nombre,
                    cantidad,
                ),
            )

        # ============================================================
        # 3. Insertar reactivos
        # ============================================================

        reactivos = getattr(
            laboratorio,
            "reactivos",
            None,
        ) or []

        for reactivo in reactivos:
            if not isinstance(
                reactivo,
                dict,
            ):
                continue

            nombre = str(
                reactivo.get(
                    "nombre"
                )
                or ""
            ).strip()

            cantidad = reactivo.get(
                "cantidad"
            )

            if not nombre:
                continue

            cursor.execute(
                """
                INSERT INTO laboratorio_reactivos (
                    laboratorio_id,
                    nombre,
                    cantidad
                )
                VALUES (%s, %s, %s)
                """,
                (
                    laboratorio_id,
                    nombre,
                    cantidad,
                ),
            )

        # ============================================================
        # 4. Insertar estudiantes
        # ============================================================

        estudiantes = getattr(
            laboratorio,
            "estudiantes",
            None,
        ) or []

        for estudiante in estudiantes:
            if not isinstance(
                estudiante,
                dict,
            ):
                continue

            nombre = str(
                estudiante.get(
                    "nombre"
                )
                or ""
            ).strip()

            cedula = str(
                estudiante.get(
                    "cedula"
                )
                or ""
            ).strip()

            firma_ruta = estudiante.get(
                "firma_ruta"
            )

            if not nombre:
                continue

            cursor.execute(
                """
                INSERT INTO laboratorio_estudiantes (
                    laboratorio_id,
                    nombre,
                    cedula,
                    firma_ruta
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    laboratorio_id,
                    nombre,
                    cedula,
                    firma_ruta,
                ),
            )

        # ============================================================
        # Confirmar transacción
        # ============================================================

        conexion.commit()

        print(
            "Laboratorio guardado correctamente. "
            f"ID: {laboratorio_id}"
        )

        return True

    except Exception as error:
        print(
            "\n"
            "========== ERROR AL GUARDAR LABORATORIO =========="
        )
        print(
            error
        )
        print(
            "=================================================="
            "\n"
        )

        if conexion:
            try:
                conexion.rollback()
            except Exception as error_rollback:
                print(
                    "No se pudo revertir la transacción:",
                    error_rollback,
                )

        return False

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass

        if conexion:
            try:
                conexion.close()
            except Exception:
                pass