import streamlit as st
import pandas as pd

import sys
import os
# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from forecast import forecast



st.set_page_config(
    page_title="Kook Alarm",
    page_icon="🏄‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)


with st.sidebar:
    st.write("[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/marko800/wave-alarm)")





st.title("""Welcome to Kook Alarm!
""")


st.write("Click the button below to get alarmed for some surfspots in the Baltic sea:")


if st.button('Get pitted'):
    print('button clicked!')

    # below is the streamlit version of the alarm function from forecast

    #load API key and sensitive data from secrets.toml and convert it to dictionary
    API_key = st.secrets["general"]["API_key"]
    spots_raw = st.secrets["general"]["spots"]
    spots = {name: {
                    "lat": spot["lat"],
                    "lon": spot["lon"],
                    "wind_window": spot["wind_window"],
                    }  for name, spot in spots_raw.items()}

    # get wind forecasts
    spots_dict = forecast.get_forecast(spots)

    # loop through surf spots
    for spot in spots_dict.keys():
        # retrieve data for spot
        data = spots_dict[spot]["forecast"]
        # set alarm counter
        alarm = 0

        # check conditions (wind speed/gusts > 25/30 km/h, correct wind direction)
        st.write("")
        st.write(f"... checking forecast for {spot} ...")
        st.write("")
        for row, index in data.iterrows():
            if (index[2] > 25) and (index[3] > 30) and (
                spots_dict[spot]["wind_window"][0] <= index[4] <= spots_dict[spot]["wind_window"][1]):
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
# add spot Nohoney (window = [0,80] or 2 windows or [27^0,80]?)
