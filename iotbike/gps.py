import re
import serial
import time

class GPSData:
    def __init__(self):
        self.GPS_DATA = ""
        self.GetData_Flag = False  # Flag indicating whether GPS data is obtained
        self.ParseData_Flag = False  # Flag indicating whether parsing is complete
        self.UTCTime = ""  # UTC time
        self.latitude = ""  # Latitude
        self.N_S = ""  # North/South indicator
        self.longitude = ""  # Longitude
        self.E_W = ""  # East/West indicator
        self.Usefull_Flag = False  # Indicates whether positioning info is valid

    def read_GPS_data(self, gps_buffer):
        """Reads GPS data from the buffer."""
        gps_data_head = None

        # Check if the buffer contains GPS data starting with $GPRMC or $GNRMC
        gps_data_head = re.search(r'\$GPRMC,|\$GNRMC', gps_buffer)
        
        if gps_data_head:
            
            gps_data_head_pos = gps_data_head.start()
            gps_data_tail = gps_buffer.find('\n', gps_data_head_pos)
            
            if gps_data_tail > gps_data_head_pos:
                self.GPS_DATA = gps_buffer[gps_data_head_pos:gps_data_tail]
                self.GetData_Flag = True

    def parse_gps_data(self):
        """Parses the GPS data if data has been read."""
        if self.GetData_Flag:
            self.GetData_Flag = False

            fields = self.GPS_DATA.split(',')
            if len(fields) >= 7:
                # Extract fields based on position
                self.reset_buffer(self.UTCTime)
                self.UTCTime = fields[1]  # UTC time

                usefull_buffer = fields[2]  # Positioning status
                self.reset_buffer(self.latitude)
                self.latitude = fields[3]  # Latitude

                self.reset_buffer(self.N_S)
                self.N_S = fields[4]  # N/S indicator

                self.reset_buffer(self.longitude)
                self.longitude = fields[5]  # Longitude

                self.reset_buffer(self.E_W)
                self.E_W = fields[6]  # E/W indicator

                self.ParseData_Flag = True
                self.Usefull_Flag = usefull_buffer == 'A'  # A for valid, V for invalid
            else:
                print("Error: Incomplete GPS data")

    def reset_buffer(self, buffer):
        """Resets the buffer (clears the string)."""
        buffer = ""

    def print_save(self):
        """Prints and formats the saved GPS data."""
        print("*****************************************************")
        print(f"UTCTime\t\t:[{self.UTCTime}]")
        print(f"Slatitude\t:[{self.latitude}]")
        print(f"N/S\t\t:[{self.N_S}]")
        print(f"Slongitude\t:[{self.longitude}]")
        print(f"E/W\t\t:[{self.E_W}]")
        self.latitude = self.insert_array(self.latitude)
        self.longitude = self.insert_array(self.longitude)
        print(f"{self.latitude}, {self.longitude}")
        print("*****************************************************")

    def insert_array(self, buff):
        """Inserts a space before the last two digits of the integer part of the coordinates."""
        p = buff.find(".")
        if p > 2:
            return buff[:p-2] + ' ' + buff[p-2:]
        return buff


class GPSReader:
    BUFFER_SIZE = 1024

    def __init__(self, port="/dev/ttyACM0", baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.gps = GPSData()
        self.buffer = bytearray(self.BUFFER_SIZE)

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
        self.buffer = self.ser.read(self.BUFFER_SIZE)
        return len(self.buffer), self.buffer.decode('utf-8')

    def get_data(self):
        buffer_size, buffer_data = self.read_buffer()

        if buffer_size > 0:

            self.gps.read_GPS_data(buffer_data)
            self.gps.parse_gps_data()

            if self.gps.ParseData_Flag and self.gps.Usefull_Flag:
                self.gps.print_save()

                # Reset flags
                self.gps.Usefull_Flag = False
                self.gps.ParseData_Flag = False

                return self.gps.latitude, self.gps.longitude

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

