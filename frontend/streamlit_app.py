from streamlit_functions import *
import streamlit as st
from streamlit_folium import folium_static
import pandas as pd

# to run this page: streamlit run streamlit_app.py

# ----------------------- csv files ---------------------------
road_camera_id = pd.read_csv('./backend/src/road_camera_id.csv')

# -------------------------------------------------------------

st.set_page_config(layout="wide")

st.sidebar.title('Traffic Prediction')

project_description = """ <p> Based on live data from LTA Datamall, we display live traffic images of expressways. </p> 
                    <p> Try it out by selecting a road direction you would like to view! </p> """
st.sidebar.markdown(project_description, unsafe_allow_html=True)

major_columns = st.columns(2, gap='large')

with major_columns[0]:
    roads = road_camera_id['road_direction'].values.tolist()
    road_selection = st.selectbox("**Road Direction**", roads, index=0, placeholder='Select road direction to view traffic images')
    image_columns = st.columns(2)
    with image_columns[0]:
        st.image(['blank_test_image.png'], width=300, caption=['Road camera 1'])
    with image_columns[1]:
        st.image(['blank_test_image.png'], width=300, caption=['Road camera 2'])
    
    jam_prediction_md = "<p style='text-align: center; font-size: 110%;'><b> Prediction: Jam / No Jam <b></p> <p style='text-align: center; font-size: 90%'><em> Last updated at: ... <em></p>"
    st.markdown(jam_prediction_md, unsafe_allow_html=True)

with major_columns[1]:
    m = plot_map(road_selection)
    folium_static(m, width=600, height=500)
    st.markdown("<p style='text-align: center; font-size: 90%'><em> Hover over the markers to view the camera id <em></p>", unsafe_allow_html=True)

# css styling below
css = """
    <style>
    div[class*=stSelectbox] p {
        font-size: 130%
    }
    <style>
"""
st.write(css, unsafe_allow_html=True)