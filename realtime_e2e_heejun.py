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
control_IP = '143.248.59.11'  # linux ip
sim_IP = '143.248.50.151' # windows simulator ip
EGO_PORT = 5091  # receives ego vehicle status using this port (50Hz)
CONTROL_PORT = 9093  # port of the windows simulator that receives the control command sent from the linux server.

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
    # Use 2 threads. first receieves the ego vehicle status. the second controls the car in the simulator
