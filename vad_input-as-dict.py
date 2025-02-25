import cv2
import numpy as np
import time
from multiprocessing import Process, Manager
from lib.network.UDP import Receiver
from lib.define.Camera import Camera
from lib.define.EgoVehicleStatus import EgoVehicleStatus

# 수신할 컴퓨터의 IP와 각 포트 번호
IP = '143.248.59.11'
CAMERA_PORT_1 = 4011  # 카메라 영상1 포트
CAMERA_PORT_2 = 4021  # 카메라 영상2 포트
EGO_PORT = 4091       # EgoVehicleStatus 포트

def update_gps_buffer(self, control, theta, speed):
    yaw = np.array([(theta - np.pi/2.0)])
    speed = np.array([speed])
    action = np.array(np.stack([control.steer, control.throttle, control.brake], axis=-1))

    #Update gps locations
    for i in range(len(self.gps_buffer)):
        loc =self.gps_buffer[i]
        loc_temp = np.array([loc[1], -loc[0]]) #Bicycle model uses a different coordinate system
        next_loc_tmp, _, _ = self.ego_model.forward(loc_temp, yaw, speed, action)
        next_loc = np.array([-next_loc_tmp[1], next_loc_tmp[0]])
        self.gps_buffer[i] = next_loc

    return None

def camera_process(shared_dict):
    cam1 = Receiver(IP, CAMERA_PORT_1, Camera())
    cam2 = Receiver(IP, CAMERA_PORT_2, Camera())
    while True:
        # 카메라1 데이터 처리
        data1 = cam1.get_data()
        buf1 = np.frombuffer(data1.image.data, dtype=np.uint8)
        image1 = None if buf1.size == 0 else cv2.imdecode(buf1, cv2.IMREAD_COLOR)
        if image1 is not None:
            # 실제 영상 데이터 대신 영상의 shape 정보만 저장
            shared_dict['camera1'] = f"Image shape: {image1.shape}"
        else:
            shared_dict['camera1'] = "No image"
        
        # 카메라2 데이터 처리
        data2 = cam2.get_data()
        buf2 = np.frombuffer(data2.image.data, dtype=np.uint8)
        image2 = None if buf2.size == 0 else cv2.imdecode(buf2, cv2.IMREAD_COLOR)
        if image2 is not None:
            shared_dict['camera2'] = f"Image shape: {image2.shape}"
        else:
            shared_dict['camera2'] = "No image"
        
        time.sleep(0.01)  # 짧은 딜레이

def ego_status_process(shared_dict):
    ego_receiver = Receiver(IP, EGO_PORT, EgoVehicleStatus())
    while True:
        status = ego_receiver.get_data()
        # status 객체의 멤버에 접근해 필요한 항목만 공유 딕셔너리에 저장
        shared_dict['vel_x'] = status.vel_x
        shared_dict['vel_y'] = status.vel_y
        shared_dict['vel_z'] = status.vel_z
        shared_dict['pos_x'] = status.pos_x
        shared_dict['pos_y'] = status.pos_y
        shared_dict['pos_z'] = status.pos_z
        time.sleep(0.1)

def print_status(shared_dict):
    while True:
        # 터미널에는 딕셔너리의 키들만 출력 (영상 데이터는 생략)
        if bool(shared_dict):
            # print("현재 dict keys:", list(shared_dict.keys()))
            print("pos_X: ", shared_dict['pos_x'])
            print("pos_Y: ", shared_dict['pos_y'])
            print("pos_Z: ", shared_dict['pos_z'])
            print("\n\n")
        time.sleep(0.5)

if __name__ == '__main__':
    manager = Manager()
    shared_dict = manager.dict()
    
    p_camera = Process(target=camera_process, args=(shared_dict,))
    p_ego = Process(target=ego_status_process, args=(shared_dict,))
    p_print = Process(target=print_status, args=(shared_dict,))
    
    p_camera.start()
    p_ego.start()
    p_print.start()
    
    p_camera.join()
    p_ego.join()
    p_print.join()
