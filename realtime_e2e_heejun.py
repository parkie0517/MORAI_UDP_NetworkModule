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
import math
import matplotlib.pyplot as plt
import pygame

# 네트워크 설정
control_IP = '143.248.59.11' 
sim_IP = '143.248.50.151'
CAMERA_PORTS = [1111, 1121, 1131, 1141, 1151, 1161]  # 6개 카메라 포트
EGO_PORT = 5091  # 차량 상태 수신 포트 (50Hz)
CONTROL_PORT = 9093  # 차량 제어 전송 포트

# Receiver 설정
# camera_receivers = [Receiver(control_IP, port, Camera()) for port in CAMERA_PORTS]
ego_receiver = Receiver(control_IP, EGO_PORT, EgoVehicleStatus())
# Sender 설정
ego_ctrl = Sender(sim_IP, CONTROL_PORT)

# 공유 변수: 최신 waypoint 저장 (스레드 간 공유)
latest_waypoint = None
waypoint_lock = threading.Lock()  # 데이터 동기화용 Lock

# **🔹 Pygame 초기화**
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ego Vehicle & Waypoints Visualization")
# **🔹 패딩 비율 (전체 범위의 10%)**
PADDING_RATIO = 0.1  
# **🔹 색상 정의**
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)


class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0.0
        self.integral = 0.0

    def control(self, error, dt):
        """
        PID 속도 제어
        error: 목표 속도와 현재 속도의 차이
        dt: 시간 간격 (s)
        """
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        return self.kp * error + self.ki * self.integral + self.kd * derivative

