from datetime import date
from decimal import Decimal, InvalidOperation
import re

from database.conexion import obtener_conexion


# ============================================================
# Configuración de tablas
# ============================================================

TABLA_LABORATORIOS = "laboratorios"
TABLA_PRACTICAS = "practicas"
TABLA_REACTIVOS = "laboratorio_reactivos"
TABLA_MATERIALES = "laboratorio_materiales"


# ============================================================
# Funciones internas de apoyo
# ============================================================

def _cerrar_recursos(cursor=None, conexion=None):
    """
    Cierra de forma segura el cursor y la conexión.
    """

    if cursor is not None:
        try:
            cursor.close()
        except Exception:
            pass

    if conexion is not None:
        try:
            conexion.close()
        except Exception:
            pass


def _tabla_existe(cursor, nombre_tabla):
    """
    Comprueba si una tabla existe en el esquema público.
    """

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = %s
        )
        """,
        (nombre_tabla,),
    )

    resultado = cursor.fetchone()

    return bool(resultado and resultado[0])


def _obtener_columnas(cursor, nombre_tabla):
    """
    Devuelve un conjunto con los nombres de las columnas
    disponibles en una tabla.
    """

    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
        """,
        (nombre_tabla,),
    )

    return {
        fila[0]
        for fila in cursor.fetchall()
    }


def _seleccionar_primera_columna(columnas, opciones):
    """
    Devuelve la primera columna existente entre las opciones.
    """

    for opcion in opciones:
        if opcion in columnas:
            return opcion

    return None


def _expresion_fecha(columnas, alias=None):
    """
    Crea una expresión SQL utilizando la mejor columna de fecha
    disponible en la tabla.

    Prioridad:
        1. fecha_creacion
        2. fecha_registro
        3. created_at
        4. fecha_practica
        5. fecha
    """

    prefijo = f"{alias}." if alias else ""

    columnas_fecha = [
        "fecha_creacion",
        "fecha_registro",
        "created_at",
        "fecha_practica",
        "fecha",
    ]

    disponibles = [
        f"{prefijo}{columna}"
        for columna in columnas_fecha
        if columna in columnas
    ]

    if not disponibles:
        return None

    if len(disponibles) == 1:
        return disponibles[0]

    return f"COALESCE({', '.join(disponibles)})"


def _convertir_decimal(valor):
    """
    Convierte un valor en Decimal cuando sea posible.

    Admite:
        10
        10.5
        10,5
        10 ml
        5 gramos

    Solo extrae el primer número encontrado.
    """

    if valor is None:
        return Decimal("0")

    if isinstance(valor, Decimal):
        return valor

    if isinstance(valor, (int, float)):
        try:
            return Decimal(str(valor))
        except InvalidOperation:
            return Decimal("0")

    texto = str(valor).strip().replace(",", ".")

    coincidencia = re.search(
        r"-?\d+(?:\.\d+)?",
        texto,
    )

    if not coincidencia:
        return Decimal("0")

    try:
        return Decimal(coincidencia.group())
    except InvalidOperation:
        return Decimal("0")


def _normalizar_numero(valor):
    """
    Convierte Decimal a int o float para facilitar su uso
    en CustomTkinter y en las gráficas.
    """

    numero = _convertir_decimal(valor)

    if numero == numero.to_integral_value():
        return int(numero)

    return float(round(numero, 2))


