
import requests
import time
import cv2
import base64
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2

from iotbike import objectdetection
from iotbike import sensorhandler

def api_post(data, suffix, url="http://joehartley.pythonanywhere.com"):
    
    response = requests.post(url + suffix, json=data)

    if not(response.ok):
        raise Exception(f"{datetime.now().isoformat()} Error posting data to the api: {response.text}")
    else:
        return response.json()

def api_get(suffix, url="http://joehartley.pythonanywhere.com"):
    
    response = requests.get(url + suffix)

    if not(response.ok):
        raise Exception(f"{datetime.now().isoformat()} Error getting data from the api: {response.text}")
    else:
        return response.json()

def log(message):
    print(f"{datetime.now().isoformat()} {message}")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c  # Distance in meters


def is_outside_tolerance(coord1, coord2, tolerance=10):
    distance = haversine(coord1[0], coord1[1], coord2[0], coord2[1])
    return distance > tolerance


def main(source=0, pi=True):

    try:
        
        log("Initialising sensors and object detector")

        detector = objectdetection.ObjectDetection()

        sensors = sensorhandler.SensorHandler(src=int(source), pi=pi)
        sensors.start()
        sensor_data = sensors.read()

        saved_coord = (None, None)

        log("Uploading initial data to api")

        sentry_mode = False

        movement_flag = False
        object_flag = False
        coord_flag = False

        bike_status = {
            "sentry_mode": sentry_mode, 
            "latitude": sensor_data["latitude"], 
            "longitude": sensor_data["longitude"],
            "objects": None
        }
        log(f"Initial data being sent: {bike_status}")
        api_post(bike_status, "/api/bike")

        flags = {
            "movement_flag": movement_flag,
            "object_flag": object_flag,
            "coord_flag": coord_flag
        }
        log(f"Initial flags being send: {flags}")
        api_post(flags, "/api/alerts")

        log("Initialisation completed, now entering loop")

        people_counter = 0

        close_flag = True
        while close_flag:

            sensor_data = sensors.read()
            bike_status = api_get("/api/bike")["bike_status"]
            sentry_mode = bool(bike_status["sentry_mode"])

            flags = api_get("/api/alerts")["alerts"]

            movement_flag = flags["movement_flag"]
            object_flag = flags["object_flag"]
            coord_flag = flags["coord_flag"]


            if sentry_mode and not all(saved_coord):
                saved_coord = (sensor_data["latitude"], sensor_data["longitude"])
            elif sentry_mode and is_outside_tolerance(saved_coord, (sensor_data["latitude"], sensor_data["longitude"])):
                coord_flag = True
            elif not sentry_mode and saved_coord:
                saved_coord = (None, None)
                coord_flag = False
            else:
                coord_flag = False


            detection_output = detector.detect_filtered(sensor_data["frame"], 0.9)
            num_people = detection_output.get_people()

            if num_people > 0:
                # object_flag = True
                people_counter += 1

                capture_frame = detection_output.draw_boxes()
                ret, buffer = cv2.imencode(".jpg", capture_frame)
                api_post({"image": base64.b64encode(buffer)}, "/api/image")

                log(f"Found {num_people} people in current frame -- uploaded frame to api")
            else:
                # object_flag = False
                people_counter = 0

            if people_counter > 5:
                object_flag = True
            else:
                object_flag = False

            if sensor_data["is_moving"]:
                movement_flag = True
            else:
                movement_flag = False

            flags = {
                "movement_flag": movement_flag,
                "object_flag": object_flag,
                "coord_flag": coord_flag,
                "save_coord_flag": save_coord_flag
            }
            bike_status = {
                "latitude": sensor_data["latitude"], 
                "longitude": sensor_data["longitude"],
                "objects": num_people
            }

            log(f"Flags: {flags}")
            log(f"Status: {bike_status}")

            api_post(bike_status, "/api/bike")
            api_post(flags, "/api/alerts")

    finally:
        sensors.stop()


if __name__ == "__main__":
    main()


# def main(pi=True, source=0):

#     try:

#         detector = objectdetection.ObjectDetection()

#         sensors = sensorhandler.SensorHandler(src=int(source), pi=pi)
#         sensors.start()
#         sensor_data = sensors.read()

#         sentry_mode = False

#         api_post({"sentry_mode": sentry_mode, "latitude":sensor_data["latitude"], "longitude":sensor_data["longitude"], "objects": 0}, "/api/bike")
#         response = api_get("/api/bike")

#         if response.ok:
#             server_data = response.json()
#         else:
#             raise Exception(f"Something was wrong with POSTing data to the webserver. \n{response.text}")

#         close_flag = True
#         frame_rate = 30
#         prev = 0

#         while close_flag:

#             time_elapsed = time.time() - prev
            
#             sensor_data = sensors.read()
#             response = api_get("/api/bike")
            
#             if response.ok:
#                 server_data = response.json()
#             else:
#                 raise Exception(response.text)

#             sentry_mode = bool(server_data["bike_status"]["sentry_mode"])
            
#             if time_elapsed > 1. / frame_rate:
#                 prev = time.time()
                
#                 output = detector.detect_filtered(sensor_data["frame"], 0.8)
#                 boxes_frame = output.draw_boxes()

#                 num_objects = output.get_objects()
#                 if num_objects > 0:
#                     object_flag = True

#                     ret, frame_buffer = cv2.imencode(".jpg",boxes_frame)
#                     api_post({"image": base64.b64encode(frame_buffer)}, "/api/image")

#                     print(f"Found {num_objects} objects.")
#                 else:
#                     object_flag = False

#             if object_flag or sensor_data["is_moving"]:

#                 # TODO: add code for sending alert(s)

#                 continue

#             post = {"sentry_mode": sentry_mode, "latitude": sensor_data["latitude"], "longitude": sensor_data["longitude"], "objects": num_objects}
#             print(post)
#             api_post(post, "/api/bike")
#             response = api_get("/api/bike")

#             if response.ok:
#                 response = response.json()

#     finally:
#         sensors.stop()
