import cv2
import torch
import os
import time
import sys

occupied_path = "./images/occupied_boundingBox"
empty_path = "./images/empty_boundingBox"
weight_path = "C:/tutorial/tutorial/yolo/best_5_10.pt"

# 이미지 스티칭에 사용할 이미지 촬영(웹캠 사용)
def image_capture(numOfImage):
    output_folder ="image_for_stitching"  # 이미지 저장 폴더 경로

    # 저장 폴더가 없으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(1)   # 웹캠 열기

    frame_interval = 3  # 몇 초마다 사진 촬영할 건지
    image_counter = 0   # 이미지 카운터 초기화
    #max_images = 6  # 최대 이미지 수

    while image_counter < numOfImage:  # 이미지 카운터가 최대 이미지 수에 도달하면 종료
        # 프레임 읽기
        ret, frame = cap.read() # 프레임 읽기

        if not ret:
            break

        image_name =f"image_{image_counter}.jpg"    # 이미지 파일명 생성

        image_path = os.path.join(output_folder, image_name)    # 이미지 파일 결로 생성
        cv2.imwrite(image_path, frame)  # 이미지 저장
        print(f"Captured:{image_path}")

        image_counter += 1  # 이미지 카운터 증가

        time.sleep(frame_interval)  # 지정된 시간(초) 동안 대기

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' 키를 누르면 종료
            break

    # 웹캠 종료
    cap.release()
    cv2.destroyAllWindows()



### 이미지 스티칭 코드
def image_stitch(img_name_seq, path):
    imgs = []
    for img_name in img_name_seq:
        img = cv2.imread(path+img_name)

        if img is None:
            print("Image load failed!")
            sys.exit()
        imgs.append(img)

    # 객체 생성
    stitcher = cv2.Stitcher_create()
    # 이미지 스티칭
    status, dst = stitcher.stitch(imgs)

    if status != cv2.Stitcher_OK:
        print('Stitch failed!')
        sys.exit()

    # 결과 저장
    cv2.imwrite('stitch_result.jpg', dst)

    # 출력 영상이 화면보다 커질 가능성이 있어 WINDOW_NORMAL 지정
    #cv2.namedWindow('dst', cv2.WINDOW_NORMAL)
    #cv2.imshow('dst', dst)
    #cv2.waitKey()
    #cv2.destroyAllWindows()



def yolo_detect():
    occupied_path = "./images/occupied_boundingBox"
    empty_path = "./images/empty_boundingBox"
    # YOLOv5 모델 로드
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/tutorial/tutorial/yolo/best_5_10.pt')

    # 이미지 예측할 경로 지정
    image_path = 'C:/tutorial/stitch_result.jpg'

    # 예측 수행
    results = model(image_path)

    # 결과 처리
    predictions = results.pred[0]  # 예측 결과 가져오기

    # 이전에 predict해서 저장한 bounding box 이미지 파일 전부 삭제
    for f in os.listdir(occupied_path):
        os.remove(os.path.join(occupied_path, f))
    for f in os.listdir(empty_path):
        os.remove(os.path.join(empty_path, f))

    # 바운딩 박스 정렬 및 저장할 디렉토리 생성
    if not os.path.exists(occupied_path):
        os.makedirs(occupied_path)
    if not os.path.exists(empty_path):
        os.makedirs(empty_path)

    # 바운딩 박스 정렬을 위한 리스트 초기화
    boundingBoxOrdered = []
    for i in range(len(predictions)):
        row = [i, 0]
        boundingBoxOrdered.append(row)

    # 예측된 객체 수 만큼 반복
    for index, pred in enumerate(predictions):
        class_id = int(pred[5])
        confidence = float(pred[4])
        if confidence > 0.4:  # 필요한 경우 신뢰도 임계값 조정
            class_name = model.names[class_id]
            print(f"클래스: {class_name}, 신뢰도: {confidence:.2f}")

            # 바운딩 박스 좌표 추출
            bbox = pred[:4].tolist()
            x0, y0, x1, y1 = map(int, bbox)

            # 바운딩 박스 자리 정렬
            x0_center = (x0 + x1) // 2
            boundingBoxOrdered[index][1] = x0_center

    # 바운딩 박스 좌표로 정렬
    sortedBoundingBoxOrdered = sorted(boundingBoxOrdered, key=lambda x: x[1])

    # 이미지에 정렬된 바운딩 박스 번호 표시 및 저장
    for i, (_, _) in enumerate(sortedBoundingBoxOrdered):
        index = sortedBoundingBoxOrdered[i][0]
        pred = predictions[index]
        class_id = int(pred[5])
        class_name = model.names[class_id]
        x0, y0, x1, y1 = map(int, pred[:4].tolist())
        frame_copy = results.render()[0][y0:y1, x0:x1]
        
        if class_name == "occupied":
            image_path = f'{occupied_path}/A-{i + 1}.jpg'
        elif class_name == "empty":
            image_path = f'{empty_path}/A-{i + 1}.jpg'
            
        cv2.imwrite(image_path, frame_copy)
        cv2.putText(results.render()[0], f'{i + 1}', (x0, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        print(f"{class_name} 이미지 저장 완료: {image_path}")

    print(f"바운딩 박스 정렬 결과: {sortedBoundingBoxOrdered}")

# Call the function to run the detection and sorting
yolo_detect()


# 이미지 출력
# predict 결과 확인용
# 창 이름 설정
#cv2.namedWindow('yolo detect', cv2.WINDOW_NORMAL)    # 창 이름 설정
#cv2.resizeWindow('yolo detect', 800, 600) # 창 크기 조절 (가로폭: 800, 세로높이: 600)
#cv2.imshow('yolo detect', results.render()[0]) # 이미지 표시
#cv2.waitKey(0) # 키 입력 대기
#cv2.destroyAllWindows() # 모든 창 닫기


# 실행 코드
#img_names = ['image_0.jpg', 'image_1.jpg', 'image_2.jpg'] # 찍은 이미지 개수에 따라 조정
#path = 'C:/tutorial/image_for_stitching/'

#image_capture()
#image_stitch(img_name_seq=img_names, path=path)
#yolo_detect()