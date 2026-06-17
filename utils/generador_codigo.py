from datetime import datetime

def generar_codigo():

    fecha = datetime.now()

    return f"PRA-{fecha.strftime('%Y%m%d%H%M%S')}"