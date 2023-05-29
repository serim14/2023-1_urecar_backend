import numpy as np
import platform
from PIL import ImageFont, ImageDraw, Image
from matplotlib import pyplot as plt

import uuid
import json
import time
import cv2
import requests

def clova(api_url, secret_key, path):
    api_url = api_url
    secret_key = secret_key

    save_path = path
    files = [('file', open(path, 'rb'))]

    request_json = {
        'images': [
            {
                'format': 'png',
                'name': 'demo'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }
    payload = {'message': json.dumps(request_json).encode('UTF-8')}

    headers = {
        'X-OCR-SECRET': secret_key,
    }
    response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
    result = response.json()

    return result

def image_load(path, result, save_path, save_image_name):

    # 한글 폰트 위치
    font_path = 'C/Windows/Fonts/HMKMG.TTF'
    # 폰트 객체 생성
    font = ImageFont.truetype(font_path, 40)

    # 이미지 로드
    image = cv2.imread(path)

    for field in result['images'][0]['fields']:
        vertices = field['boundingPoly']['vertices']
        x0, y0 = int(vertices[0]['x']), int(vertices[0]['y'])
        x1, y1 = int(vertices[2]['x']), int(vertices[2]['y'])
        text = field['inferText']
        confidence = field['inferConfidence']

        # 바운딩 박스 그리기
        cv2.rectangle(image, (x0, y0), (x1, y1), (0, 255, 0), 2)

        # 텍스트와 신뢰도 표시
        # cv2.putText(image, f'{text}', (x0, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        # 텍스트와 신뢰도 표시
        img_pil = Image.fromarray(image)
        draw = ImageDraw.Draw(img_pil)
        draw.text((x0, y0 - 30), text, font=font, fill=(0, 255, 0))
        image = np.array(img_pil)

    # 이미지 출력
    cv2.imshow('OCR Result', image)
    cv2.imwrite(f'{save_path}/{save_image_name}.png', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

'''
api_url = 'https://em19qzhk73.apigw.ntruss.com/custom/v1/22367/012ff1ea564eacc4379dd5444bfb9d6fb6e08954487dbb9945208defc49b9032/general'
secret_key = 'TnlCdUlFTmRRalltRGpWY3JCRlBsclVWUlJ1VkRJcng='
path = 'images/img2.png'
clova_save_path = "images"
save_image_name = "OCRresult"

result = clova(api_url=api_url, secret_key=secret_key, path=path)
image_load(path=path, result=result, save_path=clova_save_path, save_image_name=save_image_name)

'''

'''
# 한글 폰트 위치
font_path = 'C/Windows/Fonts/HMKMG.TTF'
# 폰트 객체 생성
font = ImageFont.truetype(font_path, 40)

api_url = 'https://em19qzhk73.apigw.ntruss.com/custom/v1/22367/012ff1ea564eacc4379dd5444bfb9d6fb6e08954487dbb9945208defc49b9032/general'
secret_key = 'TnlCdUlFTmRRalltRGpWY3JCRlBsclVWUlJ1VkRJcng='

path = 'images/img2.png'
files = [('file', open(path,'rb'))]

request_json = {
    'images': [
        {
            'format': 'png',
            'name': 'demo'
        }
    ],
    'requestId': str(uuid.uuid4()),
    'version': 'V2',
    'timestamp': int(round(time.time() * 1000))
}
payload = {'message': json.dumps(request_json).encode('UTF-8')}

headers = {
    'X-OCR-SECRET': secret_key,
}

response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
result = response.json()




# 이미지 로드
image = cv2.imread(path)

for field in result['images'][0]['fields']:
    vertices = field['boundingPoly']['vertices']
    x0, y0 = int(vertices[0]['x']), int(vertices[0]['y'])
    x1, y1 = int(vertices[2]['x']), int(vertices[2]['y'])
    text = field['inferText']
    confidence = field['inferConfidence']

    # 바운딩 박스 그리기
    cv2.rectangle(image, (x0, y0), (x1, y1), (0, 255, 0), 2)

    # 텍스트와 신뢰도 표시
    #cv2.putText(image, f'{text}', (x0, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    # 텍스트와 신뢰도 표시
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)
    draw.text((x0, y0-30), text, font=font, fill=(0, 255, 0))
    image = np.array(img_pil)

# 이미지 출력
cv2.imshow('OCR Result', image)
cv2.imwrite('OCR_result.png', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''