import streamlit as st
import pandas as pd
from forecast import forecast
from dotenv import load_dotenv
import os
import json

st.set_page_config(page_title="View forecast", page_icon="🏄‍♂️")


st.write("Click the button to see full forecast for all spots.")


if st.button('Get pitted'):
    print('button clicked!')

    # retrieve data and display every forecast, one by one

    load_dotenv()
    spots = os.getenv("spots")
    spots = json.loads(spots)

    # get wind forecasts
    spots_dict = forecast.get_forecast(spots)

    # loop through surf spots
    for spot in spots_dict.keys():
        # retrieve data for spot
        data = spots_dict[spot]["forecast"]

        st.write(f"{spot}:")
        st.table(data)
        #.style.apply(forecast.color_rows, axis=1,args = (spot,spots_dict)))
