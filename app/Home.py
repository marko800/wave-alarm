import streamlit as st
import pandas as pd
from datetime import datetime, timezone
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

st.write('''This app calls every hour a wind forecast from [Open-Meteo](https://open-meteo.com/) for a list of spots in the Baltic.
         If conditions for surf are found, it displays the relevant part of the forecast. Let's get pitted!''')



# load spots data from secrets.toml
spots_raw = st.secrets["general"]["spots"]
spots = {
    name: {
        "lat": spot["lat"],
        "lon": spot["lon"],
        "wind_window": spot["wind_window"],
    }
    for name, spot in spots_raw.items()
}

# function to fetch forecast automatically
@st.cache_data(ttl=1 * 60 * 60)
def fetch_forecast():
    '''
    retrieve and process forecasts every hour
    '''

    # get wind forecasts
    spots_dict = forecast.get_forecast(spots)

    # store the timestamp
    last_updated = datetime.now(timezone.utc).isoformat()

    # loop through each spot and save results
    results = {}
    for spot, spot_data in spots_dict.items():

        # retrieve data
        data = spot_data["forecast"]

        # set alarm counter
        alarm = 0

        # if surf is found, we display only relevant rows of the forecast
        surf_rows = []

        # check conditions (wind speed/gusts > 25/30 km/h, correct wind direction) in two consecutive rows
        for row in range(len(data) - 1):
            current_row = data.iloc[row]
            next_row = data.iloc[row + 1]

            if (
                current_row["wind_speed (km/h)"] > 25
                and current_row["wind_gusts (km/h)"] > 30
                and spots_dict[spot]["wind_window"][0] <= current_row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]
                and next_row["wind_speed (km/h)"] > 25
                and next_row["wind_gusts (km/h)"] > 30
                and spots_dict[spot]["wind_window"][0] <= next_row["wind_deg (°)"] <= spots_dict[spot]["wind_window"][1]
            ):
                alarm = 1
                surf_rows.append(row)

        # store results
        if alarm == 1:
            start_row = min(surf_rows)
            end_row = max(surf_rows)
            surrounding_rows = data.iloc[max(0, start_row - 2) : min(len(data), end_row + 4)]
            results[spot] = surrounding_rows
        else:
            results[spot] = None

    return results, last_updated

# retrieve cached data
forecast_results, last_updated_utc = fetch_forecast()

# display results
for spot, forecast_data in forecast_results.items():
    if forecast_data is not None:
        st.write(f"🌊 Yeewww, surf's up in {spot}:")
        st.write(forecast_data.style.apply(forecast.color_rows, axis=1, args=(spot, spots)).to_html(escape=False), unsafe_allow_html=True)
    else:
        st.write(f"Nothing on the horizon for {spot}.")
st.write(f"Last updated: {datetime.fromisoformat(last_updated_utc).strftime('%Y-%m-%d %H:%M:%S')}")
