'''
Here we define functions used for building a forecast alarm for surf (generated by windswell, e.g. in the baltic sea)
'''
import pandas as pd
from datetime import datetime
import requests
from dotenv import load_dotenv
import os


# below is the list of surf spots we want to keep an eye on with their relevant geographical data
spots = { "Kolifornia" : { "lat" : 54.1759, "lon" : 15.5833, "wind_window" : [225,350]} ,
         "Seabridge" : { "lat" : 54.4022 , "lon" : 13.6060 , "wind_window" : [10,170]},
         "Valhalla" : { "lat" : 54.3929, "lon": 13.6803, "wind_window" : [0,45]},
         "Borncold" : { "lat" : 54.1414 , "lon" : 11.7530, "wind_window" : [225,350]}
        }



def windmap(x):
    # translates wind direction given as degree 0 <= x <= 360 to string like "SSE"

    # dictionary for translation
    wind_directions = {
    "N": 0,
    "NNE": 22.5,
    "NE": 45,
    "ENE": 67.5,
    "E": 90,
    "ESE": 112.5,
    "SE": 135,
    "SSE": 157.5,
    "S": 180,
    "SSW": 202.5,
    "SW": 225,
    "WSW": 247.5,
    "W": 270,
    "WNW": 292.5,
    "NW": 315,
    "NNW": 337.5}

    # generate buckets of width 2*step_size for wind directions in degrees. given a degree x, find bucket and return corresponding string
    step_size = 11.25
    direction_degrees = list(wind_directions.values())
    direction_names = list(wind_directions.keys())

    # handle "N" separately, because 359 is next to 0 on the circle:
    if -step_size%360 < x or x <= step_size%360:
        return "N"
    # all other directions work by simply checking in which bucket x lies...
    else:
        for i in range(1,len(wind_directions)):
            if (direction_degrees[i]-step_size)%360 < x <= (direction_degrees[i]+step_size)%360:
                return direction_names[i]



def request(lat,lon):
    # access api, retrieve forecast, return (wind) data in dataframe

    load_dotenv()
    API_key = os.getenv("API_key")
    url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly&appid={API_key}'
    df = pd.DataFrame(requests.get(url).json()["daily"])[["dt","sunrise","sunset","wind_speed","wind_gust","wind_deg"]]

    # change unix to normal time
    df.dt = df.dt.apply(lambda x : datetime.utcfromtimestamp(x).strftime('%d-%m-%Y %H:%M:%S'))
    df.sunrise = df.sunrise.apply(lambda x : datetime.utcfromtimestamp(x).strftime('%H:%M'))
    df.sunset = df.sunset.apply(lambda x : datetime.utcfromtimestamp(x).strftime('%H:%M'))

    # round wind speed and gusts
    df.wind_speed = (df.wind_speed*3.6).round(decimals=0).astype(int)
    df.wind_gust = (df.wind_gust*3.6).round(decimals=0).astype(int)

    # rename columns and set date & time as index
    df.rename({"dt":"date", "wind_speed":"wind_speed (km/h)", "wind_gust":"wind_gust (km/h)","wind_deg":"wind_deg (°)"},axis = 1, inplace=True)
    df = df.set_index(df.date).drop(columns = "date")

    # use windmap to create new column for wind direction
    df["wind_dir"] = df["wind_deg (°)"].apply(lambda x: windmap(x))
    return df



def get_forecast(spots_dict = spots):
    # retrieve the wind forecast for all locations in spots

    for spot in spots_dict.keys():
        spots_dict[spot]["forecast"] = request(spots_dict[spot]["lat"],spots_dict[spot]["lon"])
    return spots_dict



def color_rows(row,spot,spots_dict):
    # highlight rows in the forecast with favourable conditions

    if (row["wind_speed (km/h)"] > 25) and (row["wind_gust (km/h)"] > 25) and (
                spots_dict[spot]["wind_window"][0] <= row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]):
        return ['background-color: lightcoral'] * len(row)
    else:
        return ['background-color: white'] * len(row)



def alarm():
    # for each spot check if wind speed and direction are such that waves can be expected
    # return message and display corresponding data

    spots_dict = get_forecast(spots)

    # loop through surf spots:
    for spot in spots_dict.keys():
        # retrieve data
        data = spots_dict[spot]["forecast"]
        # set alarm counter
        alarm = 0

        # check conditions (wind speed/gusts > 25/30 km/h, correct wind direction)
        print(f"\n...checking forecast for {spot}...\n")
        for row, index in data.iterrows():
            if (index[2] > 25) and (index[3] > 30) and (
                spots_dict[spot]["wind_window"][0] <= index[4] <= spots_dict[spot]["wind_window"][1]):
                print(f"Yeewww, surf's up in {spot} on",row[:10])
                alarm = 1
        # if any surf is found, display the forecast
        if alarm == 1:
            # in terminal:
            print(data)
            # in jupyter:
            #display(data.style.apply(color_rows, axis=1,args = (spot,spots_dict)))
        # if nothing is found, print a negative message
        if alarm == 0:
            print("Nope, nothing on the horizon :(")
    return None


# test run
alarm()
