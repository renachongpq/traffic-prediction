from streamlit_functions import *
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import re
import os
import requests
import time
import zipfile
import io
from datetime import datetime
import shutil

# to run this page: streamlit run streamlit_app.py
st.set_page_config(layout="wide")

flask_url = "http://backend:5000"

# ----------------------- Helper functions ---------------------------

# Store the last update time
last_update_time = None


def fetch_traffic_stats(flask_url):
    try:
        response = requests.get(f'{flask_url}/traffic_stats')
        if response.status_code == 200:
            # Parse CSV data into a DataFrame
            traffic_stats_df = pd.read_csv(io.BytesIO(response.content))
            return traffic_stats_df
        else:
            st.error(
                f"Failed to fetch traffic stats. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching traffic stats: {str(e)}")
        return None


def download_assets():
    global last_update_time
    try:
        # Check if assets folder exists and clear it if it does
        if os.path.exists("assets"):
            shutil.rmtree("assets")
        response = requests.get(f'{flask_url}/assets')
        if response.status_code == 200:
            # Save the zip file
            with open("assets.zip", "wb") as f:
                f.write(response.content)
            # Extract the zip file
            with zipfile.ZipFile("assets.zip", "r") as zip_ref:
                zip_ref.extractall("assets")
            st.success("Original images downloaded and extracted successfully.")
            # Update the last update time
            last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            st.error(
                f"Failed to download original images. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error downloading original images: {str(e)}")


def display_traffic_images_and_predictions(road_selection, traffic_stats):
    image_columns = st.columns(2)

    # Display traffic images and predictions
    folder_road_selection = road_selection.replace('/', '_').upper()
    original_images = [f for f in os.listdir(
        './assets/') if os.path.isfile(os.path.join('./assets/', f))]
    jam_pred = []

    for path in os.listdir(os.path.join('./assets/', folder_road_selection)):
        fname, fext = os.path.splitext(path)
        if fext in ('.jpg', '.png'):
            mask_fullpath = os.path.join(
                './assets', folder_road_selection, path)
            c_id = re.findall(r'\d{4}', fname)[0]
            jam_pred.extend(traffic_stats[(traffic_stats['Direction'] == road_selection) & (
                traffic_stats['Camera_Id'] == int(c_id))]['Jam'].values)

            with image_columns[1]:
                st.image(mask_fullpath, width=350,
                         caption=f'Masked image for camera id: {c_id}')
            with image_columns[0]:
                r = re.compile(f'^{c_id}.*')
                img_path = os.path.join(
                    './assets', list(filter(r.match, original_images))[0])
                st.image(img_path, width=350, caption=f'Camera Id: {c_id}')

    jam_status = "Jam" if sum(jam_pred) > len(jam_pred)//2 else "No Jam"
    jam_prediction_md = f"""<p style='text-align: center; font-size: 110%;'><b> Prediction: {jam_status} <b></p>"""
    st.markdown(jam_prediction_md, unsafe_allow_html=True)
    if last_update_time:
        last_updated_html = f"""<p style='text-align: center; font-size: 90%'><em> Last updated at: {last_update_time} <em></p>"""
        st.markdown(last_updated_html, unsafe_allow_html=True)
    else:
        st.markdown(
            "<p style='text-align: center; font-size: 90%'><em> Last updated at: Not available <em></p>", unsafe_allow_html=True)


# ----------------------- csv files ---------------------------
road_camera_id = pd.read_csv('./utils/road_camera_id.csv')


# Fetch traffic stats with retries
traffic_stats = fetch_traffic_stats(flask_url)

if traffic_stats is None:
    st.error("Failed to fetch traffic stats. Please try again later.")

# download_assets()

# ----------------------- sidebar ---------------------------

st.sidebar.title('Traffic Prediction')

project_description = """ <p> Based on live data from LTA Datamall, we display live traffic images of expressways. </p> 
                    <p> Try it out by selecting a road direction you would like to view! </p> """
st.sidebar.markdown(project_description, unsafe_allow_html=True)

if st.sidebar.button("Refresh Assets"):
    download_assets()

# ----------------------- main ---------------------------

major_columns = st.columns((12, 8), gap='large')

with major_columns[0]:
    roads = road_camera_id['road_direction'].values.tolist()
    road_selection = st.selectbox("**Road Direction**", roads, index=0,
                                  placeholder='Select road direction to view traffic images')

    # Call the function to display traffic images and predictions
    display_traffic_images_and_predictions(road_selection, traffic_stats)

with major_columns[1]:
    m = plot_map(road_selection)
    st.markdown("#")  # to align the map lower
    st.markdown("#")
    folium_static(m, width=500, height=400)
    st.markdown("<p style='text-align: center; font-size: 90%'><em> Hover over the markers to view the camera id <em></p>", unsafe_allow_html=True)


# styling below
style = """
    <style>
    div[class*=stSelectbox] p {
        font-size: 130%;
    }
    </style>
"""
st.write(style, unsafe_allow_html=True)
