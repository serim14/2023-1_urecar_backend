from django.shortcuts import render
from .models import ParkingLot, ParkingSlot, User, Reservation

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


###### 원래 구분했지만 이젠 안쓰는 api
# get_marker에 통합함
# 1. 각각 주차장의 slot 정보 가져오기
# (안드) plotid 를 줌
"""
# 주차장의 (주차id, 위도, 경도) 반환 api
class ParkingLotList(APIView):
    @api_view(['GET'])
    def get_plot_list(self):
        parking_lots = ParkingLot.objects.all()
        data = [{"plotid": lot.plotid, "latitude": lot.latitude, "longitude": lot.longitude} for lot in parking_lots]
        return Response(data, status=status.HTTP_200_OK)

    @api_view(['POST'])
    def get_plot_info(request):
        data = JSONParser().parse(request)
        parking_lot_id = data['plotid']
        parking_lot = ParkingLot.objects.get(plotid=parking_lot_id)
        response_data = {
            'plotname': parking_lot.plotname,
            'location': parking_lot.location,
            'total_space': parking_lot.total_space,
        }
        return Response(response_data)
"""
###### 안드로이드 앱 시작시 호출하는 api
# 마커 정보 + 주차장 정보 등 필요한 모든 정보 반환
@api_view(['GET'])
def get_marker(self):
    Parking_Lot = ParkingLot.objects.all()
    data = [{"plotid": lot.plotid, "latitude": lot.latitude, "longitude": lot.longitude,
            "plotname": lot.plotname , "location": lot.location, "fee": lot.fee,
            "total_space": lot.total_space, "available_space": lot.available_space} 
            for lot in Parking_Lot]
    return Response(data, status=status.HTTP_200_OK)  

###### 예약 API 구현
# availble 속성 인공지능 모델에 따라 업데이트
# 0. 주차장의 parking_slot 테이블의 availble 속성 딥러닝으로 계속 업데이트

from rest_framework.response import Response
from .models import ParkingSlot, ParkingLot
from .detectWebcam import init_roboflow, makePath, webCamStart
#import clova as cv

### Roboflow 모델을 가져와서 객체 인식을 수행하는 함수
# 이 함수의 결과는 {0: "empty"} 와 같은 객체 인식 결과 딕셔너리
# detectWebcam.py에서 함수 호출해 사용
def perform_object_detection():
    # 로직을 추가하여 객체 인식을 수행하는 코드 작성
    # 인식 결과를 반환 (occupied 또는 empty)
    occupied_path = "./images/occupied_boundingBox"
    empty_path = "./images/empty_boundingBox"
    api_key="Ndgqrpfsb4lW0aJHDg8q"  # 로보플로우 api key
    project = "pl-sr"   #로보플로우 프로젝트 이름
    version = 1

    model = init_roboflow(api_key, project, version)
    makePath(occupied_path, empty_path)
    # 슬랏 인덱스 별 occupied/empty 정보를 저장한 딕셔너리를 반환
    slot_detection_result = webCamStart(model, occupied_path, empty_path, confidence= 40, slotName="A")
    return slot_detection_result

#import clova as cv
from .clova import clova
import os    

# 번호판 비교 업데이트 하고, 번호판 일치하면 입차시간 업데이트
def update_time_plate(real_slotid):
    print("update_time_plate 진입")
    occupied_path = "./images/occupied_boundingBox"
    #empty_path = "./images/empty_boundingBox"
    api_url = 'https://em19qzhk73.apigw.ntruss.com/custom/v1/22367/012ff1ea564eacc4379dd5444bfb9d6fb6e08954487dbb9945208defc49b9032/general'
    secret_key = 'TnlCdUlFTmRRalltRGpWY3JCRlBsclVWUlJ1VkRJcng='
    #clova_save_path = "images/"
    #save_image_name = "OCRresult"

    occupied_plate_dict = {}
    print("update_time_plate: for문 앞")
    for img_name in os.listdir(occupied_path): # occupied 됐으면 번호판 인식
        print("update_time_plate: for문 진입: ", img_name[:4])

        if real_slotid == img_name[:4]:
            print("이미지 이름이 slotid랑 일치한다면")
            #print(img_name)
            f = occupied_path  + "/" + img_name
            result = clova(api_url=api_url, secret_key=secret_key, path=f)
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

            print(occupied_plate_dict)  # 예약된 특정 한 슬랏에 대한 번호판 텍스트 
    

     
    try:
        reservation = Reservation.objects.get(slotid=real_slotid)
    except Reservation.DoesNotExist:
        return Response({'error': '해당하는 예약이 없습니다'}, status=status.HTTP_400_BAD_REQUEST)

    if reservation.carnum == occupied_plate_dict[real_slotid]:
        reservation.intime = timezone.now()
        reservation.finished = 'y'
        reservation.save()
    else:   # 번호판이 일치하지 않을 경우 경고,,,,
        print("##########경고###########")

    
    
    

    serializer = ReservationSerializer(reservation)
    return Response(serializer.data, status=status.HTTP_200_OK)

        

