
import requests

from iotbike import objectdetection
from iotbike import sensorhandler

def api_post(data, suffix, url="http://joehartley.pythonanywhere.com"):

    response = requests.post(url + suffix, json={
        "sentry_mode": sentry_mode,
        "latitude": latitude,
        "longitude": longitude
    })

    return response.json()

def api_get(suffix, url="http://joehartley.pythonanywhere.com"):
    response = requests.get(url + suffix)
    return response.json()


def main(pi=True, source=0):

    detector = objectdetection.ObjectDetection()

    sensors = sensorhandler.SensorHandler(src=int(source), pi=pi)
    sensors.start()
    sensor_data = sensors.read()

    sentry_mode = False

    r, code = api_post({"sentry_mode": sentry_mode, "latitude":sensor_data["latitude"], "longitude":sensor_data["longitude"], "is_moving": False, "objects": 0}, "/api/bike/")

    if code != 200:
        raise Exception("Not able to post to API. Try again.")
    
    close_flag = True
    frame_rate = 30
    prev = 0

    while close_flag:

        time_elapsed = time.time() - prev
        
        sensor_data = sensors.read()
        response = api_get("/api/bike/")
        sentry_mode = bool(response["bike_status"]["sentry_mode"])
        
        if time_elapsed > 1. / frame_rate:
            prev = time.time()
            
            output = detector.detect_filtered(sensor_data["frame"], 0.8)
            boxes_frame = output.draw_boxes()

            num_objects = output.get_objects()
            if num_objects > 0:
                now = datetime.datetime.now().isoformat()
                object_flag = True

                # print(f"{now}: found {num_objects} objects. Is moving? {sensor_data['is_moving']}")
            else:
                object_flag = False

        if object_flag or sensor_data["is_moving"]:

            # TODO: add code for sending alert(s)

            continue

        r, code = api_post({"sentry_mode": sentry_mode, "latitude": sensor_data["latitude"], "longitude": sensor_data["longitude"], "is_moving": sensor_data["is_moving"], "objects": num_objects}, "/api/bike/")

        if code != 200:
            raise Exception("Not able to post to API. Try again.")


    camera.stop()
    cv.destroyAllWindows()
