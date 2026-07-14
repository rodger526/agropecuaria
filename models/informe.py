from datetime import datetime


class InformeLaboratorio:

    def __init__(self):

        self.id = None

        self.codigo = ""

        self.titulo = ""

        self.autores = ""

        self.asignatura = ""

        self.carrera = ""

        self.semestre = ""

        self.docente = ""

        self.resumen = ""

        self.palabras_clave = ""

        self.introduccion = ""

        self.objetivo_general = ""

        self.objetivos_especificos = ""

        self.materiales_reactivos = ""

        self.procedimiento_experimental = ""

        self.resultados = ""

        self.discusion = ""

        self.conclusiones = ""

        self.recomendaciones = ""

        self.bibliografia = ""

        self.cuestionario = ""

        self.anexos = ""

        self.hoja_datos_url = ""

        self.pdf_url = ""

        self.fotos = []

        self.fecha_creacion = datetime.now()

    @classmethod
    def from_row(cls, fila):

        informe = cls()

        informe.id = fila[0]
        informe.codigo = fila[1]
        informe.titulo = fila[2]
        informe.autores = fila[3]
        informe.asignatura = fila[4]
        informe.carrera = fila[5]
        informe.semestre = fila[6]
        informe.docente = fila[7]
        informe.resumen = fila[8]
        informe.palabras_clave = fila[9]
        informe.introduccion = fila[10]
        informe.objetivo_general = fila[11]
        informe.objetivos_especificos = fila[12]
        informe.materiales_reactivos = fila[13]
        informe.procedimiento_experimental = fila[14]
        informe.resultados = fila[15]
        informe.discusion = fila[16]
        informe.conclusiones = fila[17]
        informe.recomendaciones = fila[18]
        informe.bibliografia = fila[19]
        informe.cuestionario = fila[20]
        informe.anexos = fila[21]
        informe.hoja_datos_url = fila[22]
        informe.pdf_url = fila[23]
        informe.fecha_creacion = fila[24]

        return informe

    def to_dict(self):

        return {

            "id": self.id,

            "codigo": self.codigo,

            "titulo": self.titulo,

            "autores": self.autores,

            "asignatura": self.asignatura,

            "carrera": self.carrera,

            "semestre": self.semestre,

            "docente": self.docente,

            "resumen": self.resumen,

            "palabras_clave": self.palabras_clave,

            "introduccion": self.introduccion,

            "objetivo_general": self.objetivo_general,

            "objetivos_especificos": self.objetivos_especificos,

            "materiales_reactivos": self.materiales_reactivos,

            "procedimiento_experimental": self.procedimiento_experimental,

            "resultados": self.resultados,

            "discusion": self.discusion,

            "conclusiones": self.conclusiones,

            "recomendaciones": self.recomendaciones,

            "bibliografia": self.bibliografia,

            "cuestionario": self.cuestionario,

            "anexos": self.anexos,

            "hoja_datos_url": self.hoja_datos_url,

            "pdf_url": self.pdf_url,

            "fecha_creacion": self.fecha_creacion,

            "fotos": self.fotos
        }