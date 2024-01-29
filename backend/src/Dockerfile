FROM renachongpq/dsa3101_proj_base:latest
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY flask_app.py flask_app.py

COPY main.py main.py
COPY api_calls.py src/api_calls.py
COPY vehicle_count.py src/vehicle_count.py
COPY roi_masks.csv utils/roi_masks.csv
COPY camera_id_lat_long.csv utils/camera_id_lat_long.csv
COPY vehicle_detector.pt utils/vehicle_detector.pt
COPY __init__.py src/__init__.py

ENV FLASK_APP flask_app
ENTRYPOINT ["/usr/bin/python3", "/app/flask_app.py"]

