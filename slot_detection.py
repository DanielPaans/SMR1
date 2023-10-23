import serial

# SER = serial.Serial(port="/dev/ttyUSB0", baudrate=115200, timeout=1)


class SlotDetection:
    def __init__(self) -> None:
        self.ser = SER
        self.last_width = 0

        self._settings_sensor()

    def _send_command(self, controlcommand):
        controlcommand = "{" + controlcommand
        for i in range(len(controlcommand)):
            if i == 0:
                value = int(ord(controlcommand[i]))
            else:
                value = int(ord(controlcommand[i])) ^ value
        checksum = str(value) + "}"
        fullcommand = (controlcommand + checksum).encode("ascii")
        # return fullcommand
        SER.write(bytearray(fullcommand))
        return SER.read(32)

    def _settings_sensor(self):
        if SER.isOpen():
            self._send_command("1,000,1,") # get control
            self._send_command("1,040,1," ) # set precision
            self._send_command("1,010,2,") # set baudrate
            self._send_command("1,020,4,") # set measurement to width
            self._send_command("1,054,150,") # set field of view
            self._send_command("1,001,1,") # store settings
            self._send_command("1,002,1,") # apply settings
        print("settings set")

    def get_measurements(self):
        while True:
            try:
                # self._send_command("1,000,1,") # get control
                get_measurement = self._send_command("1,031,")
                width_decode = (
                    get_measurement.decode("utf-8").strip("{}").split(",")
                )
                width = float(width_decode[2])

                print(f"width is {width} {self.last_width}")

                if width is not None and self.last_width is not None:
                    slot = 1 if width < self.last_width - 1.8 else 0
                    self.last_width = width
                    return slot, width

            except Exception as e:
                print("error: ", get_measurement)

