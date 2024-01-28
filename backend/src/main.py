from api_calls import ApiCall
from vehicle_count import VehicleCount
import os


class Main:
    def update_stats(self):
        # needs to be full directory
        dir = '/app'
        api_call = ApiCall(dir)
        # downloads into api_data folder in your specified dir
        api_call.download_images()

        weights = dir + 'best.pt'
        images_dir = dir + '/assets/*.jpg'
        roi_df = dir + '/Image_ROI.csv'
        lat_long = dir + '/camera_id_lat_long.csv'

        # change back to directory containing dnn weights
        os.chdir('/app')
        vc = VehicleCount(weights, images_dir, roi_df, lat_long)
        traffic_stats = vc.predict_vehicle_count()
        with open('traffic_stats.csv', 'a') as f:
            traffic_stats.to_csv(f, mode='a', index=False,
                                 header=f.tell() == 0)
