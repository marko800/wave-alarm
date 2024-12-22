import streamlit as st
import pandas as pd
from forecast import forecast



st.set_page_config(page_title="View forecast", page_icon="🏄‍♂️")


st.write("Click the button to see full forecast for all spots.")


if st.button('View forecast'):
    print('button clicked!')

    # retrieve data and display every forecast, one by one

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

        st.write(f"{spot}:")
        st.table(data)
        #.style.apply(forecast.color_rows, axis=1,args = (spot,spots_dict)))
