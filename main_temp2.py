import sys
import time
import threading
from pathlib import Path
import numpy as np
from simple_pid import PID  # PID Controller library
from lib.network.UDP import Receiver, Sender
from lib.define.EgoVehicleStatus import EgoVehicleStatus
from lib.define.EgoCtrlCmd import EgoCtrlCmd
import math
import yaml
import argparse
import matplotlib.pyplot as plt


# Global variable to store the current vehicle status
current_status = None

def parse_args():
    parser = argparse.ArgumentParser(description="Test script for loading YAML config")
    parser.add_argument("--config", type=str, required=True, help="Path to the YAML config file (e.g., ./config/test.yaml)")
    return parser.parse_args()


def receive_status_thread():
    global current_status
    while True:
        status = ego_receiver.get_data()
        if status:
            current_status = status
            x = current_status.pos_x
            y = current_status.pos_y
            print(f"X: {x:.2f} Y: {y:.2f}", end='\r') # 캐리지 리턴
        time.sleep(0.02)  # roughly 50Hz

def control_thread():
    global current_status, waypoints, previous_steer
    previous_steer = 0.0
    alpha = 0.8  # smoothing factor (0 < alpha < 1); higher means more smoothing
    lookahead_distance = 1.0  # meters (design parameter; try increasing if wobbling persists)
    v_desired = 1.0           # desired speed in m/s


    # Initialize PID controllers
    steer_pid = PID(1.0, 0.0, 0.1, setpoint=0)
    steer_pid.output_limits = (-1.0, 1.0)
    speed_pid = PID(0.5, 0.0, 0.05, setpoint=v_desired)
    speed_pid.output_limits = (-1.0, 1.0)
    
    dt = 0.02  # control loop time step

    while True:
        if current_status is not None:
            # Extract current state
            x = current_status.pos_x
            y = current_status.pos_y
            # Convert yaw (assumed in degrees) to radians
            yaw = math.radians(current_status.yaw)
            v = current_status.signed_vel

            # Compute distances to all waypoints
            dists = np.sqrt((waypoints[:, 0] - x)**2 + (waypoints[:, 1] - y)**2)
            # Select the waypoint closest to the desired lookahead distance
            target_index = np.argmin(np.abs(dists - lookahead_distance))
            target_point = waypoints[target_index, :2]

            # Calculate desired heading and heading error (wrapped to [-pi, pi])
            desired_heading = math.atan2(target_point[1] - y, target_point[0] - x)
            heading_error = desired_heading - yaw
            heading_error = (heading_error + math.pi) % (2 * math.pi) - math.pi

            # Compute steering command using PID
            #steer_command = steer_pid(heading_error)
            raw_steer_command = steer_pid(heading_error)
            steer_command = alpha * previous_steer + (1 - alpha) * raw_steer_command
            previous_steer = steer_command
            # Speed control: compute acceleration command from speed error
            accel_command = speed_pid(v)
            if accel_command >= 0:
                accel = min(accel_command, 1.0)
                brake = 0.0
            else:
                accel = 0.0
                brake = min(-accel_command, 1.0)

            # Build and send control command
            cmd = EgoCtrlCmd()
            cmd.ctrl_mode = 2   # Auto mode
            cmd.gear = 4        # Gear (e.g., D)
            cmd.cmd_type = 1    # Throttle control mode
            cmd.accel = accel
            cmd.brake = brake
            cmd.steer = steer_command

            ego_ctrl.send(cmd)
        time.sleep(dt)

def visualization_thread():
    # Set up the matplotlib interactive plot
    plt.ion()
    fig, ax = plt.subplots()
    # Plot the global path as a blue line
    ax.plot(waypoints[:, 0], waypoints[:, 1], 'b-', label='Global Path')
    # Create a red dot for the vehicle position
    vehicle_dot, = ax.plot([], [], 'ro', markersize=8, label='Vehicle Position')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    
    # Set plot limits with a margin
    margin = 10
    ax.set_xlim(np.min(waypoints[:, 0]) - margin, np.max(waypoints[:, 0]) + margin)
    ax.set_ylim(np.min(waypoints[:, 1]) - margin, np.max(waypoints[:, 1]) + margin)
    
    while True:
        if current_status is not None:
            x = current_status.pos_x
            y = current_status.pos_y
            vehicle_dot.set_data([x], [y])
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(0.1)

if __name__ == '__main__':
    args = parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    control_IP = config["control_IP"]
    sim_IP = config["sim_IP"]
    EGO_PORT = config["EGO_PORT"]
    CONTROL_PORT = config["CONTROL_PORT"]

    print("Current Network Setting")
    print("control_IP:", control_IP)
    print("sim_IP:", sim_IP)
    print("EGO_PORT:", EGO_PORT)
    print("CONTROL_PORT:", CONTROL_PORT)

    # Initialize UDP receiver and sender after loading config
    ego_receiver = Receiver(control_IP, EGO_PORT, EgoVehicleStatus())
    ego_ctrl = Sender(sim_IP, CONTROL_PORT)

    # Load global path waypoints from file
    waypoints = []
    with open("./hmg_mission2_global_path.txt", "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 4:
                # Extract X, Y, Z (ignoring the first field which is an identifier)
                x, y, z = map(float, parts[1:4])
                waypoints.append((x, y, z))
    waypoints = np.array(waypoints)

    
    
    # Start threads for receiving status, control, and visualization
    t1 = threading.Thread(target=receive_status_thread, daemon=True)
    # t2 = threading.Thread(target=control_thread, daemon=True)
    t3 = threading.Thread(target=visualization_thread, daemon=True)

    t1.start()
    # t2.start()
    t3.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
