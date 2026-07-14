from database.conexion import obtener_conexion


def actualizar_pdf_laboratorio(id_laboratorio, pdf_url):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE laboratorios
        SET pdf_url = %s
        WHERE id = %s
    """, (pdf_url, id_laboratorio))

    conexion.commit()

    cursor.close()
    conexion.close()