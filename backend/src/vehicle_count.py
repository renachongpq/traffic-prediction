import cv2
import os
from vehicle_detector import VehicleDetector
import pandas as pd
import ast
import numpy as np
from math import radians, cos, sin, asin, sqrt
import datetime
from ultralytics import YOLO


class VehicleCount:
    def __init__(self, weights, images, image_roi_df, cam_lat_long):
        self.images = [os.path.join(images, image)
                       for image in os.listdir(images)]
        self.image_roi_df = pd.read_csv(image_roi_df)
        self.cam_lat_long = pd.read_csv(cam_lat_long)
        self.model = YOLO(weights)

    def __roi(self, img, coords):
        x = int(img.shape[1])
        y = int(img.shape[0])
        if len(coords) < 4:
            print("minimum 4 coordinates required")
            return
        shape = np.array(coords)  # Shape of roi
        mask = np.zeros_like(img)  # np array with zeros (of image dimension)

        # Creates a polygon with the mask colour (blue), areas not in roi would be black (pixel is 0)
        cv2.fillPoly(mask, pts=np.int32([shape]), color=(255, 255, 255))

        # Select areas where mask pixels are not zero
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image

    # Distance between 2 geographical locations
    def __distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance in meters between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Radius of earth in meters.
        r = 6.371e6
        return c * r

    # Finds index of speedband df where the corresponding Lat long is closest to given camera coordinates
    def __closest(self, data, cam_coords):
        lat_long = min(
            data,
            key=lambda p: self.__distance(
                cam_coords["Latitude"],
                cam_coords["Longitude"],
                p["AvgLat"],
                p["AvgLon"],
            )
        )
        index = data.index(lat_long)
        distance = self.__distance(
            cam_coords["Latitude"],
            cam_coords["Longitude"],
            lat_long["AvgLat"],
            lat_long["AvgLon"],
        )
        return [index, lat_long, distance]

    def __time_in_range(self, start, end, x):
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end

    def __is_weekday(self, image_datetime):
        day = image_datetime.weekday()
        if day < 5:  # Monday(0) to Friday(4)
            return 1
        return 0

    def __is_peak(self, image_datetime):
        peak_hours = [
            {"Start": datetime.time(8, 0, 0), "End": datetime.time(10, 0, 0)},
            {"Start": datetime.time(18, 0, 0),
             "End": datetime.time(20, 30, 0)},
        ]
        is_peak_bool = False
        for peak_hour in peak_hours:
            if is_peak_bool:
                break
            start, end = peak_hour.get("Start"), peak_hour.get("End")
            is_peak_bool = self.__time_in_range(
                start, end, image_datetime.time())
        if is_peak_bool:
            return 1
        return 0

    def predict_vehicle_count(self):
        result_list = []
        for img_path in self.images:
            camera_id = int(img_path.split("\\")[-1].split("_")[0])
            timestamp = img_path.split("\\")[-1].split("_")[2]
            image_datetime = datetime.datetime.strptime(
                timestamp, "%Y%m%d%H%M%S")
            is_peak = self.__is_peak(image_datetime)
            is_weekday = self.__is_weekday(image_datetime)
            rois = self.image_roi_df[self.image_roi_df.Camera_Id == camera_id]
            # Coordinates of cam {Latitude: ..., Longitude: ...}
            cam_coords = (
                self.cam_lat_long[self.cam_lat_long.CameraID == camera_id]
                .iloc[:, -2:]
                .to_dict("records")[0]
            )
            img = cv2.imread(img_path)
            for i in range(len(rois)):
                roi_coords = ast.literal_eval(rois.iloc[i, 1])
                direction = rois.iloc[i, 2]
                roi_img = self.__roi(img, roi_coords)
                result = self.model.predict(roi_img, conf=0.5, iou=0.8)[0]
                vehicle_count = len(result.boxes.xyxy)
                density = vehicle_count / (0.100 * 3)
                jam = 1 if density >= 23.33 else 0
                result_list.append(
                    [
                        camera_id,
                        direction,
                        vehicle_count,
                        density,
                        image_datetime.date(),
                        image_datetime.time(),
                        cam_coords.get("Latitude"),
                        cam_coords.get("Longitude"),
                        is_weekday,
                        is_peak,
                        jam
                    ]
                )
        result_df = pd.DataFrame(
            result_list,
            columns=[
                "Camera_Id",
                "Direction",
                "Vehicle_Count",
                "Density",
                "Date",
                "Time",
                "Latitude",
                "Longitude",
                "Is_Weekday",
                "Is_Peak",
                "Jam"
            ],
        )
        return result_df

"""
images_dir = r'C:\Users\User\Desktop\DSO\traffic-prediction\backend\data\images\test'
roi_df = r'C:\Users\User\Desktop\DSO\traffic-prediction\backend\image-processing\roi_masks.csv'
lat_long = r'C:\Users\User\Desktop\DSO\traffic-prediction\backend\src\camera_id_lat_long.csv'
weights = r'C:\Users\User\Desktop\DSO\traffic-prediction\backend\results\runs\detect\train3\weights\best.pt'

# change back to directory containing dnn weights
vc = VehicleCount(weights, images_dir, roi_df, lat_long)
traffic_stats = vc.predict_vehicle_count()
with open('traffic_stats.csv', 'a') as f:
    traffic_stats.to_csv(f, mode='a', index=False,
                         header=f.tell() == 0)
"""