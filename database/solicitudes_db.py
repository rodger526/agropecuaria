from datetime import datetime

from database.conexion import obtener_conexion


# ─── Salas ─────────────────────────────────────────────────────────

def listar_salas():
    """
    Devuelve [(id, nombre, encargado_nombre, encargado_telefono,
                estado, ocupado_por, ocupado_desde), ...] de salas activas.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, encargado_nombre, encargado_telefono,
                   estado, ocupado_por, ocupado_desde
            FROM salas_laboratorio
            WHERE activo = true
            ORDER BY nombre
        """)
        return cursor.fetchall()
    except Exception as e:
        print(e)
        return []
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def obtener_sala(sala_id):
    """Devuelve (id, nombre, encargado_nombre, encargado_telefono, estado, ocupado_por, ocupado_desde) o None."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, encargado_nombre, encargado_telefono,
                   estado, ocupado_por, ocupado_desde
            FROM salas_laboratorio
            WHERE id = %s
        """, (sala_id,))
        return cursor.fetchone()
    except Exception as e:
        print(e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def marcar_ocupado(sala_id, ocupado_por):
    """Marca la sala como ocupada por 'ocupado_por' desde este momento."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE salas_laboratorio
            SET estado = 'ocupado',
                ocupado_por = %s,
                ocupado_desde = %s
            WHERE id = %s
        """, (ocupado_por, datetime.now(), sala_id))
        conexion.commit()
        return True
    except Exception as e:
        print("ERROR AL MARCAR SALA OCUPADA")
        print(e)
        if conexion:
            conexion.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def marcar_libre(sala_id):
    """Libera la sala: vuelve a estado 'libre' y limpia quién la ocupaba."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE salas_laboratorio
            SET estado = 'libre',
                ocupado_por = NULL,
                ocupado_desde = NULL
            WHERE id = %s
        """, (sala_id,))
        conexion.commit()
        return True
    except Exception as e:
        print("ERROR AL LIBERAR SALA")
        print(e)
        if conexion:
            conexion.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ─── Solicitudes ───────────────────────────────────────────────────

def crear_solicitud(sala_id, solicitante, motivo=""):
    """Crea una solicitud en estado 'pendiente' y devuelve su id, o None si falla."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO solicitudes_acceso (sala_id, solicitante, motivo)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (sala_id, solicitante, motivo))
        nuevo_id = cursor.fetchone()[0]
        conexion.commit()
        return nuevo_id
    except Exception as e:
        print("ERROR AL CREAR SOLICITUD")
        print(e)
        if conexion:
            conexion.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def guardar_whatsapp_message_id(id_solicitud, message_id):
    """Guarda el id del mensaje de WhatsApp enviado, útil para depurar."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE solicitudes_acceso
            SET whatsapp_message_id = %s
            WHERE id = %s
        """, (message_id, id_solicitud))
        conexion.commit()
        return True
    except Exception as e:
        print(e)
        if conexion:
            conexion.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def responder_solicitud(id_solicitud, estado):
    """
    estado debe ser 'aprobado' o 'rechazado'.
    Devuelve True si se actualizó correctamente (False si ya había sido
    respondida antes, para evitar procesar el mismo clic dos veces).

    NOTA: no cambia el estado de la sala aquí — eso lo hace el llamador
    (el webhook) después de confirmar que hubo actualización, usando
    los datos de sala_id/solicitante de la solicitud.
    """
    if estado not in ("aprobado", "rechazado"):
        return False

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE solicitudes_acceso
            SET estado = %s,
                respondido_en = %s
            WHERE id = %s AND estado = 'pendiente'
        """, (estado, datetime.now(), id_solicitud))
        actualizado = cursor.rowcount > 0
        conexion.commit()
        return actualizado
    except Exception as e:
        print("ERROR AL RESPONDER SOLICITUD")
        print(e)
        if conexion:
            conexion.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def obtener_solicitud(id_solicitud):
    """
    Devuelve (id, sala_id, solicitante, motivo, estado) o None si no existe.
    Usado por el webhook para saber a qué solicitud y sala corresponde un botón.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, sala_id, solicitante, motivo, estado
            FROM solicitudes_acceso
            WHERE id = %s
        """, (id_solicitud,))
        return cursor.fetchone()
    except Exception as e:
        print(e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def obtener_estado_solicitud(id_solicitud):
    """Devuelve el estado ('pendiente' | 'aprobado' | 'rechazado') o None."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT estado
            FROM solicitudes_acceso
            WHERE id = %s
        """, (id_solicitud,))
        fila = cursor.fetchone()
        return fila[0] if fila else None
    except Exception as e:
        print(e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()