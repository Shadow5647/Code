import datetime as dt  # Time
from matplotlib.dates import DateFormatter
import meteomatics.api as api
import requests  # Request API
import http.client  # HTTP status
import pandas as pd  # Graph
import matplotlib.pyplot as plt  # Graph
import pytz  # Time zone
import tkinter as tk

# Define the global variables
coordinates = []
lat = lon = 0.0
Diff = days = hours = 0
temp = ''
response = None  # Initialize the response as None

#-----------------------------------------------------------------------------------------------------

# Input time and return difference to UTC
def Get_Time(timezone_name):
    tz = pytz.timezone(timezone_name)
    utc = pytz.utc
    now = utc.localize(dt.datetime.utcnow())
    local_time = now.astimezone(tz)
    offset = local_time.utcoffset().total_seconds() / 3600
    return offset

# Plot a graph
def Plot_Graph():

    df = pd.DataFrame(response)
    df.to_csv('Test.csv', index = 'datetime')

    # Create a line chart and show
    df.plot(kind='line', title='Graph', grid=True)

    # Set the tick positions based on the first column in your DataFrame
    plt.xticks(rotation=45)
    plt.xlabel('Time')
    plt.ylabel('Unit')
    plt.show()

# Get data from user
def Get_Info():
    # Get user inputs from the entry fields
    lat = float(latitude_entry.get())
    lon = float(longitude_entry.get())
    Diff = Get_Time(timezone_entry.get())
    days = int(days_entry.get())
    hours = int(timestep_entry.get())
    temp = temp_entry.get()

    result_label.config(text="Weather data retrieved!")
    return [(lat, lon)], lat, lon, Diff, days, hours, temp

# Request API
def Get_API(coordinates, lat, lon, Diff, days, hours, temp):
    global response  # Use the global response variable
    # Meteomatics ID
    username = '-_tiewcharernsopha_jirapas'
    password = 'Hn1Ief6G8d'

    parameters = [f't_2m:{temp}', 'precip_1h:mm', 'wind_speed_10m:ms', 'uv:idx']
    model = 'mix'

    # Time
    UTC = dt.datetime.utcnow()
    User_time = UTC + dt.timedelta(hours=Diff)

    enddate = User_time + dt.timedelta(days)
    interval = dt.timedelta(hours=hours)

    # Clock
    print(f"\nCurrent date and time in UTC : {UTC}")
    print(f"Current date and time in your location : {User_time}\n")

    # Make API request
    print("Sending API request...")
    response = api.query_time_series(coordinates, UTC, enddate, interval, parameters, username, password, model=model)
    
    def Get_HTTP():
        # Check HTTP status
        url = f'https://api.meteomatics.com/{username}/{password}/weather?lat={lat}&lon={lon}&start={User_time.isoformat()}&end={enddate.isoformat()}&interval={interval.total_seconds()}s&model={model}&parameters={",".join(parameters)}'

        HTTP_code = (requests.get(url)).status_code
        status_message = http.client.responses.get(HTTP_code, 'Unknown Status Code')

        # Printout HTTP code and status
        print(f'Server status : {HTTP_code} : {status_message}')

    Get_HTTP()
    print("Received a response. Sending data back...\n")

# Botton click
def On_retrieve_button_click():
    global coordinates, lat, lon, Diff, days, hours, temp
    # Retrieve and store the values when the button is clicked

    coordinates, lat, lon, Diff, days, hours, temp = Get_Info()
    Get_API(coordinates, lat, lon, Diff, days, hours, temp)  # Call the API request function
    result_label.config(text="Weather data retrieved!")

# Print the data
def Print_Data():
    global response

    # Create dataframe ,CSV
    df = pd.DataFrame(response)
    df.to_csv('Test.csv', index = 'datetime')

    # Print data
    if response is not None:
        # Change header of columns and printout
        column_mapping = {
            't_2m': f'Temperature at 2m : {temp}',
            'precip_1h': 'Precipitation : mm',
            'wind_speed_10m': 'Wind speed at 10m : m/s',
            'uv': 'UV Index',
        }
        
        response = response.rename(columns=column_mapping)
        print(response)
    else:
        print("Data not retrieved yet. Click 'Retrieve Weather Data' first.")

#-----------------------------------------------------------------------------------------------------

# Create the main GUI window
root = tk.Tk()
root.title("Weather Forecasting")
root.geometry(f"400x400")

# Create and place input labels and entry fields
latitude_label = tk.Label(root, text="Latitude:")
latitude_label.pack()
latitude_entry = tk.Entry(root)
latitude_entry.pack()

longitude_label = tk.Label(root, text="Longitude:")
longitude_label.pack()
longitude_entry = tk.Entry(root)
longitude_entry.pack()

timezone_label = tk.Label(root, text="Timezone (e.g., America/New_York):")
timezone_label.pack()
timezone_entry = tk.Entry(root)
timezone_entry.pack()

days_label = tk.Label(root, text="Number of Days (1-8):")
days_label.pack()
days_entry = tk.Entry(root)
days_entry.pack()

timestep_label = tk.Label(root, text="Timestep (1-24 hours):")
timestep_label.pack()
timestep_entry = tk.Entry(root)
timestep_entry.pack()

temp_label = tk.Label(root, text="Temperature Unit (C/F/K):")
temp_label.pack()
temp_entry = tk.Entry(root)
temp_entry.pack()

# Create a button to trigger weather data retrieval
retrieve_button = tk.Button(root, text="Retrieve Weather Data", command=On_retrieve_button_click)
retrieve_button.pack()

# Create a button to print data
print_button = tk.Button(root, text="Print Data", command=Print_Data)
print_button.pack()

plot_button = tk.Button(root, text="Plot graph", command=Plot_Graph)
plot_button.pack()

# Create a label to display the result
result_label = tk.Label(root, text="")
result_label.pack()

# Start the GUI application
root.mainloop()
