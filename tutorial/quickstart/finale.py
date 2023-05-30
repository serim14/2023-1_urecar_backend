import detectWebcam as dt
import clova as cv
import os
import threading


occupied_path = "./images/occupied_boundingBox"
empty_path = "./images/empty_boundingBox"
api_key="Ndgqrpfsb4lW0aJHDg8q"
project = "pl-sr"
version = 1
api_url = 'https://em19qzhk73.apigw.ntruss.com/custom/v1/22367/012ff1ea564eacc4379dd5444bfb9d6fb6e08954487dbb9945208defc49b9032/general'
secret_key = 'TnlCdUlFTmRRalltRGpWY3JCRlBsclVWUlJ1VkRJcng='
clova_save_path = "images/"
save_image_name = "OCRresult"


model = dt.init_roboflow(api_key, project, version)
dt.makePath(occupied_path, empty_path)
slot_detect = dt.webCamStart(model, occupied_path, empty_path, confidence= 40, slotName="공영주차장")
print("finale 파일에서 출력함.", slot_detect)

for f in os.listdir(occupied_path): # occupied 됐으면 번호판 인식
    print(f)
    f = occupied_path  + "/" + f
    print(f)
    result = cv.clova(api_url=api_url, secret_key=secret_key, path=f)
    print(result)
    cv.image_load(path=f, result=result, save_path=clova_save_path, save_image_name=save_image_name)


