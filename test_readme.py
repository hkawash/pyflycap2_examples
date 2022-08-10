from pyflycap2.interface import CameraContext

context_type = 'IIDC'  # もしくは 'GigE'

cc = CameraContext(context_type)
print('Num. of cameras:', cc.get_num_cameras())

from pyflycap2.interface import GUI

gui = GUI()
ret = gui.show_selection()
guid = ret[1][0]  # 選択したカメラの1つめのGUID
print(guid)

from pyflycap2.interface import Camera

cam_serial = 13344912  # GUI で確認できる
print(cam_serial)
c = Camera(serial=cam_serial, context_type=context_type)
# c = Camera(guid=guid, context_type=context_type)
# c = Camera(index=0, context_type=context_type)

c.connect()
c.start_capture()


# 1枚取得
c.read_next_image()
frame = c.get_current_image()
print(frame.keys())

# 各キーを表示
for key in frame.keys():
    if key == 'buffer': continue
    print(key, frame[key])

import numpy as np
import matplotlib.pyplot as plt

arr = np.array(frame['buffer']).reshape((frame['rows'], frame['cols']))
plt.imshow(arr, cmap='gray')
plt.show()

import cv2

print('bayer_fmt:', frame['bayer_fmt'])
img = cv2.cvtColor(arr, cv2.COLOR_BayerBGGR2BGR)  # bggr の場合
cv2.imshow('image', img)
cv2.waitKey(0)
