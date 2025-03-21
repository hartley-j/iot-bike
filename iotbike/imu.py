
from time import sleep

from sense_hat import SenseHat

# class SenseHat:

#     def __init__(self):
#         self.acceleration = {"x": 0.001, "y": 24, "z": 9.81}

#     def get_accelerometer_raw(self):
#         return self.acceleration


class IMU:

    def __init__(self):
        self.sense = SenseHat()

        

        self.update_data()

    def update_data(self):

        acceleration = self.sense.get_accelerometer_raw()

        self.x = acceleration['x']
        self.y = acceleration['y']
        self.z = acceleration['z']

    def get_data(self):

        return self.x, self.y, self.z

    def is_moving(self):
        if abs(self.x) > 1 or abs(self.y) > 1 or abs(self.z) > 1:
            self.sense.show_letter("!",(255, 0, 0))
            return True
        else:
            self.sense.clear()
            return False

    #def __del__(self):
     #   self.sense.clear()
        
if __name__=="__main__":
    
    imu=IMU()
    while True:
        sleep(1)
        imu.update_data()
        print(imu.get_data())
        print(imu.is_moving())
        
    


