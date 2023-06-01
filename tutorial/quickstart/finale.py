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
slot_detect = dt.webCamStart(model, occupied_path, empty_path, confidence= 40, slotName="A")
print("finale 파일에서 출력함.", slot_detect)


occupied_plate_dict = {}

for img_name in os.listdir(occupied_path): # occupied 됐으면 번호판 인식
    

    print(img_name)
    f = occupied_path  + "/" + img_name
    result = cv.clova(api_url=api_url, secret_key=secret_key, path=f)
    print(result)
    #infer_text = result['images'][0]['fields'][0]['inferText'] + result['images'][0]['fields'][1]['inferText']

    infer_text = ""

    try:
        if 'inferText' in result['images'][0]['fields'][0]:
            infer_text += result['images'][0]['fields'][0]['inferText']
    except KeyError:
        print("inferText 1 존재하지 않음")

    try:
        if result['images'] and 'inferText' in result['images'][0]['fields'][1]:
            infer_text += result['images'][0]['fields'][1]['inferText']
    except (KeyError, IndexError):
        print("inferText 2 존재하지 않음")

    occupied_plate_dict[img_name[:4]] = infer_text
    #cv.image_load(path=f, result=result, save_path=clova_save_path, save_image_name=save_image_name)

print(occupied_plate_dict)


