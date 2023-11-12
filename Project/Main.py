import datetime as dt  # Time
import meteomatics.api as api
import requests  # Request API
import http.client  # HTTP status
import pandas as pd  # CSV
import markdown # Table
import matplotlib.pyplot as plt  # Graph
import pytz  # Time zone
import tkinter as tk # GUI

# Define the global variables
coordinates = []
lat = lon = Diff = days = hours = temp = response = None

# Input time and return difference to UTC
def Get_Time(timezone_name):

    tz = pytz.timezone(timezone_name)
    utc = pytz.utc
    now = utc.localize(dt.datetime.utcnow()) # Get UTC time
    local_time = now.astimezone(tz) # Get local time
    offset = local_time.utcoffset().total_seconds() / 3600 # Calculate

    return offset # Return the hours difference to UTC

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
    try:
        global response  # Use the global response variable
        # Meteomatics ID
        username = '-_tiewcharernsopha_jirapas'
        password = 'Hn1Ief6G8d'

        parameters = [f't_2m:{temp}', 'precip_1h:mm', 'wind_speed_10m:ms', 'uv:idx']
        model = 'mix'

        # Time
        UTC = dt.datetime.utcnow()
        User_time = UTC + dt.timedelta(hours=Diff)
        enddate = UTC + dt.timedelta(days)
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
    except:
        print("\nFail to requesting API. Please check internet connection")
    
# Botton click
def On_retrieve_button_click():
    global coordinates, lat, lon, Diff, days, hours, temp

    # Retrieve and store the values when the button is clicked
    try:
        lat = float(latitude_entry.get())
        lon = float(longitude_entry.get())
        days = int(days_entry.get())
        hours = int(timestep_entry.get())
    except ValueError:
        result_label.config(text="Invalid input.")
        return

    # Check the validity of latitude and longitude values
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        result_label.config(text="Invalid latitude or longitude. Please enter values within the valid range.")
        return

    # Check the validity of days and timestep values
    if not (1 <= days <= 8) or not (1 <= hours <= 24):
        result_label.config(text="Invalid number of days or timestep, Please enter values 1-8.")
        return

    # Check the validity of temperature unit
    temp = temp_entry.get().upper()  # Convert to uppercase for case-insensitive check
    if temp not in ('C', 'F', 'K'):
        result_label.config(text="Invalid temperature unit")
        return

    # If all inputs are valid, proceed with other inputs
    coordinates, lat, lon, Diff, days, hours, temp = Get_Info()
    Get_API(coordinates, lat, lon, Diff, days, hours, temp)

    result_label.config(text="Weather data retrieved!")

# Print Data
def Print_Data():

    global response

    # Check if data was collected
    if response is None:
        print("Data not retrieved yet. Click 'Retrieve Weather Data' first.")
    else:
        # Change header of columns
        column_mapping = {
            f't_2m:{temp}': f'Temperature at 2m : {temp}', 'precip_1h:mm': 'Precipitation : mm',
            'wind_speed_10m:ms': 'Wind speed at 10m : m/s', 'uv:idx': 'UV Index', }

        # Make data user-friendly
        response = response.rename(columns=column_mapping)
        response = response.reset_index()
        response = response.drop(['lon', 'lat'],axis=1)
        response['validdate'] = pd.to_datetime(response['validdate']) + pd.Timedelta(hours=int(Diff))
        response['validdate'] = response['validdate'].astype(str).str[:-6]

        # Print in Terminal
        print(response)

        # Print in Txt
        Markdown = response.to_markdown()
        with open('Report.txt', 'w') as f:
            f.write(Markdown)
        
        # Print in CSV
        df = pd.DataFrame(response.copy())
        df.to_csv('Report.csv', index='validdate')

# Plot a graph
def Plot_Graph():

    df = pd.DataFrame(response)
    df.plot(kind='line', title='Graph', grid=True)

    plt.xticks(rotation=45)
    plt.xlabel('Time')
    plt.ylabel('Unit')
    plt.show()


# Create the main GUI window
root = tk.Tk()
root.title("Weather Forecasting") # Title
root.geometry(f"500x500") # Size

# Create and place input labels and entry fields
latitude_label = tk.Label(root, text="Latitude :")
latitude_label.pack()
latitude_entry = tk.Entry(root)
latitude_entry.pack()

longitude_label = tk.Label(root, text="Longitude :")
longitude_label.pack()
longitude_entry = tk.Entry(root)
longitude_entry.pack()

timezone_label = tk.Label(root, text="Timezone (America/New_York) :")
timezone_label.pack()
timezone_entry = tk.Entry(root)
timezone_entry.pack()

days_label = tk.Label(root, text="Number of Days (1-8) :")
days_label.pack()
days_entry = tk.Entry(root)
days_entry.pack()

timestep_label = tk.Label(root, text="Timestep (1-24 hours) :")
timestep_label.pack()
timestep_entry = tk.Entry(root)
timestep_entry.pack()

temp_label = tk.Label(root, text="Temperature Unit (C/F/K) :")
temp_label.pack()
temp_entry = tk.Entry(root)
temp_entry.pack()

# Create a button
retrieve_button = tk.Button(root, text="Retrieve Weather Data", command=On_retrieve_button_click)
retrieve_button.pack()

print_button = tk.Button(root, text="Print Data", command=Print_Data)
print_button.pack()

plot_button = tk.Button(root, text="Plot graph", command=Plot_Graph)
plot_button.pack()

# Create a label to display the result
result_label = tk.Label(root, text="")
result_label.pack()

# Start the GUI application
root.mainloop()