import cv2
from roboflow import Roboflow
import time
import os
#import clova as cv
import copy

# roboflow 모델 불러오기
def init_roboflow(api_key, project, version):
    rf = Roboflow(api_key)
    project = rf.workspace().project(project)
    model = project.version(version).model
    return model


# 폴더 생성하기
def makePath(occupied_path, empty_path):
    print("\n===========================================\n")
    if not os.path.exists(occupied_path):
        os.makedirs(occupied_path)
        print(f"success to make occupied directory! | {occupied_path}")
    else:
        print("occupied directory already exists! keep going...")

    if not os.path.exists(empty_path):
        os.makedirs(empty_path)
        print(f"success to make empty directory! | {empty_path}")
    else:
        print("empty directory already exists! keep going...")


# 웹캠 켜기
# 모델 이름, occupied 바운딩박스 저장될 위치, empty 바운딩박스 저장될 위치, confidence, 주차장 이름
def webCamStart(model, occupied_path, empty_path, confidence, slotName) :
    print("\n===========================================\n")

    cap = cv2.VideoCapture(1)   # 노트북 카메라는 0, 외부 카메라는 1

    print('width :%d, height : %d' % (cap.get(3), cap.get(4)))

    #slot_detect_result = {}


    while (True):
        ret, frame = cap.read()  # Read 결과와 frame
        frame_copy = copy.deepcopy(frame)
        predictions = model.predict(frame, confidence=confidence, overlap=30)
        # prediction_json = predictions.json()
        print(f"total prediction : {len(predictions)}")

        slot_detect_result = {}
        
        # 이전에 predict해서 저장한 bounding box 이미지 파일 전부 삭제
        for f in os.listdir(occupied_path):
            os.remove(os.path.join(occupied_path, f))
        for f in os.listdir(empty_path):
            os.remove(os.path.join(empty_path, f))
        

        # 바운딩 박스 정렬하고 어디에 있는 지 정리하는 코드(왼쪽부터 0, 1, 2.... 순으로 저장함)
        boundingBoxOrdered = []
        for i in range(len(predictions)):
            row = [i, 0]
            boundingBoxOrdered.append(row)

        for index, bounding_box in enumerate(predictions):
            x0 = bounding_box['x'] - bounding_box['width'] / 2  # start_column
            boundingBoxOrdered[index][1] = x0
            sortedboundingBoxOrdered = sorted(boundingBoxOrdered, key=lambda x: x[1])

        print(f"==============\n{boundingBoxOrdered}\n==============")


        # predict한 이미지 내 바운딩박스 수 만큼 반복. 각 바운딩 박스를 그리고, 폴더에 따로 저장
        for index, bounding_box in enumerate(predictions):
            x0 = bounding_box['x'] - bounding_box['width'] / 2  # start_column
            x1 = bounding_box['x'] + bounding_box['width'] / 2  # end_column
            y0 = bounding_box['y'] - bounding_box['height'] / 2  # start row
            y1 = bounding_box['y'] + bounding_box['height'] / 2  # end_row
            # bounding box 영역 잘라내기
            frame_copy = frame[int(y0):int(y1), int(x0):int(x1)]
            class_name = bounding_box['class']

            # 정확도 나타냄
            confidence_score = bounding_box['confidence']
            #detection_results = bounding_box

            # bounding box의 인덱스 출력하기!
            print(f"Bounding Box's index : {index} | {class_name} | {confidence_score:.2f}")



            # 왼쪽부터 오른쪽으로 주차장 자리 정렬하기
            target_value = index
            sortedArray = 0
            for i, subarray in enumerate(sortedboundingBoxOrdered):
                if subarray[0] == target_value:
                    sortedArray = i
                    break

            if class_name == "occupied":
                try:
                    image_path = f'{occupied_path}/1_{slotName}{i+1}.jpg'
                    cv2.imwrite(image_path, frame_copy)
                    print(f"occupied 이미지 저장 완료: {image_path}")
                except Exception as e:
                    print(f"occupied 이미지 저장 중 오류 발생: {e}")
            elif class_name == "empty":
                try:
                    image_path = f'{empty_path}/1_{slotName}{i+1}.jpg'
                    cv2.imwrite(image_path, frame_copy)
                    print(f"empty 이미지 저장 완료: {image_path}")
                except Exception as e:
                    print(f"empty 이미지 저장 중 오류 발생: {e}")

            # Bounding box 그리기
            if(class_name == "empty"):
                cv2.rectangle(frame, (int(x0), int(y0)), (int(x1), int(y1)), (0, 0, 255), 2)
                # cv2.putText(frame, f'{class_name}: {confidence_score:.2f}', (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.putText(frame, f'{i}', (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                slot_detect_result[i] = "empty"
            else:
                cv2.rectangle(frame, (int(x0), int(y0)), (int(x1), int(y1)), (0, 255, 0), 2)
                #cv2.putText(frame, f'{class_name}: {confidence_score:.2f}', (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.putText(frame, f'{i}', (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                slot_detect_result[i] = "occupied"
            
            print(slot_detect_result)
            ######

        #cap.release()
        #cv2.destroyAllWindows()
        # 인식한 바운딩 박스 딕셔너리 반환하도록 구현
        #return slot_detect_result

        
        if (ret):
            cv2.imshow('frame_color', frame)  # 컬러 화면 출력
            if cv2.waitKey(1) == ord('q'):
                break
        else:
            break
        
    
        return slot_detect_result
    
    cap.release()   # 웹캠 리소스 해제
    cv2.destroyAllWindows() # 창을 닫는 코드

    #return slot_detect_result



'''
occupied_path = "./images/occupied_boundingBox"
empty_path = "./images/empty_boundingBox"
api_key="Ndgqrpfsb4lW0aJHDg8q"
project = "pl-sr"
version = 1

model = init_roboflow(api_key, project, version)
makePath(occupied_path, empty_path)
webCamStart(model, occupied_path, empty_path, confidence= 40)
'''

