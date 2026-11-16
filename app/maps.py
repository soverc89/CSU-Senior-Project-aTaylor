"""Map presentation data. Stand positions never change the weather lookup location."""

import math
from flask import url_for


def valid_coordinates(latitude, longitude):
    return (
        latitude is not None and longitude is not None
        and math.isfinite(latitude) and math.isfinite(longitude)
        and -90 <= latitude <= 90 and -180 <= longitude <= 180
    )


def map_data(prop, stands, wind_degree=None, csrf_token=None):
    property_location = valid_coordinates(prop.latitude, prop.longitude)
    markers = []
    for stand in stands:
        if not valid_coordinates(stand.latitude, stand.longitude):
            continue
        markers.append({
            'id': stand.id, 'name': stand.name, 'degree': stand.degree,
            'latitude': stand.latitude, 'longitude': stand.longitude,
            'score': stand.current_score(wind_degree),
            'edit_url': url_for('main.edit_stand', property_id=prop.id, stand_id=stand.id),
            'delete_url': url_for('main.delete_stand', property_id=prop.id, stand_id=stand.id),
        })
    return {
        'property': {
            'name': prop.name,
            'latitude': prop.latitude if property_location else None,
            'longitude': prop.longitude if property_location else None,
        },
        'stands': markers,
        'new_stand_url': url_for('main.new_stand', property_id=prop.id),
        'csrf_token': csrf_token,
    }
