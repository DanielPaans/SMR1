import errno
import queue
import re
import socket
from communication_queues import Queues
from slot_detection import SlotDetection

QUEUES = Queues.get_instance()
PORT = 1025
ROBOT_IP = "10.24.8.2"

SLOT_DETECTOR = SlotDetection()
SER = SLOT_DETECTOR.ser

class RobotConnection:
    robot_running = False

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sleeve_count = 0
        self.size_asked_count = 0

    def initialize_connection(self):
        while True:
            if not self.robot_running:
                continue

            self.send_coords()
            self.__init__()

        SER.close()

    def send_coords(self) -> None:
        while True:
            try:
                robot_request = self._receive()

                if robot_request == "":
                    continue

                QUEUES.logging_queue.put(f"robot: {robot_request}")

                if not self.robot_running:
                    QUEUES.logging_queue.put(f"ending process")
                    self._send("none")
                    break

                if robot_request == "coords":
                    coord_string: str = self._fetch_coords()

                    if not re.match(
                        r"(none|-?\d+\.\d+;-?\d+\.\d+;(left|right))", coord_string
                    ):
                        raise Exception(
                            "Invalid coordinate string: " + coord_string
                        )

                    self._send(coord_string)
                    self.sleeve_count += 1

                    if coord_string == "none":
                        QUEUES.logging_queue.put(f"ending process")
                        break

                    x, y, direction = coord_string.split(';')
                    QUEUES.logging_queue.put(f"sleeve coords: [{round(float(x), 2)}, {round(float(y), 2)}], sleeve going {direction}")


                elif robot_request == "size":
                    self.size_asked_count += 1

                    if self.size_asked_count >= 3:
                        size = SLOT_DETECTOR.get_final_size()
                        self.size_asked_count = 0
                        self._send(str(size))
                    else:
                        size = SLOT_DETECTOR.append_size()
                        self._send(str(0))

                else:
                    QUEUES.logging_queue.put(f"error: request {robot_request} from robot does not exist")
                    self._send("error")

            except (OSError, IOError, socket.timeout) as e:
                if e.errno in [107, 106] or e.errno == errno.EPIPE:
                    # QUEUES.logging_queue.put(f"warning: {e.strerror}")
                    if not self.robot_running:
                        break

                    self._connect()

                if socket.timeout:
                    continue

                else:
                    if e is not None and e not in ["", "\n"]:
                        QUEUES.logging_queue.put(e.with_traceback())

                print(e)

        self._close()

    def _fetch_coords(self) -> str:
        request_message = f"request_sleeve:{self.sleeve_count}"
        QUEUES.robot_request_queue.put(request_message)

        while True:
            if QUEUES.robot_data_queue.empty():
                continue

            message = QUEUES.robot_data_queue.get()
            return message

    def _connect(self) -> None:
        try:
            self.client.settimeout(5)
            self.client.connect((ROBOT_IP, 1025))
        except OSError:
            QUEUES.logging_queue.put("warning: trying to connect to robot...")
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _send(self, message: str) -> None:
        self.client.send(message.encode())

    def _receive(self) -> None:
        from_server = self.client.recv(4096)
        string = from_server.decode()
        return string

    def _close(self) -> None:
        self.client.close()


