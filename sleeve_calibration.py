import glob
import os
import pickle
import queue
import uuid
import cv2
import cv2.aruco as aruco
import numpy as np

from communication_queues import Queues

QUEUES = Queues.get_instance()
RECALLIBRATE = False

PIXEL_CORNERS = [[122, 147], [116, 400], [462, 403], [468, 157]]
REAL_CORNERS = [[223.5, 16.7], [224, 481.4], [876.3, 479.2], [883.9, 17.1]]

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(WORK_DIR, "images")

class Calibration():

    def __init__(
        self,
        _squares_x,
        _squares_y,
        _square_length=500,
        _marker_length=370,
        _arucodict=aruco.getPredefinedDictionary(aruco.DICT_6X6_250),
    ) -> None:
        self.squares_x = _squares_x
        self.squares_y = _squares_y
        self.square_length = _square_length
        self.marker_length = _marker_length
        self.arucodict = _arucodict
        self.board: aruco.CharucoBoard = aruco.CharucoBoard_create(
            _squares_x, _squares_y, _square_length, _marker_length, _arucodict
        )
        self.camera_matrix = None
        self.distortion_coefficients = None
        self.transform_matrix = None

    def get_board(self) -> cv2.Mat:
        cv2.imwrite(
            "charuco_board.png",
            self.board.draw(
                (
                    self.square_length * self.squares_x,
                    self.square_length * self.squares_y,
                )
            ),
        )
        return self.board


    def take_pictures(self) -> None:
        counter = 0
        cam = cv2.VideoCapture(-1)

        while True:
            _, frame = cam.read()
            clear_frame = frame.copy()

            corners, ids, _ = aruco.detectMarkers(frame, self.arucodict)

            detect = aruco.drawDetectedMarkers(frame, corners, ids)

            cv2.imshow("Imagetest", detect)

            k = cv2.waitKey(1)

            if k == ord("a"):
                cv2.imwrite(f"{WORK_DIR}/image_{uuid.uuid4()}.png", clear_frame)
                counter += 1

            elif k != -1:
                continue
            elif k == 27:
                break

        cam.release()
        cv2.destroyAllWindows()

    def calibrate(self) -> None:
        try:
            if RECALLIBRATE:
                raise OSError
            self.camera_matrix, self.distortion_coefficients = pickle.load(open(f"{WORK_DIR}/calibration_settings.pkl", "rb"))
        except OSError:
            self.camera_matrix, self.distortion_coefficients = self._intrinsic_calibration()
            pickle.dump((self.camera_matrix, self.distortion_coefficients), open(f"{WORK_DIR}/calibration_settings.pkl", "wb"))

        self._extrinsic_calibration()

    def _intrinsic_calibration(self) -> tuple[cv2.Mat, cv2.Mat]:
        image_files = glob.glob(os.path.join(f"{IMAGE_DIR}/", "*.jpg")) + glob.glob(
            os.path.join(f"{IMAGE_DIR}/", "*.png")
        )
        corners, ids, imsize = self._read_chessboards(image_files)
        return self._calibrate_camera(corners, ids, imsize)

    def _read_chessboards(self, images: list[str]) -> tuple[list, list, tuple]:
        """
        Charuco base pose estimation.
        """
        QUEUES.logging_queue.put("POSE ESTIMATION STARTS:")
        allCorners = []
        allIds = []
        decimator = 0
        # SUB PIXEL CORNER DETECTION CRITERION
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)

        for im in images:
            QUEUES.logging_queue.put(f"=> Processing image {im}")
            frame = cv2.imread(im)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = cv2.aruco.detectMarkers(gray, self.arucodict)

            if len(corners) > 0:
                # SUB PIXEL DETECTION
                for corner in corners:
                    cv2.cornerSubPix(gray, corner,
                                    winSize = (3,3),
                                    zeroZone = (-1,-1),
                                    criteria = criteria)
                res2 = cv2.aruco.interpolateCornersCharuco(corners,ids,gray,self.board)
                if res2[1] is not None and res2[2] is not None and len(res2[1])>3 and decimator%1==0:
                    allCorners.append(res2[1])
                    allIds.append(res2[2])

            decimator+=1

        imsize = gray.shape
        return allCorners, allIds, imsize

    def _calibrate_camera(self, allCorners: list[list[cv2.KeyPoint]], allIds: list[list[int]], imsize: tuple[int]) -> tuple[cv2.Mat, cv2.Mat]:
        """
        Calibrates the camera using the dected corners.
        """
        QUEUES.logging_queue.put("CAMERA CALIBRATION")

        cameraMatrixInit = np.array([[ 1000.,    0., imsize[0]/2.],
                                    [    0., 1000., imsize[1]/2.],
                                    [    0.,    0.,           1.]])

        distCoeffsInit = np.zeros((5,1))
        flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL + cv2.CALIB_FIX_ASPECT_RATIO)
        _, camera_matrix, distortion_coefficients = cv2.aruco.calibrateCameraCharucoExtended(
                        charucoCorners=allCorners,
                        charucoIds=allIds,
                        board=self.board,
                        imageSize=imsize,
                        cameraMatrix=cameraMatrixInit,
                        distCoeffs=distCoeffsInit,
                        flags=flags,
                        criteria=(cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9))

        return camera_matrix, distortion_coefficients

    def _extrinsic_calibration(self) -> None:
        source_points = np.array(PIXEL_CORNERS, dtype=np.float32)
        destination_points = np.array(REAL_CORNERS, dtype=np.float32)

        self.transform_matrix, _ = cv2.findHomography(source_points, destination_points)

    def correct_points(self, pixel_points: list) -> list:
        real_points = self.transform(pixel_points)

        return real_points

    def undistort(self, image: cv2.UMat) -> cv2.UMat:
        undistorted_img = cv2.undistort(
            image,
            self.camera_matrix,
            self.distortion_coefficients,
            None,
            self.camera_matrix,
        )

        return undistorted_img

    def transform(self, pixel_points: list) -> list:
        transform_points = []
        for point in pixel_points:
            new_pixel_point = np.array([*point, 1]).reshape(3, 1)
            real_point = np.dot(self.transform_matrix, new_pixel_point)
            transform_points.append(tuple(real_point.reshape(-1))[:2])

        return transform_points

