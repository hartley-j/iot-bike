from __future__ import print_function, unicode_literals

import importlib.resources
from pathlib import Path
from queue import Queue, Full

import cv2 as cv
import numpy as np
import time

from iotbike.camhandler import CamHandler


def _get_model_files(directory: str) -> tuple[str, str, str]:
    """
    Gets resources from the resource subfolder.
    :param directory: directory containing model files
    :return: path to: model, config
    """
    model_ext = ["caffemodel", "pb", "t7", "net", "weights", "bin", "onnx"]
    config_ext = ["prototxt", "pbtxt", "cfg", "xml"]
    model, config, framework = None, None, None

    resource = importlib.resources.files("camsystem") / f"resources/{directory}"
    for file in resource.iterdir():
        if file.is_file():
            extension = str(file).rsplit("/")[-1].rsplit(".")[-1]

            if extension in model_ext:
                model = str(file)
                if extension == "pb":
                    framework = "tf"
                elif extension == "weights":
                    framework = "dn"
            elif extension in config_ext:
                config = str(file)

    return model, config, framework

def _yolo_to_coco(x: float, y: float, w: float, h: float) -> tuple[int, int, int, int]:
    """Takes YOLO bounding box format [x_center, y_center, width, height] and outputs COCO bounding box format [x_min, y_min, width, height]

    Note: origin is top left corner of image

    Args:
        x (float): x coordinate of center (pixels)
        y (float): y coordinate of center (pixels)
        w (float): width of bounding box (pixels)
        h (float): height of bounding box (pixels)

    Returns:
        tuple[int, int, int, int]: COCO bounding box format. x, y coordinates of top left, width, and height"""
    return int(x - w // 2), int(y - h // 2), int(w), int(h)

def _voc_to_coco(x_min: float, y_min: float, x_max: float, y_max: float) -> tuple[int, int, int, int]:
    """Takes VOC bounding box format and outputs COCO bounding box format

    Args:
        x_min (float): x coordinate of top left corner (pixels)
        y_min (float): y coordinate of top left corner (pixels)
        x_max (float): x coordinate of bottom right corner (pixels)
        y_max (float): y coordinate of bottom right corner (pixels)

    Returns:
        tuple[int, int, int, int]: COCO bounding box format. x, y coordinates of top left, width, and height
    """
    return int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)

def _convert_detection(raw_detection, shape):
    """Splits a raw detection into a list of tuples containing bounding boxes, confidences, and classes

    ASSUMES OUTPUT OF YOLO MODEL

    Args:
        raw_detection (): raw detection from YOLO model

    Returns:
        list of tuple: of bounding boxes [x, y, w, h], confidences, and classes
    """

    lump = []
    raw_detection = np.vstack(raw_detection)

    for detection in raw_detection:
        scores = detection[5:]
        classID = np.argmax(scores)
        confidence = scores[classID]

        x, y, w, h = detection[:4] * np.array([shape[1], shape[0], shape[1], shape[0]])

        lump.append(([x,y,w,h], confidence, classID))

    return lump


