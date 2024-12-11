import streamlit as st
import pandas as pd
from forecast import forecast


st.set_page_config(page_title="Check your spot", page_icon="🏄‍♂️")

# retrieves forecast for location specified by user

st.write("Enter your spot's coordinates:")

lat = st.number_input('Insert latitude', format="%.6f")
lon = st.number_input('Insert longitude', format="%.6f")

# check for valid input, then use lat and lon as input for request function and display result

if -90 <= lat <= 90 and -180 <= lon <= 180:
    if st.button('View forecast'):
        print('button clicked!')

        API_key = st.secrets["general"]["API_key"]
        st.table(forecast.request(API_key, lat, lon))
else:
    st.error("Wrong input. Enter valid latitude (-90 to 90) and longitude (-180 to 180).")
