import datetime
import queue
import signal
import threading

from robot_connection import RobotConnection, Queues
from sleeve_detection import SleeveDetection
from communication_queues import Queues
from flask import Flask, render_template, Response, stream_with_context, request, redirect, url_for

APP = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static", )
EXIT_EVENT = threading.Event()

ROBOT_CONNECTION = RobotConnection()
SLEEVE_DETECTION = SleeveDetection()
QUEUES = Queues.get_instance()

@APP.route('/video_feed')
def video_feed():
    return Response(stream_with_context(fetch_video_feed()), mimetype='multipart/x-mixed-replace; boundary=frame')

@APP.route('/logs')
def logs():
    return Response(fetch_log_feed(), mimetype='text/plain')

@APP.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'start_btn' in request.form:
            start_robot()
        elif 'stop_btn' in request.form:
            stop_robot()

        return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('index.j2', start_btn=ROBOT_CONNECTION.robot_running)

    return render_template('index.j2', start_btn=ROBOT_CONNECTION.robot_running)

@APP.before_first_request
def initialize_app() -> None:
    main_thread = threading.Thread(target=main_loop)
    main_thread.name = "detection"
    main_thread.daemon = True
    main_thread.start()

    connection_thread = threading.Thread(target=robot_connection)
    connection_thread.name = "robot connection"
    connection_thread.daemon = True
    connection_thread.start()

def start_robot():
    ROBOT_CONNECTION.robot_running = True
    QUEUES.logging_queue.put("started robot process")

def stop_robot():
    ROBOT_CONNECTION.robot_running = False
    SLEEVE_DETECTION.reset()
    QUEUES.logging_queue.put("ending robot process")

def main_loop() -> None:
    handle_thread(SLEEVE_DETECTION.detect)

def robot_connection() -> None:
    handle_thread(ROBOT_CONNECTION.initialize_connection)


def handle_interrupt(signum=None, frame=None) -> None:
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
        try:
            frame = QUEUES.video_feed_queue.get(timeout=1.0)
            yield frame
        except queue.Empty:
            continue

def fetch_log_feed():
    while True:
        try:
            log = QUEUES.logging_queue.get() + '\n'
            log = f"[{datetime.datetime.now().strftime('%D:%H:%M:%S')}] {log}"

            if "ending process" in log:
                stop_robot()

            print(log)

            yield log
        except queue.Empty:
            continue

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt)
    APP.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
