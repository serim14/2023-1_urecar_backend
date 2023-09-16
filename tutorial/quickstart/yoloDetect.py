import torch
import cv2
import os
import copy

# YoloV5 모델 불러오기
def init_yolov5(weight_path):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=weight_path)
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

def webCamStart_yolov5(model, occupied_path, empty_path, confidence, slotName):

    print("\n===========================================\n")
    # 후면 카메라로 전환
    cap = cv2.VideoCapture(0)
    print('width :%d, height : %d' % (cap.get(3), cap.get(4)))


    while (True):
        ret, frame = cap.read()  # Read 결과와 frame
        frame_copy = copy.deepcopy(frame)

        # YoloV5 예측 수행
        results = model(frame)
        predictions = results.pred[0]       
        print(f"total prediction : {len(predictions)}")

###########################################################################################
        # ... 나머지 코드는 기존 코드와 유사하게 ...
        # 슬럿 결과 딕셔너리
        slot_detect_result = {}

        for f in os.listdir(occupied_path):
            os.remove(os.path.join(occupied_path, f))
        for f in os.listdir(empty_path):
            os.remove(os.path.join(empty_path, f))

        # 바운딩 박스 정렬, 어디에 있는 지 정리하는 코드(왼쪽부터 0, 1, 2.... 순으로 저장함)
        boundingBoxOrdered = []
        for i in range(len(predictions)):
            row = [i, 0]
            boundingBoxOrdered.append(row)

        for index, bounding_box in enumerate(predictions):
            # 텐서에서 값 추출
            x_center, y_center, width, height, conf, class_id = bounding_box.tolist()  # 텐서값을 리스트로 변환

            # 바운딩 박스 좌표 계산
            x0 = x_center - width / 2
            boundingBoxOrdered[index][1] = x0
            sortedboundingBoxOrdered = sorted(boundingBoxOrdered, key=lambda x: x[1])

        '''
        for index, bounding_box in enumerate(predictions):
            #x0 = bounding_box['x'] - bounding_box['width'] / 2  # start_column
            x0 = float(bounding_box['x']) - float(bounding_box['width']) / 2  # start_column
            boundingBoxOrdered[index][1] = x0
            sortedboundingBoxOrdered = sorted(boundingBoxOrdered, key=lambda x: x[1])
        '''

        print(f"==============\n{boundingBoxOrdered}\n==============")


        # predict한 이미지 내 바운딩박스 수 만큼 반복. 각 바운딩 박스를 그리고, 폴더에 따로 저장
        for index, bounding_box in enumerate(predictions):
            '''
            x0 = bounding_box['x'] - bounding_box['width'] / 2  # start_column
            x1 = bounding_box['x'] + bounding_box['width'] / 2  # end_column
            y0 = bounding_box['y'] - bounding_box['height'] / 2  # start row
            y1 = bounding_box['y'] + bounding_box['height'] / 2  # end_row
            # bounding box 영역 잘라내기
            frame_copy = frame[int(y0):int(y1), int(x0):int(x1)]
            class_name = bounding_box['class']
            '''
            # 텐서에서 값 추출
            x_center, y_center, width, height, conf, class_id = bounding_box

            # 바운딩 박스 좌표 계산
            x0 = x_center - width / 2
            y0 = y_center - height / 2
            x1 = x_center + width / 2
            y1 = y_center + height / 2

            # 클래스 이름 가져오기 (가정: 클래스 이름이 'empty'와 'occupied'로 구성되며 인덱스가 0과 1로 매핑됨)
            class_names = ['empty', 'occupied']
            class_name = class_names[int(class_id)]

            # 정확도
            #confidence_score = bounding_box['confidence']
            confidence_score = conf

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
                print(f"{index}====")
                cv2.imwrite(f'{occupied_path}/{slotName}-{i}.jpg', frame_copy)
            elif class_name == "empty":
                print(f"{index}====")
                cv2.imwrite(f'{empty_path}/{slotName}-{i}.jpg', frame_copy)

            # Bounding box 그리기
            if(class_name == "empty"):
                cv2.rectangle(frame, (int(x0), int(y0)), (int(x1), int(y1)), (0, 0, 255), 2)
                # cv2.putText(frame, f'{class_name}: {confidence_score:.2f}', (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.putText(frame, f'{i}', (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                # 슬롯 결과 딕셔너리에 추가
                slot_detect_result[i] = "empty"
            else:
                cv2.rectangle(frame, (int(x0), int(y0)), (int(x1), int(y1)), (0, 255, 0), 2)
                #cv2.putText(frame, f'{class_name}: {confidence_score:.2f}', (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.putText(frame, f'{i}', (int(x0), int(y0 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                # 슬롯 결과 딕셔너리에 추가
                slot_detect_result[i] = "occupied"

            print(slot_detect_result)

        #return slot_detect_result

        if (ret):
            cv2.imshow('frame_color', frame)  # 컬러 화면 출력
            if cv2.waitKey(1) == ord('q'):
                break
        else:
            break
        
        return slot_detect_result
    
    cap.release()   # 웹캠 리소스를 해제
    cv2.destroyAllWindows()   # 웹캠 미리보기 창과 같이 OpenCV로 열린 모든 창을 닫을 때
###########################################################################################
'''
# 메인 코드
weight_path = 'path_to_your_trained_weights.pt'
model = init_yolov5(weight_path)
makePath(occupied_path, empty_path)
webCamStart_yolov5(model, occupied_path, empty_path, confidence=40, slotName="공영주차장")
'''