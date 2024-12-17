import sys
import os

# add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import streamlit as st
import pandas as pd

from forecast import forecast



st.set_page_config(
    page_title="Kook Alarm",
    page_icon="🏄‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)


with st.sidebar:
    st.write("[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/marko800/wave-alarm)")



st.title("Welcome to Kook Alarm!")

st.write("Click the button below to get alarmed for some surfspots in the Baltic sea:")


if st.button('Get pitted'):
    print('button clicked!')

    # retrieve forecast for all locations, add to dictionary of spots and conditions, then check for surf

    #load API key and spots data from secrets.toml and convert spots to dictionary
    API_key = st.secrets["general"]["API_key"]
    spots_raw = st.secrets["general"]["spots"]
    spots = {name: {
                    "lat": spot["lat"],
                    "lon": spot["lon"],
                    "wind_window": spot["wind_window"],
                    }  for name, spot in spots_raw.items()}

    # get wind forecasts
    spots_dict = forecast.get_forecast(API_key,spots)

    # loop through surf spots
    for spot in spots_dict.keys():
        # retrieve data for spot
        data = spots_dict[spot]["forecast"]

        # reorder columns, should be done by get_forecast / request, but somehow doesn't work
        new_order = ["wind_speed (km/h)", "wind_gust (km/h)", "wind_dir", "wind_deg (°)", "sunrise", "sunset"]
        data = data[new_order]

        # set alarm counter
        alarm = 0

        # check conditions (wind speed/gusts > 25/30 km/h, correct wind direction)
        st.write("")
        st.write(f"... checking forecast for {spot} ...")
        st.write("")
        for row, index in data.iterrows():
            if (index["wind_speed (km/h)"] > 25) and (index["wind_gust (km/h)"] > 30) and (
                spots_dict[spot]["wind_window"][0] <= index["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]):
                alarm = 1
        # if any surf is found, display the forecast
        if alarm == 1:
            #st.dataframe(data.style.apply(forecast.color_rows, axis=1,args = (spot,spots_dict)),
            #             width=2000, height=320)
            st.write(f"Yeewww, surf's up in {spot} :")
            st.table(data.style.apply(forecast.color_rows, axis=1,args = (spot,spots_dict)))
        # if nothing is found, print a negative message
        if alarm == 0:
            st.write("Nope, nothing on the horizon :(")
            st.write("")


# TODO:
# add spot Nohoney (window = [0,80] or 2 windows or [270,80]?)
# display wind direction as arrow
