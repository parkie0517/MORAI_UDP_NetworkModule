import multiprocessing
import cv2
import numpy as np
import time

# 모듈 임포트 (경로 설정이 필요하다면 sys.path.append() 등을 이용)
from lib.network.UDP import Receiver
from lib.define.Camera import Camera
from lib.define.EgoVehicleStatus import EgoVehicleStatus

# 각 카메라의 데이터를 받는 worker 함수
def camera_worker(queue, port):
    IP = '143.248.59.11' # 카메라 받을 리눅스 서버 IP
    receiver = Receiver(IP, port, Camera())
    while True:
        data = receiver.get_data()
        buf = np.frombuffer(data.image.data, dtype=np.uint8)
        if buf.size > 0:
            image = cv2.imdecode(buf, cv2.IMREAD_COLOR)
            # 이미지가 제대로 디코딩되었는지 확인
            if image is not None:
                queue.put(image)
            else:
                queue.put(None)
        else:
            # 데이터가 없으면 None 전송
            queue.put(None)

# Ego Vehicle Status를 받는 worker 함수
def ego_status_worker():
    IP = '143.248.59.11' # 정보 받을 서버의 IP
    PORT = 4091
    receiver = Receiver(IP, PORT, EgoVehicleStatus())
    while True:
        status = receiver.get_data()
        # 받은 상태를 콘솔에 출력
        print("Ego Status:", status)
        time.sleep(0.1)

def main():
    # 프로세스 간 통신을 위한 매니저 큐 생성
    manager = multiprocessing.Manager()
    cam1_queue = manager.Queue()
    cam2_queue = manager.Queue()
    
    # 카메라와 ego status를 위한 별도 프로세스 생성
    cam1_process = multiprocessing.Process(target=camera_worker, args=(cam1_queue, 4011))
    cam2_process = multiprocessing.Process(target=camera_worker, args=(cam2_queue, 4021))
    ego_process   = multiprocessing.Process(target=ego_status_worker)
    
    cam1_process.start()
    cam2_process.start()
    ego_process.start()
    
    while True:
        # 큐에서 이미지 읽기 (여기서는 blocking으로 처리)
        image1 = cam1_queue.get()
        image2 = cam2_queue.get()
        
        # 두 이미지가 모두 없으면 다음 루프로
        if image1 is None and image2 is None:
            print("no image")
            continue
        
        # 한쪽이 None이면 다른 쪽과 동일한 크기의 빈 이미지 생성
        if image1 is None and image2 is not None:
            image1 = np.zeros_like(image2)
        if image2 is None and image1 is not None:
            image2 = np.zeros_like(image1)
        
        # 두 이미지의 높이가 다르면 높이를 맞춰서 resize
        if image1.shape[0] != image2.shape[0]:
            new_width = int(image2.shape[1] * (image1.shape[0] / image2.shape[0]))
            image2 = cv2.resize(image2, (new_width, image1.shape[0]))
        
        # 두 이미지를 수평으로 연결
        combined_image = cv2.hconcat([image1, image2])
        
        # 연결된 이미지를 윈도우에 표시
        cv2.imshow("Combined Camera Feed", combined_image)
        
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    
    # 프로세스 종료 (상황에 따라 graceful termination 고려)
    cam1_process.terminate()
    cam2_process.terminate()
    ego_process.terminate()

if __name__ == '__main__':
    main()
