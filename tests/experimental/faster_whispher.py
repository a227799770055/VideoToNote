from pywhispercpp.model import Model

# 先使用基本設定，不使用 Core ML
model = Model("small")

segments = model.transcribe("/Users/kuangtinghsiao/workspace/videoToNote/data/mp3/1010.mp4", language="zh")
for s in segments:
    print(s.text)