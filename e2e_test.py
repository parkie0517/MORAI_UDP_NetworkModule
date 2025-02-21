import sys
from pathlib import Path
import cv2
import numpy as np
from lib.network.UDP import Receiver, Sender
from lib.define.Camera import Camera
from lib.define.EgoCtrlCmd import EgoCtrlCmd
import time

IP = '143.248.50.151' # 시뮬레이터 돌리는 PC/윈도우 PC IP
PORT = 9100

PORT_1 = 1111
ACTION_PORT = 1200  # 모델의 예측을 시뮬레이터로 송신할 포트

# Receiver 및 Sender 설정
cam_data_1 = Receiver(IP, PORT_1, Camera())
cam_data_2 = Receiver(IP, PORT_2, Camera())
action_sender = Sender(IP, ACTION_PORT)

# Autonomous Driving Model (예제)
class AutonomousDrivingModel:
    def predict(self, image):
        """
        Dummy 모델 - 실제 모델로 교체 필요
        """
        steering = 0.1  # 예제: 약간 오른쪽 조향
        throttle = 0.5  # 예제: 중간 가속
        return steering, throttle

model = AutonomousDrivingModel()

def main():
    while True:
        try:
            # Camera 1 데이터 수신
            data_1 = cam_data_1.get_data()
            buf1 = np.frombuffer(data_1.image.data, dtype=np.uint8)
            image_1 = None if buf1.size == 0 else cv2.imdecode(buf1, cv2.IMREAD_COLOR)

            # Camera 2 데이터 수신
            data_2 = cam_data_2.get_data()
            buf2 = np.frombuffer(data_2.image.data, dtype=np.uint8)
            image_2 = None if buf2.size == 0 else cv2.imdecode(buf2, cv2.IMREAD_COLOR)

            # 이미지가 없으면 스킵
            if image_1 is None and image_2 is None:
                continue
            if image_1 is None: image_1 = np.zeros_like(image_2)
            if image_2 is None: image_2 = np.zeros_like(image_1)

            # 이미지 크기 맞추기
            if image_1.shape[0] != image_2.shape[0]:
                new_width = int(image_2.shape[1] * (image_1.shape[0] / image_2.shape[0]))
                image_2 = cv2.resize(image_2, (new_width, image_1.shape[0]))

            # 이미지 결합 (수평)
            combined_image = cv2.hconcat([image_1, image_2])

            # E2E Autonomous Driving Model에 전달
            steering, throttle = model.predict(combined_image)

            # 액션을 시뮬레이션에 전송
            action_data = f"{steering},{throttle}"
            action_sender.send(action_data.encode('utf-8'))

            # UI에 표시
            cv2.imshow("Combined Camera Feed", combined_image)

            # 종료 조건
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"Error: {e}")
            continue

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
