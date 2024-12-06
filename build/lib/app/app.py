import streamlit as st
import pandas as pd
from forecast import forecast

st.markdown("""# Welcome to Kook Alarm!
""")

st.write("Click the button below to get a forecast for some surfspots in the Baltic sea:")

if st.button('Get forecast'):
    print('button clicked!')

    # below is the streamlit version of the alarm function from forecast

    spots = { "Kolifornia" : { "lat" : 54.1759, "lon" : 15.5833, "wind_window" : [225,350]} ,
         "Seabridge" : { "lat" : 54.4022 , "lon" : 13.6060 , "wind_window" : [10,170]},
         "Valhalla" : { "lat" : 54.3929, "lon": 13.6803, "wind_window" : [0,45]},
         "Borncold" : { "lat" : 54.1414 , "lon" : 11.7530, "wind_window" : [225,350]}}

    # get wind forecasts
    spots_dict = forecast.get_forecast(spots)

    # loop through surf spots
    for spot in spots_dict.keys():
        # retrieve data for spot
        data = spots_dict[spot]["forecast"]
        # set alarm counter
        alarm = 0

        # check conditions (wind speed/gusts > 25/30 km/h, correct wind direction)
        st.write(f"\n...checking forecast for {spot}...\n")
        for row, index in data.iterrows():
            if (index[2] > 25) and (index[3] > 30) and (
                spots_dict[spot]["wind_window"][0] <= index[4] <= spots_dict[spot]["wind_window"][1]):
                st.write(f"Yeewww, surf's up in {spot} on",row[:10])
                alarm = 1
        # if any surf is found, display the forecast
        if alarm == 1:
            #st.dataframe(data.style.apply(forecast.color_rows, axis=1,args = (spot,spots_dict)),
            #             width=2000, height=320)
            st.table(data.style.apply(forecast.color_rows, axis=1,args = (spot,spots_dict)))
        # if nothing is found, print a negative message
        if alarm == 0:
            st.write("Nope, nothing on the horizon :(")
