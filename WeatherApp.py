import importlib.util
import sys
import subprocess

# Check if tkinter is installed
if importlib.util.find_spec("tkinter") is None:
    print("Tkinter is not installed but is required for this application.")

    # Ask if user wants to install
    install_tkinter = input("Would you like to install tkinter? (y/n): ").strip().lower()
    if install_tkinter == "y":
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tkinter"])
    else:
        sys.exit("Exiting.")

# Check if requests is installed
if importlib.util.find_spec("requests") is None:
    print("Requests is not installed but is required for this application.")

    # Ask if user wants to install
    install_requests = input("Would you like to install requests? (y/n): ").strip().lower()
    if install_requests == "y":
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    else:
        sys.exit("Exiting.")


# If all is installed ...
import tkinter as tk
from tkinter import ttk
import requests


# Returns a dictionary of state abbreviations and the full state name -- for better readability
def get_states():
    return {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado',
        'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
        'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
        'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
        'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
        'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
        'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming'
    }


# Shut down program - for handling window closes
def shutdown():
    sys.exit()


class WeatherApp:
    def __init__(self):
        self.code_var = None
        self.state_var = None

        self.forecast_window = None
        self.code_window = None
        self.state_window = None

        self.url = "https://api.weather.gov/zones/land"
        self.headers = {"User-Agent": "WeatherApp/1.0"}

        self.data = self.fetch_data()
        self.state = None
        self.ids = []
        self.code = None
        self.observation_stations = []
        self.selected_station = None

        self.daily_forecast = {}
        self.point_forecast = {}

        self.print_daily = None

    # Clear relevant data, for looping
    def clear(self):
        self.daily_forecast = {}
        self.observation_stations = {}
        self.ids = []
        self.point_forecast = {}

    # Fetches weather data from weather.gov api
    def fetch_data(self):
        response = requests.get(self.url, headers=self.headers)
        return response.json()

    # Gets state input from user. Tkinter drop-down menu.
    def select_state(self):

        # State selection window
        self.state_window = tk.Tk()
        self.state_window.title("State Selection")
        self.state_var = tk.StringVar(value="Alabama")

        state_label = ttk.Label(self.state_window, text="Please select a state:")
        state_label.grid(row=0, column=0, padx=10, pady=5)
        state_combobox = ttk.Combobox(self.state_window, textvariable=self.state_var, values=list(get_states().values()))
        state_combobox.grid(row=0, column=1, padx=10, pady=5)

        # Once state is selected, prompt to select zone code
        state_button = ttk.Button(self.state_window, text="OK", command=self.select_code)

        state_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.state_window.protocol("WM_DELETE_WINDOW", shutdown)

        self.state_window.mainloop()

    # Gets zone input from user. Tkinter drop-down menu.
    def select_code(self):
        self.state = self.state_var.get()
        self.state_window.destroy()

        # Find state abbreviation for selected state
        for abbrev, full_name in get_states().items():
            if full_name == self.state:
                self.state = abbrev
                break

        # Gather available codes for the selected state
        for feature in self.data['features']:
            if feature['properties']['state'] == self.state:
                part = feature['id'].split("/")[-1]
                self.ids.append(part)

        # Code selection window
        self.code_window = tk.Tk()
        self.code_window.title("Weather Zone Selection")
        self.code_var = tk.StringVar(value=self.ids[0])

        code_label = ttk.Label(self.code_window, text="Please select a zone code:")
        code_label.grid(row=0, column=0, padx=10, pady=5)

        code_combobox = ttk.Combobox(self.code_window, textvariable=self.code_var, values=self.ids)
        code_combobox.grid(row=0, column=1, padx=10, pady=5)

        # Once code is selected, prompt for forecast type
        code_button = ttk.Button(self.code_window, text="OK", command=self.select_forecast_type)
        code_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.code_window.protocol("WM_DELETE_WINDOW", shutdown)

        self.code_window.mainloop()

    # Select type of forecast (hourly/daily)
    def select_forecast_type(self):

        # Handle buttons
        def handle_hourly():
            self.print_daily = False
            self.get_forecast()

        def handle_daily():
            self.print_daily = True
            self.get_forecast()

        # Clear previous window
        self.code_window.destroy()

        # Forecast type window
        self.forecast_window = tk.Tk()
        self.forecast_window.title("Forecast Type Selection")

        forecast_label = ttk.Label(self.forecast_window, text="Please select forecast type:")
        forecast_label.grid(row=0, column=0, padx=10, pady=5)

        hourly_button = ttk.Button(self.forecast_window, text="Hourly Forecast", command=handle_hourly)
        hourly_button.grid(row=1, column=0, padx=10, pady=5)

        daily_button = ttk.Button(self.forecast_window, text="Daily Forecast", command=handle_daily)
        daily_button.grid(row=2, column=0, padx=10, pady=5)

        self.forecast_window.protocol("WM_DELETE_WINDOW", shutdown)

    # Gets forecast for selected zone.
    def get_forecast(self):
        self.code = self.code_var.get()

        # Clear previous window
        self.forecast_window.destroy()

        # Fetch forecast data from zone code
        for feature in self.data['features']:
            if feature['id'].split("/")[-1] == self.code:
                forecast_url = (feature['id'] + "/forecast")
                forecast_headers = {"User-Agent": "WeatherApp/1.0"}
                forecast_response = requests.get(forecast_url, headers=forecast_headers)
                forecast_data = forecast_response.json()

                # Populate forecast dictionary with forecast, by day.
                for day in forecast_data["properties"]['periods']:
                    self.daily_forecast[day['name']] = day['detailedForecast']

                # Find observation stations for this zone
                stations_url = (feature['id'])
                stations_headers = {"User-Agent": "WeatherApp/1.0"}
                stations_response = requests.get(stations_url, headers=stations_headers)
                stations_data = stations_response.json()
                self.observation_stations = stations_data['properties']['observationStations']

    # Select station - for hourly forecast
    def select_station(self):

        # station window
        station_window = tk.Tk()
        station_window.title("Observation Station Selection")

        # strip to only station name (four letter code)
        stations = [station[-4:] for station in self.observation_stations]

        selected_station_var = tk.StringVar(value=stations[0])
        station_label = ttk.Label(station_window, text="Please select an observation station:")
        station_label.grid(row=0, column=0, padx=10, pady=5)

        station_combobox = ttk.Combobox(station_window, textvariable=selected_station_var, values=stations)
        station_combobox.grid(row=0, column=1, padx=10, pady=5)

        # Find the corresponding full station name from original list
        def confirm_selection():
            selected_station = selected_station_var.get()
            full_station_name = next(
                station for station in self.observation_stations if station[-4:] == selected_station)
            self.selected_station = full_station_name
            station_window.destroy()

        confirm_button = ttk.Button(station_window, text="OK", command=confirm_selection)
        confirm_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        station_window.protocol("WM_DELETE_WINDOW", shutdown)

        station_window.mainloop()

    # find hourly forecast based on coordinates of selected station
    def get_point_forecast(self):

        # Fetch station data
        station_url = self.selected_station
        station_headers = {"User-Agent": "WeatherApp/1.0"}
        station_response = requests.get(station_url, headers=station_headers)
        station_data = station_response.json()

        point = (station_data['geometry']['coordinates'][1], station_data['geometry']['coordinates'][0])

        # Fetch point data - to convert coordinate point to grid point
        point_url = f"https://api.weather.gov/points/{point[0]},{point[1]}"
        point_headers = {"User-Agent": "WeatherApp/1.0"}
        point_response = requests.get(point_url, headers=point_headers)
        point_data = point_response.json()

        # fetch forecast for the grid point
        point_forecast_url = (point_data['properties']['forecastHourly'])
        point_forecast_headers = {"User-Agent": "WeatherApp/1.0"}
        point_forecast_response = requests.get(point_forecast_url, headers=point_forecast_headers)
        point_forecast_data = point_forecast_response.json()

        # populate point forecast member variable with the relevant point forecast
        for period in point_forecast_data['properties']['periods']:
            start_time = "Time: " + period['startTime'][11:13]+":00"
            period_info = f"""
                Temperature:  {period['temperature']} F
                Change of Precipitation:  {period['probabilityOfPrecipitation']['value']}%
                Wind Speed:  {period['windSpeed']}
                Wind Direction:  {period['windDirection']}
                Conditions:  {period['shortForecast']}
            """
            self.point_forecast[start_time] = period_info

    # Print hourly forecast
    def print_hourly_forecast(self):
        forecast_window = tk.Tk()
        forecast_window.title(f"Hourly forecast for station {self.selected_station[-4:]} in {get_states()[self.state]}")
        forecast_window.geometry("1000x600")

        canvas = tk.Canvas(forecast_window, width=980, height=580)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(forecast_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        forecast_frame = ttk.Frame(canvas)
        forecast_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=forecast_frame, anchor="nw")

        # Print forecasts by day
        for hour, forecast in self.point_forecast.items():
            hour_label = ttk.Label(forecast_frame, text=hour)
            hour_label.grid(sticky="w", padx=10, pady=5)

            forecast_text = tk.Text(forecast_frame, wrap="word", width=118, height=6)
            forecast_text.insert(tk.END, forecast)
            forecast_text.config(state="disabled")
            forecast_text.grid(sticky="w", padx=10, pady=5)

            separator = ttk.Separator(forecast_frame, orient="horizontal")
            separator.grid(row=forecast_frame.grid_size()[1], columnspan=2, sticky="ew", padx=10, pady=5)

            # Align content to bottom-left corner
            hour_label.grid_anchor("sw")
            forecast_text.grid_anchor("sw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        forecast_window.mainloop()

    # Prints daily forecast for selection. Tkinter window with scroll bar
    def print_daily_forecast(self):
        forecast_window = tk.Tk()
        forecast_window.title(f"Weather Forecast: {get_states()[self.state]}, {self.code}")
        forecast_window.geometry("1000x600")

        canvas = tk.Canvas(forecast_window, width=980, height=580)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(forecast_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        forecast_frame = ttk.Frame(canvas)
        forecast_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=forecast_frame, anchor="nw")

        # Print forecasts by day
        for day, forecast in self.daily_forecast.items():
            day_label = ttk.Label(forecast_frame, text=day)
            day_label.grid(sticky="w", padx=10, pady=5)

            forecast_text = tk.Text(forecast_frame, wrap="word", width=118, height=5)
            forecast_text.insert(tk.END, forecast)
            forecast_text.config(state="disabled")
            forecast_text.grid(sticky="w", padx=10, pady=5)

            separator = ttk.Separator(forecast_frame, orient="horizontal")
            separator.grid(row=forecast_frame.grid_size()[1], columnspan=2, sticky="ew", padx=10, pady=5)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        forecast_window.mainloop()

    # Run app
    def run(self):
        while True:
            try:
                self.clear()
                self.select_state()
                if self.print_daily:
                    self.print_daily_forecast()
                else:
                    self.select_station()
                    self.get_point_forecast()
                    self.print_hourly_forecast()

            except Exception as e:
                print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = WeatherApp()
    app.run()