def _contar_registros(cursor, tabla):
    """
    Cuenta los registros de una tabla si existe.
    """

    if not _tabla_existe(cursor, tabla):
        return 0

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {tabla}
        """
    )

    resultado = cursor.fetchone()

    return int(resultado[0] or 0)


def _contar_valores_distintos(
    cursor,
    tabla,
    columna,
):
    """
    Cuenta valores distintos no vacíos de una columna.
    """

    if not _tabla_existe(cursor, tabla):
        return 0

    columnas = _obtener_columnas(
        cursor,
        tabla,
    )

    if columna not in columnas:
        return 0

    cursor.execute(
        f"""
        SELECT COUNT(
            DISTINCT NULLIF(
                TRIM({columna}::text),
                ''
            )
        )
        FROM {tabla}
        """
    )

    resultado = cursor.fetchone()

    return int(resultado[0] or 0)


def _sumar_cantidades_tabla(
    cursor,
    tabla,
):
    """
    Suma las cantidades registradas en una tabla.

    Funciona aunque cantidad sea VARCHAR y contenga:
        10
        10.5
        10,5
        10 ml
        5 gramos
    """

    if not _tabla_existe(cursor, tabla):
        return 0

    columnas = _obtener_columnas(
        cursor,
        tabla,
    )

    columna_cantidad = _seleccionar_primera_columna(
        columnas,
        [
            "cantidad",
            "cantidad_utilizada",
            "cantidad_usada",
        ],
    )

    if columna_cantidad is None:
        return 0

    cursor.execute(
        f"""
        SELECT {columna_cantidad}
        FROM {tabla}
        WHERE {columna_cantidad} IS NOT NULL
        """
    )

    total = Decimal("0")

    for fila in cursor.fetchall():
        total += _convertir_decimal(fila[0])

    return _normalizar_numero(total)


def _obtener_total_pdfs_tabla(
    cursor,
    tabla,
):
    """
    Cuenta los registros que tienen una URL o ruta PDF válida.
    """

    if not _tabla_existe(cursor, tabla):
        return 0

    columnas = _obtener_columnas(
        cursor,
        tabla,
    )

    columna_pdf = _seleccionar_primera_columna(
        columnas,
        [
            "pdf_url",
            "ruta_pdf",
            "pdf",
            "archivo_pdf",
        ],
    )

    if columna_pdf is None:
        return 0

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {tabla}
        WHERE {columna_pdf} IS NOT NULL
          AND TRIM({columna_pdf}::text) <> ''
        """
    )

    resultado = cursor.fetchone()

    return int(resultado[0] or 0)


def _obtener_registros_del_mes_tabla(
    cursor,
    tabla,
):
    """
    Cuenta los registros creados durante el mes actual.
    """

    if not _tabla_existe(cursor, tabla):
        return 0

    columnas = _obtener_columnas(
        cursor,
        tabla,
    )

    fecha_sql = _expresion_fecha(
        columnas,
    )

    if fecha_sql is None:
        return 0

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {tabla}
        WHERE DATE_TRUNC(
                'month',
                {fecha_sql}::timestamp
              ) = DATE_TRUNC(
                'month',
                CURRENT_DATE
              )
        """
    )

    resultado = cursor.fetchone()

    return int(resultado[0] or 0)


def _obtener_registros_mes_anterior_tabla(
    cursor,
    tabla,
):
    """
    Cuenta los registros del mes anterior.
    """

    if not _tabla_existe(cursor, tabla):
        return 0

    columnas = _obtener_columnas(
        cursor,
        tabla,
    )

    fecha_sql = _expresion_fecha(
        columnas,
    )

    if fecha_sql is None:
        return 0

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {tabla}
        WHERE DATE_TRUNC(
                'month',
                {fecha_sql}::timestamp
              ) = DATE_TRUNC(
                'month',
                CURRENT_DATE - INTERVAL '1 month'
              )
        """
    )

    resultado = cursor.fetchone()

    return int(resultado[0] or 0)


def _calcular_variacion(
    valor_actual,
    valor_anterior,
):
    """
    Calcula el porcentaje de crecimiento o disminución.
    """

    actual = float(valor_actual or 0)
    anterior = float(valor_anterior or 0)

    if anterior == 0:
        if actual > 0:
            return 100.0

        return 0.0

    variacion = (
        (actual - anterior)
        / anterior
    ) * 100

    return round(
        variacion,
        2,
    )


# ============================================================
# Resumen general
# ============================================================

