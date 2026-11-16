import pytest
from unittest.mock import patch
from app.weather import WeatherManager, _WEATHER_CACHE
from app import db
from app.models import User, Property, Stand
import time

@pytest.mark.parametrize('wind_from, expected_toward', [
    (0, 180), (90, 270), (180, 0), (270, 90), (360, 180), (None, None),
])
def test_weather_api_success(wind_from, expected_toward):
    """NWS source headings become travel headings, including wraparound and calm wind."""
    # Mock requests.get to return a mock response for weather.gov points, stations, and observations
    with patch('app.weather.requests.get') as mock_get:
        # We need to simulate three sequential calls: points, stations, observation
        mock_get.return_value.json.side_effect = [
            # 1. points data
            {'properties': {'observationStations': 'http://mock-stations'}},
            # 2. stations data
            {'features': [{'properties': {'stationIdentifier': 'MOCK1'}}]},
            # 3. observation data
            {'properties': {'windDirection': {'value': wind_from}}}
        ]
        
        wm = WeatherManager()
        # Clear cache for isolated test
        _WEATHER_CACHE.clear()
        
        direction = wm.get_wind_direction(38.0, -77.0)
        assert direction == expected_toward
        assert mock_get.call_count == 3

def test_weather_api_error_handling():
    """Integration Case 2: Weather API Error Handling"""
    with patch('app.weather.requests.get') as mock_get:
        import requests
        # Simulate a timeout or 500 error
        mock_get.side_effect = requests.exceptions.Timeout("API Timeout")
        
        wm = WeatherManager()
        _WEATHER_CACHE.clear()
        
        direction = wm.get_wind_direction(38.0, -77.0)
        # Should handle gracefully and return None instead of crashing
        assert direction is None

def test_weather_data_caching():
    """Integration Case 4: Weather Data Caching"""
    with patch('app.weather.requests.get') as mock_get:
        # Mock successful call
        mock_get.return_value.json.side_effect = [
            {'properties': {'observationStations': 'http://mock-stations'}},
            {'features': [{'properties': {'stationIdentifier': 'MOCK1'}}]},
            {'properties': {'windDirection': {'value': 180}}}
        ]
        
        wm = WeatherManager()
        _WEATHER_CACHE.clear()
        
        # First call makes 3 requests
        direction1 = wm.get_wind_direction(38.0, -77.0)
        assert direction1 == 0
        assert mock_get.call_count == 3
        
        # Second call within same location should use cache (0 additional requests)
        direction2 = wm.get_wind_direction(38.0, -77.0)
        assert direction2 == 0
        assert mock_get.call_count == 3

def test_grader_refresh(client, init_database):
    """Integration Case 6: Grader Refresh & Regression Core Flow"""
    # Create User, Property, and Stand
    user = User(username="integ_user")
    user.set_password("pw")
    db.session.add(user)
    db.session.commit()
    
    prop = Property(name="Integ Prop", latitude=38.0, longitude=-77.0, user_id=user.id)
    db.session.add(prop)
    db.session.commit()
    
    stand = Stand(name="Integ Stand", degree=180, property_id=prop.id)
    db.session.add(stand)
    db.session.commit()
    
    # Login
    client.post('/login', data={'username': 'integ_user', 'password': 'pw'})
    
    # Wind from south travels north, opposite the stand's south-facing heading: 100%.
    with patch('app.weather.requests.get') as mock_get:
        mock_get.return_value.json.side_effect = [
            {'properties': {'observationStations': 'http://mock-stations'}},
            {'features': [{'properties': {'stationIdentifier': 'MOCK1'}}]},
            {'properties': {'windDirection': {'value': 180}}}
        ]
        _WEATHER_CACHE.clear()
        
        response = client.get(f'/property/{prop.id}/stands')
        assert response.status_code == 200
        assert b"Integ Stand" in response.data
        assert b"100%" in response.data

def test_regression_end_to_end(client, init_database):
    """Regression Test: End-to-End Property and Stand Creation"""
    # Register -> Login -> Create Property -> Create Stand
    
    # 1. Register
    client.post('/register', data={'username': 'reg_user', 'password': 'pw', 'confirm_password': 'pw'})
    
    # 2. Login
    client.post('/login', data={'username': 'reg_user', 'password': 'pw'})
    
    # 3. Create Property
    client.post('/property/new', data={'name': 'New Prop', 'latitude': '30.0', 'longitude': '-80.0'}, follow_redirects=True)
    prop = Property.query.filter_by(name="New Prop").first()
    assert prop is not None
    
    # 4. Create Stand
    client.post(f'/property/{prop.id}/stand/new', data={'name': 'New Stand', 'degree': '90'}, follow_redirects=True)
    stand = Stand.query.filter_by(name="New Stand").first()
    assert stand is not None
    assert stand.property_id == prop.id
