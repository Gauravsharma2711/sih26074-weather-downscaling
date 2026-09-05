import math
from typing import Union
import numpy as np
import pandas as pd

EARTH_RADIUS_KM = 6371.0


def haversine_distance(
    lat1: Union[float, np.ndarray, pd.Series],
    lon1: Union[float, np.ndarray, pd.Series],
    lat2: Union[float, np.ndarray, pd.Series],
    lon2: Union[float, np.ndarray, pd.Series],
    radius_km: float = EARTH_RADIUS_KM
) -> Union[float, np.ndarray, pd.Series]:
    """
    Calculate the great circle distance between two points on the earth
    (specified in decimal degrees) using the Haversine formula.

    Supports both scalar floats and vector inputs (NumPy arrays / Pandas Series).

    Parameters:
    - lat1, lon1: Coordinates of first point(s) (Panchayat latitude and longitude in degrees)
    - lat2, lon2: Coordinates of second point(s) (Station latitude and longitude in degrees)
    - radius_km: Mean radius of the Earth in km (default: 6371.0 km)

    Returns:
    - Distance in kilometers (rounded to 4 decimal places for floats, or full series)
    """
    if isinstance(lat1, (pd.Series, np.ndarray)) or isinstance(lat2, (pd.Series, np.ndarray)):
        # Vectorized implementation
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)

        a = (
            np.sin(delta_phi / 2.0) ** 2
            + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * np.arcsin(np.clip(np.sqrt(a), 0.0, 1.0))
        return radius_km * c

    # Scalar implementation
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    # Clip to avoid domain errors
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(radius_km * c, 4)
