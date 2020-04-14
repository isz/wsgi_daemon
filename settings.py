
try:
    from tokens import IPINFO_TOKEN, OPENWEATHER_KEY
except:
    IPINFO_TOKEN = ''
    OPENWEATHER_KEY = ''

REQUEST_TIMEOUT = 1

# https://openweathermap.org/current#multi
LANGUAGE = 'ru' 

# default: Kelvin, metric: Celsius, imperial: Fahrenheit
# https://openweathermap.org/current#data
UNITS = 'metric' 

LOG_FILE = "/var/log/ip2w/ip2w.log"