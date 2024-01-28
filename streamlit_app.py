import streamlit as st
import pandas as pd

# st.set_page_config(
#     page_title="Page 1",
# )

# st.sidebar.header("Page 1")

###################################################################
# csv files
road_camera_id = pd.read_csv('./backend/src/road_camera_id.csv')


###################################################################

st.set_page_config(layout="wide")

st.header('Singapore Traffic Prediction')

major_columns = st.columns(2)

with major_columns[0]:
    roads = road_camera_id['road_direction'].values.tolist()
    st.selectbox("**Road Direction**", roads, index=None, placeholder='Select road direction...')
    image_columns = st.columns(2)
    with image_columns[0]:
        st.image(['blank_test_image.png'], width=300, caption=['Road camera 1'])
    with image_columns[1]:
        st.image(['blank_test_image.png'], width=300, caption=['Road camera 2'])
    st.markdown("<p style='text-align: center; font-size: 110%;'><b> Prediction: Jam / No Jam <b></p> <p style='text-align: center'><em> Last updated at: ... <em></p>", unsafe_allow_html=True)


with major_columns[1]:
    st.map()


# css styling below
css = """
    <style>
    div[class*=stSelectbox] p {
        font-size: 130%
    }
    <style>
"""
st.write(css, unsafe_allow_html=True)