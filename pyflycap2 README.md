# Ubuntu 22.04 + FlyCapture2 SDK + Python (pyflycap2)

FLIR FlyCapture2 の Python wrapper です．
FLIR の（もともとは Point Grey Research の）新しいカメラは Spinnaker SDK で動きますが，古いものは FlyCapture2 SDK を使う必要があります．

しかし，FlyCapture2 や公式 Python wrapper は Ubuntu 18 までしか対応していないようです．

Docker ではなく Ubuntu 22 でそのまま動かせる SDK はないかと思っていたら，matham さんによる [pyflycap2](https://github.com/matham/pyflycap2) というのがありました．

OpenCV と組み合わせて動画表示まで行ってみます．

ちなみにここでは Ubuntu での使い方を説明しますが，Windows でも使えるようです．

## インストール

### FlyCapture2 SDK のインストール

- [FLIR公式サイト](https://www.flir.jp/products/flycapture-sdk/) の「今すぐダウンロード > Linux」から `flycapture2-2.13.3.31-amd64-pkg_Ubuntu18.04.tgz` をダウンロードしておきます．

手順で必要なパッケージを入れ，その後シェルスクリプトで SDK をインストールします．

```shell
$ sudo apt update
$ sudo apt install libraw1394-11 libgtkmm-2.4-dev libglademm-2.4-dev libgtkglextmm-x11-1.2-dev libusb-1.0-0
tar zxvf flycapture2-2.13.3.31-amd64-pkg_Ubuntu18.04.tgz
$ sudo sh install_flycapture.sh
```

最後に以下のメッセージが出てきます．

```
Would you like to add a udev entry to allow access to IEEE-1394 and USB hardware?
If this is not ran then your cameras may be only accessible by running flycap as sudo.
```

これは使い方によりますが，今回は y とします．必要なユーザー名も入れ，あともすべて y とします．

### pyflycap2 のインストール

インストール方法は[こちらのページ](https://matham.github.io/pyflycap2/installation.html)で詳しく説明されていますが，とてもかんたんです．

まず [GitHub にある pyflycap2 リポジトリの Release](https://github.com/matham/pyflycap2/releases) で，自分の使う Python のバージョンにあったものを選択してダウンロードします．Python 3.7 から 3.10 まであるようです．

あとは pip でインストールするだけです．たとえば Python 3.7 であれば以下のようになります．

```shell
$ pip install pyflycap2-0.3.1-cp37-cp37m-linux_x86_64.whl
```

[ドキュメント](https://matham.github.io/pyflycap2/installation.html)によれば，GUI を使う場合は `/usr/bin/FlyCapture2GUI_GTK.glade` を実行時のカレントディレクトリにコピーしておく必要があるようです．

また，コンパイルする方法についても説明されています．


## 基本的な使い方

### カメラ台数の確認

まずは接続されているカメラの台数を表示してみます．

```python
from pyflycap2.interface import CameraContext

context_type = 'IIDC'  # もしくは 'GigE'

cc = CameraContext(context_type)
print('Num. of cameras:', cc.get_num_cameras())
```

### GUI でカメラ選択

GUI でカメラを選んでみます．

以下のコードで，FlyCapture2 Camera Selection GUI を表示して，カメラを選択や，各種の設定ができます．

選んだカメラの GUID も取得できます．
以下の `ret` はタプルになっていて，`ret[0]`が `True` なら「OK」が押されたことを意味します（キャンセルすると `False`）．

`ret[1]` がGUIDです．複数のカメラを選ぶと複数のGUIDが返ってきます．一つのカメラのGUIDは4つの値からなるリストなので，`ret[1]` はリストのリストです．以下ではその最初のカメラのGUIDを表示しています．


```python
from pyflycap2.interface import GUI

gui = GUI()
ret = gui.show_selection()
guid = ret[1][0]  # 選択したカメラの1つめのGUID
print(guid)
```

### カメラの指定

カメラの指定は，GUID の他，上の GUI でも表示されるシリアル番号や，何番目のカメラかを表す整数値でも可能です．

```python
from pyflycap2.interface import Camera

cam_serial = 12345678  # GUI で確認できる
print(cam_serial)
c = Camera(serial=cam_serial, context_type=context_type)
# c = Camera(guid=guid, context_type=context_type)
# c = Camera(index=0, context_type=context_type)

c.connect()
c.start_capture()
```

### フレーム情報の取得

1枚撮影して，画像のサイズやタイムスタンプなどの情報を取得してみます．`get_current_image()` で取得される情報は辞書になっています．


```python
# 1枚取得
c.read_next_image()
frame = c.get_current_image()
print(frame.keys())

# 各キーを表示
for key in frame.keys():
    if key == 'buffer': continue
    print(key, frame[key])
```

各種の情報が表示されます．

```
dict_keys(['rows', 'cols', 'stride', 'data_size', 'received_size', 'pix_fmt', 'bayer_fmt', 'ts', 'buffer'])
rows 1024
cols 1280
stride 1280
data_size 1310720
received_size 1310720
pix_fmt raw8
bayer_fmt bggr
ts TimeStamp(seconds=1660031519, micro_seconds=473807, cycle_seconds=0, cycle_count=0, cycle_offset=0)
```

### 1枚分のデータを取得

そのまま NumPy の ndarray にしてみます．カラーカメラであればベイヤーパターンそのままです．

```python
import numpy as np
import matplotlib.pyplot as plt

arr = np.array(frame['buffer']).reshape((frame['rows'], frame['cols']))
plt.imshow(arr, cmap='gray')
plt.show()
```

### OpenCV で扱うには

ベイヤーの配列パターンは `bayer_fmt` で取得できるため，OpenCVを使ってカラー画像にして表示してみます．以下はベイヤーが BGGR の場合です．

```python
import cv2

print('bayer_fmt:', frame['bayer_fmt'])
img = cv2.cvtColor(arr, cv2.COLOR_BayerBGGR2BGR)  # bggr の場合
cv2.imshow('image', img)
cv2.waitKey(0)
```


## OpenCV で動画撮影 & 表示

最後に動画で表示してみます．

- ベイヤーパターンのカラーカメラを前提にしています．
- GUIで選択したカメラを使って撮影します．

```python
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
```

もっといい書き方や，おかしなところがあればぜひコメントしてください．フレームの取得もこれでよいのかどうか・・


## その他

### 各種設定など

API については https://matham.github.io/pyflycap2/interface.html に一覧があるようです．

### Failed to load module "canberra-gtk-module"

こんなメッセージが出る場合は，[ここ](https://askubuntu.com/questions/342202/failed-to-load-module-canberra-gtk-module-but-already-installed)を参考にしながら，以下のモジュールをインストールするといいかもしれません．

```shell
$ sudo apt install libcanberra-gtk-module
```



