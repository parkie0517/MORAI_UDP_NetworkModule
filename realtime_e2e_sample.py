import sys
import time
import threading
from pathlib import Path
import cv2
import numpy as np
from simple_pid import PID  # PID Controller 라이브러리
from lib.network.UDP import Receiver, Sender
from lib.define.Camera import Camera
from lib.define.EgoVehicleStatus import EgoVehicleStatus
from lib.define.EgoCtrlCmd import EgoCtrlCmd

# 네트워크 설정
IP = '143.248.50.159'
CAMERA_PORTS = [1111, 1121, 1131, 1141, 1151, 1161]  # 6개 카메라 포트
EGO_PORT = 1201  # 차량 상태 수신 포트 (50Hz)
CONTROL_PORT = 1300  # 차량 제어 전송 포트

# Receiver 설정
# camera_receivers = [Receiver(IP, port, Camera()) for port in CAMERA_PORTS]
ego_receiver = Receiver(IP, EGO_PORT, EgoVehicleStatus())

# Sender 설정
ego_ctrl = Sender(IP, CONTROL_PORT)

# 공유 변수: 최신 waypoint 저장 (스레드 간 공유)
latest_waypoint = None
waypoint_lock = threading.Lock()  # 데이터 동기화용 Lock


# **🔹 E2E Autonomous Driving Model (더미 모델)**
class AutonomousDrivingModel:
    def predict(self, data):
        """
        E2E 모델이 다음 waypoint를 예측 (2Hz)
        """
        return {
            "waypoint": (np.random.uniform(-1, 1), np.random.uniform(-1, 1)),  # 목표 위치 (x, y)
            "target_speed": np.random.uniform(5, 15)  # 목표 속도 (5~15 m/s)
        }

model = AutonomousDrivingModel()

def find_closest_waypoint(vehicle_x, vehicle_y, waypoints):
    distances = np.sqrt((waypoints[:, 0] - vehicle_x) ** 2 + (waypoints[:, 1] - vehicle_y) ** 2)
    closest_idx = np.argmin(distances)
    return waypoints[closest_idx], closest_idx

def compute_control(vehicle_x, vehicle_y, vehicle_heading, target_x, target_y, target_heading):
    dx = target_x - vehicle_x
    dy = target_y - vehicle_y
    target_yaw = math.atan2(dy, dx)
    heading_error = target_yaw - vehicle_heading
    steer = max(min(heading_error, 0.5), -0.5)  # 스티어링 값 범위 제한
    throttle = 0.3  # 기본 속도 유지
    brake = 0.0

    return throttle, steer, brake

### **🔹 PID Controller 설정**
# 스티어링 PID (yaw error 기반)
steer_pid = PID(Kp=0.5, Ki=0.02, Kd=0.1, setpoint=0)  # 목표 yaw error = 0
steer_pid.output_limits = (-1, 1)  # 스티어링 값 범위 제한

# 속도 PID (목표 속도와 현재 속도 차이 기반)
speed_pid = PID(Kp=0.2, Ki=0.01, Kd=0.05, setpoint=0)  # 목표 속도 오차 = 0
speed_pid.output_limits = (-1, 1)  # 가속(+) 또는 브레이크(-)


### **🔹 2Hz: E2E 모델 실행 (새로운 Waypoint 생성)**
def e2e_model_loop():
    global latest_waypoint

    hz = 2  # 2Hz (0.5초 주기)
    interval = 1 / hz

    while True:
        start_time = time.time()

        # Step 1: 카메라 데이터 수신
        images = []
        for cam in camera_receivers:
            data = cam.get_data()
            buf = np.frombuffer(data.image.data, dtype=np.uint8)
            image = None if buf.size == 0 else cv2.imdecode(buf, cv2.IMREAD_COLOR)
            images.append(image if image is not None else np.zeros((480, 640, 3), dtype=np.uint8))

        # Step 2: 차량 상태 데이터 수신
        ego_data = ego_receiver.get_data()

        # Step 3: 모델 입력 데이터 구성
        model_input = {
            "images": images,  # 6장의 이미지 리스트
            "vehicle_state": ego_data  # 차량 상태 데이터
        }

        # Step 4: 모델 예측 (새로운 Waypoint 생성)
        new_waypoint = model.predict(model_input)

        # Step 5: 최신 Waypoint 업데이트 (스레드 동기화)
        with waypoint_lock:
            latest_waypoint = new_waypoint

        # Step 6: 2Hz 유지
        elapsed_time = time.time() - start_time
        sleep_time = max(0, interval - elapsed_time)
        time.sleep(sleep_time)


### **🔹 50Hz: Vehicle State 수신 & PID Controller로 Ego Control 업데이트**
def control_loop():
    global latest_waypoint

    hz = 50  # 50Hz (0.02초 주기)
    interval = 1 / hz

    while True:
        start_time = time.time()

        # Step 1: 차량 상태 데이터 수신
        ego_data = ego_receiver.get_data()
        ego_x, ego_y = ego_data.position.x, ego_data.position.y
        ego_speed = ego_data.velocity  # 현재 속도 (m/s)
        ego_yaw = ego_data.heading  # 차량의 방향 (라디안)

        # Step 2: 최신 Waypoint 가져오기 (스레드 동기화)
        with waypoint_lock:
            if latest_waypoint is None:
                continue  # 아직 waypoint가 생성되지 않았다면 건너뜀
            target_x, target_y = latest_waypoint["waypoint"]
            target_speed = latest_waypoint["target_speed"]

        # Step 3: Steering PID 제어 (Yaw Error 계산)
        yaw_error = np.arctan2(target_y - ego_y, target_x - ego_x) - ego_yaw
        steer = steer_pid(yaw_error)

        # Step 4: 속도 PID 제어
        speed_error = target_speed - ego_speed
        accel_brake = speed_pid(speed_error)

        # Step 5: 가속/브레이크 값 결정
        if accel_brake > 0:
            throttle = accel_brake
            brake = 0
        else:
            throttle = 0
            brake = -accel_brake

        # Step 6: 차량 제어 명령 전송
        data = EgoCtrlCmd()
        data.ctrl_mode = 2  # AutoMode
        data.gear = 4
        data.cmd_type = 1
        data.steer = steer  # -1 ~ 1
        data.accel = throttle  # 0 ~ 1
        data.brake = brake  # 0 ~ 1
        ego_ctrl.send(data)

        # Step 7: 50Hz 유지 ###################
        elapsed_time = time.time() - start_time
        sleep_time = max(0, interval - elapsed_time)
        time.sleep(sleep_time)


if __name__ == '__main__':
    # 두 개의 스레드를 생성하여 실행
    # e2e_thread = threading.Thread(target=e2e_model_loop, daemon=True)
    control_thread = threading.Thread(target=control_loop, daemon=True)

    # e2e_thread.start()
    control_thread.start()

    # 메인 스레드가 종료되지 않도록 유지
    # e2e_thread.join()
    control_thread.join()
