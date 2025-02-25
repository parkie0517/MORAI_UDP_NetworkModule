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
EGO_PORT = 5091  # 차량 상태 수신 포트 (50Hz)
CONTROL_PORT = 9093  # 차량 제어 전송 포트

# Receiver 설정
ego_receiver = Receiver(control_IP, EGO_PORT, EgoVehicleStatus())
# Sender 설정
ego_ctrl = Sender(sim_IP, CONTROL_PORT)


with open("/home/user/e2e_challenge/MORAI_UDP_NetworkModule/hmg_mission2_global_path.txt", "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) >= 4:
            x, y, z= map(float, parts[1:4])  # X, Y, Z 추출
            waypoints.append((x, y, z))

waypoints = np.array(waypoints)

if __name__ == '__main__':
    # 두 개의 스레드를 생성하여 실행
    # e2e_thread = threading.Thread(target=e2e_model_loop, daemon=True)
    control_thread = threading.Thread(target=control_loop, daemon=True)

    # e2e_thread.start()
    control_thread.start()

    # 메인 스레드가 종료되지 않도록 유지
    # e2e_thread.join()
    control_thread.join()
