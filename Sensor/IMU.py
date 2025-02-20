import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import time
from lib.network.UDP import Receiver
from lib.define.IMU import IMU

IP = '143.248.50.159' # ego info 받는 컴퓨터/서버의 ip주소
PORT = 9091 # imu 센서의 destination port (시뮬에서 f3누르고 imu 세팅 들어가면 확인 가능)

#Protocol 정보
#https://help-morai-sim.scrollhelp.site/ko/morai-sim-drive/24.R2/ros-1#id-(24.R2-ko)통신메시지프로토콜-EgoVehicleStatus.1

import ctypes
print(ctypes.sizeof(IMU()))
def main():
    sensor_imu = Receiver(IP, PORT, IMU())
    while True :
        imu_data = sensor_imu.get_data()
        print(imu_data)
        
        time.sleep(0.1)

if __name__ == '__main__':
    main()