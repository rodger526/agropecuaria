class Laboratorio:
    """
    Modelo de datos para la tabla `laboratorios`.

    Atributos que corresponden 1 a 1 con columnas de la tabla SQL,
    más tres listas (materiales, reactivos, estudiantes) que se
    guardan en tablas relacionadas (laboratorio_materiales,
    laboratorio_reactivos, laboratorio_estudiantes).
    """

    def __init__(
        self,

        codigo,

        # ==========================
        # DATOS INFORMATIVOS
        # ==========================
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

        # ==========================
        # DATOS ACADÉMICOS
        # ==========================
        tema_practica,
        subtema,
        logro_aprendizaje,

        # ==========================
        # PLANIFICACIÓN
        # ==========================
        objetivos,
        metodologia,
        resultados,
        conclusiones,
        observaciones,

        # ==========================
        # TABLAS RELACIONADAS
        # ==========================
        materiales=None,
        reactivos=None,
        estudiantes=None,

        # ==========================
        # METADATOS
        # ==========================
        id=None,
        pdf_url=None,
    ):
        self.id = id
        self.codigo = codigo

        # DATOS INFORMATIVOS
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

        # DATOS ACADÉMICOS
        self.tema_practica = tema_practica
        self.subtema = subtema
        self.logro_aprendizaje = logro_aprendizaje

        # PLANIFICACIÓN
        self.objetivos = objetivos
        self.metodologia = metodologia
        self.resultados = resultados
        self.conclusiones = conclusiones
        self.observaciones = observaciones

        # TABLAS RELACIONADAS (listas de dicts, ej:
        # [{"nombre": "Vaso de precipitado", "cantidad": 5}, ...])
        self.materiales = materiales if materiales is not None else []
        self.reactivos = reactivos if reactivos is not None else []
        self.estudiantes = estudiantes if estudiantes is not None else []

        self.pdf_url = pdf_url

    def to_dict(self):
        """Convierte el objeto a diccionario, útil para guardar en BD o generar el PDF."""
        return {
            "id": self.id,
            "codigo": self.codigo,
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
            "materiales": self.materiales,
            "reactivos": self.reactivos,
            "estudiantes": self.estudiantes,
            "pdf_url": self.pdf_url,
        }

    @classmethod
    def from_row(cls, row, materiales=None, reactivos=None, estudiantes=None):
        """
        Construye un Laboratorio a partir de una fila de la tabla `laboratorios`.
        `row` debe ser una tupla/lista en el mismo orden de las columnas SQL:
        (id, codigo, laboratorio, asignatura, carrera, semestre,
         unidad_academica, institucion, ciudad, docente_responsable,
         fecha_practica, hora_entrada, hora_salida, numero_estudiantes,
         tema_practica, subtema, logro_aprendizaje, objetivos,
         metodologia, resultados, conclusiones, observaciones, pdf_url, created_at)
        """
        return cls(
            id=row[0],
            codigo=row[1],
            laboratorio=row[2],
            asignatura=row[3],
            carrera=row[4],
            semestre=row[5],
            unidad_academica=row[6],
            institucion=row[7],
            ciudad=row[8],
            docente_responsable=row[9],
            fecha_practica=row[10],
            hora_entrada=row[11],
            hora_salida=row[12],
            numero_estudiantes=row[13],
            tema_practica=row[14],
            subtema=row[15],
            logro_aprendizaje=row[16],
            objetivos=row[17],
            metodologia=row[18],
            resultados=row[19],
            conclusiones=row[20],
            observaciones=row[21],
            pdf_url=row[22],
            materiales=materiales,
            reactivos=reactivos,
            estudiantes=estudiantes,
        )