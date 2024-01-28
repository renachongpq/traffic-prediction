FROM renachongpq/dsa3101_proj_base:latest
WORKDIR /app
COPY flask_app.py flask_app.py

COPY api_calls.py src/api_calls.py
COPY ../main.py main.py
COPY vehicle_count.py src/vehicle_count.py
COPY ../utils/roi_masks.csv roi_masks.csv
COPY ../utils/camera_id_lat_long.csv camera_id_lat_long.csv
COPY ../utils/training_data.csv training_data.csv
COPY ../utils/vehicle_detector.pt vehicle_detector.pt

ENV FLASK_APP flask_app
ENTRYPOINT ["/usr/bin/python3", "/app/flask_app.py"]

