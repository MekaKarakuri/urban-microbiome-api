import aiohttp
import os
from typing import Dict, Any
from datetime import datetime

class ExternalAPIsManager:
    def __init__(self):
        self.api_keys = {
            'openweather': os.getenv('OPENWEATHER_API_KEY'),
            'airquality': os.getenv('AIRQUALITY_API_KEY'),
            'ncbi': os.getenv('NCBI_API_KEY')
        }
        
    async def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        url = f"https://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_keys['openweather']
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def get_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/"
        params = {
            'token': self.api_keys['airquality']
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def get_microbiome_data(self, taxa: str) -> Dict[str, Any]:
        url = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/taxonomy/taxon"
        params = {
            'api_key': self.api_keys['ncbi'],
            'taxon': taxa
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()