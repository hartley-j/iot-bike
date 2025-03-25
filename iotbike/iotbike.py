
import requests
import time
import cv2
import base64

from iotbike import objectdetection
from iotbike import sensorhandler

def api_post(data, suffix, url="http://joehartley.pythonanywhere.com"):

    response = requests.post(url + suffix, json=data)

    return response

def api_get(suffix, url="http://joehartley.pythonanywhere.com"):
    response = requests.get(url + suffix)
    return response


def main(pi=True, source=0):

    try:

        detector = objectdetection.ObjectDetection()

        sensors = sensorhandler.SensorHandler(src=int(source), pi=pi)
        sensors.start()
        sensor_data = sensors.read()

        sentry_mode = False

        api_post({"sentry_mode": sentry_mode, "latitude":sensor_data["latitude"], "longitude":sensor_data["longitude"], "objects": 0}, "/api/bike")
        response = api_get("/api/bike")

        if response.ok:
            server_data = response.json()
        else:
            raise Exception(f"Something was wrong with POSTing data to the webserver. \n{response.text}")

        close_flag = True
        frame_rate = 30
        prev = 0

        while close_flag:

            time_elapsed = time.time() - prev
            
            sensor_data = sensors.read()
            response = api_get("/api/bike")
            
            if response.ok:
                server_data = response.json()
            else:
                raise Exception(response.text)

            sentry_mode = bool(server_data["bike_status"]["sentry_mode"])
            
            if time_elapsed > 1. / frame_rate:
                prev = time.time()
                
                output = detector.detect_filtered(sensor_data["frame"], 0.8)
                boxes_frame = output.draw_boxes()

                num_objects = output.get_objects()
                if num_objects > 0:
                    object_flag = True

                    ret, frame_buffer = cv2.imencode(".jpg",boxes_frame)
                    api_post({"image": base64.b64encode(frame_buffer)}, "/api/image")

                    print(f"Found {num_objects} objects.")
                else:
                    object_flag = False

            if object_flag or sensor_data["is_moving"]:

                # TODO: add code for sending alert(s)

                continue

            post = {"sentry_mode": sentry_mode, "latitude": sensor_data["latitude"], "longitude": sensor_data["longitude"], "objects": num_objects}
            print(post)
            api_post(post, "/api/bike")
            response = api_get("/api/bike")

            if response.ok:
                response = response.json()

    finally:
        sensors.stop()
