import math
import queue
import uuid
import cv2
import flask_socketio as socket
import numpy as np

from sleeve_callibration import Callibration

CALLIBRATION = Callibration(5, 8)

class SleeveDetection:
    def __init__(self) -> None:
        self.sleeve_amount = 0
        self.previous_sleeve_count = 0

    def detect(self, queues):
        self.connect_camera(self._find_circles_with_blobs, queues)

    def connect_camera(self, detect_func: callable, queues: tuple[queue.Queue]) -> None:
        cam = cv2.VideoCapture(0, cv2.CAP_V4L)

        while True:
            try:
                ret, frame = cam.read()

                if detect_func is None:
                    frame = frame.copy()
                    # cv2.imshow("Raw camera feed", raw_image)
                else:
                    if frame is None:
                        continue

                    pixel_coords, detected_image = detect_func(frame)
                    # calibrated_img = CALLIBRATION.undistort(detected_image)

                    coords, calibrated_img = CALLIBRATION.transform(detected_image, pixel_coords)
                    if coords:
                        self._guess_sleeve_count(coords)
                        self.send_data(queues[:2], coords)

                        for coord in coords:
                            if len(coord) == 2:
                                real_coord = [int(c) for c in coords[coords.index(coord)]]
                                coord = [int(c) for c in coord]
                                cv2.putText(
                                    img=calibrated_img,
                                    text=str(real_coord),
                                    org=(coord[0], coord[1]),
                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                    fontScale=0.7,
                                    color=(0, 255, 0),
                                    thickness=1,
                                )
                    # print(coords)
                    frame = calibrated_img

                # _, buffer = cv2.imencode('.jpg', frame)
                # frame = buffer.tobytes()
                # video_queue: queue.Queue = queues[2]

                # video_queue.put((b'--frame\r\n'
                #                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'))
                cv2.imshow("Sleeves", frame)

                k = cv2.waitKey(1)

                if k == ord("a"):
                    cv2.imwrite(f"images/image{uuid.uuid4()}.png", frame.copy())

                elif k != -1:
                    continue
                elif k == 27:
                    break
            except AttributeError as e:
                print(e)
                cam = cv2.VideoCapture(0, cv2.CAP_V4L)
                continue

        cam.release()
        cv2.destroyAllWindows()



    def send_data(self, queues: tuple[queue.Queue, queue.Queue], coords) -> None:
        request_queue, info_queue = queues
        if request_queue.empty():
            return

        message = request_queue.queue[0]
        if "request_sleeve" not in message:
            return

        sleeve_count = int(message.split(":")[-1])
        request_queue.get()  # Remove the message from the queue

        data_string = ""
        try:
            coord = coords[sleeve_count]
            data_string = f"{coord[0]};{coord[1]};{self._get_left_or_right(coord)}"
        except IndexError:
            data_string = "none"

        if len(data_string) > 0:
            info_queue.put(data_string)

    def _find_circles_with_blobs(self, image: cv2.UMat) -> cv2.UMat:
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(img_gray, (3, 3), 0)

        alpha = 1.2  # Contrast control (1.0-3.0)
        mean_intensity = np.mean(img_gray)  # Brightness of the image
        beta = -0.8078 * mean_intensity + 170
        # beta = -200
        # beta = -0.0015 * mean_intensity**2 + -0.8572 * mean_intensity + 120

        adjusted = cv2.convertScaleAbs(blur, alpha=alpha, beta=beta)
        mean_intensity_adjusted = np.mean(adjusted)  # Brightness of the image

        _, thresholded = cv2.threshold(
            adjusted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        kernel = np.ones((3, 3), np.uint8)

        # Apply morphological closing
        dilated = cv2.dilate(thresholded, kernel, iterations=1)
        closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

        cv2.putText(
            img=closed,
            text=str((mean_intensity, mean_intensity_adjusted, beta)),
            org=(10, 30),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=(0, 255, 0),
            thickness=1,
        )

        params = cv2.SimpleBlobDetector_Params()

        params.filterByArea = True
        params.minArea = 1000
        params.filterByCircularity = True
        params.minCircularity = 0.6
        params.filterByInertia = True
        params.minInertiaRatio = 0.2
        params.filterByConvexity = True
        params.minConvexity = 0.6

        detector = cv2.SimpleBlobDetector_create(params)

        keypoints = detector.detect(closed)
        coordinates = [k.pt for k in keypoints]

        for x, y in coordinates:
            image = cv2.circle(
                image, (int(x), int(y)), radius=2, color=(0, 0, 255), thickness=-1
            )

        img_with_blobs = cv2.drawKeypoints(
            image,
            keypoints,
            np.array([]),
            (0, 255, 0),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )

        return coordinates, img_with_blobs

    def _get_left_or_right(self, coords: tuple[int, int]) -> str:
        x = coords[0]
        return "right" if x <= 650 else "left"

        # sorted_on_x = sorted(coords, key=lambda x: x[0])
        # sorted_on_y = sorted(sorted_on_x, key=lambda x: x[1])

        # return sorted_on_y

    def _guess_sleeve_count(self, coords):
        if self.sleeve_amount == 0:
            self.sleeve_amount = len(coords)
        else:
            self.sleeve_amount = math.ceil((self.sleeve_amount + len(coords)) // 2)

    def _stack_views(self, scale, imgArray):
        rows = len(imgArray)
        cols = len(imgArray[0])
        rowsAvailable = isinstance(imgArray[0], list)
        width = imgArray[0][0].shape[1]
        height = imgArray[0][0].shape[0]

        # Check if rows are available
        if rowsAvailable:
            for x in range(0, rows):
                for y in range(0, cols):
                    if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                        imgArray[x][y] = cv2.resize(
                            imgArray[x][y], (0, 0), None, scale, scale
                        )
                    else:
                        imgArray[x][y] = cv2.resize(
                            imgArray[x][y],
                            (imgArray[0][0].shape[1], imgArray[0][0].shape[0]),
                            None,
                            scale,
                            scale,
                        )
                    if len(imgArray[x][y].shape) == 2:
                        imgArray[x][y] = cv2.cvtColor(
                            imgArray[x][y], cv2.COLOR_GRAY2BGR
                        )

            imageBlank = np.zeros((height, width, 3), np.uint8)
            hor = [imageBlank] * rows

            for x in range(0, rows):
                hor[x] = np.hstack(imgArray[x])
            ver = np.vstack(hor)
        else:
            for x in range(0, rows):
                if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                    imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
                else:
                    imgArray[x] = cv2.resize(
                        imgArray[x],
                        (imgArray[0].shape[1], imgArray[0].shape[0]),
                        None,
                        scale,
                        scale,
                    )
                if len(imgArray[x].shape) == 2:
                    imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
            hor = np.hstack(imgArray)
            ver = hor

        return ver