### slot별 주차현황 db에 업데이트하는 함수
# perform_object_detection() 에서 반환한 slot_detection_result를 통해 parking_slot테이블의 availble 속성 업데이트
# 업데이트 한 슬랏 현황을 바탕으로 parking_lot 테이블의 available_space 업데이트
def slot_db_update(slot_detection_result):
    print("slot_db_update 호출")
    # 객체 인식 수행, 딕셔너리 형태
    #slot_detection_result = perform_object_detection()

    # 받아온 딕셔너리를 가공하여 해당 slotid의 occupied/empty에 따라 parking_slot 테이블의 available 속성 수정
    for slotid in slot_detection_result.keys(): # 슬랏의 인덱스 가져옴( 0, 1, 2, ... 형태)
        print("for문 진입 성공")
        # plotid를 안드에서 받아온다면...
        # slotid = f"{plotid}_A{slotid+1}"로 수정
        real_slotid = f"1_A{slotid+1}"  # 인덱스 0부터 시작하니 slotid 포맷 생성

        try:
            parking_slot = ParkingSlot.objects.get(slotid=real_slotid)  # 슬랏id가 일치하는 슬랏 튜플 가져옴
        except ParkingSlot.DoesNotExist:
            return Response({'error': '슬랏이 존재하지 않습니다. Invalid slotid'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if slot_detection_result[slotid] == "occupied": # 딕셔너리에 인덱스 값을 키값으로 넣었을때 "occupied" 라면(slot_detection_result[0] 형태)
            
            # 만약 parking_slot.slotid가 예약된 거라면 입차시간 업데이트 후 번호판 비교
            try:
                print("예약된 슬랏인지 비교할게")
                print(real_slotid)
                reservation  = Reservation.objects.get(slotid=real_slotid)  # 슬랏id가 일치하는 슬랏 튜플 가져옴
                if reservation.finished == 'n':
                    print("예약된 슬랏이라면")
                    print("reservation.slotid: ", reservation.slotid)
                    # 예약된 slot이라면 입차시간 업데이트하고, 번호판 비교(api 따로 작성)
                    update_time_plate(real_slotid)
                
                parking_slot.available = 'n'    # 슬랏에 차가 존재하니 예약할 수 없음
            except:
                print("예약된 슬랏 없어요")



        elif slot_detection_result[slotid] == "empty":  # 딕셔너리에 인덱스 값을 키값으로 넣었을때 "empty" 라면
            ####### 여기 안에 reservation 테이블 안에 slotid와 finished 속성 비교해서 업데이트 하도록,,,,
            #reserved_slot = Reservation.objects.filter(slotid=slotid, finished='n')
            if Reservation.objects.filter(slotid=real_slotid, finished='n').exists():
                pass  # 예약이 존재할 경우 아무 작업도 수행하지 않음
            else:
                parking_slot.available = 'y'
            
            
            
        
        parking_slot.save() # 수정한 속성값 DB에 최종 저장

    # ParkingLot 테이블 업데이트
    parking_lots = ParkingLot.objects.all() # 주차장 다 가져오기
    for parking_lot in parking_lots:    # 주차장들 중 특정 주차장 튜플 가져오기
        # plotid 일치하는 해당 주차장의 슬롯 개수를 세어서 total_space 업데이트
        total_slots = ParkingSlot.objects.filter(plotid=parking_lot.plotid).count()
        available_slots = ParkingSlot.objects.filter(plotid=parking_lot.plotid, available='y').count()  # 예약 가능한 슬랏만 카운트
        parking_lot.total_space = total_slots   # 속성에 값 저장
        parking_lot.available_space = available_slots
        parking_lot.save()  # DB에 최종 업데이트

    return Response(status=200)

import threading
import time

###### 실시간 슬랏현황 업데이트 api
# 실시간으로 돌아야하기 때문에 스레드 분기
class SlotUpdateThread(threading.Thread):
    def run(self):
        occupied_path = "./images/occupied_boundingBox"
        empty_path = "./images/empty_boundingBox"
        api_key="Ndgqrpfsb4lW0aJHDg8q"  # 로보플로우 api key
        project = "pl-sr"   #로보플로우 프로젝트 이름
        version = 1

        model = init_roboflow(api_key, project, version)
        makePath(occupied_path, empty_path)
        # 슬랏 인덱스 별 occupied/empty 정보를 저장한 딕셔너리를 반환
        

        while True: # 실시간으로 돌리기
            # 실시간으로 객체인식하고 db업데이트하는 함수 호출
            slot_detection_result = webCamStart(model, occupied_path, empty_path, confidence= 40, slotName="A")
            slot_db_update(slot_detection_result)    
            time.sleep(8)  # 8초마다 API 호출

# 스레드 시작
slot_update_thread = SlotUpdateThread()
slot_update_thread.start()
        
###### 주차장별 slot 정보 가져오는 api (slotid, available)
@api_view(['POST'])
def get_slot_info(request):
    plotid = request.data.get('plotid') # 안드에서 받은 plotid 저장
    parking_slots = ParkingSlot.objects.filter(plotid=plotid)   # parking_slot 테이블에서 해당 plotid와 일치하는 슬랏 정보 모두 가져옴 
    data = [{"slotid": slot.slotid, "available": slot.available} for slot in parking_slots] # 가져온 튜플 중 slotid와 available 속성 뽑아서 저장
    return Response(data, status=status.HTTP_200_OK)
    

###### 2. 예약 정보 받아서 예약 db 업데이트하는 api
@api_view(['POST'])
def update_reservation(request):
    plotid = request.data.get('plotid')
    slotid = request.data.get('slotid')
    userid = request.data.get('userid')
    carnum = request.data.get('carnum')
    usagetime = request.data.get('usagetime')

    # 예약번호 생성
    last_reservation = Reservation.objects.last()
    if last_reservation:
        resnum = last_reservation.resnum + 1
    else:
        resnum = 1

    # 예약 정보 생성
    reservation = Reservation(
        resnum=resnum,
        plotid=plotid,
        slotid_id=slotid,
        userid_id=userid,
        carnum=carnum,
        usagetime=usagetime,
        intime=None,
        outtime=None,
        finished='n'
    )
    reservation.save()  # 예약 DB에 저장

    # 예약이 완료됐으니
    # parking_slot 테이블에서 slotid가 일치하는 튜플에서 available 속성 n로 업데이트
    try:
        parking_slot = ParkingSlot.objects.get(slotid=slotid)
        parking_slot.available = 'n'
        parking_slot.save()
    except ParkingSlot.DoesNotExist:
        return Response({'error': 'Invalid slotid'}, status=status.HTTP_400_BAD_REQUEST)

    # 사용자에게 예약 완료 팝업 띄워주기 위해
    # parking_lot 테이블에서 plotname, location 정보 가져오기
    try:
        parking_lot = ParkingLot.objects.get(plotid=plotid)
    except ParkingLot.DoesNotExist:
        return Response({'error': 'Invalid plotid'}, status=status.HTTP_400_BAD_REQUEST)

    # 반환할 값
    response_data = {
        'parking_lot_name': parking_lot.plotname,
        'parking_lot_location': parking_lot.location,
        'slotid': slotid,
        'usagetime': usagetime,
        'available': parking_slot.available
    }
    return Response(response_data, status=status.HTTP_200_OK)


###### 예약 후 입차시 번호판 비교 api
# 딥러닝 모델을 통해 reservation 테이블에 존재하는 slotid에 차량이 입차했다고 판단되면,
# 해당 reservation 튜플의 carnum과 실제 입차한 차량의 차량번호가 일치하는지 clova ocr 을 이용해 비교하고,
# 만약 일치한다면 reservation 테이블의 intime 속성에 입차한 시각(현재 시각)을 업데이트
# 만약 불일치한다면 경고메세지 출력
# 아직 구현중...
# 입차가 되면 finished='y'로 수정

from django.utils import timezone
import datetime
from .serializers import ReservationSerializer

@api_view(['POST'])
def check_in(request):
    slotid = request.data.get('slotid')
    carnum = request.data.get('carnum')


    #data = 클로바의 result 결과
    #infer_text = data['images'][0]['fields'][0]['inferText'] + data['images'][0]['fields'][1]['inferText']


    try:
        reservation = Reservation.objects.get(slotid=slotid, carnum=carnum)
    except Reservation.DoesNotExist:
        return Response({'error': '해당하는 예약이 없습니다'}, status=status.HTTP_400_BAD_REQUEST)

    current_time = timezone.now()
    reservation.intime = current_time
    reservation.save()

    serializer = ReservationSerializer(reservation)
    return Response(serializer.data, status=status.HTTP_200_OK)


###### 로그인 api
@api_view(['POST'])
def login(request):
    userid = request.data.get('userid')
    password = request.data.get('password')

    obj = User.objects.get(userid=userid)   # 아이디 일치하는 튜플 가져옴

    if password == obj.password:    # 비밀번호 비교
        return Response({'result':200}, status=status.HTTP_200_OK)  # 로그인 성공
    else:
        return Response({'result':400}, status=status.HTTP_400_BAD_REQUEST) # 로그인 실패


###### 마이페이지 API
@api_view(['POST'])
def get_mypage(request):
    # 현재 로그인한 사용자의 아이디 가져오기
    userid = request.data.get('userid')

    try:
        # User 테이블에서 해당 사용자의 정보 가져오기
        user = User.objects.get(userid=userid)

        # 사용자 정보에서 필요한 속성 추출
        username = user.username
        carnum = user.carnum
        phone = user.phone
        address = user.address

        # 사용자 정보 응답 데이터 구성
        response_data = {
            "username": username,
            "carnum": carnum,
            "phone": phone,
            "address": address
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # 사용자가 존재하지 않을 경우 오류 상태 반환
        response_data = {
            "error": "사용자 정보를 찾을 수 없습니다."
        }
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)