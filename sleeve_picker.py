import queue
import signal
import threading
import time
from robot_connection import RobotConnection
from sleeve_callibration import Callibration
from sleeve_detection import SleeveDetection

from flask import Flask, render_template, Response, stream_with_context


APP = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static", )
EXIT_EVENT = threading.Event()

ROBOT_CONNECTION = RobotConnection()
SLEEVE_DETECTION = SleeveDetection()
# CALLIBRATION = Callibration(5, 8)

video_feed_queue = queue.Queue()

@APP.route('/video_feed')
def video_feed():
    return Response(stream_with_context(fetch_video_feed()), mimetype='multipart/x-mixed-replace; boundary=frame')

@APP.route('/')
def index():
    return render_template('index.html')

@APP.before_first_request
def start_app() -> None:
    # CALLIBRATION.take_pictures()
    # return
    # SLEEVE_DETECTION.connect_camera(None, None)
    # return

    # x, y = SLOT_DETECTOR.detect_slot()
    # print(x, y)
    # return
    robot_data_queue = queue.Queue()
    robot_request_queue = queue.Queue()

    # SLEEVE_DETECTION.detect(shared_queues)
    # return

    main_thread = threading.Thread(target=main_loop, args=((robot_data_queue, robot_request_queue, video_feed_queue), ))
    connection_thread = threading.Thread(target=robot_connection, args=((robot_data_queue, robot_request_queue), ))

    main_thread.name = "detection"
    connection_thread.name = "robot connection"

    main_thread.daemon = True
    connection_thread.daemon = True

    main_thread.start()
    connection_thread.start()

    while connection_thread.is_alive():
        if EXIT_EVENT.is_set():
            raise Exception("Program stopped")
        time.sleep(1)

    main_thread.join()
    connection_thread.join()

def main_loop(queues):
    handle_thread(SLEEVE_DETECTION.detect, queues)

def robot_connection(queues):
    handle_thread(ROBOT_CONNECTION.send_coords, queues)


def handle_interrupt(signum=None, frame=None):
    EXIT_EVENT.set()

def handle_thread(function: callable, *args) -> None:
    while not EXIT_EVENT.is_set():
        try:
            function(*args)
        except Exception as e:
            raise e
        finally:
            handle_interrupt()

def fetch_video_feed():
    while True:
        if len(video_feed_queue.queue) <= 0:
            continue

        frame = video_feed_queue.get()
        yield frame

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt)
    # APP.run(host='0.0.0.0', port=5000, debug=True)
    start_app()