import math
import time
from typing import Literal
import cv2
import numpy as np

from sleeve_calibration import Calibration
from communication_queues import Queues

QUEUES = Queues.get_instance()
CALIBRATION = Calibration(5, 8)
CAMERA_PORT = -1

class SleeveDetection:
    def __init__(self) -> None:
        self.sleeve_amount = 0
        self.previous_sleeve_count = 0

    def reset(self):
        self.__init__()

    def detect(self) -> None:
        self.connect_camera()

    def connect_camera(self, detect=False) -> None:
        cam = cv2.VideoCapture(CAMERA_PORT, cv2.CAP_V4L)
        CALIBRATION.calibrate()

        while True:
            ret, frame = cam.read()

            if not ret:
                QUEUES.logging_queue.put("warning: camera disconnected")
                cam.release()
                cv2.destroyAllWindows()

                cam = self._reconnect_camera(cam)
            if detect:
                frame = frame.copy()
            else:
                if frame is None:
                    continue

                undistorted_img = CALIBRATION.undistort(frame)
                pixel_coords, detected_image = self._detect_circles(undistorted_img)

                coords = CALIBRATION.correct_points(pixel_coords)

                if coords:
                    self._guess_sleeve_count(coords)

                    self._send_data(coords)

                    for i in range(len(coords)):
                        if len(coords[i]) != 2:
                            continue

                        real_coord = [int(c) for c in coords[i]]
                        pixel_coord = [int(c) for c in pixel_coords[i]]
                        self._draw_coord(detected_image, real_coord, pixel_coord, coords)

                frame = detected_image

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            QUEUES.video_feed_queue.put((b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'))

            k = cv2.waitKey(1)

            if k == 27:
                break

        cam.release()
        cv2.destroyAllWindows()

    def _draw_coord(self, img: cv2.UMat, real_coord: tuple[float, float], pixel_coord: tuple[int, int], all_coords: list) -> cv2.UMat:
        x, y = pixel_coord
        coord_text = str(real_coord)
        direction_text = str(self._get_left_or_right(all_coords, real_coord))
        (w, h), _ = cv2.getTextSize(coord_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)

        img = cv2.rectangle(img, (x, y - int(h*3.2)), (x + w, y), (0, 0, 255), -1)
        cv2.putText(
            img=img,
            text=coord_text,
            org=(x, y-8),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.7,
            color=(255, 255, 255),
            thickness=1,
        )
        cv2.putText(
            img=img,
            text=direction_text,
            org=(x, y-32),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.7,
            color=(255, 255, 255),
            thickness=1,
        )

        return img

    def _reconnect_camera(self, cam: cv2.VideoCapture) -> cv2.VideoCapture:
        wait_increment = 2
        for i in range(10):
            wait_time = wait_increment*i
            QUEUES.logging_queue.put(f"reconnecting after {wait_time} seconds...")
            cam = cv2.VideoCapture(CAMERA_PORT, cv2.CAP_V4L)
            ret, _ = cam.read()

            if ret:
                return cam

            time.sleep(wait_time)

    def _send_data(self, coords) -> None:
        if QUEUES.robot_request_queue.empty():
            return

        message = QUEUES.robot_request_queue.queue[0]
        if "request_sleeve" not in message:
            return

        sleeve_count = int(message.split(":")[-1])
        QUEUES.robot_request_queue.get()  # Remove the message from the queue

        data_string = ""
        try:
            coord = coords[sleeve_count]
            data_string = f"{coord[0]};{coord[1]};{self._get_left_or_right(coords, coord)}"
        except IndexError:
            data_string = "none"

        if len(data_string) > 0:
            QUEUES.robot_data_queue.put(data_string)

    def _detect_circles(self, image: cv2.UMat) -> tuple[list, cv2.UMat]:
        prepared_img = self._prepare_image(image)

        params = cv2.SimpleBlobDetector_Params()

        params.filterByArea = True
        params.minArea = 2000
        params.filterByCircularity = True
        params.minCircularity = 0.6
        params.filterByInertia = True
        params.minInertiaRatio = 0.2
        params.filterByConvexity = True
        params.minConvexity = 0.6

        detector = cv2.SimpleBlobDetector_create(params)

        keypoints = detector.detect(prepared_img)
        coordinates = [k.pt for k in keypoints]

        # Draw middle point of circle
        for x, y in coordinates:
            image = cv2.circle(
                image, (int(x), int(y)), radius=2, color=(0, 0, 255), thickness=-1
            )

        # Increase size of circle by 4 pixels
        for keypoint in keypoints:
            size = keypoint.size
            keypoint.size = size + 4

        img_with_blobs = cv2.drawKeypoints(
            image,
            keypoints,
            np.array([]),
            (0, 255, 0),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )

        return coordinates, img_with_blobs

    def _prepare_image(self, image: cv2.UMat) -> cv2.UMat:
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)

        alpha = 1.2
        mean_intensity = np.mean(img_gray)
        beta = -0.8078 * mean_intensity + 200

        img_contrast_adjusted = cv2.convertScaleAbs(img_blur, alpha=alpha, beta=beta)

        _, img_thresholded = cv2.threshold(
            img_contrast_adjusted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        kernel = np.ones((3, 3), np.uint8)
        img_dilated = cv2.dilate(img_thresholded, kernel, iterations=3)

        return img_dilated

    def _get_left_or_right(self, all_coords: list[tuple[int, int]], current_coord: tuple[int, int]) -> Literal["right", "left"]:
        x_coords = [coord[0] for coord in all_coords]

        if len(x_coords) <= 1:
            return "right"

        x_coords.sort()
        difference = x_coords[-1] - x_coords[0]
        minimal_difference = 200
        if difference < minimal_difference:
            return "right"

        middle = x_coords[0] + difference / 2
        return "right" if current_coord[0] <= middle else "left"

    def _guess_sleeve_count(self, coords: list[tuple[int, int]]) -> None:
        if self.sleeve_amount == 0:
            self.sleeve_amount = len(coords)
        else:
            self.sleeve_amount = math.ceil((self.sleeve_amount + len(coords)) // 2)