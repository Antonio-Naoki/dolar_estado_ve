from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_dolar_bcv():
    url = "https://www.bcv.org.ve/"
    try:
        response = requests.get(url, verify=False) 
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, "html.parser")
        
        usd_value = soup.find("div", {"id": "dolar"}).find("strong").text.strip()
        
        return {"USD": usd_value}
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return {"USD": "No disponible"}

def get_dolar_paralelo():
    url = "https://www.dolarvenezuela.com/"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        h3_elements = soup.find_all("h3", class_="text-center")
        if len(h3_elements) >= 2: 
            paralelo_value = h3_elements[1].text.strip()
            return {"USD_PARAL": paralelo_value}
        else:
            return {"USD_PARAL": "No disponible"}
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return {"USD_PARAL": "Error"}
    except Exception as e:
        print(f"Otro error ocurrió: {e}")
        return {"USD_PARAL": "Error"}

def get_date():
    url = "https://www.dolarvenezuela.com/"
    try:
        response = requests.get(url, verify=False) 
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        h2_element = soup.find("h2", class_="h4 fecha text-center")
        date_text = h2_element.text.strip() if h2_element else "Fecha no encontrada"
        return date_text
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return "Error en la fecha"
    except Exception as e:
        print(f"Otro error ocurrió: {e}")
        return "Error en la fecha"

@app.route("/")
def index():
    data = {
        "fecha": get_date(),
        "dolar_bcv": get_dolar_bcv(),
        "dolar_paral": get_dolar_paralelo(),
    }
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
