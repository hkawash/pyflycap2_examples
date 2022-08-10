# %%
# https://github.com/matham/pyflycap2/ + OpenCV で動画撮影
from pyflycap2.interface import Camera
from pyflycap2.interface import CameraContext
from pyflycap2.interface import GUI
import numpy as np
import cv2

context_type = 'IIDC'  # or 'GigE'

cc = CameraContext(context_type)
print('# cameras:', cc.get_num_cameras())

# FlyCapture2 Camera Selection GUI を表示
# この段階で Configure Selected もしておくとよい
gui = GUI()
ret = gui.show_selection()
guid = ret[1][0]
print(guid)

# GUIで選択したカメラを使う
c = Camera(guid=guid, context_type=context_type)
c.connect()
c.start_capture()

# 1枚取得してみる
c.read_next_image()
frame = c.get_current_image()
# 各キーを表示
for key in frame.keys():
    if key == 'buffer': continue
    print(key, frame[key])

# 動画撮影 & 表示
prev_sec = frame['ts'][0] + frame['ts'][1] / 1e6
n = 0
while True:
    # 1枚取得
    c.read_next_image()
    frame = c.get_current_image()
    # ベイヤーからBGR画像へ
    cvimage = cv2.cvtColor(
        np.array(frame['buffer']).reshape((frame['rows'], frame['cols'])),
        cv2.COLOR_BayerBGGR2BGR)
    # タイムスタンプからフレームレート計算
    sec = frame['ts'][0] + frame['ts'][1] / 1e6
    fps = 1.0 / (sec - prev_sec)
    text = f'{n:08d} - {fps:0.2f} fps'
    cv2.putText(cvimage, text,
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 32), 2)
    # 描画
    cv2.imshow('image', cvimage)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    n += 1
    prev_sec = sec

cv2.destroyAllWindows()
c.stop_capture()
c.disconnect()

