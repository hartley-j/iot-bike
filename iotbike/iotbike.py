
from iotbike import objectdetection
from iotbike import sensorshandler

def main(pi=True, source=0):

    detector = objectdetection.ObjectDetection()

    sensors = sensorhandler.SensorHandler(src=int(source), pi=pi)
    sensors.start()

    close_flag = True
    frame_rate = 30
    prev = 0

    while close_flag:

        time_elapsed = time.time() - prev

        if time_elapsed > 1. / frame_rate:
            prev = time.time()

            sensor_data = sensors.read()
            
            frame = sensor_data["frame"]
            output = detector.detect_filtered(frame, 0.8)

            boxes_frame = output.draw_boxes()

            if disp:
                detector.display(boxes_frame, output.elapsed, frames=1 / time_elapsed)

            num_objects = output.get_objects()
            if num_objects > 0:
                now = datetime.datetime.now().isoformat()

                print(f"{now}: found {num_objects} objects. Is moving? {sensor_data['is_moving']}")


        if disp and cv.waitKey(1) == 27:
            close_flag = False

    camera.stop()
    cv.destroyAllWindows()