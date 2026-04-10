import requests
import time
from flask import current_app

# Simple module-level cache: {(lat, lng): (wind_direction, timestamp)}
_WEATHER_CACHE = {}
# Cache duration in seconds (1 hour)
CACHE_DURATION = 3600

class WeatherManager:
    """
    Utility class for interacting with the US National Weather Service API.
    """
    def __init__(self):
        # The NWS requires a User-Agent identifying the app/developer
        self.headers = {"User-Agent": "HuntingStandApp/1.0 (andrew.taylor2525@gmail.com)"}

    def get_wind_direction(self, lat, lng):
        """
        Fetches the current wind direction (in degrees) for the given lat/long coordinates.
        Uses the free weather.gov API. Returns None if there is an error or no data.
        """
        if lat is None or lng is None:
            return None

        # Check Cache
        cache_key = (lat, lng)
        if cache_key in _WEATHER_CACHE:
            cached_degree, timestamp = _WEATHER_CACHE[cache_key]
            if time.time() - timestamp < CACHE_DURATION:
                return cached_degree

        # Step 1: Get the metadata for this specific coordinate point point
        points_url = f"https://api.weather.gov/points/{lat},{lng}"
        try:
            point_response = requests.get(points_url, headers=self.headers, timeout=5)
            point_response.raise_for_status()
            point_data = point_response.json()
            
            # Step 2: Get the observation stations for this grid area
            stations_url = point_data['properties']['observationStations']
            stations_response = requests.get(stations_url, headers=self.headers, timeout=5)
            stations_response.raise_for_status()
            stations_data = stations_response.json()
            
            # We want the nearest station, which is the first one in the features list
            if not stations_data.get('features'):
                return None
                
            nearest_station_id = stations_data['features'][0]['properties']['stationIdentifier']
            
            # Step 3: Get the latest observation from that station
            obs_url = f"https://api.weather.gov/stations/{nearest_station_id}/observations/latest"
            obs_response = requests.get(obs_url, headers=self.headers, timeout=5)
            obs_response.raise_for_status()
            obs_data = obs_response.json()
            
            wind_direction = obs_data['properties']['windDirection']['value']
            
            # Some stations might report wind direction as None if it's perfectly calm
            if wind_direction is not None:
                wind_deg = int(wind_direction)
                # Save to cache
                _WEATHER_CACHE[cache_key] = (wind_deg, time.time())
                return wind_deg
            return None
            
        except requests.exceptions.RequestException as e:
            # If the API fails, times out, or returns a 500, we simply log it and return None 
            # so the app doesn't crash. The UI will just say "Weather Unavailable".
            print(f"Weather API Error for {lat},{lng}: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            print(f"Weather Data Parsing Error for {lat},{lng}: {e}")
            return None
