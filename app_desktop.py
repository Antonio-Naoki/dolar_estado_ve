import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup

# Función para obtener el valor del tipo de cambio USD del BCV
def get_dolar_bcv():
    url = "https://www.bcv.org.ve/"
    try:
        response = requests.get(url, verify=False)  # Deshabilita la verificación de certificados SSL
        response.raise_for_status()  # Verifica si la solicitud fue exitosa
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extraer el valor del USD del BCV
        usd_value = soup.find("div", {"id": "dolar"}).find("strong").text.strip()
        return {"USD": usd_value}
    except Exception as e:
        return {"USD": f"Error ({e})"}

# Función para obtener el valor del tipo de cambio paralelo
def get_dolar_paralelo():
    url = "https://www.dolarvenezuela.com/"
    try:
        response = requests.get(url, verify=False)  # Ignorar advertencia de SSL
        response.raise_for_status()  # Verificar que no hay errores HTTP
        soup = BeautifulSoup(response.text, "html.parser")

        # Buscar todos los elementos <h3> con clase "text-center"
        h3_elements = soup.find_all("h3", class_="text-center")
        if len(h3_elements) >= 2:  # Asegurarnos de que existe el segundo <h3>
            paralelo_value = h3_elements[1].text.strip()  # Extraer texto del segundo <h3>
            return {"USD_PARAL": paralelo_value}
        else:
            return {"USD_PARAL": "No disponible"}
    except Exception as e:
        return {"USD_PARAL": f"Error ({e})"}

# Función para extraer solo la fecha
def get_date():
    url = "https://www.dolarvenezuela.com/"
    try:
        response = requests.get(url, verify=False)  
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, "html.parser")

        h2_element = soup.find("h2", class_="h4 fecha text-center")
        date_text = h2_element.text.strip() if h2_element else "Fecha no encontrada"
        return date_text
    except Exception as e:
        return f"Error ({e})"

class DolarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dólar en Venezuela")
        self.root.geometry("800x600") 
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)

        header_frame = tk.Frame(self.root, bg="#34495e")
        header_frame.pack(fill="x")

        header_label = tk.Label(
            header_frame,
            text="💲 Dólar en Venezuela 💲",
            font=("Helvetica", 24, "bold"),
            fg="white",
            bg="#34495e",
            pady=15,
        )
        header_label.pack()

        main_frame = tk.Frame(self.root, bg="#2c3e50", pady=30)  
        main_frame.pack(fill="both", expand=True)

        # Fecha
        self.fecha_label = tk.Label(
            main_frame,
            text="Fecha: Cargando...",
            font=("Helvetica", 16, "italic"), 
            fg="white",
            bg="#2c3e50",
        )
        self.fecha_label.pack(pady=10)

        self.bcv_frame = self.create_card(main_frame, "Dólar BCV", "Cargando...")
        self.bcv_frame.pack(pady=15)

        self.paralelo_frame = self.create_card(main_frame, "Dólar Paralelo", "Cargando...")
        self.paralelo_frame.pack(pady=15)

        update_button = ttk.Button(
            main_frame,
            text="Actualizar Tasas",
            command=self.update_rates,
            style="Custom.TButton",
        )
        update_button.pack(pady=30) 

        # Estilo personalizado
        style = ttk.Style()
        style.configure("Custom.TButton", font=("Helvetica", 14), padding=10)

        self.update_rates()

    def create_card(self, parent, title, content):
        """Crea un marco estilizado para mostrar una tarjeta de información."""
        frame = tk.Frame(parent, bg="#34495e", padx=30, pady=30)
        title_label = tk.Label(
            frame,
            text=title,
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#34495e",
        )
        title_label.pack(anchor="w")

        content_label = tk.Label(
            frame,
            text=content,
            font=("Helvetica", 16), 
            fg="#1abc9c",
            bg="#34495e",
        )
        content_label.pack(anchor="w")

        return frame

    def update_rates(self):
        """Actualiza las tasas de cambio y la fecha."""
        try:
            fecha = get_date()
            self.fecha_label.config(text=f"Fecha: {fecha}")

            dolar_bcv = get_dolar_bcv()
            bcv_label = self.bcv_frame.winfo_children()[1]
            bcv_label.config(text=dolar_bcv["USD"])

            dolar_paral = get_dolar_paralelo()
            paralelo_label = self.paralelo_frame.winfo_children()[1]
            paralelo_label.config(text=dolar_paral["USD_PARAL"])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron actualizar las tasas: {e}")


# aplicacion 
if __name__ == "__main__":
    root = tk.Tk()
    app = DolarApp(root)
    root.mainloop()
