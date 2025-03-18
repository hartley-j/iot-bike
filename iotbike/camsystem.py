from pathlib import Path

import cv2 as cv
import time
import datetime

from iotbike import camhandler, objectdetection


def detect_images(path: str) -> None:
    """
    Detects objects from images in directory
    :param path: path to directory containing images
    :return: None
    """
    detector = objectdetection.ObjectDetection()
    objectdetection.detect_from_dir(path, 0.8, detector)


def use_webcam_live(source, pi, disp):
    """
    Uses the webcam to live detect objects.
    :param source: index of webcam to use
    :type source: int
    :return: None
    """

    detector = objectdetection.ObjectDetection()

    camera = camhandler.CamHandler(src=int(source),pi=pi)
    camera.start()

    close_flag = True
    frame_rate = 30
    prev = 0

    while close_flag:

        time_elapsed = time.time() - prev

        if time_elapsed > 1. / frame_rate:
            prev = time.time()

            frame = camera.read()["frame"]
            output = detector.detect_filtered(frame, 0.8)

            boxes_frame = output.draw_boxes()

            if disp:
                detector.display(boxes_frame, output.elapsed, frames=1 / time_elapsed)

            num_objects = output.get_objects()
            if num_objects > 0:
                now = datetime.datetime.now().isoformat()

                # print(f"{now}: found {num_objects} objects. Saving file.")

                # cv.imwrite(f"/home/joehartley/Desktop/{now}.png", boxes_frame)

            # # result, t = frame, 0.000
            # if using_pi:
            #     camera.update_boxes(boxes)
            # else:
            #     # image = detector.draw_boxes(frame, boxes)
            #     # detector.display(image, t, frames=1./time_elapsed)
            #     camera.update_boxes(boxes)
            # camera.update_boxes(boxes)

        if disp and cv.waitKey(1) == 27:
            close_flag = False

    camera.stop()
    cv.destroyAllWindows()


def use_webcam_pic(source: int):
    """
    Uses webcam to take a photo and detects objects
    :param source: webcam index
    """
    objectdetection.detect_from_photo(source=source)

def track_from_webcam(source):
    """Tracks objects from webcam

    Args:
        source (int): webcam index
    """

    detector = objectdetection.ObjectDetection()

    camera = camhandler.CamHandler(src=int(source))
    camera.start()

    init_frame = camera.read()["frame"]
    shape = init_frame.shape
    frame_width = shape[1]
    frame_height = shape[0]

    close_flag = True
    frame_rate = 30
    prev = 0

    while close_flag:

        time_elapsed = time.time() - prev

        if time_elapsed > 1. / frame_rate:
            prev = time.time()

            frame = camera.read()["frame"]
            tracks, t = detector.detect_tracks(frame, 0.8)

            for track in tracks:
                if not track.is_confirmed():
                    continue
                track_id = track.track_id
                track_class = track.det_class
                x1, y1, x2, y2 = track.to_ltrb()

                cv.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv.putText(frame, f"ID: {track_id}", (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, lineType=cv.LINE_AA)

        cv.imshow("Tracking", frame)

        if cv.waitKey(1) == 27:
            close_flag = False
