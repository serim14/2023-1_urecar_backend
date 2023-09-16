import torch
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from torchvision.transforms import functional as F

# YOLOv5 모델을 로드합니다. best.pt 파일의 경로를 설정하세요.
model = torch.hub.load('ultralytics/yolov5:master', 'yolov5s', path_or_model='./best.pt')

# 테스트할 이미지 파일의 경로를 설정하세요.
image_path = 'test.jpg'

# 이미지를 로드하고 예측을 수행합니다.
img = Image.open(image_path)
results = model(img)

# 예측 결과를 시각화합니다.
results.show()

# 결과물을 표시하기 위해 이미지를 matplotlib를 사용하여 출력합니다.
results.imgs

# 결과를 저장하려면 다음과 같이 할 수 있습니다.
# results.save(Path('output'))

# 각 객체의 좌표, 클래스, 신뢰도를 얻으려면 다음과 같이 할 수 있습니다.
# print(results.xyxy[0])  # 첫 번째 객체의 정보 출력
