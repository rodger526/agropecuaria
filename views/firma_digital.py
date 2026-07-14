import os
from pathlib import Path

import customtkinter as ctk
from PIL import ImageGrab
from tkinter import messagebox


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_FIRMAS = BASE_DIR / "firma" / "firmas"


class VentanaFirma(ctk.CTkToplevel):
    """
    Ventana para capturar una firma con el mouse.

    callback(ruta) se ejecuta después de guardar correctamente
    la imagen.
    """

    def __init__(
        self,
        master,
        callback,
        nombre_archivo="firma_docente.png",
    ):
        super().__init__(master)

        self.callback = callback
        self.nombre_archivo = os.path.basename(
            nombre_archivo or "firma_docente.png"
        )

        self._ultimo_x = None
        self._ultimo_y = None
        self._tiene_trazo = False

        self.title("Firma Digital")
        self.geometry("700x360")
        self.minsize(600, 320)
        self.configure(fg_color="#0F1923")

        ctk.CTkLabel(
            self,
            text="FIRMA DIGITAL",
            font=("Consolas", 15, "bold"),
            text_color="#E8EDF2",
        ).pack(pady=(14, 4))

        ctk.CTkLabel(
            self,
            text=(
                "Mantén presionado el botón izquierdo y firma "
                "dentro del área blanca."
            ),
            font=("Consolas", 10),
            text_color="#8A9BB0",
        ).pack(pady=(0, 10))

        self.canvas = ctk.CTkCanvas(
            self,
            bg="white",
            highlightthickness=1,
            highlightbackground="#4CAF7D",
            cursor="pencil",
        )
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 12),
        )

        self.canvas.bind(
            "<Button-1>",
            self._iniciar_trazo,
        )
        self.canvas.bind(
            "<B1-Motion>",
            self.dibujar,
        )
        self.canvas.bind(
            "<ButtonRelease-1>",
            self._terminar_trazo,
        )

        botones = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        botones.pack(
            fill="x",
            padx=20,
            pady=(0, 14),
        )

        ctk.CTkButton(
            botones,
            text="Limpiar",
            fg_color="#1E2D42",
            hover_color="#243348",
            text_color="#E8EDF2",
            command=self.limpiar,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 6),
        )

        ctk.CTkButton(
            botones,
            text="Guardar Firma",
            fg_color="#4CAF7D",
            hover_color="#3A9166",
            text_color="#0F1923",
            command=self.guardar,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(6, 0),
        )

        self.transient(master)
        self.grab_set()
        self.focus_force()

    def _iniciar_trazo(self, event):
        self._ultimo_x = event.x
        self._ultimo_y = event.y

    def dibujar(self, event):
        if self._ultimo_x is None or self._ultimo_y is None:
            self._ultimo_x = event.x
            self._ultimo_y = event.y
            return

        self.canvas.create_line(
            self._ultimo_x,
            self._ultimo_y,
            event.x,
            event.y,
            fill="black",
            width=3,
            capstyle="round",
            smooth=True,
        )

        self._ultimo_x = event.x
        self._ultimo_y = event.y
        self._tiene_trazo = True

    def _terminar_trazo(self, _event):
        self._ultimo_x = None
        self._ultimo_y = None

    def limpiar(self):
        self.canvas.delete("all")
        self._ultimo_x = None
        self._ultimo_y = None
        self._tiene_trazo = False

    def guardar(self):
        if not self._tiene_trazo:
            messagebox.showwarning(
                "Firma vacía",
                "Debe dibujar una firma antes de guardarla.",
                parent=self,
            )
            return

        try:
            RUTA_FIRMAS.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.update_idletasks()
            self.update()

            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()

            imagen = ImageGrab.grab(
                bbox=(x, y, x1, y1)
            )

            ruta = RUTA_FIRMAS / self.nombre_archivo

            imagen.save(
                ruta,
                format="PNG",
            )

            if callable(self.callback):
                self.callback(str(ruta))

            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No fue posible guardar la firma:\n\n{e}",
                parent=self,
            )