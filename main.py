from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --------------------------
# Modelos (Esquemas Pydantic)
# --------------------------

class BCVRates(BaseModel):
    usd: str
    eur: str

class ParallelRate(BaseModel):
    usd: str

class LastUpdate(BaseModel):
    date: str

class RatesResponse(BaseModel):
    bcv_usd: str
    bcv_eur: str
    paralelo_usd: str
    ultima_actualizacion: str
    estado: str

# --------------------------
# Servicios
# --------------------------

class ScraperService:
    @staticmethod
    def get_bcv_rates() -> BCVRates:
        """Obtiene las tasas del BCV"""
        url = "https://www.bcv.org.ve/"
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            dolar_div = soup.find("div", id="dolar")
            usd_value = dolar_div.find("strong").text.strip() if dolar_div else "No disponible"

            euro_div = soup.find("div", id="euro")
            eur_value = euro_div.find("strong").text.strip() if euro_div else "No disponible"

            return BCVRates(usd=usd_value, eur=eur_value)
        except Exception as err:
            print(f"Error BCV: {err}")
            return BCVRates(usd="Error", eur="Error")

    @staticmethod
    def get_parallel_rate() -> ParallelRate:
        """Obtiene la tasa del dólar paralelo"""
        url = "https://monitordolarvenezuela.com/"
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--remote-debugging-port=0")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = webdriver.ChromeService()
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get(url)
            # Espera a que cargue el contenido dinámico
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".font-bold"))
            )
            
            # Intenta con diferentes selectores
            selectors = [
                "//h3[contains(., 'Paralelo')]/following::p[contains(@class, 'font-bold')][1]",
                "//*[contains(text(), 'Dólar Paralelo')]/following::p[1]",
                "//p[contains(@class, 'font-bold') and contains(., 'Bs')]"
            ]
            
            for selector in selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    texto = element.text.strip()
                    if "Bs" in texto:
                        driver.quit()
                        return ParallelRate(usd=texto.replace("Bs", "").replace("=", "").strip())
                except:
                    continue
            
            # Si ningún selector funciona, toma screenshot para debug
            driver.save_screenshot("debug_screenshot.png")
            return ParallelRate(usd="No disponible")
            
        except Exception as e:
            print(f"Error Selenium: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            return ParallelRate(usd="Error")

    @staticmethod
    def get_last_update() -> LastUpdate:
        """Obtiene la última fecha de actualización"""
        url = "https://www.dolarvenezuela.com/"
        try:
            response = requests.get(url, verify=False) 
            soup = BeautifulSoup(response.text, "html.parser")
            h2_element = soup.find("h2", class_="h4 fecha text-center")
            date = h2_element.text.strip() if h2_element else "Fecha no disponible"
            return LastUpdate(date=date)
        except Exception as e:
            print(f"Error fecha: {e}")
            return LastUpdate(date="Error fecha")

# --------------------------
# Controladores
# --------------------------

class RatesController:
    def __init__(self, scraper_service: ScraperService = Depends()):
        self.scraper_service = scraper_service
    
    def get_rates(self) -> RatesResponse:
        try:
            bcv_rates = self.scraper_service.get_bcv_rates()
            parallel_rate = self.scraper_service.get_parallel_rate()
            last_update = self.scraper_service.get_last_update()
            
            return RatesResponse(
                bcv_usd=bcv_rates.usd,
                bcv_eur=bcv_rates.eur,
                paralelo_usd=parallel_rate.usd,
                ultima_actualizacion=last_update.date,
                estado="success"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

# --------------------------
# Configuración de FastAPI
# --------------------------

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencias
def get_scraper_service():
    return ScraperService()

def get_rates_controller(
    scraper_service: ScraperService = Depends(get_scraper_service)
) -> RatesController:
    return RatesController(scraper_service=scraper_service)

# Rutas
@app.get("/api/rates", response_model=RatesResponse)
async def get_rates(controller: RatesController = Depends(get_rates_controller)):
    return controller.get_rates()

@app.get("/health")
async def health_check():
    return {"status": "active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)