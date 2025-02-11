import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
from lib.network.UDP import Receiver
from lib.define.Camera import Camera


IP = '143.248.50.159' # 이미지를 받는 컴퓨터의 ip주소
PORT_1 = 1111 # 카메라의 destination port를 입력
PORT_2 = 1121 # 두 번째 카메라의 destination port 입력
# 만약 surround view를 원하면 카메라를 총 6개 세팅하면 됨
# PORT_3 = 1131
# PORT_4 = 1141
# PORT_5 = 1151
# PORT_6 = 1161


#Protocol 정보
#https://help-morai-sim.scrollhelp.site/ko/morai-sim-drive/24.R2/-35#id-(24.R2-ko)센서통신프로토콜-UDP
def main():
    cam_data_1 = Receiver(IP, PORT_1, Camera())
    cam_data_2 = Receiver(IP, PORT_2, Camera())
    # surroundview용
    # cam_data_3 = Receiver(IP, PORT_3, Camera())
    # cam_data_4 = Receiver(IP, PORT_4, Camera())
    # cam_data_5 = Receiver(IP, PORT_5, Camera())
    # cam_data_6 = Receiver(IP, PORT_6, Camera())
    
    while True:
        # Process Camera 1 feed
        data_1 = cam_data_1.get_data()
        buf1 = np.frombuffer(data_1.image.data, dtype=np.uint8)
        if buf1.size == 0:
            # Buffer is empty; skip decoding and create a blank image if needed
            # print("Received empty data for Camera 1")
            image_1 = None
        else:
            image_1 = cv2.imdecode(buf1, cv2.IMREAD_COLOR)
        
        # Process Camera 2 feed
        data_2 = cam_data_2.get_data()
        buf2 = np.frombuffer(data_2.image.data, dtype=np.uint8)
        if buf2.size == 0:
            # Buffer is empty; skip decoding and create a blank image if needed
            # print("Received empty data for Camera 2")
            image_2 = None
        else:
            image_2 = cv2.imdecode(buf2, cv2.IMREAD_COLOR)

        """
        카메라 3~6에 대한 것도 추가하면 됨
        """
        
        # If both images are missing, skip this iteration
        if image_1 is None and image_2 is None:
            continue

        # If one of the images is None, create a blank image of similar size
        if image_1 is None and image_2 is not None:
            image_1 = np.zeros_like(image_2)
        if image_2 is None and image_1 is not None:
            image_2 = np.zeros_like(image_1)
            
        # Ensure both images have the same height for horizontal concatenation
        if image_1.shape[0] != image_2.shape[0]:
            # Resize image_2 to match image_1's height (adjusting width proportionally)
            new_width = int(image_2.shape[1] * (image_1.shape[0] / image_2.shape[0]))
            image_2 = cv2.resize(image_2, (new_width, image_1.shape[0]))

        # Concatenate images side by side
        combined_image = cv2.hconcat([image_1, image_2])
        
        # Display the combined feed
        cv2.imshow("Combined Camera Feed", combined_image)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()