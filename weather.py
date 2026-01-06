import requests, os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv("weatherKey")


HEADERS = {
    "User-Agent": "WESTLEY/1.0 (local assistant)"
}


BASE_URL = "https://api.openweathermap.org/data/2.5/"



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


def getWeather(paramators):
    
    request, locationString = paramators.split(" - ")
    
    lat, lon = getCoordinates(locationString)
    
    if request.lower() == "current":
        url=f"{BASE_URL}weather"
    elif request.lower() == "forecast":
        url=f"{BASE_URL}forecast"
    else: return f'Error in "Type" paramator, {request} is not a valid type.'
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": key,
        "units": "imperial"
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    
    return parser(data)



def parser(data, indent=0):
    """
    Recursively prints nested JSON-like structures.
    - data: dict | list | primitive
    - indent: current indentation level
    - maxDepth: optional safety limit
    """
    
    txt=""
    prefix = " " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            txt+=f"{prefix}{key}:\n"
            txt+=parser(value, indent + 2)

    elif isinstance(data, list):
        for i, item in enumerate(data):
            txt+=f"{prefix}[{i}]\n"
            txt+=parser(item, indent + 2)

    else:
        txt+=f"{prefix}{data}\n"
    return txt


if __name__ == "__main__":
    '''
    e=input("Enter 1 for weather, \nAnd 2 for forecast: ")
    
    if e=="1":
        x="weather"
    elif e == "2":
        x="forecast"
        
    x+=" - "
    
    x+=input("Enter town, city, country: ")
    '''
    print(getWeather("Current - New York, NY"))
