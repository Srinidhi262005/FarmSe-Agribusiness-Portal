import requests

CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_current_weather(city_name, api_key):
    url = f"{CURRENT_WEATHER_URL}?q={city_name}&units=metric&appid={api_key}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    if str(data.get('cod')) not in ('200', '201'):
        raise ValueError(data.get('message', 'Could not retrieve current weather data.'))

    weather = data['weather'][0]
    main = data['main']
    sys = data.get('sys', {})

    return {
        'location': f"{data.get('name', city_name).title()}, {sys.get('country', '').upper()}".strip(', '),
        'temperature': main.get('temp'),
        'feels_like': main.get('feels_like'),
        'humidity': main.get('humidity'),
        'description': weather.get('description', '').title(),
        'icon': weather.get('icon'),
        'wind_speed': data.get('wind', {}).get('speed'),
    }


def get_weather_forecast(city_name, api_key):
    url = f"{FORECAST_URL}?q={city_name}&units=metric&appid={api_key}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    if str(data.get('cod')) != '200':
        raise ValueError(data.get('message', 'Could not retrieve forecast data.'))

    forecast_list = data.get('list', [])
    daily_forecast = []
    seen_dates = set()

    for item in forecast_list:
        dt_txt = item.get('dt_txt', '')
        if not dt_txt:
            continue
        date, time = dt_txt.split(' ')
        if time == '12:00:00' and date not in seen_dates:
            daily_forecast.append(item)
            seen_dates.add(date)
            if len(daily_forecast) >= 5:
                break

    if not daily_forecast and forecast_list:
        daily_forecast = forecast_list[0:5]

    return {
        'location': f"{data.get('city', {}).get('name', city_name).title()}, {data.get('city', {}).get('country', '')}".strip(', '),
        'list': daily_forecast,
    }
