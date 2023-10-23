from collections import Counter
import glob
import os
import pickle
import uuid

import cv2
import cv2.aruco as aruco
import numpy as np

RECALLIBRATE = False
# PIXEL_CORNERS = [[5, 146], [503, 146], [5, 462], [503, 462]]
PIXEL_CORNERS = [[16, 140], [514, 140], [16, 461], [514, 461]]
# PIXEL_CORNERS = [[65, 196], [482, 212], [471, 416], [125, 437]]
# REAL_CORNERS = [[0, 0], [961.35, 0], [0, 621.44], [961.35, 621.44]]
REAL_CORNERS = [[0, 0], [961, 0], [0, 621], [961, 621]]
# REAL_CORNERS = [[111, 111], [914, 118], [914, 520], [234, 571]]
CAMERA_PROPERTIES = {
    "sensor_width": 36,
    "focal_length": 2.8,
    "pixels_width": 1920,
    "pixels_height": 1080,
}  # First iteration camera properties (in mm or pixels). Assuming standard sensor width

IMAGE_WIDTH = 1
IMAGE_HEIGHT = 1

for x, y in REAL_CORNERS:
    if x > IMAGE_WIDTH:
        IMAGE_WIDTH = x
    if y > IMAGE_HEIGHT:
        IMAGE_HEIGHT = y


