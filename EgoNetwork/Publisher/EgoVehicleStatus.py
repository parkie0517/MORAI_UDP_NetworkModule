import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import time
from lib.network.UDP import Receiver
from lib.define.EgoVehicleStatus import EgoVehicleStatus

IP = '143.248.59.11' 
PORT = 5091

#Protocol 정보
#https://help-morai-sim.scrollhelp.site/ko/morai-sim-drive/24.R2/ros-1#id-(24.R2-ko)통신메시지프로토콜-EgoVehicleStatus.1
def main():
    egovehiclestatus = Receiver(IP, PORT, EgoVehicleStatus())
    while True :
        status = egovehiclestatus.get_data()
        print(status)
        time.sleep(0.1)
        # print(f"pos_X: {status.pos_x}")
        # print(f"pos_Y: {status.pos_y}")
        # print(f"pos_Z: {status.pos_z}")
        
        # 커서를 3줄 위로 이동
        # sys.stdout.write("\033[F\033[F\033[F")  
        # sys.stdout.flush()

        
if __name__ == '__main__':
    main()