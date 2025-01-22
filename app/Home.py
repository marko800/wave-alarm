import streamlit as st
import pandas as pd
from datetime import time
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

    #load spots data from secrets.toml and convert spots to dictionary
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
        # retrieve data for spot, format "time" to datetime
        data = spots_dict[spot]["forecast"]
        data["time"] = pd.to_datetime(data["time"], format='%H:%M').dt.time

        # set alarm counter
        alarm = 0

        # if surf is found, we display only relevant rows of the forecast
        surf_rows = []

        # check conditions (wind speed/gusts > 25/30 km/h, correct wind direction) in two consecutive rows
        for row in range(len(data)-1):
            current_row = data.iloc[row]
            next_row = data.iloc[row + 1]

            if (current_row["time"] >= time(5,0)) and (current_row["time"] <= time(23,0)) and (
                current_row["wind_speed (km/h)"] > 25) and (current_row["wind_gusts (km/h)"] > 30) and (
                spots_dict[spot]["wind_window"][0] <= current_row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]) and (
                next_row["wind_speed (km/h)"] > 25) and (next_row["wind_gusts (km/h)"] > 30) and (
                spots_dict[spot]["wind_window"][0] <= next_row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]
                ):
                alarm = 1
                surf_rows.append(row)

        # if any surf is found, display the relevant part of the forecast
        if alarm == 1:
            st.write(f"Yeewww, surf's up in {spot}:")

            start_row = min(surf_rows)
            end_row = max(surf_rows)
            surrounding_rows = data.iloc[max(0, start_row - 2) : min(len(data), end_row + 4)]

            # display time correctly
            surrounding_rows["time"] = surrounding_rows["time"].apply(lambda t: t.strftime('%H:%M'))

            st.table(surrounding_rows.style.apply(forecast.color_rows, axis=1, args=(spot, spots_dict)))

        # if nothing is found, print a negative message
        else:
            st.write(f"Nope, nothing on the horizon for {spot}.")
            st.write("")
