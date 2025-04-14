from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RatesResponse(BaseModel):
    bcv_usd: str
    bcv_eur: str
    paralelo_usd: str
    ultima_actualizacion: str
    estado: str

def get_tasas_bcv():
    # (Misma implementación original)
    url = "https://www.bcv.org.ve/"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        dolar_div = soup.find("div", id="dolar")
        usd_value = dolar_div.find("strong").text.strip() if dolar_div else "No disponible"

        euro_div = soup.find("div", id="euro")
        eur_value = euro_div.find("strong").text.strip() if euro_div else "No disponible"

        return {"USD": usd_value, "EUR": eur_value}
    except Exception as err:
        print(f"Error BCV: {err}")
        return {"USD": "Error", "EUR": "Error"}

def get_dolar_paralelo():
    # (Misma implementación original)
    url = "https://monitordolarvenezuela.com/"
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
            return {"USD_PARAL": texto.replace("Bs = ", "").strip()}
        return {"USD_PARAL": "No disponible"}
    except Exception as e:
        print(f"Error Selenium: {e}")
        driver.quit()
        return {"USD_PARAL": "Error"}

def get_date():
    # (Misma implementación original)
    url = "https://www.dolarvenezuela.com/"
    try:
        response = requests.get(url, verify=False) 
        soup = BeautifulSoup(response.text, "html.parser")
        h2_element = soup.find("h2", class_="h4 fecha text-center")
        return h2_element.text.strip() if h2_element else "Fecha no disponible"
    except Exception as e:
        print(f"Error fecha: {e}")
        return "Error fecha"

@app.get("/api/rates", response_model=RatesResponse)
async def get_rates():
    try:
        tasas = get_tasas_bcv()
        paralelo = get_dolar_paralelo()
        fecha = get_date()
        
        return {
            "bcv_usd": tasas["USD"],
            "bcv_eur": tasas["EUR"],
            "paralelo_usd": paralelo["USD_PARAL"],
            "ultima_actualizacion": fecha,
            "estado": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)