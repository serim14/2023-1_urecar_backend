from django.shortcuts import render
from rest_framework import generics
from .serializers import ParkingLotSerializer
from .models import ParkingLot, ParkingSlot, User
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
            'total_space': parking_lot.total_space,
        }
        return Response(response_data)


@api_view(['GET'])
def get_marker(self):
    parking_lots = ParkingLot.objects.all()
    data = [{"plotid": lot.plotid,"plotname": lot.plotname, "location": lot.location,
              "latitude": lot.latitude, "longitude": lot.longitude, "fee": lot.fee, "total_space": lot.total_space, "available_space": lot.available_space} for lot in parking_lots]
    return Response(data, status=status.HTTP_200_OK)



    
# availble 속성 인공지능 모델에 따라 업데이트
class ParkingSlotList(generics.ListAPIView):
    serializer_class = ParkingSlotSerializer

    def get_queryset(self):
        plotid = self.kwargs['plotid']
        queryset = ParkingSlot.objects.filter(plotid=plotid)
        return queryset
    

# 로그인 기능 구현
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        search_id = data['userid']
        obj = User.objects.get(userid=search_id)

        if data['password'] == obj.password:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)