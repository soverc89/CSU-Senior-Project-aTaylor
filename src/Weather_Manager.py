#Weather Manager
import requests

class Weather_Manager:

    def __init__(self):
        #not sure yet
        self.weather = "weather"

    def get_weather(self):
        headers = {"User-Agent": "myweatherapp/1.0 (andrew.taylor2525@gmail.com)"}
        
        response = requests.get("https://api.weather.gov/stations/D8485/observations/latest?require_qc=false", headers=headers)
        data = response.json()
        #forecast_url = data['properties']['forecastGridData']
        #forecast = requests.get(forecast_url, headers=headers).json()

        wind = data['properties']['windDirection']['value']

        return wind

