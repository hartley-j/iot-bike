import re

class GPSData:
    def __init__(self):
        self.GPS_DATA = ""
        self.GetData_Flag = False  # Flag indicating whether GPS data is obtained
        self.ParseData_Flag = False  # Flag indicating whether parsing is complete
        self.UTCTime = ""  # UTC time
        self.Slatitude = ""  # Latitude
        self.N_S = ""  # North/South indicator
        self.Slongitude = ""  # Longitude
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
                self.reset_buffer(self.Slatitude)
                self.Slatitude = fields[3]  # Latitude

                self.reset_buffer(self.N_S)
                self.N_S = fields[4]  # N/S indicator

                self.reset_buffer(self.Slongitude)
                self.Slongitude = fields[5]  # Longitude

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
        print(f"Slatitude\t:[{self.Slatitude}]")
        print(f"N/S\t\t:[{self.N_S}]")
        print(f"Slongitude\t:[{self.Slongitude}]")
        print(f"E/W\t\t:[{self.E_W}]")
        self.Slatitude = self.insert_array(self.Slatitude)
        self.Slongitude = self.insert_array(self.Slongitude)
        print(f"{self.Slatitude}, {self.Slongitude}")
        print("*****************************************************")

    def insert_array(self, buff):
        """Inserts a space before the last two digits of the integer part of the coordinates."""
        p = buff.find(".")
        if p > 2:
            return buff[:p-2] + ' ' + buff[p-2:]
        return buff
