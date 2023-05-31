from django.shortcuts import render
from rest_framework import generics
from .serializers import ParkingLotSerializer
from .models import ParkingLot, ParkingSlot, User, Reservation
from .serializers import ParkingSlotSerializer

from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser

from rest_framework.decorators import api_view

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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

# 마커정보, 주차장 정보 등 반환



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


from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ParkingSlot, ParkingLot
from .detectWebcam import init_roboflow, makePath, webCamStart
#import clova as cv
import os
import threading
# Roboflow 모델을 가져와서 객체 인식을 수행하는 함수
def perform_object_detection():
    # 로직을 추가하여 객체 인식을 수행하는 코드 작성
    # 인식 결과를 반환 (occupied 또는 empty)
    occupied_path = "./images/occupied_boundingBox"
    empty_path = "./images/empty_boundingBox"
    api_key="Ndgqrpfsb4lW0aJHDg8q"
    project = "pl-sr"
    version = 1

    model = init_roboflow(api_key, project, version)
    makePath(occupied_path, empty_path)
    slot_detection_result = webCamStart(model, occupied_path, empty_path, confidence= 40, slotName="공영주차장")
    return slot_detection_result

    


"""
# APIView를 상속받아서 실시간 주차장 슬롯 상태를 업데이트하는 API 구현
class ParkingSlotUpdateAPIView(APIView):
    def post(self, request):
        # 카메라에서 촬영한 이미지를 받음
        #image = request.data.get('image')

        # 객체 인식 수행
        # 딕셔너리 형태
        slot_detection_result = perform_object_detection()


         # 받아온 딕셔너리를 가공하여 해당 slotid를 occupied empty에 따라 parking_slot 테이블의 available 속성 수정

        for slotid in slot_detection_result.keys():
            # plotid를 안드에서 받아온다면,,,
            # slotid = f"{plotid}_A{slotid+1}"
            real_slotid = f"1_A{slotid+1}"

            try:
                parking_slot = ParkingSlot.objects.get(slotid=real_slotid)
            except ParkingSlot.DoesNotExist:
                return Response({'error': '슬랏이 존재하지 않습니다. Invalid slotid'}, status=status.HTTP_400_BAD_REQUEST)
            
            if slot_detection_result[slotid] == "occupied":
                parking_slot.available = 'n'
            elif slot_detection_result[slotid] == "empty":
                parking_slot.available = 'y'
            
            parking_slot.save()

        # ParkingLot 테이블 업데이트
        parking_lots = ParkingLot.objects.all()
        for parking_lot in parking_lots:
            # 해당 주차장의 슬롯 개수를 세어서 total_space 업데이트
            total_slots = ParkingSlot.objects.filter(plotid=parking_lot.plotid).count()
            available_slots = ParkingSlot.objects.filter(plotid=parking_lot.plotid, available='y').count()
            parking_lot.total_space = total_slots
            parking_lot.available_space = available_slots
            parking_lot.save()

        return Response(status=200)
"""

def slot_db_update():
    # 카메라에서 촬영한 이미지를 받음
    #image = request.data.get('image')

    # 객체 인식 수행
    # 딕셔너리 형태
    slot_detection_result = perform_object_detection()


        # 받아온 딕셔너리를 가공하여 해당 slotid를 occupied empty에 따라 parking_slot 테이블의 available 속성 수정

    for slotid in slot_detection_result.keys():
        # plotid를 안드에서 받아온다면,,,
        # slotid = f"{plotid}_A{slotid+1}"
        real_slotid = f"1_A{slotid+1}"

        try:
            parking_slot = ParkingSlot.objects.get(slotid=real_slotid)
        except ParkingSlot.DoesNotExist:
            return Response({'error': '슬랏이 존재하지 않습니다. Invalid slotid'}, status=status.HTTP_400_BAD_REQUEST)
        
        if slot_detection_result[slotid] == "occupied":
            parking_slot.available = 'n'
        elif slot_detection_result[slotid] == "empty":
            parking_slot.available = 'y'
        
        parking_slot.save()

    # ParkingLot 테이블 업데이트
    parking_lots = ParkingLot.objects.all()
    for parking_lot in parking_lots:
        # 해당 주차장의 슬롯 개수를 세어서 total_space 업데이트
        total_slots = ParkingSlot.objects.filter(plotid=parking_lot.plotid).count()
        available_slots = ParkingSlot.objects.filter(plotid=parking_lot.plotid, available='y').count()
        parking_lot.total_space = total_slots
        parking_lot.available_space = available_slots
        parking_lot.save()

    return Response(status=200)



