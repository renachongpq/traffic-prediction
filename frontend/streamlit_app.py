from streamlit_functions import *
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import re
import os

# to run this page: streamlit run streamlit_app.py

# ----------------------- csv files ---------------------------
road_camera_id = pd.read_csv('./utils/road_camera_id.csv')
traffic_stats = pd.read_csv('traffic_stats.csv')

# -------------------------------------------------------------

st.set_page_config(layout="wide")

st.sidebar.title('Traffic Prediction')

project_description = """ <p> Based on live data from LTA Datamall, we display live traffic images of expressways. </p> 
                    <p> Try it out by selecting a road direction you would like to view! </p> """
st.sidebar.markdown(project_description, unsafe_allow_html=True)

major_columns = st.columns((12, 8), gap='large')

with major_columns[0]:
    roads = road_camera_id['road_direction'].values.tolist()
    road_selection = st.selectbox("**Road Direction**", roads, index=0, placeholder='Select road direction to view traffic images')
    image_columns = st.columns(2)
    
    # display traffic images
    folder_road_selection = road_selection.replace('/', '_') # to match folder naming
    original_images = [f for f in os.listdir('./assets/') if os.path.isfile(os.path.join('./assets/', f))]
    jam_pred = []

    for path in os.listdir(os.path.join('./assets/', folder_road_selection)):
        fname, fext = os.path.splitext(path)
        if fext in ('.jpg', '.png'):
            mask_fullpath = os.path.join('./assets', folder_road_selection, path)
            c_id = re.findall(r'\d{4}', fname)[0]
            jam_pred.append(traffic_stats[(traffic_stats['Direction'] == road_selection) & (traffic_stats['Camera_Id'] == int(c_id))]['Jam'].values)

            with image_columns[1]:
                st.image(mask_fullpath, width=350, caption=f'Masked image for camera id: {c_id}')
            with image_columns[0]:
                r = re.compile(f'^{c_id}.*')
                img_path = os.path.join('./assets', list(filter(r.match, original_images))[0])
                st.image(img_path, width=350, caption=f'Camera Id: {c_id}')
    
    jam_status = "Jam" if sum(jam_pred) > len(jam_pred)//2 else "No Jam"
    jam_prediction_md = f"""<p style='text-align: center; font-size: 110%;'><b> Prediction: {jam_status} <b></p>
                        <p style='text-align: center; font-size: 90%'><em> Last updated at: ... <em></p>"""
    st.markdown(jam_prediction_md, unsafe_allow_html=True)

with major_columns[1]:
    m = plot_map(road_selection)
    st.markdown("#") # to align the map lower
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