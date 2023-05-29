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
            'total_space': parking_lot.totalspace,
        }
        return Response(response_data)


@api_view(['GET'])
def get_marker(self):
    parking_lots = ParkingLot.objects.all()
    data = [{"plotid": lot.plotid,"plotname": lot.plotname, "location": lot.location,
              "latitude": lot.latitude, "longitude": lot.longitude, "fee": lot.fee, "total_space": lot.total_space, "available_space": lot.available_space} for lot in parking_lots]
    return Response(data, status=status.HTTP_200_OK)


###### 예약 API 구현
    
# availble 속성 인공지능 모델에 따라 업데이트

# 0. 주차장의 parking_slot 테이블의 availble 속성 딥러닝으로 계속 업데이트

# 1. 각각 주차장의 slot 정보 가져오기
# (안드) plotid 를 줌

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
