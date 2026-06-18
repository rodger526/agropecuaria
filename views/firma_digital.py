import customtkinter as ctk
from PIL import ImageGrab

class VentanaFirma(ctk.CTkToplevel):

    def __init__(self, master, callback):

        super().__init__(master)

        self.callback = callback

        self.title("Firma Digital")

        self.geometry("700x300")

        self.canvas = ctk.CTkCanvas(
            self,
            bg="white"
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.dibujar
        )

        ctk.CTkButton(
            self,
            text="Guardar Firma",
            command=self.guardar
        ).pack(
            pady=10
        )

    def dibujar(self, event):

        x = event.x
        y = event.y

        self.canvas.create_oval(
            x,
            y,
            x + 2,
            y + 2,
            fill="black",
            outline="black"
        )

    def guardar(self):

        x = self.winfo_rootx() + self.canvas.winfo_x()
        y = self.winfo_rooty() + self.canvas.winfo_y()

        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        imagen = ImageGrab.grab(
            (x, y, x1, y1)
        )

        ruta = "firmas/firma_docente.png"

        imagen.save(ruta)

        self.callback(ruta)

        self.destroy()