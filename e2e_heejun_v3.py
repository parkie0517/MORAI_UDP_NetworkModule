#!/usr/bin/env python3
import sys
import time
import threading
from pathlib import Path
import numpy as np
from simple_pid import PID # PID Controller library
from lib.network.UDP import Receiver, Sender 
from lib.define.EgoVehicleStatus import EgoVehicleStatus 
from lib.define.EgoCtrlCmd import EgoCtrlCmd 
import math

Network settings
control_IP = '143.248.59.11' # Linux server IP 
sim_IP = '143.248.50.151' # Windows simulator IP 
EGO_PORT = 5091 # Port to receive ego vehicle status (50Hz) 
CONTROL_PORT = 9093 # Port to send control commands to the simulator

Initialize UDP receiver and sender
ego_receiver = Receiver(control_IP, EGO_PORT, EgoVehicleStatus()) ego_ctrl = Sender(sim_IP, CONTROL_PORT)

Load global path waypoints from file
waypoints = [] with open("/home/user/e2e_challenge/MORAI_UDP_NetworkModule/hmg_mission2_global_path.txt", "r") as file: for line in file: parts = line.strip().split() if len(parts) >= 4: # Extract X, Y, Z (ignoring the first string field) x, y, z = map(float, parts[1:4]) waypoints.append((x, y, z)) waypoints = np.array(waypoints)

Global variable to store the current vehicle status
current_status = None

def receive_status_thread(): global current_status while True: status = ego_receiver.get_data() if status: current_status = status time.sleep(0.02) # about 50Hz

def control_thread(): global current_status, waypoints lookahead_distance = 10.0 # meters (this is a design parameter) v_desired = 10.0 # desired speed in m/s

python
복사
# Initialize PID controllers
steer_pid = PID(1.0, 0.0, 0.1, setpoint=0)
steer_pid.output_limits = (-1.0, 1.0)
speed_pid = PID(0.5, 0.0, 0.05, setpoint=v_desired)
speed_pid.output_limits = (-1.0, 1.0)

dt = 0.02  # control loop time step

while True:
    if current_status is not None:
        # Get current state from the received status
        x = current_status.pos_x
        y = current_status.pos_y
        # Convert yaw from degrees to radians for calculations
        yaw = math.radians(current_status.yaw)
        v = current_status.signed_vel

        # Find the target waypoint based on the lookahead distance
        dists = np.sqrt((waypoints[:, 0] - x) ** 2 + (waypoints[:, 1] - y) ** 2)
        target_index = np.argmin(np.abs(dists - lookahead_distance))
        target_point = waypoints[target_index, :2]

        # Compute desired heading from current position to target waypoint
        desired_heading = math.atan2(target_point[1] - y, target_point[0] - x)
        # Calculate heading error (wrapped to [-pi, pi])
        heading_error = desired_heading - yaw
        heading_error = (heading_error + math.pi) % (2 * math.pi) - math.pi

        # Use PID to compute steering command based on heading error
        steer_command = steer_pid(heading_error)

        # Compute speed control using a PID controller on speed error
        accel_command = speed_pid(v)
        # Map the acceleration command to throttle (accel) and brake values
        if accel_command >= 0:
            accel = min(accel_command, 1.0)
            brake = 0.0
        else:
            accel = 0.0
            brake = min(-accel_command, 1.0)

        # Build control command message
        cmd = EgoCtrlCmd()
        cmd.ctrl_mode = 2   # Set to Auto Mode (as in MoraiCmdController.py)
        cmd.gear = 4        # Set gear (example: D)
        cmd.cmd_type = 1    # Throttle control mode
        cmd.accel = accel
        cmd.brake = brake
        cmd.steer = steer_command

        # Send the command via UDP
        ego_ctrl.send(cmd)
    time.sleep(dt)
if name == 'main': # Start two threads: one for receiving vehicle status and one for control t1 = threading.Thread(target=receive_status_thread, daemon=True) t2 = threading.Thread(target=control_thread, daemon=True) t1.start() t2.start()

python
복사
# Keep the main thread alive
while True:
    time.sleep(1)