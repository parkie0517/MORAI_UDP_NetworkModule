import torch
import math

# 현재 차량의 위치 (x, y)와 목표 지점의 위치 (goal_x, goal_y)
ego_pos = torch.tensor([0.0, 0.0])  # 현재 위치 (예시)      # TODO:  current ego position
goal_pos = torch.tensor([10.0, 5.0])  # 목표 지점 (예시)    # TODO:  3초 뒤의 goal global path 위치 -> 이거 어떤 point로 할지...? 를 결정해야함.

# 3초 후 목표 지점까지 이동할 때, 각도를 계산
dx = goal_pos[0] - ego_pos[0]
dy = goal_pos[1] - ego_pos[1]

# 목표 지점까지의 각도 (radians)
target_angle = torch.atan2(dy, dx)

# 현재 차량이 향하고 있는 방향 (가정: 차량이 x축을 따라 진행하고 있다고 가정)
current_angle = 0.0  # 차량이 현재 x축을 향하고 있다고 가정         # TODO: ego data의 current angle을 받아오자. 

# 목표 각도와 현재 각도의 차이 계산
angle_diff = target_angle - current_angle

# 각도 차이를 기준으로 명령을 결정
threshold = 0.05  # 일정 범위 내에서는 직진으로 간주

if angle_diff > threshold:  # 우회전
    ego_fut_cmd = torch.tensor([[[0, 0, 1]]])  # 우회전 명령
elif angle_diff < -threshold:  # 좌회전
    ego_fut_cmd = torch.tensor([[[1, 0, 0]]])  # 좌회전 명령
else:  # 직진
    ego_fut_cmd = torch.tensor([[[0, 1, 0]]])  # 직진 명령

# 최종 명령 출력
print(f"Steering Command: {ego_fut_cmd}")           # TODO: 이 cmd아웃풋이 모델 인풋으로 들어가도록하자. 

