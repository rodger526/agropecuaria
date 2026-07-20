from datetime import date

from database.conexion import obtener_conexion


# ============================================================
# Constantes
# ============================================================

MESES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


# ============================================================
# Funciones internas
# ============================================================

def _ejecutar_consulta(
    consulta,
    parametros=None,
    uno=False,
):
    """
    Ejecuta una consulta SELECT y devuelve los resultados.

    No modifica información de PostgreSQL.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            consulta,
            parametros or (),
        )

        if uno:
            return cursor.fetchone()

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def _numero(valor):
    """
    Convierte valores PostgreSQL a números seguros.
    """

    if valor is None:
        return 0

    try:
        return int(valor)
    except (TypeError, ValueError):
        try:
            return float(valor)
        except (TypeError, ValueError):
            return 0


def _texto(valor, defecto="Sin especificar"):
    """
    Limpia valores de texto recibidos desde PostgreSQL.
    """

    texto = str(
        valor or ""
    ).strip()

    return texto if texto else defecto


def _obtener_total_mes(
    anio,
    mes,
):
    """
    Obtiene el total de prácticas de un mes específico.
    """

    fila = _ejecutar_consulta(
        """
        SELECT COUNT(*)
        FROM practicas
        WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
          AND EXTRACT(MONTH FROM fecha_creacion) = %s
        """,
        (
            anio,
            mes,
        ),
        uno=True,
    )

    return _numero(
        fila[0] if fila else 0
    )


# ============================================================
# Resumen principal
# ============================================================

def obtener_resumen_practicas(
    anio=None,
):
    """
    Devuelve los indicadores principales del módulo de prácticas.
    """

    hoy = date.today()

    if anio is None:
        anio = hoy.year

    fila = _ejecutar_consulta(
        """
        SELECT
            COUNT(*) AS total_practicas,

            COUNT(DISTINCT NULLIF(TRIM(carrera), ''))
                AS total_carreras,

            COUNT(DISTINCT NULLIF(TRIM(asignatura), ''))
                AS total_asignaturas,

            COUNT(DISTINCT NULLIF(TRIM(ingeniero_revisor), ''))
                AS total_revisores,

            COUNT(DISTINCT semestre)
                AS total_semestres,

            COUNT(DISTINCT NULLIF(TRIM(tipo_practica), ''))
                AS total_tipos,

            COUNT(*) FILTER (
                WHERE pdf_url IS NOT NULL
                  AND TRIM(pdf_url) <> ''
            ) AS con_pdf,

            COUNT(*) FILTER (
                WHERE pdf_url IS NULL
                   OR TRIM(pdf_url) = ''
            ) AS sin_pdf,

            COUNT(*) FILTER (
                WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
            ) AS total_anio

        FROM practicas
        """,
        (
            anio,
        ),
        uno=True,
    )

    if not fila:
        fila = (
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )

    total_mes_actual = _obtener_total_mes(
        hoy.year,
        hoy.month,
    )

    if hoy.month == 1:
        anio_anterior = hoy.year - 1
        mes_anterior = 12
    else:
        anio_anterior = hoy.year
        mes_anterior = hoy.month - 1

    total_mes_anterior = _obtener_total_mes(
        anio_anterior,
        mes_anterior,
    )

    if total_mes_anterior > 0:
        variacion = (
            (
                total_mes_actual
                - total_mes_anterior
            )
            / total_mes_anterior
        ) * 100

    elif total_mes_actual > 0:
        variacion = 100.0

    else:
        variacion = 0.0

    return {
        "total_practicas": _numero(fila[0]),
        "total_carreras": _numero(fila[1]),
        "total_asignaturas": _numero(fila[2]),
        "total_revisores": _numero(fila[3]),
        "total_semestres": _numero(fila[4]),
        "total_tipos": _numero(fila[5]),
        "con_pdf": _numero(fila[6]),
        "sin_pdf": _numero(fila[7]),
        "total_anio": _numero(fila[8]),
        "registros_este_mes": total_mes_actual,
        "registros_mes_anterior": total_mes_anterior,
        "variacion_mensual": round(
            variacion,
            2,
        ),
    }


# ============================================================
# Registros mensuales
# ============================================================

def obtener_practicas_por_mes(
    anio=None,
):
    """
    Devuelve los doce meses, incluso cuando alguno tenga cero.
    """

    if anio is None:
        anio = date.today().year

    filas = _ejecutar_consulta(
        """
        SELECT
            EXTRACT(MONTH FROM fecha_creacion)::INTEGER AS mes,
            COUNT(*) AS total
        FROM practicas
        WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
        GROUP BY EXTRACT(MONTH FROM fecha_creacion)
        ORDER BY mes
        """,
        (
            anio,
        ),
    )

    datos_por_mes = {
        int(fila[0]): _numero(fila[1])
        for fila in filas
    }

    return [
        {
            "numero_mes": numero_mes,
            "mes": MESES[numero_mes - 1],
            "total": datos_por_mes.get(
                numero_mes,
                0,
            ),
        }
        for numero_mes in range(1, 13)
    ]


# ============================================================
# Prácticas por carrera
# ============================================================

def obtener_practicas_por_carrera(
    limite=10,
    anio=None,
):
    """
    Agrupa las prácticas por carrera.
    """

    parametros = []
    filtro_anio = ""

    if anio is not None:
        filtro_anio = """
            WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
        """

        parametros.append(
            anio
        )

    parametros.append(
        limite
    )

    filas = _ejecutar_consulta(
        f"""
        SELECT
            COALESCE(
                NULLIF(TRIM(carrera), ''),
                'Sin especificar'
            ) AS carrera,
            COUNT(*) AS total
        FROM practicas
        {filtro_anio}
        GROUP BY
            COALESCE(
                NULLIF(TRIM(carrera), ''),
                'Sin especificar'
            )
        ORDER BY total DESC, carrera
        LIMIT %s
        """,
        tuple(parametros),
    )

    return [
        {
            "carrera": _texto(fila[0]),
            "total": _numero(fila[1]),
        }
        for fila in filas
    ]


# ============================================================
# Prácticas por semestre
# ============================================================

def obtener_practicas_por_semestre(
    anio=None,
):
    """
    Agrupa los registros por semestre académico.
    """

    parametros = []
    filtro_anio = ""

    if anio is not None:
        filtro_anio = """
            WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
        """

        parametros.append(
            anio
        )

    filas = _ejecutar_consulta(
        f"""
        SELECT
            semestre,
            COUNT(*) AS total
        FROM practicas
        {filtro_anio}
        GROUP BY semestre
        ORDER BY semestre
        """,
        tuple(parametros),
    )

    resultado = []

    for fila in filas:
        semestre = fila[0]

        if semestre is None:
            nombre = "Sin especificar"
        else:
            nombre = f"Semestre {semestre}"

        resultado.append(
            {
                "semestre": semestre,
                "nombre": nombre,
                "total": _numero(fila[1]),
            }
        )

    return resultado


# ============================================================
# Prácticas por tipo
# ============================================================

def obtener_practicas_por_tipo(
    limite=10,
    anio=None,
):
    """
    Agrupa los registros por tipo de práctica.
    """

    parametros = []
    filtro_anio = ""

    if anio is not None:
        filtro_anio = """
            WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
        """

        parametros.append(
            anio
        )

    parametros.append(
        limite
    )

    filas = _ejecutar_consulta(
        f"""
        SELECT
            COALESCE(
                NULLIF(TRIM(tipo_practica), ''),
                'Sin especificar'
            ) AS tipo,
            COUNT(*) AS total
        FROM practicas
        {filtro_anio}
        GROUP BY
            COALESCE(
                NULLIF(TRIM(tipo_practica), ''),
                'Sin especificar'
            )
        ORDER BY total DESC, tipo
        LIMIT %s
        """,
        tuple(parametros),
    )

    return [
        {
            "tipo": _texto(fila[0]),
            "total": _numero(fila[1]),
        }
        for fila in filas
    ]


# ============================================================
# Prácticas por asignatura
# ============================================================

def obtener_practicas_por_asignatura(
    limite=10,
    anio=None,
):
    """
    Devuelve las asignaturas con más prácticas.
    """

    parametros = []
    filtro_anio = ""

    if anio is not None:
        filtro_anio = """
            WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
        """

        parametros.append(
            anio
        )

    parametros.append(
        limite
    )

    filas = _ejecutar_consulta(
        f"""
        SELECT
            COALESCE(
                NULLIF(TRIM(asignatura), ''),
                'Sin especificar'
            ) AS asignatura,
            COUNT(*) AS total
        FROM practicas
        {filtro_anio}
        GROUP BY
            COALESCE(
                NULLIF(TRIM(asignatura), ''),
                'Sin especificar'
            )
        ORDER BY total DESC, asignatura
        LIMIT %s
        """,
        tuple(parametros),
    )

    return [
        {
            "asignatura": _texto(fila[0]),
            "total": _numero(fila[1]),
        }
        for fila in filas
    ]


# ============================================================
# Prácticas por revisor
# ============================================================

def obtener_practicas_por_revisor(
    limite=10,
    anio=None,
):
    """
    Devuelve los revisores con mayor cantidad de prácticas.
    """

    parametros = []
    filtro_anio = ""

    if anio is not None:
        filtro_anio = """
            WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
        """

        parametros.append(
            anio
        )

    parametros.append(
        limite
    )

    filas = _ejecutar_consulta(
        f"""
        SELECT
            COALESCE(
                NULLIF(TRIM(ingeniero_revisor), ''),
                'Sin especificar'
            ) AS revisor,
            COUNT(*) AS total
        FROM practicas
        {filtro_anio}
        GROUP BY
            COALESCE(
                NULLIF(TRIM(ingeniero_revisor), ''),
                'Sin especificar'
            )
        ORDER BY total DESC, revisor
        LIMIT %s
        """,
        tuple(parametros),
    )

    return [
        {
            "revisor": _texto(fila[0]),
            "total": _numero(fila[1]),
        }
        for fila in filas
    ]


# ============================================================
# Estado de documentos PDF
# ============================================================

def obtener_estado_pdfs_practicas(
    anio=None,
):
    """
    Devuelve cuántas prácticas tienen PDF y cuántas no.
    """

    parametros = []
    filtro_anio = ""

    if anio is not None:
        filtro_anio = """
            WHERE EXTRACT(YEAR FROM fecha_creacion) = %s
        """

        parametros.append(
            anio
        )

    fila = _ejecutar_consulta(
        f"""
        SELECT
            COUNT(*) FILTER (
                WHERE pdf_url IS NOT NULL
                  AND TRIM(pdf_url) <> ''
            ) AS con_pdf,

            COUNT(*) FILTER (
                WHERE pdf_url IS NULL
                   OR TRIM(pdf_url) = ''
            ) AS sin_pdf

        FROM practicas
        {filtro_anio}
        """,
        tuple(parametros),
        uno=True,
    )

    if not fila:
        fila = (
            0,
            0,
        )

    con_pdf = _numero(
        fila[0]
    )

    sin_pdf = _numero(
        fila[1]
    )

    total = con_pdf + sin_pdf

    porcentaje = (
        round(
            (con_pdf / total) * 100,
            2,
        )
        if total > 0
        else 0
    )

    return {
        "con_pdf": con_pdf,
        "sin_pdf": sin_pdf,
        "total": total,
        "porcentaje_con_pdf": porcentaje,
    }


# ============================================================
# Años disponibles
# ============================================================

def obtener_anios_practicas():
    """
    Obtiene los años en que existen registros.
    """

    filas = _ejecutar_consulta(
        """
        SELECT DISTINCT
            EXTRACT(YEAR FROM fecha_creacion)::INTEGER AS anio
        FROM practicas
        WHERE fecha_creacion IS NOT NULL
        ORDER BY anio DESC
        """
    )

    anios = [
        _numero(fila[0])
        for fila in filas
        if fila[0] is not None
    ]

    anio_actual = date.today().year

    if anio_actual not in anios:
        anios.insert(
            0,
            anio_actual,
        )

    return anios


# ============================================================
# Últimas prácticas
# ============================================================

def obtener_ultimas_practicas(
    limite=10,
):
    """
    Devuelve los últimos registros creados.
    """

    filas = _ejecutar_consulta(
        """
        SELECT
            id,
            codigo,
            fecha_creacion,
            carrera,
            semestre,
            asignatura,
            tipo_practica,
            ingeniero_revisor,
            tema_practica,
            pdf_url
        FROM practicas
        ORDER BY fecha_creacion DESC NULLS LAST, id DESC
        LIMIT %s
        """,
        (
            limite,
        ),
    )

    return [
        {
            "id": fila[0],
            "codigo": _texto(
                fila[1],
                "—",
            ),
            "fecha": fila[2],
            "carrera": _texto(
                fila[3],
                "—",
            ),
            "semestre": fila[4],
            "asignatura": _texto(
                fila[5],
                "—",
            ),
            "tipo_practica": _texto(
                fila[6],
                "—",
            ),
            "revisor": _texto(
                fila[7],
                "—",
            ),
            "tema": _texto(
                fila[8],
                "—",
            ),
            "pdf_url": str(
                fila[9] or ""
            ).strip(),
        }
        for fila in filas
    ]


# ============================================================
# Consulta completa del dashboard
# ============================================================

def obtener_dashboard_practicas(
    anio=None,
):
    """
    Ejecuta todas las consultas necesarias para construir la vista.
    """

    if anio is None:
        anio = date.today().year

    return {
        "anio": anio,
        "resumen": obtener_resumen_practicas(
            anio
        ),
        "mensuales": obtener_practicas_por_mes(
            anio
        ),
        "carreras": obtener_practicas_por_carrera(
            limite=8,
            anio=anio,
        ),
        "semestres": obtener_practicas_por_semestre(
            anio=anio
        ),
        "tipos": obtener_practicas_por_tipo(
            limite=8,
            anio=anio,
        ),
        "asignaturas": obtener_practicas_por_asignatura(
            limite=8,
            anio=anio,
        ),
        "revisores": obtener_practicas_por_revisor(
            limite=8,
            anio=anio,
        ),
        "pdfs": obtener_estado_pdfs_practicas(
            anio=anio
        ),
        "ultimas": obtener_ultimas_practicas(
            limite=10
        ),
        "anios": obtener_anios_practicas(),
    }


# ============================================================
# Prueba directa
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== DASHBOARD DE PRÁCTICAS ==========\n"
    )

    anio_prueba = date.today().year

    print(
        f"Año consultado: {anio_prueba}\n"
    )

    print(
        "RESUMEN:"
    )

    print(
        obtener_resumen_practicas(
            anio_prueba
        )
    )

    print(
        "\nREGISTROS POR MES:"
    )

    for registro in obtener_practicas_por_mes(
        anio_prueba
    ):
        print(
            registro
        )

    print(
        "\nPRÁCTICAS POR CARRERA:"
    )

    for registro in obtener_practicas_por_carrera(
        anio=anio_prueba
    ):
        print(
            registro
        )

    print(
        "\nPRÁCTICAS POR SEMESTRE:"
    )

    for registro in obtener_practicas_por_semestre(
        anio=anio_prueba
    ):
        print(
            registro
        )

    print(
        "\nPRÁCTICAS POR TIPO:"
    )

    for registro in obtener_practicas_por_tipo(
        anio=anio_prueba
    ):
        print(
            registro
        )

    print(
        "\nPRÁCTICAS POR ASIGNATURA:"
    )

    for registro in obtener_practicas_por_asignatura(
        anio=anio_prueba
    ):
        print(
            registro
        )

    print(
        "\nREVISORES:"
    )

    for registro in obtener_practicas_por_revisor(
        anio=anio_prueba
    ):
        print(
            registro
        )

    print(
        "\nESTADO DE PDFs:"
    )

    print(
        obtener_estado_pdfs_practicas(
            anio=anio_prueba
        )
    )

    print(
        "\nAÑOS DISPONIBLES:"
    )

    print(
        obtener_anios_practicas()
    )

    print(
        "\nÚLTIMAS PRÁCTICAS:"
    )

    for registro in obtener_ultimas_practicas():
        print(
            registro
        )

    print(
        "\n============================================\n"
    )