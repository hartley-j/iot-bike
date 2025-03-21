import re
import serial
import time

class GPS:

    BUFFER_SIZE = 1024

    def __init__(self, port="/dev/ttyACM0", baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.buffer = bytearray(self.BUFFER_SIZE)


        if not self.serial.is_open:
            self.serial.open()

        self.utc_time = ""
        self.useful = False # Flag to check if data is useful at any single point
        self.latitude = None
        self.longitude = None
        self.n_s = ""
        self.e_w = ""

    def update(self):
        """Reads data from the serial port and saves data if useful
        """
        
        self.buffer = self.serial.read(self.BUFFER_SIZE).decode("utf-8")
        head = re.search(r'\$GPRMC|\$GNRMC', self.buffer)

        if head:
            head_pos = head.start()
            tail = self.buffer.find('\n', head_pos)

            if tail > head_pos:
                raw_data = self.buffer[head_pos:tail]

                fields = raw_data.split(',')
                
                if len(fields) >= 7:
                    self.utc_time = fields[1]
                    self.useful = fields[2] == 'A'
                    
                    if self.useful:
                        self.latitude, self.longitude = self._dm_to_dd(fields[3], fields[4], fields[5], fields[6])

                else:
                    self.useful = False

    def get_latlong(self):
        return self.useful, (self.latitude, self.longitude)

    def save_latlong(self):
        if self.useful:

            self.saved_latitude = self.latitude
            self.saved_longitude = self.longitude

            return True
        else:
            return False

    def check_latlong(self):
        lat_difference = abs(self.latitude_buffer - self.savedlatitude)
        lon_difference = abs(self.longitude_buffer - self.savedlongitude)

        if lat_difference <= 0.0000898 or lon_difference <= 0.0000898:
            return True
        else:
            return False
    
    def loop(self):
        """Used for testing
        """

        try:
            while True:

                self.update()

                if self.useful:
                    print(f"***************************************************")
                    print(f"UTC Time: {self.utc_time}")
                    print(f"Latitude: {self.latitude}\n")
                    print(f"Longitude: {self.longitude}\n")
                    print(f"***************************************************\n")
                else:
                    print(f"***************************************************")
                    print("Data is not useful")
                    print(f"***************************************************\n")

        except KeyboardInterrupt:
            print("Stopping")
        finally:
            self.serial.close()

    def _dm_to_dd(self, lat, n_s, long, e_w):
        
        lat_multiplier = -1 if n_s == 'S' else 1
        long_multiplier = -1 if e_w == 'W' else 1

        d_lat = float(lat[:2])
        d_long = float(long[:3])

        m_lat = float(lat[2:])
        m_long = float(long[3:])

        return lat_multiplier*(d_lat + (m_lat/60)), long_multiplier*(d_long + (m_long/60))






        


# class GPS:
#     BUFFER_SIZE = 1024

#     def __init__(self, port="/dev/ttyACM0", baudrate=115200):
#         self.ser = serial.Serial(port, baudrate, timeout=1)
#         self.buffer = bytearray(self.BUFFER_SIZE)

#         self.latitude_buffer = None
#         self.longitude_buffer = None

#         self.GPS_DATA = ""
#         self.GetData_Flag = False  # Flag indicating whether GPS data is obtained
#         self.ParseData_Flag = False  # Flag indicating whether parsing is complete
#         self.UTCTime = ""  # UTC time
#         self.latitude_buffer = ""  # Latitude
#         self.N_S = ""  # North/South indicator
#         self.longitude_buffer = ""  # Longitude
#         self.E_W = ""  # East/West indicator
#         self.Usefull_Flag = False  # Indicates whether positioning info is valid

#         self.latitude = None
#         self.longitude = None

#     def open_port(self):
#         """Open the serial port."""
#         if not self.ser.is_open:
#             self.ser.open()

#     def close_port(self):
#         """Close the serial port."""
#         if self.ser.is_open:
#             self.ser.close()

#     def read_buffer(self):
#         """Read from the serial port."""
#         self.buffer = self.ser.read(self.BUFFER_SIZE)
#         return len(self.buffer), self.buffer.decode('utf-8')

#     def update_data(self):
#         buffer_size, buffer_data = self.read_buffer()

#         if buffer_size > 0:

#             self.read_GPS_data(buffer_data)
#             self.parse_gps_data()

#             if self.ParseData_Flag and self.Usefull_Flag:

#                 # self.print_save()
#                 self.latitude = float(self.latitude_buffer)
#                 self.longitude = float(self.longitude_buffer)

#                 # Reset flags
#                 self.Usefull_Flag = False
#                 self.ParseData_Flag = False


#     def read_GPS_data(self, gps_buffer):
#         gps_data_head = None

#         # Check if the buffer contains GPS data starting with $GPRMC or $GNRMC
#         gps_data_head = re.search(r'\$GPRMC,|\$GNRMC', gps_buffer)
        
#         if gps_data_head:
            
#             gps_data_head_pos = gps_data_head.start()
#             gps_data_tail = gps_buffer.find('\n', gps_data_head_pos)
            
#             if gps_data_tail > gps_data_head_pos:
#                 self.GPS_DATA = gps_buffer[gps_data_head_pos:gps_data_tail]
#                 self.GetData_Flag = True

#     def parse_gps_data(self):
#         """Parses the GPS data if data has been read."""
#         if self.GetData_Flag:
#             self.GetData_Flag = False

#             fields = self.GPS_DATA.split(',')
#             if len(fields) >= 7:
#                 # Extract fields based on position
#                 self.reset_buffer(self.UTCTime)
#                 self.UTCTime = fields[1]  # UTC time

#                 usefull_buffer = fields[2]  # Positioning status
#                 self.reset_buffer(self.latitude_buffer)
#                 self.latitude_buffer = fields[3]  # Latitude

#                 self.reset_buffer(self.N_S)
#                 self.N_S = fields[4]  # N/S indicator

#                 self.reset_buffer(self.longitude_buffer)
#                 self.longitude_buffer = fields[5]  # Longitude

#                 self.reset_buffer(self.E_W)
#                 self.E_W = fields[6]  # E/W indicator

#                 self.ParseData_Flag = True
#                 self.Usefull_Flag = usefull_buffer == 'A'  # A for valid, V for invalid
#             else:
#                 print("Error: Incomplete GPS data")

#     def reset_buffer(self, buffer):
#         """Resets the buffer (clears the string)."""
#         buffer = ""

#     def print_save(self):
#         """Prints and formats the saved GPS data."""
#         print("*****************************************************")
#         print(f"UTCTime\t\t:[{self.UTCTime}]")
#         print(f"Slatitude\t:[{self.latitude_buffer}]")
#         print(f"N/S\t\t:[{self.N_S}]")
#         print(f"Slongitude\t:[{self.longitude_buffer}]")
#         print(f"E/W\t\t:[{self.E_W}]")
#         print(f"{self.latitude_buffer}, {self.longitude_buffer}")
#         print("*****************************************************")

#     def insert_array(self, buff):
#         """Inserts a space before the last two digits of the integer part of the coordinates."""
#         p = buff.find(".")
#         if p > 2:
#             return buff[:p-2] + ' ' + buff[p-2:]
#         return buff

#     def get_data(self):
#         return self.latitude, self.longitude

#     def savelatlong(self): # To be ran when sentry mode activated

#         if self.Usefull_Flag:
#             self.savedlatitude=self.latitude
#             self.savedlongitude=self.longitude

#     def checklatlong(self): # To be ran while in sentry mode
#         lat_difference = abs(self.latitude_buffer - self.savedlatitude)
#         lon_difference = abs(self.longitude_buffer - self.savedlongitude)

#         if lat_difference <= 0.0000898 or lon_difference <= 0.0000898:
#             return True
#         else:
#             return False
    
#     def main_loop(self):
#         """Main loop to continuously read and process GPS data."""
#         try:
#             while True:
#                 # Read from the buffer
#                 buffer_size, buffer_data = self.read_buffer()
#                 if buffer_size > 0:
#                     # Pass the buffer data to GPS data handling
#                     self.read_GPS_data(buffer_data)
#                     self.parse_gps_data()

#                     # Check if data is valid and ready
#                     if self.ParseData_Flag and self.Usefull_Flag:
#                         self.print_save()

#                         # Reset flags
#                         self.Usefull_Flag = False
#                         self.ParseData_Flag = False
#                     else:
#                         print("Invalid GPS data")

#                 time.sleep(1)

#         except KeyboardInterrupt:
#             print("Stopping GPS reader.")
#         finally:
#             self.close_port()

# # Example usage
if __name__ == "__main__":
    gps = GPS()
    gps.loop()