class Callibration:
    def __init__(
        self,
        _squares_x=4,
        _squares_y=3,
        _square_length=490,
        _marker_length=362,
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
        self.Rvectors = None
        self.Tvectors = None
        self.new_camera_matrix = None
        self.transform_ratio = self.get_transformation_ratio()

    def get_board(self):
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

    def take_pictures(self):
        counter = 0
        cam = cv2.VideoCapture(0)

        while True:
            ret, image = cam.read()
            og_img = image.copy()

            corners, ids, rejected = aruco.detectMarkers(image, self.arucodict)

            detect = aruco.drawDetectedMarkers(image, corners, ids)

            cv2.imshow("Imagetest", detect)

            k = cv2.waitKey(1)

            if k == ord("a"):
                cv2.imwrite(f"images/image_{uuid.uuid4()}.png", og_img)
                counter += 1

            elif k != -1:
                continue
            elif k == 27:
                break

        cam.release()
        cv2.destroyAllWindows()

    def _callibrate(self):
        image_files = glob.glob(os.path.join("./images/", "*.jpg")) + glob.glob(
            os.path.join("./images/", "*.png")
        )

        if len(image_files) == 0:
            raise Exception("No calibration images found in ./images/")

        all_markers = []
        for file in image_files:
            image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
            corners, ids, rejected = aruco.detectMarkers(image, self.arucodict)
            all_markers.append([corners, ids])

        all_corners = []
        all_ids = []
        for corners, ids in all_markers:
            if len(corners) >= 4:
                # Refine and interpolate Charuco board corners
                retval, charuco_corners, charuco_ids = aruco.interpolateCornersCharuco(
                    corners, ids, image, self.board
                )

                if charuco_corners is not None and len(charuco_corners) >= 4:
                    all_corners.append(charuco_corners)
                    all_ids.append(charuco_ids)

        focal_length_pixels = CAMERA_PROPERTIES["pixels_width"] * (
            CAMERA_PROPERTIES["focal_length"] / CAMERA_PROPERTIES["sensor_width"]
        )
        # print(image.shape)
        cameraMatrixInit = np.array(
            [
                [focal_length_pixels, 0, CAMERA_PROPERTIES["pixels_width"] / 2],
                [0, focal_length_pixels, CAMERA_PROPERTIES["pixels_height"] / 2],
                [0, 0, 1],
            ],
            dtype=np.float32,
        )

        distCoeffsInit = np.zeros((5, 1))
        flags = (
            cv2.CALIB_USE_INTRINSIC_GUESS
            + cv2.CALIB_RATIONAL_MODEL
            + cv2.CALIB_FIX_ASPECT_RATIO
        )

        # Perform camera calibration
        (
            ret,
            camera_matrix,
            distortion_coefficients,
            rotation_vectors,
            translation_vectors,
            stdDeviationsIntrinsics,
            stdDeviationsExtrinsics,
            perViewErrors,
        ) = aruco.calibrateCameraCharucoExtended(
            charucoCorners=all_corners,
            charucoIds=all_ids,
            board=self.board,
            imageSize=(CAMERA_PROPERTIES["pixels_width"], CAMERA_PROPERTIES["pixels_height"]),  # Image dimensions (width, height)
            cameraMatrix=cameraMatrixInit,
            distCoeffs=distCoeffsInit,
            flags=flags,
            criteria=(cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9),
        )

        return (
            camera_matrix,
            distortion_coefficients,
            rotation_vectors,
            translation_vectors,
        )

    def undistort(self, image):
        try:
            if RECALLIBRATE:
                raise OSError
            self.camera_matrix, self.distortion_coefficients, self.Rvectors, self.Tvectors = pickle.load(open('callibration_settings.pkl', 'rb'))
        except (OSError) as e:
            self.camera_matrix, self.distortion_coefficients, self.Rvectors, self.Tvectors = self._callibrate()
            pickle.dump((self.camera_matrix, self.distortion_coefficients, self.Rvectors, self.Tvectors), open('callibration_settings.pkl', 'wb'))

        # cam.release()
        # self.new_camera_matrix, _ = cv2.getOptimalCameraMatrix(
        #     self.camera_matrix, self.distortion_coefficients, (IMAGE_WIDTH, IMAGE_HEIGHT), 1, (IMAGE_WIDTH, IMAGE_HEIGHT)
        # )
        # cam.read()

        undistorted_img = cv2.undistort(
            image,
            self.camera_matrix,
            self.distortion_coefficients,
            None,
            self.camera_matrix,
        )

        return undistorted_img

    def transform(self, image, pixel_points):
        undistorted_img = self.undistort(image)

        # world_points = []
        # # Assume we have a pixel coordinate (u, v) in the image
        # for pixel_point in pixel_points:
        #     u, v = pixel_point  # Example pixel coordinate

        #     # Assume we have the depth of the point (z)
        #     z = 1.0  # Example depth

        #     # Convert the pixel coordinate to a 3D point in the camera's coordinate system
        #     point_camera = np.array([[u], [v], [1]]) * z

        #     # Convert the rotation and translation vectors to a rotation matrix
        #     rotation_matrices = []
        #     for rvec in self.Rvectors:
        #         rmat, _ = cv2.Rodrigues(rvec)
        #         rotation_matrices.append(rmat)

        #     res = [sum(idx) / len(idx) for idx in zip(*rotation_matrices)]

        #     # extracts all elements mean
        #     rvec = sum(res) / len(res)
        #     # Transform the point from the camera's coordinate system to the world coordinate system
        #     world_points.append(np.dot(rvec, point_camera) + self.Tvectors)

        final_points, callibrated_img = self._transform(undistorted_img, pixel_points)

        print(final_points)
        return final_points, callibrated_img


    def _transform(self, image, pixel_points):
        # print(f"pixel_points: {pixel_points}")
        # undistorted_img = self.undistort(image)

        source_points = np.array(PIXEL_CORNERS, dtype=np.float32)

        undistorted_source_points = np.array(
            [
                cv2.undistortPoints(
                    point,
                    self.camera_matrix,
                    self.distortion_coefficients,
                    None,
                    self.camera_matrix,

                )[0][0]
                for point in source_points
            ],
            dtype=np.float32,
        )

        destination_points = np.array(REAL_CORNERS, dtype=np.float32)

        perspective_matrix = cv2.getPerspectiveTransform(
            undistorted_source_points, destination_points
        )
        # affine_matrix = cv2.getAffineTransform(
        #     undistorted_source_points[:3], destination_points[:3]
        # )

        transform_points = [[]]
        if len(pixel_points) > 0:
            transform_points = np.array(
                [
                    cv2.undistortPoints(
                        point,
                        self.camera_matrix,
                        self.distortion_coefficients,
                        None,
                        self.camera_matrix,
                    )[0][0]
                    for point in pixel_points
                ],
                dtype=np.float32,
            )
            # print(f"undistorted_points: {transform_points}")

            points = np.array(transform_points, dtype=np.float32)
            points = points[np.newaxis]

            transform_points = cv2.perspectiveTransform(points, perspective_matrix)
            # transform_points = np.hstack([transform_points, np.ones((transform_points.shape[0], 1))])
            # transform_points = np.dot(affine_matrix, transform_points.T).T
            # transform_points = cv2.warpAffine(points, affine_matrix, (IMAGE_WIDTH, IMAGE_HEIGHT))


        corrected_img = cv2.warpPerspective(
            image, perspective_matrix, (IMAGE_WIDTH, IMAGE_HEIGHT)
        )

        drawn_img = self.draw_axis(
            corrected_img,
            self.camera_matrix,
            self.distortion_coefficients,
            self.Rvectors,
            self.Tvectors,
        )

        # print("Transformed: " + str(transform_points))
        # transform_points = [(point[0] + 26, point[1] - 11) for point in transform_points[0]]

        # transform_points = [tuple(point) for point in transform_points[0]]
        calculated_points = []
        print(self.transform_ratio)
        for point in transform_points[0]:
            point = tuple(point)
            print(point)
            point = (point[0] / self.transform_ratio[0] / 2, point[1] / self.transform_ratio[1] / 2)

            # calculated_point = self.y_transform(point)
            calculated_points.append(point)
        # transform_points = [tuple(point) for point in transform_points[0]]
        # print(f"transform_points: {transform_points}")
        # print("calculated: " + str(calculated_points))
        return calculated_points, drawn_img


    def get_transformation_ratio(self):
        # PIXEL_CORNERS = [[5, 146], [503, 146], [5, 462], [503, 462]]
        PIXEL_CORNERS = [[16, 140], [514, 140], [16, 461], [514, 461]]
        # PIXEL_CORNERS = [[65, 196], [482, 212], [471, 416], [125, 437]]
        # REAL_CORNERS = [[0, 0], [961.35, 0], [0, 621.44], [961.35, 621.44]]
        REAL_CORNERS = [[0, 0], [961, 0], [0, 621], [961, 621]]

        # pixel_width = 514 - 16
        pixel_height = 461 - 140

        # real_width = 961
        real_height = 621

        # width_ratio = pixel_width / real_width
        height_ratio = pixel_height / real_height
        image_file = glob.glob(os.path.join("./extrinsic/", "*.jpg")) + glob.glob(
            os.path.join("./extrinsic/", "*.png")
        )

        image = cv2.imread(image_file[0], cv2.IMREAD_GRAYSCALE)
        corners, _, _ = aruco.detectMarkers(image, self.arucodict)

        print(corners[0])
        aruco_perimeter = cv2.arcLength(corners[0], True)
        # Pixel to cm ratio
        pixel_mm_ratio = aruco_perimeter / (self.marker_length * 4) * 10

        # print(aruco_perimeter, pixel_mm_ratio)

        return (pixel_mm_ratio, height_ratio)

    def y_transform(self, coords):
        x, y = coords
        fac = 100 + (35 / 621 * 100)
        ty = y /100 * fac
        yform_coords = x, ty
        xform_coords = self.x_transform(yform_coords)
        return xform_coords

    def x_transform(self, coords):
        x, ty = coords
        fac = (20 / 961 * 100) +100
        tx = x /100 * fac
        facy = 100 - (30 / 621 * 100)
        tty = ty / 100 * facy
        xform_coords = tx, tty
        return xform_coords

    def draw_axis(
        self,
        img,
        camera_matrix,
        distortion_coefficients,
        rotation_vectors,
        translation_vectors,
    ):
        # Define the 3D points for the axes
        points = np.float32([[1000, 0, 0], [0, 1000, 0], [0, 0, 1000], [0, 0, 0]]).reshape(
            -1, 3
        )

        # Use the rotation and translation vectors returned from the camera calibration
        R = rotation_vectors[0]  # Use the first rotation vector
        t = translation_vectors[0]  # Use the first translation vector

        # Define the camera matrix and distortion coefficients returned from the camera calibration
        K = camera_matrix
        distCoeffs = distortion_coefficients

        # Project the 3D points onto the image plane
        axisPoints, _ = cv2.projectPoints(points, R, t, K, distCoeffs)

        # Draw the axes on the image
        cv2.line(img, tuple(axisPoints[3].ravel().astype(int)), tuple(axisPoints[0].ravel().astype(int)), (255, 0, 0), 3)  # Red color for X-axis
        cv2.line(img, tuple(axisPoints[3].ravel().astype(int)), tuple(axisPoints[1].ravel().astype(int)), (0, 255, 0), 3)  # Green color for Y-axis
        cv2.line(img, tuple(axisPoints[3].ravel().astype(int)), tuple(axisPoints[2].ravel().astype(int)), (0, 0, 255), 3)  # Blue color for Z-axis


        return img
