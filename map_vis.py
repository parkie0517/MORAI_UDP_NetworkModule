import matplotlib.pyplot as plt
import numpy as np

# 데이터 파일 경로
file_path = "hmg_mission2_global_path.txt"

# 데이터 읽기
coordinates = []
with open(file_path, "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) == 4:
            try:
                x, y, z = map(float, parts[1:])
                coordinates.append((x, y, z))
            except ValueError:
                continue  # 숫자로 변환 불가능한 경우 무시

# numpy 배열로 변환
coordinates = np.array(coordinates)

# 시각화
plt.figure(figsize=(10, 8))
plt.scatter(coordinates[0, 0], coordinates[0, 1], s=10, c=1)
plt.plot(coordinates[:, 0], coordinates[:, 1], marker='o', linestyle='-', markersize=2, label='Path')
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("Global Path Visualization")
plt.legend()
plt.grid()

# 이미지 파일로 저장
output_image_path = "global_path.png"
plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Image saved to {output_image_path}")
