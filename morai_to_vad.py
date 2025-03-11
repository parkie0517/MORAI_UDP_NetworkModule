# import sys
# sys.path.append("/mnt/ssd_e2e/VAD/tools/data_converter")
# from moraidataset import MoraiDataset
from torchvision import transforms
import torch
import numpy as np

class data_processer():
    def __init__(self):
        pass

    def forward(self, data):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # breakpoint()
        transform = transforms.Compose([
            # transforms.Resize((720, 1280)),               # TODO: nuscenes image resolution 
            transforms.ToTensor(),  # 이미지를 Tensor로 변환 (0~255 -> 0~1 범위로 정규화)
        ])

        img_0 = transform(data["images"][0])
        img_1 = transform(data["images"][1])
        img_2 = transform(data["images"][2])
        img_3 = transform(data["images"][3])
        img_4 = transform(data["images"][4])
        sur_image = torch.stack([img_0, img_1, img_2, img_3, img_4]).to(device)
        img_shape = np.array([img_0.size(1), img_0.size(2), img_0.size(0)])

        # breakpoint()
        # TODO 250311: 아래 9개 global -> 차량 좌표계로 바꾸기  
        vel_x = torch.tensor(data['vehicle_state'].vel_x).unsqueeze(0).to(device)
        vel_y = torch.tensor(data['vehicle_state'].vel_y).unsqueeze(0).to(device)
        vel_z = torch.tensor(data['vehicle_state'].vel_z).unsqueeze(0).to(device)
        accel_x = torch.tensor(data['vehicle_state'].accel_x).unsqueeze(0).to(device)
        accel_y = torch.tensor(data['vehicle_state'].accel_y).unsqueeze(0).to(device)
        accel_z = torch.tensor(data['vehicle_state'].accel_z).unsqueeze(0).to(device)
        accel = torch.tensor(data['vehicle_state'].accel).unsqueeze(0).to(device)
        brake = torch.tensor(data['vehicle_state'].brake).unsqueeze(0).to(device)
        steer = torch.tensor(data['vehicle_state'].steer).unsqueeze(0).to(device)

        ang_vel_x = torch.tensor(data['vehicle_state'].ang_vel_x).unsqueeze(0).to(device)
        ang_vel_y = torch.tensor(data['vehicle_state'].ang_vel_y).unsqueeze(0).to(device)
        ang_vel_z = torch.tensor(data['vehicle_state'].ang_vel_z).unsqueeze(0).to(device)
        
        # sur_image = sur_image.unsqueeze(0)      # len_queue = 1이 되도록 함
        ego_lcf_feat = torch.stack([vel_x, vel_y, accel_x, accel_y, accel, brake, steer])

        ego_pos = np.array([0,0,0])
        ego_ori = np.array([0,0,0])
        # can_bus = torch.cat([torch.tensor(ego_pos), torch.tensor(ego_ori), torch.tensor([0]), ego_acc, ego_rotation_rate, ego_velo, torch.tensor([0]), torch.tensor([0])]).squeeze()
        # breakpoint()
        can_bus = torch.cat([torch.tensor(ego_pos).to(device), torch.tensor(ego_ori).to(device), torch.zeros(1).to(device), accel_x, accel_y, accel_z, ang_vel_x, ang_vel_y, ang_vel_z, vel_x, vel_y, vel_z, torch.zeros(1).to(device), torch.zeros(1).to(device)]).unsqueeze(0) 
        # breakpoint()

        lidar2img_list = []
        for cam_idx in range(1, 6):
            # LiDAR-to-Camera 변환 행렬 로드
            calibration_src = "/mnt/ssd_e2e/morai_dataset_final/Calibration"
            tr_ego_to_lidar = np.load(str(calibration_src) + "/LIDAR3D_6__extrinsic.npy")
            tr_ego_to_cam = np.load(str(calibration_src) + f"/CAMERA_{cam_idx}__extrinsic.npy")
            cam_to_lidar = np.linalg.inv(tr_ego_to_cam) @ tr_ego_to_lidar

            # 카메라 내적 행렬 로드
            cam_mat = np.load(str(calibration_src) + f"/CAMERA_{cam_idx}__intrinsic.npy")
            # breakpoint()
            # 최종 lidar2img 변환 행렬
            # breakpoint()
            cam_mat_4x4 = np.eye(4)
            cam_mat_4x4[:3, :3] = cam_mat  # 3x3 카메라 매트릭스를 4x4에 배치
            cam_mat_4x4[3, 3] = 1  # 동차 좌표
            
            lidar2img = np.matmul(cam_mat_4x4, cam_to_lidar)
            lidar2img[3] = np.array([0, 0, 0, 1])  # 3,4 행렬을 4,4 행렬로 맞춰줌. 
            lidar2img_list.append(lidar2img)

        lidar2img_tensor = torch.tensor(lidar2img_list).to(device)
        # breakpoint()
        # img_metas = [{0: {"can_bus" : can_bus.squeeze(), "lidar2img" : lidar2img_tensor, "img_shape" : img_shape}}]
        img_metas = [{0: {"can_bus" : can_bus, "lidar2img" : lidar2img_tensor.unsqueeze(0), "img_shape" : img_shape}}]
        
        return sur_image, ego_lcf_feat, img_metas
        