# %%
from pyflycap2.interface import CameraContext

context_type = 'IIDC'

cc = CameraContext(context_type)
print('# cameras:', cc.get_num_cameras())


# %%
from pyflycap2.interface import GUI
gui = GUI()
ret = gui.show_selection()
print(ret)
guid = ret[1][0]
print(guid)

# %%
from pyflycap2.interface import Camera

cam_serial = 13344912
print(cam_serial)
# c = Camera(guid=guid, context_type=context_type)
# c = Camera(index=0, context_type=context_type)
c = Camera(serial=cam_serial, context_type=context_type)

c.connect()
c.start_capture()
c.read_next_image()
frame = c.get_current_image()  # last image
c.disconnect()

# %%
# 各キーを表示
print(frame.keys())
for key in frame.keys():
    if key == 'buffer': continue
    print(key, frame[key])

# %%
# numpy array に変換
import numpy as np
import matplotlib.pyplot as plt

arr = np.array(frame['buffer']).reshape((frame['rows'], frame['cols']))
plt.imshow(arr, cmap='gray')
plt.show()

# %%
# opencv で表示
import cv2
print('bayer_fmt:', frame['bayer_fmt'])
img = cv2.cvtColor(arr, cv2.COLOR_BayerBGGR2BGR)
cv2.imshow('image', img)
cv2.waitKey(0)
# %%
# cv2.destroyAllWindows()

# %%
