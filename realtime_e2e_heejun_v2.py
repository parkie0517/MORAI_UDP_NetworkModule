import sys
import time
import threading
from pathlib import Path
import cv2
import numpy as np
from simple_pid import PID  # PID Controller library
from lib.network.UDP import Receiver, Sender
from lib.define.Camera import Camera
from lib.define.EgoVehicleStatus import EgoVehicleStatus
from lib.define.EgoCtrlCmd import EgoCtrlCmd
import math
import matplotlib.pyplot as plt
import pygame

# 네트워크 설정
control_IP = '143.248.59.11'  # linux server IP (this machine)
sim_IP = '143.248.50.151'     # windows simulator IP
EGO_PORT = 5091               # port to receive ego vehicle status (50Hz)
CONTROL_PORT = 9093           # port to send control commands to simulator

# Receiver and Sender 설정
ego_receiver = Receiver(control_IP, EGO_PORT, EgoVehicleStatus())
ego_ctrl = Sender(sim_IP, CONTROL_PORT)

# Global path loading
waypoints = []  # list to store (x,y,z) tuples
with open("/home/user/e2e_challenge/MORAI_UDP_NetworkModule/hmg_mission2_global_path.txt", "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) >= 4:
            # Extract X, Y, Z (assuming the first part is an ID)
            x, y, z = map(float, parts[1:4])
            waypoints.append((x, y, z))
waypoints = np.array(waypoints)

# Global variable to hold the latest ego state and a lock for thread safety
ego_state = None
ego_state_lock = threading.Lock()

def receive_thread():
    global ego_state
    while True:
        status = ego_receiver.get_data()  # Blocking receive of EgoVehicleStatus
        with ego_state_lock:
            ego_state = status

def control_thread():
    global ego_state
    # PID controllers
    # PID for steering: the setpoint is zero heading error.
    pid_steer = PID(1.0, 0.0, 0.1, setpoint=0)
    pid_steer.output_limits = (-1, 1)  # steer range: -1 to 1

    # PID for speed: target speed (m/s); adjust gains and target as needed.
    target_speed = 10.0  # desired speed in m/s (example value)
    pid_speed = PID(1.0, 0.0, 0.1, setpoint=target_speed)
    pid_speed.output_limits = (-5, 5)  # acceleration command limits

    dt = 0.1  # control loop period [s]
    lookahead_distance = 5.0  # lookahead distance [m]

    while True:
        # Copy the current ego state in a thread-safe way.
        with ego_state_lock:
            if ego_state is None:
                time.sleep(dt)
                continue
            current_status = ego_state

        # Get current state from the ego vehicle status
        current_x = current_status.pos_x
        current_y = current_status.pos_y
        # Convert yaw (assumed to be in degrees) to radians for computation.
        current_yaw = math.radians(current_status.yaw)
        current_speed = current_status.signed_vel

        # Find a target waypoint at a lookahead distance
        target_point = None
        for wp in waypoints:
            wp_x, wp_y, _ = wp
            dist = math.hypot(wp_x - current_x, wp_y - current_y)
            if dist >= lookahead_distance:
                target_point = (wp_x, wp_y)
                break
        # If no waypoint is found (e.g. near the end), use the last one.
        if target_point is None:
            target_point = (waypoints[-1][0], waypoints[-1][1])

        # Compute desired heading to the target point
        desired_heading = math.atan2(target_point[1] - current_y, target_point[0] - current_x)
        # Compute heading error (normalize to [-pi, pi])
        heading_error = desired_heading - current_yaw
        while heading_error > math.pi:
            heading_error -= 2 * math.pi
        while heading_error < -math.pi:
            heading_error += 2 * math.pi

        # Use the PID controller for steering based on heading error
        steer_command = pid_steer(heading_error)

        # For speed, compute error relative to target speed and use the PID controller
        speed_error = target_speed - current_speed
        accel_command = pid_speed(speed_error)

        # Prepare control command using EgoCtrlCmd
        data = EgoCtrlCmd()
        data.cmd_type = 3  # use acceleration control
        data.acceleration = accel_command  # computed acceleration (m/s^2)
        data.steer = steer_command         # computed steering command (-1 to 1)

        # Send the control command to the simulator
        ego_ctrl.send(data)
        time.sleep(dt)

if __name__ == '__main__':
    # Start the receiver and control threads.
    recv_thread = threading.Thread(target=receive_thread, daemon=True)
    ctrl_thread = threading.Thread(target=control_thread, daemon=True)
    recv_thread.start()
    ctrl_thread.start()

    # Main thread simply waits while the other threads run.
    while True:
        time.sleep(1)
