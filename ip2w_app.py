import os
import json
import requests
import logging
import importlib.util


os.sys.path.append("/usr/local/etc/settings.py")
try:
    import settings
except:
    logging.error("Can't import settings")
    os.sys.exit("Can't import settings")

logging.basicConfig(
    filename=settings.LOG_FILE,
    format="[%(asctime)s] %(levelname).1s %(message)s",
    level=logging.ERROR,
    datefmt="%Y.%m.%d %H:%M:%S",
)

IPINFO_TOKEN = settings.IPINFO_TOKEN
OPENWEATHER_KEY = settings.OPENWEATHER_KEY


def get_city(token, ip="", timeout=1):
    url = f"https://ipinfo.io/{ip}?token={token}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()

    return r.json()["city"]


def get_weather(city, api_key, units="metric", language="ru", timeout=1):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units={units}&lang={language}&appid={api_key}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()

    weather = r.json()

    return {
        "city": weather["name"],
        "temp": f'{weather["main"]["temp"]:+}',
        "conditions": weather["weather"][0]["description"],
    }


def response(status, start_response, data):
    data = json.dumps(data).encode("utf-8")

    response_headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(data))),
    ]
    start_response(status, response_headers)

    return [data]


def application(env, start_response):
    uri = env.get("PATH_INFO")
    if uri != "/":
        return response("404 Not Found", start_response, {"error": "404 Not Found"})

    remote_addr = env.get("REMOTE_ADDR")

    try:
        city = get_city(IPINFO_TOKEN, remote_addr, settings.REQUEST_TIMEOUT)
        weather = get_weather(
            city,
            OPENWEATHER_KEY,
            units=settings.UNITS,
            language=settings.LANGUAGE,
            timeout=settings.REQUEST_TIMEOUT,
        )
    except:
        logging.exception(f"Error during request processing from {remote_addr}")
        status = "500 Internal Server Error"
        data = {"error": "500 Internal Server Error"}
    else:
        status = "200 OK"
        data = weather

    return response(status, start_response, data)