class DetectionOutput:
    """Object for output of a single object detection.

    On initiation, filters boxes with non maximum suppression.

    Can output image with bounding boxes drawn.
    """

    def __init__(self, raw_detections, shape: tuple[int, ...], threshold: float, elapsed: float, framework: str,
                 image: np.ndarray):
        """Takes raw detection from neural network and filters into a list of all of the bounding boxes in image.

        Args:
            raw_detections (output of neural network): raw detections of neural network
            shape (tuple[int, ...]): shape of image
            threshold (float): threshold confidence value for filtering
            elapsed (float): time taken for forward propagation of neural network
            framework (str): framework of neural network used. Accepts ["dn", "tf"] for "darknet" or "tensorflow"
            image (np.ndarray): frame
        """
        self.elapsed = elapsed
        self.__framework = framework

        names_file = importlib.resources.files("camsystem") / "resources/coco.names"
        with importlib.resources.as_file(names_file) as f:
            self.__classes = open(f).read().strip().split("\n")

        raw_detections = np.vstack(raw_detections)

        boxes, confidences, classIDs = self._filter_boxes(raw_detections, shape, threshold)

        indices = cv.dnn.NMSBoxes(boxes, confidences, threshold, 0.2)

        if len(indices) > 0:
            lump = [[boxes[i], confidences[i], classIDs[i]] for i in indices]
            self.boxes, self.confidences, self.classIDs = list(zip(*lump))
        else:
            self.boxes, self.confidences, self.classIDs = None, None, None

        self.image = image

    def draw_boxes(self) -> np.ndarray:
        """Draws bounding boxes and confidences on frame.

        Returns:
            np.ndarray: frame with bounding boxes drawn
        """
        if self.boxes is not None:
            for i in range(len(self.boxes)):
                box = self.boxes[i]

                x, y = box[0], box[1]
                w, h = box[2], box[3]

                cv.rectangle(self.image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                text = f"{self.__classes[self.classIDs[i]]}: {self.confidences[i]:.4f}"
                cv.putText(self.image, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        return self.image

    def get_name(self, i: int) -> str:
        """Gets name of COCO class from index number

        Args:
            i (int): index in COCO.names

        Returns:
            str: name of class
        """
        return self.__classes[i]

    def get_objects(self):
        """Gets number of objects in frame

        Returns:
            int: number of objects.
        """
        if self.boxes is not None:
            return len(self.boxes)
        else:
            return 0

    def _filter_boxes(self, raw_detections: np.ndarray, shape: tuple[int, ...], threshold: float):
        """Performs non-maximum suppression on bounding boxes

        Args:
            raw_detections (np.ndarray): raw detections (ensure it has been vstacked)
            shape (tuple[int, ...]): shape of imagefjdskj
            threshold (float): threshold confidence

        Returns:
            list : list of boxes, confidences, and classIDs
        """
        boxes, confs, classIDs = [], [], []

        if self.__framework == "dn":
            for detection in raw_detections:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                if confidence > threshold:
                    x, y, w, h = detection[:4] * np.array([shape[1], shape[0],
                                                           shape[1], shape[0]])
                    boxes.append(_yolo_to_coco(x, y, w, h))
                    confs.append(float(confidence))
                    classIDs.append(classID)

            return boxes, confs, classIDs
        elif self.__framework == "tf":
            for detection in raw_detections[0][0]:
                classID = int(detection[1])
                confidence = float(detection[2])

                if confidence > threshold:
                    x_min, y_min, x_max, y_max = detection[3:7] * np.array([shape[1], shape[0],
                                                                            shape[1], shape[0]])
                    boxes.append(_voc_to_coco(x_min, y_min, x_max, y_max))
                    confs.append(float(confidence))
                    classIDs.append(classID)

            return boxes, confs, classIDs


class ObjectDetection:
    """ObjectDetection class.
    """
    def __init__(self):
        """Gets neural network config files and initiates network
        """
        resource_dirs = importlib.resources.files("camsystem") / "resources"
        # models = [str(model) for model in resource_dirs.iterdir()
        #           if (model.is_dir() and (str(model).rsplit("/")[-1] != "position"))]
        # questions = [
        #     {
        #         'type': 'list',
        #         'name': 'model',
        #         'message': 'Please select model to use. ',
        #         'choices': [{'name': m.rsplit("/")[-1], 'value': m.rsplit("/")[-1]} for m in models]
        #     }
        # ]
        model_dir = "yolov7-tiny"

        model, config, self.__framework = _get_model_files(model_dir)

        self.__net = cv.dnn.readNet(model, config)
        self.__net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.__net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
        self.__outputNames = self.__net.getUnconnectedOutLayersNames()

    def detect(self, image: np.ndarray, threshold: float) -> DetectionOutput:
        """
        Takes image and returns the output from the __net

        :param threshold:
        :param image: image to be analysed
        :type image: ndarray
        :return: raw output of detection, time
        """

        if image.shape[0] > 1080:
            image = self.resize(image, 0.2)

        blob = cv.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.__net.setInput(blob)

        t0 = time.time()
        outputs = self.__net.forward(self.__outputNames)
        elapsed_time = time.time() - t0

        return outputs, elapsed_time

    def detect_filtered(self, image: np.ndarray, threshold: float) -> DetectionOutput:
        """Detects objects with __net and outputs filtered detections as DetectionOutput object

        Args:
            image (np.ndarray): image to be detected
            threshold (float): threshold for detection

        Returns:
            DetectionOutput: DetectionOutput object, which performs nms on initialisation
        """
        outputs, elapsed_time = self.detect(image, threshold)

        return DetectionOutput(outputs, image.shape[:2], threshold, elapsed_time, self.__framework, image)

    # def detect_tracks(self, image: np.ndarray, threshold: float):
    #     """Detects objects and used DEEP SORT to track objects

    #     Args:
    #         image (np.ndarray): current image/frame
    #         threshold (float): threshold for detection

    #     Returns:
    #         list[deep_sort_realtime.deep_sort.track.Track]: list of tracks from deep sort algorithm
    #     """
        
    #     outputs, elapsed_time = self.detect(image, threshold)

    #     return self.__tracker.update_tracks(_convert_detection(outputs, image.shape), frame=image), elapsed_time 

    @staticmethod
    def resize(img, percent):
        """
        Reduces the size of input image by percent amount
        :param img: input image
        :param percent: percent to reduce image by
        :return: resized image
        """
        return cv.resize(img, None, fx=percent, fy=percent, interpolation=cv.INTER_LINEAR)

    @staticmethod
    def display(img, fpt, name="Object Detection", frames=0.0):
        """
        Displays the result of the object detection
        """

        # reduce = 0.2
        # img = self.resize(img, reduce)

        cv.namedWindow(name)
        cv.imshow(name, img)
        cv.displayOverlay(name, f"Forward propagation time = {fpt:.3}\nfps = {frames:.3}")



def detect_from_file(file_path: str, conf_thresh: float, detector: ObjectDetection = None):
    """
    Performs object detection on an image and displays result
    :param file_path: absolute path to single image file
    :param conf_thresh: threshold for detection
    :param detector: ObjectDetection object (not required)
    """
    if not detector:
        detector = ObjectDetection()
    image = cv.imread(file_path)

    output = detector.detect(image, conf_thresh)
    detector.display(output.draw_boxes(), output.elapsed, name=file_path.rsplit("/")[-1])


def detect_from_dir(dir_path: str, conf_thresh: float, detector: ObjectDetection = None):
    """
    Performs object detection on a directory of images
    :param dir_path: absolute path to a directory containing images
    :param conf_thresh: threshold for detection
    :param detector: ObjectDetection object (not required)
    """
    if not detector:
        detector = ObjectDetection()

    p = Path(dir_path)

    for file in p.glob("**/*"):
        detect_from_file(str(file.resolve()), conf_thresh, detector)

    close_flag = True
    while close_flag:
        if cv.waitKey(0) == 27:
            close_flag = False

    cv.destroyAllWindows()


def detect_from_photo(source: int = 0, conf_thresh: float = 0.8, detector: ObjectDetection = None):
    """
    Takes photo from webcam and detects objects
    :param source: webcam index (default is 0)
    :param conf_thresh: threshold for detection
    :param detector: ObjectDetection object (not required), only used if inheriting a detector
    """
    if not detector:
        detector = ObjectDetection()

    camera = CamHandler(src=source)
    camera.start()

    while True:
        frame = camera.read()["frame"]
        cv.imshow("Preview", frame)

        # if space is pressed
        if cv.waitKey(1) == 0x20:
            cv.destroyWindow("Preview")
            camera.stop()
            break

    output = detector.detect(frame, conf_thresh)
    detector.display(output.draw_boxes(), output.elapsed, "Detection from webcam")

    close_flag = True
    while close_flag:
        if cv.waitKey(0) == 27:
            close_flag = False

    cv.destroyAllWindows()