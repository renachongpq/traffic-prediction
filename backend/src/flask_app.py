from flask import Flask, jsonify, request, send_file
import pandas as pd
import os
from main import Main
import time
import datetime
import pickle
import json
import urllib
import urllib.request
from urllib.parse import urlparse
import httplib2 as http  # external library
from io import BytesIO
import zipfile
import threading

app = Flask(__name__)


def wait_for_file(file_path, timeout=60):
    start_time = time.time()
    while not os.path.exists(file_path):
        if time.time() - start_time > timeout:
            return False
        time.sleep(1)
    return True


@app.route("/live_image", methods=["GET"])
def return_live_image():
    camera_id = request.args.get('camera_id')
    images = './assets'
    img_paths = [os.path.join(images, image) for image in os.listdir(
        images) if image.endswith(".jpg")]
    for img_path in img_paths:
        img_id = int(img_path.split("/")[-1].split("_")[0])
        if int(camera_id) == img_id:
            return send_file(img_path)

# to be updated when finalised


@app.route("/assets", methods=["GET"])
def return_original_images():
    images = f'./assets'
    img_paths = [os.path.join(images, image) for image in os.listdir(
        images)]
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for img_path in img_paths:
            zip_file.write(img_path, os.path.basename(img_path))

    zip_buffer.seek(0)

    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="assets.zip")


@app.route("/roi_image", methods=["GET"])
def return_roi_image(road_direction):
    road_direction = road_direction.replace("/", "_")
    images = f'./assets/{road_direction}'
    img_paths = [os.path.join(images, image) for image in os.listdir(
        images) if image.endswith(".jpg")]
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for img_path in img_paths:
            zip_file.write(img_path, os.path.basename(img_path))

    zip_buffer.seek(0)

    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name=f"{road_direction}_images.zip")


@app.route("/roi_jam_info", methods=["GET"])
def return_roi_jam_info(road_direction):
    road_direction = road_direction.replace("/", "_")
    texts = f'./assets/{road_direction}'
    text_paths = [os.path.join(texts, text) for text in os.listdir(
        texts) if text.endswith(".txt")]
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for text_path in text_paths:
            zip_file.write(text_path, os.path.basename(text_path))

    zip_buffer.seek(0)

    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name=f"{road_direction}_texts.zip")


@app.route("/traffic_stats", methods=["GET"])
def return_traffic_stats():
    stats = './traffic_stats.csv'
    if wait_for_file(stats):
        return send_file(stats, as_attachment=True)
    else:
        return "Timeout: CSV file not found", 404


"""
@app.route("/stats", methods=["GET"])
def get_stats():
    camera_id = request.args.get('camera_id')
    df = pd.read_csv('traffic_stats.csv')
    match_df = df.loc[df['Camera_Id'] == int(camera_id)]
    result_df = match_df[['Density', 'Average_Speed',
                          'Direction', 'Jam', 'Date', 'Time']]
    return jsonify(result_df.to_dict(orient="records"))

# for past data
# to update to GET if filtering is required


@app.route("/archive")
def return_past_data():
    df = pd.read_csv('traffic_stats.csv')
    return jsonify(df.to_dict(orient="records"))

# for prediction based on user input


@app.route("/prediction", methods=["GET"])
def make_prediction():
    time = request.args.get('time')
    date = request.args.get('date')
    camera_id = int(request.args.get('camera_id'))
    road = request.args.get('road')
    model = pickle.load(open("model.pkl", "rb"))
    result = model.predict(camera_id, road, date, time)
    if result == 0:
        return jsonify({'prediction': 'No Jam'})
    elif result == 1:
        return jsonify({'prediction': 'Jam'})
"""


@app.route("/")
def run_main():
    main = Main()
    while True:
        startTime = datetime.datetime.now()
        print(f'{startTime}: Updating traffic stats...')
        main.update_stats()
        print(
            f'Stats updated. Time taken: {datetime.datetime.now() - startTime} minutes')
        print('Resting for 15 minutes...')
        time_wait = 15
        time.sleep(time_wait * 60)


"""
@app.route("/incidents")
def get_incidents():
    traffic_incidents = pd.read_csv('./assets/incidents.csv')
    return jsonify(traffic_incidents.to_dict(orient="records"))
"""


def start_run_main_thread():
    run_main_thread = threading.Thread(target=run_main)
    # Daemonize the thread so it stops when the main program exits
    run_main_thread.daemon = True
    run_main_thread.start()


# Start run_main() in a separate thread
start_run_main_thread()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
