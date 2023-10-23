import queue
import re
import socket
import time
from slot_detection import SlotDetection

PORT = 1025

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ROBOT_IP = "10.24.8.2"

# SLOT_DETECTOR = SlotDetection()
# SER = SLOT_DETECTOR.ser

class RobotConnection:
    def __init__(self):
        self.sleeve_count = 0
        # self.server = socket.create_server(("", PORT))

    # def start_server(self):
    #     with socket.create_server(("", PORT)):
    #         while True:
    #             pass

    def start_server(self, queues):
        while True:
            client_socket, client_address = self.server.accept()
            print(f"Accepted connection from {client_address}")
            try:
                while True:
                    from_client = client_socket.recv(4096)
                    string = from_client.decode()

                    print(string)

                    if string == "end":
                        self.send("ending")
                        break

                    if string == "coords":
                        coord_string = self._fetch_coords(queues)

                        if not re.match(
                            r"(none|-?\d+\.\d+;-?\d+\.\d+;(left|right))", coord_string
                        ):
                            raise Exception(
                                "Invalid coordinate string: " + coord_string
                            )

                        print(coord_string)
                        self.send(coord_string)

                    elif string == "size":
                        _, size = SLOT_DETECTOR.get_measurements()
                        self.send(str(size))

                    elif string == "slot":
                        detected_slot, _ = SLOT_DETECTOR.get_measurements()
                        self.send(str(detected_slot))

                    else:
                        self.send("error")
            except:
                pass
            finally:
                client_socket.close()

    def connect(self):
        CLIENT.connect((ROBOT_IP, 1025))

    def send(self, message):
        CLIENT.send(message.encode())

    def receive(self):
        from_server = CLIENT.recv(4096)
        string = from_server.decode()
        return string

    def close(self):
        CLIENT.close()

    def send_coords(self, queues):
        while True:
            try:
                from_server = CLIENT.recv(4096)
                string = from_server.decode()

                print(string)

                if string == "end":
                    self.send("ending")
                    break

                if string == "coords":
                    coord_string: str = self._fetch_coords(queues)

                    if not re.match(
                        r"(none|-?\d+\.\d+;-?\d+\.\d+;(left|right))", coord_string
                    ):
                        raise Exception(
                            "Invalid coordinate string: " + coord_string
                        )

                    print(coord_string)
                    self.send(coord_string)
                    self.sleeve_count += 1

                # elif string == "size":
                #     _, size = SLOT_DETECTOR.get_measurements()
                #     self.send(str(size))

                # elif string == "slot":
                #     detected_slot, _ = SLOT_DETECTOR.get_measurements()
                #     self.send(str(detected_slot))

                else:
                    self.send("error")
            except:
                self.connect()

        self.close()
        SER.close()

    def _fetch_coords(self, queues):
        request_queue, info_queue = queues
        request_message = f"request_sleeve:{self.sleeve_count}"
        request_queue.put(request_message)

        while True:
            if info_queue.empty():
                continue

            message = info_queue.get()
            return message
