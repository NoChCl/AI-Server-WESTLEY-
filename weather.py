import requests, os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv("weatherKey")


HEADERS = {
    "User-Agent": "WESTLEY/1.0 (local assistant)"
}


print(key)
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"



def getCoordinates(locationString):
    """
    locationString example:
    'Lebanon, NH, US'
    """

    params = {
        "q": locationString,
        "format": "json",
        "limit": 1
    }

    r = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params=params,
        headers=HEADERS,
        timeout=10
    )
    r.raise_for_status()
    data = r.json()

    if not data:
        raise ValueError("Location not found")

    return float(data[0]["lat"]), float(data[0]["lon"])


def getWeather(locationString):
    lat, lon = getCoordinates(locationString)

    params = {
        "lat": lat,
        "lon": lon,
        "appid": key,
        "units": "imperial"
    }

    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    data = r.json()
    
    return data
    # Normalize output (important!)
    return {
        "location": locationString,
        "temp": data["main"]["temp"],
        "feelsLike": data["main"]["feels_like"],
        "condition": data["weather"][0]["description"],
        "windMph": data["wind"]["speed"]
    }


print(getWeather(input("enter town, city, country")))
