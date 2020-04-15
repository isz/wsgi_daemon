import os
import json
import requests
import logging
import importlib.util
from time import sleep


os.sys.path.append("/usr/local/etc/settings.py")
try:
    import settings
except:
    logging.error("Can't import settings")
    os.sys.exit("Can't import settings")


def retry_when_timeout(attempts, attempt_timeout):
    def decorator(func):
        def wrapped(*args, **kwargs):
            for _ in range(attempts):
                try:
                    result = func(*args, **kwargs)
                except requests.exceptions.ConnectTimeout as e:
                    sleep(attempt_timeout)
                except Exception as e:
                    raise e
                else:
                    return result
            raise e

        return wrapped

    return decorator


logging.basicConfig(
    filename=settings.LOG_FILE,
    format="[%(asctime)s] %(levelname).1s %(message)s",
    level=logging.ERROR,
    datefmt="%Y.%m.%d %H:%M:%S",
)

IPINFO_TOKEN = settings.IPINFO_TOKEN
OPENWEATHER_KEY = settings.OPENWEATHER_KEY

NOT_FOUND = 404
INTERNAL_ERROR = 500
GATEWAY_TIMEOUT = 504

ERROR = {
    NOT_FOUND: "Not Found",
    INTERNAL_ERROR: "Internal Server Error",
    GATEWAY_TIMEOUT: "Gateway Timeout",
}


@retry_when_timeout(settings.REQUEST_ATTEMPTS, settings.REQUEST_ATTEMPT_TIMEOUT)
def get_city(token, ip="", timeout=1):
    url = f"https://ipinfo.io/{ip}?token={token}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()

    return r.json()["city"]


@retry_when_timeout(settings.REQUEST_ATTEMPTS, settings.REQUEST_ATTEMPT_TIMEOUT)
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
        status = f"{NOT_FOUND} {ERROR[NOT_FOUND]}"
        return response(status, start_response, {"error": status})

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
    except KeyError:
        logging.exception(f"Weather not found for ip {remote_addr}")
        status = f"{NOT_FOUND} {ERROR[NOT_FOUND]}"
        data = {"error": status}
    except requests.exceptions.ConnectTimeout:
        logging.exception(
            f"Connection timeout during request processing from {remote_addr}"
        )
        status = f"{GATEWAY_TIMEOUT} {ERROR[GATEWAY_TIMEOUT]}"
        data = {"error": status}
    except:
        logging.exception(f"Error during request processing from {remote_addr}")
        status = f"{INTERNAL_ERROR} {ERROR[INTERNAL_ERROR]}"
        data = {"error": status}
    else:
        status = "200 OK"
        data = weather

    return response(status, start_response, data)


def start_response(status, headers):
    print(status, headers)


if __name__ == "__main__":
    env = {"PATH_INFO": "/", "REMOTE_ADDR": "8.8.8.8"}
    resp = application(env, start_response)

    for r in resp:
        print(json.loads(r))