# 1. 각각 주차장의 slot 정보 가져오기
# (안드) plotid 를 줌
"""
class Get_parkingslot_info(generics.ListAPIView):
    serializer_class = ParkingSlotSerializer
# (백엔드) parking_slot 테이블에서 plotid 일치하는 정보 조회해 돌려줌
    def get_queryset(self):
        plotid = self.request.data.get('plotid')    # 안드가 준 plotid 받아옴
        queryset = ParkingSlot.objects.filter(plotid=plotid)    # parking_slot 테이블에서 plotid로 특정 주차장의 slot정보 모두 조회해 가져옴
        return queryset

    def post(self, request, *args, **kwargs):
        if not request.data.get('plotid'):  # 안드에서 plotid를 주지 않았을 경우
            return Response({'error': 'plotid is required'}, status=status.HTTP_400_BAD_REQUEST)

        return self.list(request, *args, **kwargs)
"""
        
############ 주차장별 slot 정보 가져오기 (slotid, available)
@api_view(['POST'])
def get_slot_info(request):
    plotid = request.data.get('plotid')
    parking_slots = ParkingSlot.objects.filter(plotid=plotid)
    data = [{"slotid": slot.slotid, "available": slot.available} for slot in parking_slots]
    return Response(data, status=status.HTTP_200_OK)


from django.core.exceptions import ObjectDoesNotExist

"""
@api_view(['POST'])
def get_slot_info(request):
    plotid = request.data.get('plotid')

    try:
        parking_slot = ParkingSlot.objects.get(plotid=plotid)
    except ParkingSlot.DoesNotExist:
        return Response({'error': 'Invalid plotid'}, status=status.HTTP_400_BAD_REQUEST)
    except ParkingSlot.MultipleObjectsReturned:
        return Response({'error': 'Multiple parking slots found for the given plotid'}, status=status.HTTP_400_BAD_REQUEST)

    # 반환할 값
    serializer = ParkingSlotSerializer(parking_slot)
    return Response(serializer.data)

"""
    

# 2. 예약 정보 받아서 예약 db 업데이트
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
        outtime=None
    )
    reservation.save()

    # parking_slot 테이블에서 slotid가 일치하는 튜플에서 available 속성 n로 업데이트
    try:
        parking_slot = ParkingSlot.objects.get(slotid=slotid)
        parking_slot.available = 'n'
        parking_slot.save()
    except ParkingSlot.DoesNotExist:
        return Response({'error': 'Invalid slotid'}, status=status.HTTP_400_BAD_REQUEST)

    # ParkingLot 정보 가져오기
    try:
        parking_lot = ParkingLot.objects.get(plotid=plotid)
    except ParkingLot.DoesNotExist:
        return Response({'error': 'Invalid plotid'}, status=status.HTTP_400_BAD_REQUEST)

    # 반환할 값
    response_data = {
        'parking_lot_name': parking_lot.plotname,
        'parking_lot_location': parking_lot.location,
        'slotid': slotid,
        'usagetime': usagetime
    }

    return Response(response_data, status=status.HTTP_200_OK)


# 예약 후 입차시 번호판 비교 api
# 딥러닝 모델을 통해 reservation 테이블에 존재하는 slotid에 차량이 입차했다고 판단되면,
# 해당 reservation 튜플의 carnum과 실제 입차한 차량의 차량번호가 일치하는지 clova ocr 을 이용해 비교하고,
# 만약 일치한다면 reservation 테이블의 intime 속성에 입차한 시각(현재 시각)을 업데이트
# 만약 불일치한다면 경고메세지 출력
# 여기를 채워줘

from django.utils import timezone
import datetime
from .serializers import ReservationSerializer

@api_view(['POST'])
def check_in(request):
    slotid = request.data.get('slotid')
    carnum = request.data.get('carnum')

    try:
        reservation = Reservation.objects.get(slotid=slotid, carnum=carnum)
    except Reservation.DoesNotExist:
        return Response({'error': '해당하는 예약이 없습니다'}, status=status.HTTP_400_BAD_REQUEST)

    current_time = timezone.now()
    reservation.intime = current_time
    reservation.save()

    serializer = ReservationSerializer(reservation)
    return Response(serializer.data, status=status.HTTP_200_OK)




# 로그인 기능 구현
@api_view(['POST'])
def login(request):
    
    userid = request.data.get('userid')
    password = request.data.get('password')

    obj = User.objects.get(userid=userid)

    if password == obj.password:
        return Response({'result':200}, status=status.HTTP_200_OK)
    else:
        return Response({'result':400}, status=status.HTTP_400_BAD_REQUEST)


# 마이페이지 API

from rest_framework import status
from .models import User

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



import threading
import time

class SlotUpdateThread(threading.Thread):
    def run(self):
        while True:
            # 실시간 주차 슬롯 업데이트 API 호출
            #ParkingSlotUpdateAPIView.as_view()
            #perform_object_detection()
            
            #slot_detection_result = perform_object_detection()

            slot_db_update()

         # 받아온 딕셔너리를 가공하여 해당 slotid를 occupied empty에 따라 parking_slot 테이블의 available 속성 수정

        
            time.sleep(5)  # 3초마다 API 호출
            #return Response(status=200)


# 스레드 시작
slot_update_thread = SlotUpdateThread()
slot_update_thread.start()
