from database.conexion import obtener_conexion

try:

    conexion = obtener_conexion()

    print("CONEXIÓN EXITOSA")

    conexion.close()

except Exception as e:

    print("ERROR:")
    print(e)