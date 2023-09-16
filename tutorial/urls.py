"""tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from tutorial.quickstart import views
from django.conf.urls import include

urlpatterns = [
    path('login/', views.login),
    #path('plot/', views.ParkingLotList.get_plot_info),
    #path('plot_list/', views.ParkingLotList.get_plot_list),
    path('marker/', views.get_marker),
    # /reservation/ 엔드포인트로 POST 요청이 들어오면 Reservation 클래스의 post 메서드 실행
    # GET 요청이 들어오면 Reservation 클래스의 get_queryset 메서드가 실행
    # 예약전 해당 주차장의 slot 보여주는 api
    path('get_slot_info/', views.get_slot_info, name='get_slot_info'),
    path('update_reservation/', views.update_reservation, name='update_reservation'),
    path('mypage/',views.get_mypage),
    #path('parking-slot/slot-update/', views.ParkingSlotUpdateAPIView.as_view(), name='parking-slot-update'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 주차장 통계 api
    path('get_parking_stats/', views.get_parking_stats, name='get_parking_stats'),
    path('get_nearby_places/', views.get_nearby_places, name='get_nearby_places'),  # 인근장소추천
]
