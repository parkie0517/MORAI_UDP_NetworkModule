import cv2
import numpy as np
import time
from multiprocessing import Process
from lib.network.UDP import Receiver
from lib.define.Camera import Camera
from lib.define.EgoVehicleStatus import EgoVehicleStatus

# 데이터 전송 받을 컴퓨터 IP와 포트 설정
IP = '143.248.59.11' # 데이터를 받을 리눅스 서버 IP 입력하기
CAMERA_PORT_1 = 4011  # 첫 번째 카메라 포트
CAMERA_PORT_2 = 4021  # 두 번째 카메라 포트
EGO_PORT = 4091       # EgoVehicleStatus 포트

def camera_process():
    # 두 카메라의 Receiver 객체 생성
    cam_data_1 = Receiver(IP, CAMERA_PORT_1, Camera())
    cam_data_2 = Receiver(IP, CAMERA_PORT_2, Camera())
    # 카메라 5개 사용할 거면 아래에 3개 더 추가하면 됨

    while True:
        # 첫 번째 카메라 데이터 처리
        data_1 = cam_data_1.get_data()
        buf1 = np.frombuffer(data_1.image.data, dtype=np.uint8)
        image_1 = None if buf1.size == 0 else cv2.imdecode(buf1, cv2.IMREAD_COLOR)
        
        # 두 번째 카메라 데이터 처리
        data_2 = cam_data_2.get_data()
        buf2 = np.frombuffer(data_2.image.data, dtype=np.uint8)
        image_2 = None if buf2.size == 0 else cv2.imdecode(buf2, cv2.IMREAD_COLOR)
        
        # 두 이미지 모두 데이터가 없으면 이번 루프 건너뛰기
        if image_1 is None and image_2 is None:
            continue
        
        # 한 쪽 이미지가 None이면, 다른 이미지와 동일한 크기의 빈 이미지 생성
        if image_1 is None and image_2 is not None:
            image_1 = np.zeros_like(image_2)
        if image_2 is None and image_1 is not None:
            image_2 = np.zeros_like(image_1)
        
        # 두 이미지의 높이가 다르면, 두 번째 이미지를 첫 번째 이미지의 높이에 맞게 리사이즈
        if image_1.shape[0] != image_2.shape[0]:
            new_width = int(image_2.shape[1] * (image_1.shape[0] / image_2.shape[0]))
            image_2 = cv2.resize(image_2, (new_width, image_1.shape[0]))
        
        # 두 이미지를 수평으로 이어 붙임
        combined_image = cv2.hconcat([image_1, image_2])
        cv2.imshow("Combined Camera Feed", combined_image)
        
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

def ego_status_process():
    # EgoVehicleStatus Receiver 객체 생성
    egovehiclestatus = Receiver(IP, EGO_PORT, EgoVehicleStatus())
    while True:
        status = egovehiclestatus.get_data()
        print(status)
        time.sleep(0.1)

if __name__ == '__main__':
    # 멀티프로세싱을 이용해 각각의 함수(카메라 처리, ego status 처리)를 별도의 프로세스로 실행
    p_camera = Process(target=camera_process)
    p_ego = Process(target=ego_status_process)
    
    p_camera.start()
    p_ego.start()
    
    p_camera.join()
    p_ego.join()