def obtener_resumen_general():
    """
    Devuelve las tarjetas principales del dashboard.

    El resultado tiene esta estructura:

    {
        "total_laboratorios": 0,
        "total_practicas": 0,
        "total_pdfs": 0,
        "total_reactivos": 0,
        "total_materiales": 0,
        "total_docentes": 0,
        "total_carreras": 0,
        "registros_este_mes": 0,
        "variacion_mensual": 0
    }
    """

    conexion = None
    cursor = None

    resumen_vacio = {
        "total_laboratorios": 0,
        "total_practicas": 0,
        "total_pdfs": 0,
        "total_reactivos": 0,
        "total_materiales": 0,
        "total_docentes": 0,
        "total_carreras": 0,
        "registros_este_mes": 0,
        "registros_mes_anterior": 0,
        "variacion_mensual": 0.0,
    }

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        total_laboratorios = _contar_registros(
            cursor,
            TABLA_LABORATORIOS,
        )

        total_practicas = _contar_registros(
            cursor,
            TABLA_PRACTICAS,
        )

        total_reactivos = _sumar_cantidades_tabla(
            cursor,
            TABLA_REACTIVOS,
        )

        total_materiales = _sumar_cantidades_tabla(
            cursor,
            TABLA_MATERIALES,
        )

        total_pdfs = (
            _obtener_total_pdfs_tabla(
                cursor,
                TABLA_LABORATORIOS,
            )
            + _obtener_total_pdfs_tabla(
                cursor,
                TABLA_PRACTICAS,
            )
        )

        total_docentes = 0
        total_carreras = 0

        tablas_principales = [
            TABLA_LABORATORIOS,
            TABLA_PRACTICAS,
        ]

        docentes_encontrados = set()
        carreras_encontradas = set()

        for tabla in tablas_principales:
            if not _tabla_existe(cursor, tabla):
                continue

            columnas = _obtener_columnas(
                cursor,
                tabla,
            )

            columna_docente = _seleccionar_primera_columna(
                columnas,
                [
                    "docente_responsable",
                    "docente",
                    "nombre_docente",
                ],
            )

            if columna_docente:
                cursor.execute(
                    f"""
                    SELECT DISTINCT
                        NULLIF(
                            TRIM({columna_docente}::text),
                            ''
                        )
                    FROM {tabla}
                    WHERE {columna_docente} IS NOT NULL
                    """
                )

                for fila in cursor.fetchall():
                    if fila[0]:
                        docentes_encontrados.add(
                            fila[0].strip().lower()
                        )

            columna_carrera = _seleccionar_primera_columna(
                columnas,
                [
                    "carrera",
                    "nombre_carrera",
                ],
            )

            if columna_carrera:
                cursor.execute(
                    f"""
                    SELECT DISTINCT
                        NULLIF(
                            TRIM({columna_carrera}::text),
                            ''
                        )
                    FROM {tabla}
                    WHERE {columna_carrera} IS NOT NULL
                    """
                )

                for fila in cursor.fetchall():
                    if fila[0]:
                        carreras_encontradas.add(
                            fila[0].strip().lower()
                        )

        total_docentes = len(
            docentes_encontrados
        )

        total_carreras = len(
            carreras_encontradas
        )

        registros_este_mes = (
            _obtener_registros_del_mes_tabla(
                cursor,
                TABLA_LABORATORIOS,
            )
            + _obtener_registros_del_mes_tabla(
                cursor,
                TABLA_PRACTICAS,
            )
        )

        registros_mes_anterior = (
            _obtener_registros_mes_anterior_tabla(
                cursor,
                TABLA_LABORATORIOS,
            )
            + _obtener_registros_mes_anterior_tabla(
                cursor,
                TABLA_PRACTICAS,
            )
        )

        variacion_mensual = _calcular_variacion(
            registros_este_mes,
            registros_mes_anterior,
        )

        return {
            "total_laboratorios": total_laboratorios,
            "total_practicas": total_practicas,
            "total_pdfs": total_pdfs,
            "total_reactivos": total_reactivos,
            "total_materiales": total_materiales,
            "total_docentes": total_docentes,
            "total_carreras": total_carreras,
            "registros_este_mes": registros_este_mes,
            "registros_mes_anterior": registros_mes_anterior,
            "variacion_mensual": variacion_mensual,
        }

    except Exception as error:
        print(
            "\n"
            "========== ERROR EN DASHBOARD GENERAL =========="
        )
        print(error)
        print(
            "================================================\n"
        )

        return resumen_vacio

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Registros por mes
# ============================================================

