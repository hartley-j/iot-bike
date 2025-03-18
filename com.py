import serial
import time

class SerialPort:
    BUFFER_SIZE = 600  # Maximum buffer size
    
    def __init__(self, device):
        self.device = device
        self.ser = None

    def open_port(self, baud_rate=115200, data_bits=8, parity='N', stop_bits=1):
        print(f"Opening device [{self.device}]")
        try:
            # Initialize the serial connection
            self.ser = serial.Serial(
                port=self.device,
                baudrate=baud_rate,
                bytesize=self._data_bits(data_bits),
                parity=self._parity(parity),
                stopbits=self._stop_bits(stop_bits),
                timeout=1
            )
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            return -1

        if self.ser.is_open:
            print(f"Serial port {self.device} opened successfully")
            return self.ser
        else:
            print(f"Failed to open serial port {self.device}")
            return -1

    def _data_bits(self, data_bits):
        """Map data bits to pyserial constants"""
        if data_bits == 7:
            return serial.SEVENBITS
        return serial.EIGHTBITS

    def _parity(self, parity):
        """Map parity to pyserial constants"""
        if parity in ('n', 'N'):
            return serial.PARITY_NONE
        elif parity in ('o', 'O'):
            return serial.PARITY_ODD
        elif parity in ('e', 'E'):
            return serial.PARITY_EVEN
        elif parity in ('s', 'S'):  # No parity
            return serial.PARITY_SPACE
        return serial.PARITY_NONE

    def _stop_bits(self, stop_bits):
        """Map stop bits to pyserial constants"""
        if stop_bits == 1:
            return serial.STOPBITS_ONE
        elif stop_bits == 2:
            return serial.STOPBITS_TWO
        return serial.STOPBITS_ONE

    def delay_ms(self, ms):
        """Delay in milliseconds"""
        time.sleep(ms / 1000)

    def read_buffer(self):
        """Read data from serial buffer"""
        if not self.ser or not self.ser.is_open:
            print("Serial port is not open")
            return -1
        
        buffer = bytearray()
        total_read = 0

        while True:
            rbuffer = self.ser.read(32)
            if len(rbuffer) == 0:
                break

            buffer.extend(rbuffer)
            total_read += len(rbuffer)

            if total_read >= self.BUFFER_SIZE:
                print("Buffer overflow")
                return -1

            self.delay_ms(20)
        
        return total_read, buffer.decode('utf-8')
