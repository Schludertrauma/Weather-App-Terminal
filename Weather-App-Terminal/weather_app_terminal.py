'''Weather Forecast Simulator'''
'''This script gives weather data and forecasts for a given city.'''
'''It checks on startup for a "weather api key" in a subdirectory called "config".'''
'''When not subdirectory is found, it will create a new one and ask for the key.'''
'''This script has a simple terminal interface.'''
'''The user can save cities in a JSON file, which are shown on startup.'''

# Import necessary libraries and Modules


import sys
import time
import os
import json
import requests

# classes definition


class weather_app_terminal:
    def welcome(self):
        # Welcome message for the user
        print("Welcome to the Weather Forecast Simulator!")
        print("This application provides weather data and forecasts for a given city.")
        print("You can save cities to quickly access their weather information.")
        print()
        time.sleep(1)

    def check_for_internet_connection(self):
        # Check if the internet connection is available
        try:
            requests.get("https://www.google.com", timeout=5)
            print("Internet connection is available.")
            time.sleep(1)
            return True
        except requests.ConnectionError:
            print("No internet connection. Please check your connection and try again.")
            return False

    def check_api_key(self):
        # Check if the API key exists in the config directory
        # If not, create the directory and ask for the key or to skip for testing
        config_dir = "config"
        api_key_path = os.path.join(config_dir, "api_key.txt")
        test_api_key_path = os.path.join(config_dir, "test_api_key.txt")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            print("Config directory created.")
        # Try to load API key from file first
        if os.path.exists(api_key_path):
            with open(api_key_path, 'r') as f:
                self.api_key = f.read().strip()
            print()
            time.sleep(1)
            print("API key loaded from file.")
            time.sleep(1)
        # If the API key file does not exist, check for a test API key
        elif os.path.exists(test_api_key_path):
            with open(test_api_key_path, 'r') as f:
                self.api_key = f.read().strip()
            print()
            time.sleep(1)
            print("Test API key loaded from file.")
            time.sleep(1)

        else:
            # If no API key is found, prompt the user to enter one or skip for testing
            print(
                "Please enter your Weather API key or type 'skip' for testing without API key:")
            api_key_test = "test_api_key"
            api_key = input("API Key: ").strip()
            if api_key.lower() == 'skip':
                self.api_key = api_key_test
                with open(test_api_key_path, 'w') as f:
                    f.write(self.api_key)
                print("Skipping API key setup for testing purposes.")
            else:
                self.api_key = api_key
                with open(api_key_path, 'w') as f:
                    f.write(self.api_key)
                print("API key saved successfully.")

    def ip_location(self):
        # Get the user's IP address and location using requests.get
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            ip_address = data.get("ip", "Unknown")
            city = data.get("city", "Unknown")
            region = data.get("region", "Unknown")
            country = data.get("country", "Unknown")
        except Exception as e:
            print(f"Error fetching IP location: {e}")
            ip_address = city = region = country = "Unknown"

        return {
            "ip_address": ip_address,
            "city": city,
            "region": region,
            "country": country
        }

    def load_api_weather_data(self, city):
        # Load weather data for a given city using requests.get
        url = f"https://api.weatherapi.com/v1/current.json?key={self.api_key}&q={city}&aqi=no"
        try:
            response = requests.get(url)
            data = response.json()
            current = data.get("current", {})
            temperature = current.get("temp_c", "Unknown")
            condition = current.get("condition", {}).get("text", "Unknown")
            humidity = current.get("humidity", "Unknown")
            wind_speed = current.get("wind_kph", "Unknown")
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            temperature = condition = humidity = wind_speed = "Unknown"

        request_data = {
            "city": city,
            "temperature": temperature,
            "condition": condition,
            "humidity": humidity,
            "wind_speed": wind_speed
        }
        return request_data

    def forecast_weather_data(self, city, days):
        # Load forecast data for a given city for the specified number of days
        # If the API key is None or set to the test value, return mock forecast
        if self.api_key is None or self.api_key == "test_api_key":
            from datetime import datetime, timedelta
            today = datetime.now()
            mock_conditions = ["Sunny", "Partly Cloudy", "Rainy"]
            mock_forecast = [
                {
                    "city": city,
                    "date": (today + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                    "max_temp": 25 - i*2,
                    "min_temp": 15 - i,
                    "condition": mock_conditions[i % len(mock_conditions)]
                }
                for i in range(days)
            ]
            return mock_forecast

        url = f"https://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={city}&days={days}&aqi=no&alerts=no"
        forecast_data = []
        try:
            response = requests.get(url)
            data = response.json()
            forecast = data.get("forecast", {}).get("forecastday", [])
            for day in forecast[:days]:
                date = day.get("date", "Unknown")
                day_info = day.get("day", {})
                max_temp = day_info.get("maxtemp_c", "Unknown")
                min_temp = day_info.get("mintemp_c", "Unknown")
                condition = day_info.get(
                    "condition", {}).get("text", "Unknown")
                forecast_data.append({
                    "city": city,
                    "date": date,
                    "max_temp": max_temp,
                    "min_temp": min_temp,
                    "condition": condition
                })
        except Exception as e:
            print(f"Error fetching forecast data: {e}")
        if not forecast_data:
            forecast_data = [{
                "city": city,
                "date": "Unknown",
                "max_temp": "Unknown",
                "min_temp": "Unknown",
                "condition": "Unknown"
            }]
        return forecast_data

    def load_saved_cities(self):
        # Load saved cities and their weather data from a single JSON file
        weather_json_file = "saved_cities_weather.json"
        self.saved_cities_weather = []
        if os.path.exists(weather_json_file):
            with open(weather_json_file, 'r') as wf:
                self.saved_cities_weather = json.load(wf)
            print()
            print("Saved cities with weather data loaded successfully.")

    def show_saved_cities(self):
        # Display the saved cities and their weather data to the user
        weather_json_file = "saved_cities_weather.json"
        if os.path.exists(weather_json_file):
            with open(weather_json_file, 'r') as wf:
                cities_weather = json.load(wf)
            if cities_weather:
                print()
                for entry in cities_weather:
                    print(
                        f"- {entry['city']}: {entry['temperature']}°C, {entry['condition']}, Humidity: {entry['humidity']}%, Wind: {entry['wind_speed']} kph")
            else:
                print("No cities saved yet.")
        else:
            print("No saved cities weather file found. Please save a city first.")

    def menu(self):
        # Display the menu options to the user
        print("\nMenu:")
        print("1. View Weather Data for a City")
        print("2. View Weather Forecast")
        print("3. Save a City")
        print("4. Show Saved Cities")
        print("5. Exit")
        choice = input("Please choose an option: ")
        print()
        return choice

    def end_message(self):
        # Display a goodbye message when exiting the application
        print("Thank you for using the Weather Forecast Simulator. Goodbye!")
        time.sleep(1)

    def run(self):
        # Main loop to run the weather application
        self.welcome()
        if not self.check_for_internet_connection():
            print("Exiting the application due to no internet connection.")
            return
        self.check_api_key()
        self.load_saved_cities()
        self.show_saved_cities()
        while True:
            choice = self.menu()
            if choice == '1':
                city = input("Enter the city name: ").strip()
                weather_data = self.load_api_weather_data(city)
                print(
                    f"Weather in {city}: {weather_data['temperature']}°C, {weather_data['condition']}, Humidity: {weather_data['humidity']}%, Wind: {weather_data['wind_speed']} kph")
            elif choice == '2':
                city = input("Enter the city name for forecast: ").strip()
                days = input(
                    "Enter the number of days for the forecast (1-3): ").strip()
                if days.isdigit() and 1 <= int(days) <= 3:
                    days = int(days)
                    forecast_data = self.forecast_weather_data(city, days)
                    print()
                    print(f"Forecast for {city} for the next {days} days:")
                    for day in forecast_data:
                        print(
                            f"{day['date']}: Max Temp: {day['max_temp']}°C, Min Temp: {day['min_temp']}°C, Condition: {day['condition']}")
                else:
                    print("Invalid input. Please enter a number between 1 and 3.")
                    continue
            elif choice == '3':
                city = input("Enter the city name to save: ").strip()
                weather_data = self.load_api_weather_data(city)
                self.saved_cities_weather.append(weather_data)
                with open("saved_cities_weather.json", 'w') as wf:
                    json.dump(self.saved_cities_weather, wf, indent=4)
                print(f"{city} saved successfully.")
            elif choice == '4':
                self.show_saved_cities()
            elif choice == '5':
                self.end_message()
                sys.exit()
            else:
                print("Invalid choice. Please try again.")

# Starting point of the script


if __name__ == "__main__":
    app = weather_app_terminal()
    app.run()