def obtener_registros_por_mes(
    anio=None,
):
    """
    Devuelve los registros combinados de laboratorios y prácticas
    para cada mes del año.

    Retorna:

    [
        {
            "numero_mes": 1,
            "mes": "Enero",
            "laboratorios": 3,
            "practicas": 5,
            "total": 8
        },
        ...
    ]
    """

    conexion = None
    cursor = None

    nombres_meses = [
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

    resultado = [
        {
            "numero_mes": numero,
            "mes": nombres_meses[numero - 1],
            "laboratorios": 0,
            "practicas": 0,
            "total": 0,
        }
        for numero in range(1, 13)
    ]

    try:
        if anio is None:
            anio = date.today().year

        anio = int(anio)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        configuraciones = [
            (
                TABLA_LABORATORIOS,
                "laboratorios",
            ),
            (
                TABLA_PRACTICAS,
                "practicas",
            ),
        ]

        for tabla, clave in configuraciones:
            if not _tabla_existe(cursor, tabla):
                continue

            columnas = _obtener_columnas(
                cursor,
                tabla,
            )

            fecha_sql = _expresion_fecha(
                columnas,
            )

            if fecha_sql is None:
                continue

            cursor.execute(
                f"""
                SELECT
                    EXTRACT(
                        MONTH FROM {fecha_sql}::timestamp
                    )::integer AS numero_mes,
                    COUNT(*) AS total

                FROM {tabla}

                WHERE EXTRACT(
                    YEAR FROM {fecha_sql}::timestamp
                )::integer = %s

                GROUP BY numero_mes

                ORDER BY numero_mes
                """,
                (anio,),
            )

            for numero_mes, total in cursor.fetchall():
                indice = int(numero_mes) - 1

                resultado[indice][clave] = int(
                    total or 0
                )

        for fila in resultado:
            fila["total"] = (
                fila["laboratorios"]
                + fila["practicas"]
            )

        return resultado

    except Exception as error:
        print(
            "\n"
            "========== ERROR EN REGISTROS POR MES =========="
        )
        print(error)
        print(
            "================================================\n"
        )

        return resultado

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Registros por carrera
# ============================================================

def obtener_registros_por_carrera(
    limite=10,
):
    """
    Devuelve la cantidad de registros por carrera, combinando
    laboratorios y prácticas.
    """

    conexion = None
    cursor = None

    acumulado = {}

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        for tabla in [
            TABLA_LABORATORIOS,
            TABLA_PRACTICAS,
        ]:
            if not _tabla_existe(cursor, tabla):
                continue

            columnas = _obtener_columnas(
                cursor,
                tabla,
            )

            columna_carrera = _seleccionar_primera_columna(
                columnas,
                [
                    "carrera",
                    "nombre_carrera",
                ],
            )

            if columna_carrera is None:
                continue

            cursor.execute(
                f"""
                SELECT
                    COALESCE(
                        NULLIF(
                            TRIM({columna_carrera}::text),
                            ''
                        ),
                        'Sin especificar'
                    ) AS carrera,
                    COUNT(*) AS total

                FROM {tabla}

                GROUP BY carrera
                """
            )

            for carrera, total in cursor.fetchall():
                clave = str(carrera).strip()

                acumulado[clave] = (
                    acumulado.get(clave, 0)
                    + int(total or 0)
                )

        ordenado = sorted(
            acumulado.items(),
            key=lambda elemento: elemento[1],
            reverse=True,
        )

        return [
            {
                "carrera": carrera,
                "total": total,
            }
            for carrera, total in ordenado[:int(limite)]
        ]

    except Exception as error:
        print(
            "\n"
            "========== ERROR EN REGISTROS POR CARRERA =========="
        )
        print(error)
        print(
            "====================================================\n"
        )

        return []

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Reactivos más utilizados
# ============================================================

def obtener_reactivos_mas_utilizados(
    limite=10,
):
    """
    Devuelve los reactivos con mayor cantidad acumulada.

    La función admite cantidades guardadas como:
        10
        10.5
        10,5
        10 ml
        5 gramos
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if not _tabla_existe(
            cursor,
            TABLA_REACTIVOS,
        ):
            return []

        columnas = _obtener_columnas(
            cursor,
            TABLA_REACTIVOS,
        )

        columna_nombre = _seleccionar_primera_columna(
            columnas,
            [
                "nombre",
                "reactivo",
                "nombre_reactivo",
                "descripcion",
            ],
        )

        columna_cantidad = _seleccionar_primera_columna(
            columnas,
            [
                "cantidad",
                "cantidad_utilizada",
                "cantidad_usada",
            ],
        )

        columna_unidad = _seleccionar_primera_columna(
            columnas,
            [
                "unidad",
                "unidad_medida",
                "medida",
            ],
        )

        if (
            columna_nombre is None
            or columna_cantidad is None
        ):
            return []

        columnas_select = [
            columna_nombre,
            columna_cantidad,
        ]

        if columna_unidad:
            columnas_select.append(
                columna_unidad
            )

        cursor.execute(
            f"""
            SELECT {", ".join(columnas_select)}
            FROM {TABLA_REACTIVOS}
            WHERE {columna_nombre} IS NOT NULL
              AND TRIM({columna_nombre}::text) <> ''
            """
        )

        reactivos = {}

        for fila in cursor.fetchall():
            nombre = str(
                fila[0]
            ).strip()

            cantidad = _convertir_decimal(
                fila[1]
            )

            unidad = ""

            if (
                columna_unidad
                and len(fila) >= 3
                and fila[2] is not None
            ):
                unidad = str(
                    fila[2]
                ).strip()

            clave = (
                nombre.lower(),
                unidad.lower(),
            )

            if clave not in reactivos:
                reactivos[clave] = {
                    "reactivo": nombre,
                    "cantidad": Decimal("0"),
                    "unidad": unidad,
                }

            reactivos[clave]["cantidad"] += cantidad

        ordenados = sorted(
            reactivos.values(),
            key=lambda elemento: elemento["cantidad"],
            reverse=True,
        )

        return [
            {
                "reactivo": elemento["reactivo"],
                "cantidad": _normalizar_numero(
                    elemento["cantidad"]
                ),
                "unidad": elemento["unidad"],
            }
            for elemento in ordenados[:int(limite)]
        ]

    except Exception as error:
        print(
            "\n"
            "========== ERROR EN REACTIVOS MÁS UTILIZADOS =========="
        )
        print(error)
        print(
            "=======================================================\n"
        )

        return []

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Años disponibles
# ============================================================

def obtener_anios_disponibles():
    """
    Devuelve todos los años disponibles en laboratorios y
    prácticas.
    """

    conexion = None
    cursor = None

    anios = set()

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        for tabla in [
            TABLA_LABORATORIOS,
            TABLA_PRACTICAS,
        ]:
            if not _tabla_existe(cursor, tabla):
                continue

            columnas = _obtener_columnas(
                cursor,
                tabla,
            )

            fecha_sql = _expresion_fecha(
                columnas,
            )

            if fecha_sql is None:
                continue

            cursor.execute(
                f"""
                SELECT DISTINCT
                    EXTRACT(
                        YEAR FROM {fecha_sql}::timestamp
                    )::integer AS anio

                FROM {tabla}

                WHERE {fecha_sql} IS NOT NULL

                ORDER BY anio DESC
                """
            )

            for fila in cursor.fetchall():
                if fila[0] is not None:
                    anios.add(
                        int(fila[0])
                    )

        if not anios:
            anios.add(
                date.today().year
            )

        return sorted(
            anios,
            reverse=True,
        )

    except Exception as error:
        print(
            "\n"
            "========== ERROR OBTENIENDO AÑOS =========="
        )
        print(error)
        print(
            "===========================================\n"
        )

        return [
            date.today().year
        ]

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Últimos registros
# ============================================================

def obtener_ultimos_registros(
    limite=10,
):
    """
    Devuelve los últimos registros combinados de laboratorios
    y prácticas.

    La estructura de cada elemento es:

    {
        "modulo": "Laboratorio",
        "id": 1,
        "codigo": "LAB-001",
        "fecha": datetime,
        "carrera": "Agropecuaria",
        "asignatura": "Química",
        "responsable": "Nombre docente",
        "pdf_url": "..."
    }
    """

    conexion = None
    cursor = None

    registros = []

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        configuraciones = [
            (
                TABLA_LABORATORIOS,
                "Laboratorio",
            ),
            (
                TABLA_PRACTICAS,
                "Práctica",
            ),
        ]

        for tabla, nombre_modulo in configuraciones:
            if not _tabla_existe(cursor, tabla):
                continue

            columnas = _obtener_columnas(
                cursor,
                tabla,
            )

            columna_id = _seleccionar_primera_columna(
                columnas,
                [
                    "id",
                    "laboratorio_id",
                    "practica_id",
                ],
            )

            columna_codigo = _seleccionar_primera_columna(
                columnas,
                [
                    "codigo",
                    "codigo_practica",
                    "codigo_laboratorio",
                ],
            )

            columna_carrera = _seleccionar_primera_columna(
                columnas,
                [
                    "carrera",
                    "nombre_carrera",
                ],
            )

            columna_asignatura = _seleccionar_primera_columna(
                columnas,
                [
                    "asignatura",
                    "materia",
                ],
            )

            columna_responsable = _seleccionar_primera_columna(
                columnas,
                [
                    "docente_responsable",
                    "docente",
                    "responsable",
                ],
            )

            columna_pdf = _seleccionar_primera_columna(
                columnas,
                [
                    "pdf_url",
                    "ruta_pdf",
                    "pdf",
                    "archivo_pdf",
                ],
            )

            fecha_sql = _expresion_fecha(
                columnas,
            )

            if (
                columna_id is None
                or fecha_sql is None
            ):
                continue

            select_codigo = (
                f"{columna_codigo}::text"
                if columna_codigo
                else "''::text"
            )

            select_carrera = (
                f"{columna_carrera}::text"
                if columna_carrera
                else "''::text"
            )

            select_asignatura = (
                f"{columna_asignatura}::text"
                if columna_asignatura
                else "''::text"
            )

            select_responsable = (
                f"{columna_responsable}::text"
                if columna_responsable
                else "''::text"
            )

            select_pdf = (
                f"{columna_pdf}::text"
                if columna_pdf
                else "''::text"
            )

            cursor.execute(
                f"""
                SELECT
                    {columna_id},
                    {select_codigo},
                    {fecha_sql} AS fecha,
                    {select_carrera},
                    {select_asignatura},
                    {select_responsable},
                    {select_pdf}

                FROM {tabla}

                WHERE {fecha_sql} IS NOT NULL

                ORDER BY
                    {fecha_sql} DESC,
                    {columna_id} DESC

                LIMIT %s
                """,
                (int(limite),),
            )

            for fila in cursor.fetchall():
                registros.append(
                    {
                        "modulo": nombre_modulo,
                        "id": fila[0],
                        "codigo": fila[1] or "",
                        "fecha": fila[2],
                        "carrera": fila[3] or "",
                        "asignatura": fila[4] or "",
                        "responsable": fila[5] or "",
                        "pdf_url": fila[6] or "",
                    }
                )

        registros.sort(
            key=lambda elemento: (
                elemento["fecha"]
                or date.min
            ),
            reverse=True,
        )

        return registros[:int(limite)]

    except Exception as error:
        print(
            "\n"
            "========== ERROR EN ÚLTIMOS REGISTROS =========="
        )
        print(error)
        print(
            "================================================\n"
        )

        return []

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Prueba directa del archivo
# ============================================================

if __name__ == "__main__":
    print(
        "\n========== RESUMEN GENERAL =========="
    )
    print(
        obtener_resumen_general()
    )

    print(
        "\n========== REGISTROS POR MES =========="
    )
    for registro in obtener_registros_por_mes():
        print(registro)

    print(
        "\n========== REGISTROS POR CARRERA =========="
    )
    for registro in obtener_registros_por_carrera():
        print(registro)

    print(
        "\n========== REACTIVOS MÁS UTILIZADOS =========="
    )
    for registro in obtener_reactivos_mas_utilizados():
        print(registro)

    print(
        "\n========== AÑOS DISPONIBLES =========="
    )
    print(
        obtener_anios_disponibles()
    )

    print(
        "\n========== ÚLTIMOS REGISTROS =========="
    )
    for registro in obtener_ultimos_registros():
        print(registro)