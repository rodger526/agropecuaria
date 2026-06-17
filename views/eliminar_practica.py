from tkinter import messagebox

from database.eliminar import eliminar_practica

def eliminar(id_practica):

    respuesta = messagebox.askyesno(
        "Eliminar",
        "¿Desea eliminar el registro?"
    )

    if respuesta:

        eliminar_practica(id_practica)

        messagebox.showinfo(
            "Correcto",
            "Registro eliminado"
        )
