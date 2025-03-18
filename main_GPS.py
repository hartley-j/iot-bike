import serial
import time

from GPS import GPSData
from com import SerialPort

class GPSReader:
    BUFFER_SIZE = 1024

    def __init__(self, port="/dev/ttyACM0", baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.gps = GPSData()
        self.read_buffer = bytearray(self.BUFFER_SIZE)

    def open_port(self):
        """Open the serial port."""
        if not self.ser.is_open:
            self.ser.open()

    def close_port(self):
        """Close the serial port."""
        if self.ser.is_open:
            self.ser.close()

    def read_buffer(self):
        """Read from the serial port."""
        self.read_buffer = self.ser.read(self.BUFFER_SIZE)
        return len(self.read_buffer), self.read_buffer.decode('utf-8')

    def main_loop(self):
        """Main loop to continuously read and process GPS data."""
        try:
            while True:
                # Read from the buffer
                buffer_size, buffer_data = self.read_buffer()
                if buffer_size > 0:
                    # Pass the buffer data to GPS data handling
                    self.gps.read_GPS_data(buffer_data)
                    self.gps.parse_gps_data()

                    # Check if data is valid and ready
                    if self.gps.ParseData_Flag and self.gps.Usefull_Flag:
                        self.gps.print_save()

                        # Reset flags
                        self.gps.Usefull_Flag = False
                        self.gps.ParseData_Flag = False
                    else:
                        print("Invalid GPS data")

                time.sleep(1)

        except KeyboardInterrupt:
            print("Stopping GPS reader.")
        finally:
            self.close_port()

# Example usage
if __name__ == "__main__":
    gps_reader = GPSReader("/dev/ttyACM0", 115200)
    gps_reader.open_port()
    gps_reader.main_loop()
