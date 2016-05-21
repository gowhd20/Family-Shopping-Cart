
## api key for the weather data
API_KEY = "bf34a92b1b957544764499725084482d"

## config url with name of city or name of country to get weather info
def config_url(locality):
	return "http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=%s" % (locality, API_KEY)

## Kelvin value for tempearture
VAL_DIFF_KELVIN_N_CELSIUS = 274.15