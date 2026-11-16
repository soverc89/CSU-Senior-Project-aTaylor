"""Compass labels for meteorological (coming-from) wind directions."""

WIND_DIRECTIONS = (
    'North', 'North-northeast', 'Northeast', 'East-northeast',
    'East', 'East-southeast', 'Southeast', 'South-southeast',
    'South', 'South-southwest', 'Southwest', 'West-southwest',
    'West', 'West-northwest', 'Northwest', 'North-northwest',
)


def wind_from_name(wind_toward):
    """Describe the source of the app's travel-toward heading, or missing data."""
    if wind_toward is None:
        return None
    wind_from = (wind_toward + 180) % 360
    return WIND_DIRECTIONS[int((wind_from + 11.25) // 22.5) % 16]
