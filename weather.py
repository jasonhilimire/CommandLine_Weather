# weather.py

import argparse
import json
import sys
from configparser import ConfigParser
from urllib import error, parse, request

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

def read_user_cli_args():
        """Handles the CLI user interactions
        Returns:
                argpars.Namespace: Populated namespace object
        """
        parser = argparse.ArgumentParser(
                description='gets weather and temperature information for a city'
        )
        parser.add_argument(
                "city", nargs="+", type=str, help="enter the city name"
        )
        parser.add_argument(
                "-i",
                "--imperial",
                action="store_true",
                help="display the temperature in imperial units"
        )
        return parser.parse_args()

def _get_api_key():
        """Fetch the API key from your configuration file.

        Expects a configuration file named "secrets.ini with structure:

            [openweather]
            api_key=<YOUR-OPENWEATHER-API-KEY
        """
        config = ConfigParser()
        config.read("secrets.ini")
        return config["openweather"]["api_key"]

def build_weather_query(city_input, imperial=False):
        """ Builds the URL for an API request to OpenWeathers API

        Args:
                city_input (List[str]): Name of a city as collected by argparse
                imperial (bool): Whether or not to use imperial units for temp
        Returns:
                str: URL formatted for OpenWEathers city name endpoint
        """
        api_key = _get_api_key()
        city_name = " ".join(city_input)
        url_encoded_city_name = parse.quote_plus(city_name)
        units = "imperial" if imperial else "metric"
        url = (
                f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
                f"&units={units}&appid={api_key}"
        )
        return url

def get_weather_data(query_url):
        """Makes an API request to URL and returns the data as a Python Object
        Args:
                query_url (str): URL formatted for OpenWeathers city name endpoint
        Returns:
                dict: Weather information for a specific city
        """
        try:
                response = request.urlopen(query_url)
        except error.HTTPError as http_error:
                if http_error.code == 401: # 401 - Unauthorized
                        sys.exit("Access denied- Check API Key")
                elif http_error.code == 404: #404 - Not found
                        sys.exit("Can't find weather data for this city")
                else:
                        sys.exit(f"Something went wrong ... ({http_error.code})")
        data = response.read()
        try:
                return json.loads(data)
        except json.JSONDecodeError:
                sys.exit("Coudlnt read the server response")

if __name__ == "__main__":
        user_args= read_user_cli_args()
        print(user_args.city, user_args.imperial)
        query_url = build_weather_query(user_args.city, user_args.imperial)
        weather_Data = get_weather_data(query_url)
        print(
                f"{weather_Data['name']}: "
                f"{weather_Data['weather'][0]['description']} "
                f"({weather_Data['main']['temp']})"
                )