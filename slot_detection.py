import serial

from communication_queues import Queues

QUEUES = Queues.get_instance()

try:
    SER = serial.Serial(port="/dev/ttyUSB0", baudrate=115200, timeout=1)
except:
    raise Exception("Could not connect to lasersensor")

class SlotDetection:
    def __init__(self) -> None:
        self.ser = SER
        self.width_list = []

        self._settings_sensor()

    def append_size(self) -> None:
        self._send_command("1,000,1,") # get control
        self._send_command("1,002,1,") # apply settings
        measurement = self._send_command("1,031,") #get measurement
        decode = measurement.decode("utf-8").strip("{}").split(",")
        saved = float(decode[2])
        self.width_list.append(saved)

    def get_final_size(self) -> float:
        self._send_command("1,000,1,") # get control
        width = max(self.width_list)

        lower_bound = 1
        upper_bound = round(width - 2.5, 1)
        self._send_command(f"1,070,1,{lower_bound},{upper_bound},0,") # set digital out (window)

        self.width_list.clear()
        self._send_command("1,000,0,") # release control

        QUEUES.logging_queue.put(f"sleeve width: {width}")

        return width

    def _settings_sensor(self) -> None:
        if SER.isOpen():
            self._send_command("1,000,1,") # get control
            self._send_command("1,040,1,") # set precision
            self._send_command("1,010,2,") # set baudrate
            self._send_command("1,020,4,") # set measurement to width
            self._send_command("1,070,1,0.5,50,0,") # set digital out (window)
            self._send_command("1,001,1,") # store settings
            self._send_command("1,002,1,") # apply settings
            self._send_command("1,000,0,") # release control

            QUEUES.logging_queue.put("laser settings set")

    def _send_command(self, controlcommand: str) -> bytes:
        controlcommand = "{" + controlcommand
        for i in range(len(controlcommand)):
            if i == 0:
                value = int(ord(controlcommand[i]))
            else:
                value = int(ord(controlcommand[i])) ^ value
        checksum = str(value) + "}"
        fullcommand = (controlcommand + checksum).encode("ascii")
        SER.write(bytearray(fullcommand))

        byte_amount = 48 if len(controlcommand) >= 9 else 40

        return SER.read(byte_amount)