speed_pid = PIDController(kp=0.5, ki=0.02, kd=0.1)
max_speed = 30
min_speed = 10
waypoints = []
with open("/home/user/e2e_challenge/MORAI_UDP_NetworkModule/hmg_mission2_global_path.txt", "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) >= 4:
            x, y, z= map(float, parts[1:4])  # X, Y, Z 추출
            waypoints.append((x, y, z))

waypoints = np.array(waypoints)
# x1,y1,z1=waypoints[5]
# breakpoint()
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

def transform_to_local(vehicle_x, vehicle_y, vehicle_heading, target_x, target_y):

    dx = target_x - vehicle_x
    dy = target_y - vehicle_y
    local_x = dx * math.cos(-vehicle_heading) - dy * math.sin(-vehicle_heading)
    local_y = dx * math.sin(-vehicle_heading) + dy * math.cos(-vehicle_heading)
    return local_x, local_y

def find_closest_waypoint(vehicle_x, vehicle_y, waypoints):
    distances = np.sqrt((waypoints[:, 0] - vehicle_x) ** 2 + (waypoints[:, 1] - vehicle_y) ** 2)
    closest_k_indices = np.argsort(distances)[:5]
    closest_idx = np.max(closest_k_indices)
    x1,y1,_ = waypoints[closest_idx]
    x2,y2,_ = waypoints[closest_idx+1]
    if closest_idx == 0:
        x0,y0 = x1,y1
    else:
        x0,y0,_ = waypoints[closest_idx - 1]
    # 두 선분의 길이 계산
    L1 = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    L2 = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    L3 = np.sqrt((x2 - x0) ** 2 + (y2 - y0) ** 2)

    A = abs(0.5 * ((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)))
    # 곡률 계산
    if L1 * L2 * L3 == 0:
        curvature = 0.0  # 분모가 0이면 직선으로 간주
    else:
        curvature = (2 * A) / (L1 * L2 * L3)
        
    yaw = math.atan2(y2 - y1, x2 - x1)
    return x1,y1, yaw, curvature, closest_idx, closest_k_indices

def compute_steer(vehicle_x, vehicle_y, vehicle_heading,vehicle_speed, target_x, target_y, waypoint_yaw):
    local_x, local_y = transform_to_local(vehicle_x, vehicle_y, vehicle_heading, target_x, target_y)
    heading_error = math.atan2(local_y, local_x)
    cte = local_y

    
    # Stanley Control Law
    k=0.5
    velocity_factor = max(vehicle_speed, 5.0) 
    steer = heading_error + math.atan2(k * cte, velocity_factor)
    # print(steer)
    steer = max(min(steer, 0.5), -0.5)
    return steer

def compute_target_speed(waypoint_curvature, max_speed=15.0, min_speed=3.0):
    """
    곡률 기반 목표 속도 계산
    waypoint_curvature: 현재 웨이포인트의 곡률 값 (곡률이 클수록 커브가 급함)
    max_speed: 최대 속도 (m/s)
    min_speed: 최소 속도 (m/s)
    """
    # 곡률이 클수록 속도를 줄임 (곡률이 0이면 최대 속도 유지)
    target_speed = max_speed / (1 + 5 * abs(waypoint_curvature))

    return max(min_speed, min(target_speed, max_speed))

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

def normalize(value, min_val, max_val, new_min, new_max):
    return int((value - min_val) / (max_val - min_val) * (new_max - new_min) + new_min)
### **🔹 50Hz: Vehicle State 수신 & PID Controller로 Ego Control 업데이트**
def control_loop():
    global latest_waypoint
    
    
    hz = 0.1  # 50Hz (0.02초 주기)
    interval = 1 / hz
    min_x, max_x = waypoints[:, 0].min(), waypoints[:, 0].max()
    min_y, max_y = waypoints[:, 1].min(), waypoints[:, 1].max()
    # **🔹 Padding 추가**
    padding_x = (max_x - min_x) * PADDING_RATIO
    padding_y = (max_y - min_y) * PADDING_RATIO
    min_x -= padding_x
    max_x += padding_x
    min_y -= padding_y
    max_y += padding_y
    
    while True:
        start_time = time.time()

        # Step 1: 차량 상태 데이터 수신
        ego_data = ego_receiver.get_data()
        # print(ego_data)   
        ego_x, ego_y = ego_data.pos_x, ego_data.pos_y
        ego_vel_x = ego_data.vel_x  # 현재 속도 (m/s)
        ego_vel_y = ego_data.vel_y
        ego_speed = np.sqrt((ego_vel_x) ** 2 + (ego_vel_y) ** 2)
        ego_yaw = ego_data.yaw  # 차량의 방향 (라디안)
        print(f"ego_x: {ego_x}  / ego_y: {ego_y}  / ego_speed: {ego_speed}  /  ego_yaw: {ego_yaw}")
        if ego_x ==0:
            continue
        # Step 2: 최신 Waypoint 가져오기 (스레드 동기화)
        # with waypoint_lock:
        #     if latest_waypoint is None:
        #         continue  # 아직 waypoint가 생성되지 않았다면 건너뜀
        #     target_x, target_y = latest_waypoint["waypoint"]
        #     target_speed = latest_waypoint["target_speed"]
        
        waypoint_x, waypoint_y, waypoint_yaw, waypoint_curvature, waypoint_idx,closest_k_indices = find_closest_waypoint(ego_x, ego_y, waypoints)
        target_speed = max_speed / (1 + 10 * abs(waypoint_curvature))
        target_velocity = max(min_speed, min(target_speed, max_speed))
        steer = compute_steer(ego_x, ego_y, ego_yaw,ego_speed, waypoint_x, waypoint_y, waypoint_yaw)
        print(f"steer: {steer}    /  velocity: {target_velocity}   /  waypoint_idx: {waypoint_idx}, {waypoint_x}, {waypoint_y}" )
        
        # **🔹 Pygame 화면 업데이트**
        screen.fill(WHITE)
        # Global Path 표시
        # **🔹 Global Path 그리기**
        for wp in waypoints:
            x = normalize(wp[0], min_x, max_x, 0, WIDTH)
            y = normalize(wp[1], min_y, max_y, 0, HEIGHT)
            pygame.draw.circle(screen, BLACK, (x, y), 2)
        # **🔹 Ego Vehicle 위치 표시**
        ego_x_norm = normalize(ego_x, min_x, max_x, 0, WIDTH)
        ego_y_norm = normalize(ego_y, min_y, max_y, 0, HEIGHT)
        pygame.draw.circle(screen, RED, (ego_x_norm, ego_y_norm), 5)
        # **🔹 가장 가까운 k개의 웨이포인트**
        for idx in closest_k_indices:
            x = normalize(waypoints[idx, 0], min_x, max_x, 0, WIDTH)
            y = normalize(waypoints[idx, 1], min_y, max_y, 0, HEIGHT)
            pygame.draw.circle(screen, GREEN, (x, y), 5)
         # **🔹 선택된 최적 웨이포인트**
        wp_x_norm = normalize(waypoint_x, min_x, max_x, 0, WIDTH)
        wp_y_norm = normalize(waypoint_y, min_y, max_y, 0, HEIGHT)
        pygame.draw.circle(screen, BLUE, (wp_x_norm, wp_y_norm), 5)

        pygame.display.flip()
        # time.sleep(0.1)  # 100ms마다 업데이트
        # breakpoint()
        
        # # Step 3: Steering PID 제어 (Yaw Error 계산)
        # yaw_error = np.arctan2(target_y - ego_y, target_x - ego_x) - ego_yaw
        # steer = steer_pid(yaw_error)

        # # Step 4: 속도 PID 제어
        # speed_error = target_speed - ego_speed
        # accel_brake = speed_pid(speed_error)

        # Step 5: 가속/브레이크 값 결정
        # if accel_brake > 0:
        #     throttle = accel_brake
        #     brake = 0
        # else:
        #     throttle = 0
        #     brake = -accel_brake

        # Step 6: 차량 제어 명령 전송
        # continue
        data = EgoCtrlCmd()
        data.ctrl_mode = 2  # AutoMode
        data.gear = 4
        data.cmd_type = 2
        data.steer = steer  # -1 ~ 1
        data.velocity = target_velocity  # 0 ~ 1
        ego_ctrl.send(data)

        # Step 7: 50Hz 유지 ###################
        time.sleep(0.1)
        # elapsed_time = time.time() - start_time
        # sleep_time = max(0, interval - elapsed_time)
        # time.sleep(sleep_time)


if __name__ == '__main__':
    # 두 개의 스레드를 생성하여 실행
    # e2e_thread = threading.Thread(target=e2e_model_loop, daemon=True)
    control_thread = threading.Thread(target=control_loop, daemon=True)

    # e2e_thread.start()
    control_thread.start()

    # 메인 스레드가 종료되지 않도록 유지
    # e2e_thread.join()
    control_thread.join()
