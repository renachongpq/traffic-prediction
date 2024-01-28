import pandas as pd
import ast
import folium

def get_camera_lat_long(road_selection):
    road_camera_df = pd.read_csv('./backend/src/road_camera_id.csv')
    cam_lat_long_df = pd.read_csv('./backend/src/camera_id_lat_long.csv')

    camera_id = road_camera_df[road_camera_df['road_direction'] ==  road_selection]['camera_id'].values[0]
    camera_id = ast.literal_eval(camera_id) # convert string representation of list to list
    lat_long_df = cam_lat_long_df[cam_lat_long_df['CameraID'].isin(camera_id)]
    return lat_long_df

def plot_map(road_direction=None):
    sg_lat_long = {'latitude': 1.3521, 'longitude': 103.8198}
    m = folium.Map(location=[sg_lat_long['latitude'], sg_lat_long['longitude']], 
                zoom_start=11, control_scale=True)
    
    # add camera to map
    if road_direction:
        lat_long_df = get_camera_lat_long(road_direction)
        for i, row in lat_long_df.iterrows():
            # iframe = folium.IFrame('Camera ID:' + str(int(row['CameraID']))) # content of popup
            # popup = folium.Popup(iframe, min_width=100, max_width=150) # initialise popup
            folium.Marker(location=[row['Latitude'], row['Longitude']], tooltip='Camera ID:' + str(int(row['CameraID']))).add_to(m)
    return m
