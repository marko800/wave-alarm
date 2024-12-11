'''
Here we define functions used for building a forecast alarm for surf (generated by windswell, e.g. in the baltic sea)
'''
import pandas as pd
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import json


# load sensitive data (if local)
#load_dotenv()
#spots = os.getenv("spots")
#spots = json.loads(spots)
#API_key = os.getenv("API_key")



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



def request(API_key,lat,lon):
    # access api, retrieve forecast, return (wind) data in dataframe

    url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly&appid={API_key}'
    df = pd.DataFrame(requests.get(url).json()["daily"])[["dt","sunrise","sunset","wind_speed","wind_gust","wind_deg"]]

    # change unix to normal time
    df.dt = df.dt.apply(lambda x : datetime.utcfromtimestamp(x).strftime('%d-%m-%Y %H:%M:%S'))
    df.sunrise = df.sunrise.apply(lambda x : datetime.utcfromtimestamp(x).strftime('%H:%M'))
    df.sunset = df.sunset.apply(lambda x : datetime.utcfromtimestamp(x).strftime('%H:%M'))

    # convert wind speed and gusts to km/h, and round to int
    df.wind_speed = (df.wind_speed*3.6).round(decimals=0).astype(int)
    df.wind_gust = (df.wind_gust*3.6).round(decimals=0).astype(int)

    # rename columns and set date & time as index
    df.rename({"dt":"date", "wind_speed":"wind_speed (km/h)", "wind_gust":"wind_gust (km/h)","wind_deg":"wind_deg (°)"},axis = 1, inplace=True)
    df = df.set_index(df.date).drop(columns = "date")

    # use windmap to create new column for wind direction
    df["wind_dir"] = df["wind_deg (°)"].apply(lambda x: windmap(x))

    # reorder columns
    new_order = ["wind_speed (km/h)", "wind_gust (km/h)", "wind_dir", "wind_deg (°)", "sunrise", "sunset"]
    df = df[new_order]
    return df



def get_forecast(API_key,spots_dict):
    # retrieve the wind forecast for all locations, spots_dict is a list of locations, saved in secrets.toml/.env

    for spot in spots_dict.keys():
        spots_dict[spot]["forecast"] = request(API_key,spots_dict[spot]["lat"],spots_dict[spot]["lon"])
    return spots_dict



def color_rows(row,spot,spots_dict):
    # highlight rows in the forecast with favourable conditions, color code by strenght of wind

    if (25 < row["wind_speed (km/h)"] <= 30) and (30 < row["wind_gust (km/h)"]) and (
                spots_dict[spot]["wind_window"][0] <= row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]):
        return ['background-color: lightgreen'] * len(row)
    elif (30 < row["wind_speed (km/h)"] <= 40) and (30 < row["wind_gust (km/h)"]) and (
                spots_dict[spot]["wind_window"][0] <= row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]):
        return ['background-color: yellow'] * len(row)
    elif (40 < row["wind_speed (km/h)"] <= 50) and (30 < row["wind_gust (km/h)"]) and (
                spots_dict[spot]["wind_window"][0] <= row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]):
        return ['background-color: lightsalmon'] * len(row)
    elif (50 < row["wind_speed (km/h)"]) and (30 < row["wind_gust (km/h)"]) and (
                spots_dict[spot]["wind_window"][0] <= row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]):
        return ['background-color: lightcoral'] * len(row)
    else:
        return ['background-color: white'] * len(row)
