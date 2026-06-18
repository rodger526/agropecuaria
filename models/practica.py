from datetime import datetime


class Practica:

    def __init__(
        self,

        # DATOS INFORMATIVOS
        carrera,
        semestre,
        asignatura,
        unidad_silabo,
        tipo_practica,
        ingeniero_revisor,
        lugar_ejecucion,
        semana_planificada,

        # DATOS ACADÉMICOS
        tema_practica,
        resultado_aprendizaje,
        articulacion_curricular,

        # PLANIFICACIÓN
        objetivo_general,
        materiales_equipos,
        descripcion_actividad,
        evidencias,
        
    ):

        # Fecha generada automáticamente (reemplaza al código)
        self.fecha_creacion = datetime.now()

        self.carrera = carrera
        self.semestre = semestre
        self.asignatura = asignatura
        self.unidad_silabo = unidad_silabo
        self.tipo_practica = tipo_practica

        self.ingeniero_revisor = ingeniero_revisor

        self.lugar_ejecucion = lugar_ejecucion
        self.semana_planificada = semana_planificada

        self.tema_practica = tema_practica
        self.resultado_aprendizaje = resultado_aprendizaje
        self.articulacion_curricular = articulacion_curricular

        self.objetivo_general = objetivo_general
        self.materiales_equipos = materiales_equipos
        self.descripcion_actividad = descripcion_actividad

        self.evidencias = evidencias

        self.pdf_url = None
        self.firma_docente = None
        self.firma_comision = None
