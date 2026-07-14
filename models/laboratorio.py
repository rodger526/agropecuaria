class Laboratorio:
    """
    Modelo principal para un registro de práctica de laboratorio.

    Mantiene compatibilidad con el constructor que ya utiliza
    views/nueva_laboratorio.py y agrega los datos correspondientes a:

        - Encargado del laboratorio.
        - Cargo del encargado.
        - Firma del encargado.
        - Firma del docente responsable.
    """

    def __init__(
        self,
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
        pdf_url=None,
        materiales=None,
        reactivos=None,
        estudiantes=None,
        encargado_laboratorio=None,
        cargo_encargado=None,
        firma_encargado_ruta=None,
        firma_docente_ruta=None,
        codigo_sesion=None,
        id=None,
    ):
        # ============================================================
        # Identificación
        # ============================================================

        self.id = id
        self.codigo = codigo
        self.codigo_sesion = codigo_sesion

        # ============================================================
        # Datos informativos
        # ============================================================

        self.laboratorio = laboratorio
        self.numero_estudiantes = numero_estudiantes
        self.asignatura = asignatura
        self.unidad_academica = unidad_academica
        self.semestre = semestre
        self.carrera = carrera

        self.hora_entrada = hora_entrada
        self.hora_salida = hora_salida

        self.institucion = institucion
        self.ciudad = ciudad
        self.docente_responsable = docente_responsable
        self.fecha_practica = fecha_practica

        # ============================================================
        # Datos académicos
        # ============================================================

        self.tema_practica = tema_practica
        self.subtema = subtema
        self.logro_aprendizaje = logro_aprendizaje

        # ============================================================
        # Desarrollo de la práctica
        # ============================================================

        self.objetivos = objetivos
        self.metodologia = metodologia
        self.resultados = resultados
        self.conclusiones = conclusiones
        self.observaciones = observaciones

        # ============================================================
        # Archivo PDF
        # ============================================================

        self.pdf_url = pdf_url

        # ============================================================
        # Relaciones
        # ============================================================

        self.materiales = materiales or []
        self.reactivos = reactivos or []
        self.estudiantes = estudiantes or []

        # ============================================================
        # Responsables y firmas
        # ============================================================

        self.encargado_laboratorio = encargado_laboratorio
        self.cargo_encargado = cargo_encargado
        self.firma_encargado_ruta = firma_encargado_ruta
        self.firma_docente_ruta = firma_docente_ruta

    @classmethod
    def from_row(
        cls,
        fila,
        materiales=None,
        reactivos=None,
        estudiantes=None,
    ):
        """
        Construye un objeto Laboratorio desde una fila de PostgreSQL.

        El SELECT recomendado debe devolver las columnas en este orden:

            0  id
            1  codigo
            2  laboratorio
            3  asignatura
            4  carrera
            5  semestre
            6  unidad_academica
            7  institucion
            8  ciudad
            9  docente_responsable
            10 fecha_practica
            11 hora_entrada
            12 hora_salida
            13 numero_estudiantes
            14 tema_practica
            15 subtema
            16 logro_aprendizaje
            17 objetivos
            18 metodologia
            19 resultados
            20 conclusiones
            21 observaciones
            22 pdf_url
            23 encargado_laboratorio
            24 cargo_encargado
            25 firma_encargado_ruta
            26 firma_docente_ruta
            27 codigo_sesion

        También acepta filas antiguas que todavía no incluyan
        las columnas nuevas.
        """

        if not fila:
            return None

        if len(fila) < 23:
            raise ValueError(
                "La fila del laboratorio no contiene todas las "
                "columnas mínimas requeridas."
            )

        # Columnas nuevas, compatibles con filas antiguas.
        encargado_laboratorio = (
            fila[23]
            if len(fila) > 23
            else None
        )

        cargo_encargado = (
            fila[24]
            if len(fila) > 24
            else None
        )

        firma_encargado_ruta = (
            fila[25]
            if len(fila) > 25
            else None
        )

        firma_docente_ruta = (
            fila[26]
            if len(fila) > 26
            else None
        )

        codigo_sesion = (
            fila[27]
            if len(fila) > 27
            else None
        )

        return cls(
            codigo=fila[1],
            laboratorio=fila[2],
            numero_estudiantes=fila[13],
            asignatura=fila[3],
            unidad_academica=fila[6],
            semestre=fila[5],
            carrera=fila[4],
            hora_entrada=fila[11],
            hora_salida=fila[12],
            institucion=fila[7],
            ciudad=fila[8],
            docente_responsable=fila[9],
            fecha_practica=fila[10],
            tema_practica=fila[14],
            subtema=fila[15],
            logro_aprendizaje=fila[16],
            objetivos=fila[17],
            metodologia=fila[18],
            resultados=fila[19],
            conclusiones=fila[20],
            observaciones=fila[21],
            pdf_url=fila[22],
            materiales=materiales,
            reactivos=reactivos,
            estudiantes=estudiantes,
            encargado_laboratorio=encargado_laboratorio,
            cargo_encargado=cargo_encargado,
            firma_encargado_ruta=firma_encargado_ruta,
            firma_docente_ruta=firma_docente_ruta,
            codigo_sesion=codigo_sesion,
            id=fila[0],
        )

    def to_dict(self):
        """
        Convierte el objeto Laboratorio en un diccionario.
        """

        return {
            "id": self.id,
            "codigo": self.codigo,
            "codigo_sesion": self.codigo_sesion,
            "laboratorio": self.laboratorio,
            "numero_estudiantes": self.numero_estudiantes,
            "asignatura": self.asignatura,
            "unidad_academica": self.unidad_academica,
            "semestre": self.semestre,
            "carrera": self.carrera,
            "hora_entrada": self.hora_entrada,
            "hora_salida": self.hora_salida,
            "institucion": self.institucion,
            "ciudad": self.ciudad,
            "docente_responsable": self.docente_responsable,
            "fecha_practica": self.fecha_practica,
            "tema_practica": self.tema_practica,
            "subtema": self.subtema,
            "logro_aprendizaje": self.logro_aprendizaje,
            "objetivos": self.objetivos,
            "metodologia": self.metodologia,
            "resultados": self.resultados,
            "conclusiones": self.conclusiones,
            "observaciones": self.observaciones,
            "pdf_url": self.pdf_url,
            "materiales": self.materiales,
            "reactivos": self.reactivos,
            "estudiantes": self.estudiantes,
            "encargado_laboratorio": self.encargado_laboratorio,
            "cargo_encargado": self.cargo_encargado,
            "firma_encargado_ruta": self.firma_encargado_ruta,
            "firma_docente_ruta": self.firma_docente_ruta,
        }