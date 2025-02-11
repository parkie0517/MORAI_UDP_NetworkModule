import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import cv2
import numpy as np
from lib.network.UDP import Receiver
from lib.define.Camera import Camera


IP = '143.248.50.159' # 이미지를 받는 컴퓨터의 ip주소
PORT_1 = 1111 # 카메라의 destination port를 입력
PORT_2 = 1121

#Protocol 정보
#https://help-morai-sim.scrollhelp.site/ko/morai-sim-drive/24.R2/-35#id-(24.R2-ko)센서통신프로토콜-UDP
def main():
    cam_data_1 = Receiver(IP, PORT_1, Camera())
    cam_data_2 = Receiver(IP, PORT_2, Camera())
    
    while True:
        # Retrieve image data from Camera 1
        data_1 = cam_data_1.get_data()   
        try:
            image_1 = cv2.imdecode(np.frombuffer(data_1.image.data, dtype=np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            print("Camera 1 error:", e)
            image_1 = None

        # Retrieve image data from Camera 2
        data_2 = cam_data_2.get_data()
        try:
            image_2 = cv2.imdecode(np.frombuffer(data_2.image.data, dtype=np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            print("Camera 2 error:", e)
            image_2 = None

        # If both images are missing, continue to next iteration
        if image_1 is None and image_2 is None:
            continue

        # If one of the images is None, create a blank image of similar size
        if image_1 is None and image_2 is not None:
            image_1 = np.zeros_like(image_2)
        if image_2 is None and image_1 is not None:
            image_2 = np.zeros_like(image_1)
            
        # Ensure the images have the same height before concatenation.
        if image_1.shape[0] != image_2.shape[0]:
            # Resize image_2 to match image_1's height (adjust width proportionally)
            new_width = int(image_2.shape[1] * (image_1.shape[0] / image_2.shape[0]))
            image_2 = cv2.resize(image_2, (new_width, image_1.shape[0]))

        # Combine the images horizontally
        combined_image = cv2.hconcat([image_1, image_2])
        
        # Display the combined feed
        cv2.imshow("Combined Camera Feed", combined_image)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()