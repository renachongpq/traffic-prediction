from src.api_calls import ApiCall
from src.vehicle_count import VehicleCount
import os


class Main:
    def update_stats(self):
        # needs to be full directory
        dir = '/app'
        api_call = ApiCall(dir)
        # downloads into api_data folder in your specified dir
        api_call.download_images()

        weights = dir + '/utils/vehicle_detector.pt'
        images_dir = dir + '/assets'
        roi_df = dir + '/utils/roi_masks.csv'
        lat_long = dir + '/utils/camera_id_lat_long.csv'

        # change back to directory containing dnn weights
        os.chdir(dir)
        vc = VehicleCount(weights, images_dir, roi_df, lat_long, dir)
        traffic_stats = vc.predict_vehicle_count()
        with open('traffic_stats.csv', 'a') as f:
            traffic_stats.to_csv(f, mode='a', index=False,
                                 header=f.tell() == 0)
