"""Wind source labels and the server data behind temporary dashboard previews."""

import json
import re
from unittest.mock import patch

import pytest

from app import db
from app.models import Property, Stand, User
from app.weather import _WEATHER_CACHE
from app.wind import WIND_DIRECTIONS, wind_from_name


@pytest.mark.parametrize('source, expected', [
    (0, 'North'), (22.5, 'North-northeast'), (45, 'Northeast'),
    (67.5, 'East-northeast'), (90, 'East'), (112.5, 'East-southeast'),
    (135, 'Southeast'), (157.5, 'South-southeast'), (180, 'South'),
    (202.5, 'South-southwest'), (225, 'Southwest'), (247.5, 'West-southwest'),
    (270, 'West'), (292.5, 'West-northwest'), (315, 'Northwest'),
    (337.5, 'North-northwest'), (360, 'North'),
    (11.24, 'North'), (11.25, 'North-northeast'),
    (348.74, 'North-northwest'), (348.75, 'North'),
])
def test_wind_name_converts_travel_heading_to_nearest_source(source, expected):
    assert wind_from_name((source + 180) % 360) == expected


def test_missing_wind_has_no_compass_name():
    assert wind_from_name(None) is None


@pytest.fixture
def wind_property(client):
    saved_cache = _WEATHER_CACHE.copy()
    _WEATHER_CACHE.clear()
    user = User(username='wind_owner')
    user.set_password('test-password')
    prop = Property(name='Wind Property', latitude=34, longitude=-81, owner=user)
    db.session.add_all([
        user, prop,
        Stand(name='North Stand', degree=0, property=prop, latitude=34.01, longitude=-81.01),
        Stand(name='South Stand', degree=180, property=prop, latitude=34.02, longitude=-81.02),
        Stand(name='Legacy Stand', degree=None, property=prop),
    ])
    db.session.commit()
    client.post('/login', data={'username': 'wind_owner', 'password': 'test-password'})
    yield prop
    _WEATHER_CACHE.clear()
    _WEATHER_CACHE.update(saved_cache)


def marker_data(response):
    match = re.search(rb'<script id="map-data" type="application/json">(.*?)</script>', response.data, re.S)
    return json.loads(match.group(1))


@pytest.mark.parametrize('wind_toward, label', [(135, b'northwest'), (270, b'east'), (22, b'south-southwest')])
def test_dashboard_labels_wind_source_and_offers_all_preview_directions(client, wind_property, wind_toward, label):
    with patch('app.weather.WeatherManager.get_wind_direction', return_value=wind_toward):
        response = client.get(f'/property/{wind_property.id}/stands')
    assert response.status_code == 200
    assert b'From the ' + label in response.data
    assert b'id="wind-override"' in response.data and b'/static/wind.js' in response.data
    for name in WIND_DIRECTIONS:
        assert name.encode() in response.data
    assert b'data-facing=""' in response.data  # Legacy stands have no invented heading.


def test_dashboard_uses_cached_actual_wind_despite_preview_query(client, wind_property):
    url = f'/property/{wind_property.id}/stands'
    with patch('app.weather.requests.get') as api:
        api.return_value.json.side_effect = [
            {'properties': {'observationStations': 'https://mock/stations'}},
            {'features': [{'properties': {'stationIdentifier': 'MOCK'}}]},
            {'properties': {'windDirection': {'value': 0}}},
        ]
        first = client.get(url)
        cached = _WEATHER_CACHE.copy()
        # Preview state is deliberately not accepted through URLs or persisted server-side.
        refreshed = client.get(url + '?wind_override=90')
    assert api.call_count == 3
    assert _WEATHER_CACHE == cached
    assert _WEATHER_CACHE[(34.0, -81.0)][0] == 180
    for response in (first, refreshed):
        assert b'From the north' in response.data
        assert b'data-actual-wind="180"' in response.data
        scores = {stand['name']: stand['score'] for stand in marker_data(response)['stands']}
        assert scores == {'North Stand': 100, 'South Stand': 0}
    assert Stand.query.count() == 3


def test_unavailable_weather_keeps_preview_controls_available(client, wind_property):
    wind_property.latitude = wind_property.longitude = None
    db.session.commit()
    with patch('app.weather.WeatherManager.get_wind_direction', return_value=None):
        response = client.get(f'/property/{wind_property.id}/stands')
    assert response.status_code == 200
    assert b'data-actual-wind=""' in response.data
    assert b'id="wind-override"' in response.data
    assert all(stand['score'] is None for stand in marker_data(response)['stands'])
    assert not _WEATHER_CACHE
