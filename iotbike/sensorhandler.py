import threading

import cv2 as cv
from threading import Thread, Lock
import numpy as np


def _draw_boxes(image, boxes):
    """DEPRECATED: draws boxes from a list

    Args:
        image (np.ndarray): image to draw on         
        boxes (list): list of boxes, confidences, and classes   

    Returns:
        np.ndarray: image with boxes drawn on
    """
    for box in boxes:
        (x, y) = (box[0][0], box[0][1])
        (w, h) = (box[0][2], box[0][3])

        colour = [255, 0, 0]

        cv.rectangle(image, (x, y), (x + w, y + h), colour, 2)
        text = f"{box[3]}: {box[2]:.4f}"
        cv.putText(image, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1)

    return image


class SensorHandler:
    """Class to handle webcam`
    """

    def __init__(self, name: str = "WebcamStream", src: int = 0, pi: bool = False):
        self.stopped = False
        self.name = name
        self.boxes = None

        if pi:
            from picamera2 import Picamera2
            from iotbike.imu import IMU
            from iotbike.gps import GPS
 
            self.stream = Picamera2()
            self.stream.configure(self.stream.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
            self.stream.start()

            self.frame = self.stream.capture_array()

            self.sensehat = IMU()
            self.sensehat.update_data()

            self.gps = GPS()
            self.gps.update()

            self.thread = Thread(target=self._update_picam, name=name, args=())
        else:
            self.stream = cv.VideoCapture(src)
            self.grabbed, self.frame = self.stream.read()

            self.thread = Thread(target=self._update_webcam, name=name, args=())
            self.thread.daemon = True

        # self.lock = Lock()

    def start(self):
        """Starts thread
        """
        self.thread.start()

    def read(self):
        """Returns current frame

        Returns:
            np.ndarray: current frame
        """
        return {"frame": self.frame, 
                "is_moving": self.sensehat.is_moving(), 
                "gps": {"latitude": self.gps.latitude, "longitude": self.gps.longitude}
            }

    def stop(self):
        """Stops the while loop in the update function
        """
        self.stopped = True

    def update_boxes(self, b):
        """Depracted.
        """
        self.boxes = b

    def _update_webcam(self):
        """This runs continuously in the thread. Updates the frame from the camera
        """

        # cv.namedWindow(self.name)

        while True:
            if self.stopped is True:
                break

            self.grabbed, self.frame = self.stream.read()

            # with self.lock:
            #     self._display()

        # cv.destroyAllWindows()
        self.stream.release()

    def _update_picam(self):
        """Same but for the picam
        """
        while True:
            if self.stopped is True:
                break

            self.frame = self.stream.capture_array()
            self.sensehat.update_data()
            self.gps.update()


    def _display(self):
        """Deprecated.
        """

        # self.detection = _draw_boxes(self.frame, self.boxes)
        cv.imshow(self.name, self.detection)
