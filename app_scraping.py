import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_tasas_bcv():
    url = "https://www.bcv.org.ve/"
    try:
        # Realizar la solicitud HTTP sin verificar el certificado SSL
        response = requests.get(url, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        dolar_div = soup.find("div", id="dolar")
        usd_value = dolar_div.find("strong").text.strip() if dolar_div else "No disponible"

        euro_div = soup.find("div", id="euro")
        eur_value = euro_div.find("strong").text.strip() if euro_div else "No disponible"

        return {"USD": usd_value, "EUR": eur_value}
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
    except Exception as err:
        print(f"Otro error: {err}")
    return {"USD": "No disponible", "EUR": "No disponible"}

def get_dolar_paralelo():
    url = "https://monitordolarvenezuela.com/"
    
    # Configuración de opciones para Chrome en modo headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        xpath = "//h3[contains(., 'Dólar Paralelo')]/following::p[contains(@class, 'font-bold')][1]"
        dolar_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        
        texto = dolar_element.text.strip()
        driver.quit()
        
        if "Bs = " in texto:
            paralelo_value = texto.replace("Bs = ", "").strip()
            return {"USD_PARAL": paralelo_value}
        else:
            return {"USD_PARAL": "No disponible"}
    except Exception as e:
        print(f"Error con Selenium: {e}")
        driver.quit()
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

if __name__ == "__main__":
    tasas = get_tasas_bcv()
    # bcv_data = get_tasas_bcv()
    paralelo_data = get_dolar_paralelo()
    # paralelo_data = get_dolar_paralelo()
    date = get_date()

    print("Resultados obtenidos:")
    print(f"BCV (EUR): {tasas['EUR']}")
    print(f"BCV (USD): {tasas['USD']}")
    print(f"Paralelo USD: {paralelo_data['USD_PARAL']}")
    print(f"Fecha: {date}")
