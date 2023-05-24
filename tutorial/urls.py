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
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from tutorial.quickstart import views

from django.conf.urls import include


urlpatterns = [
    path('login/', views.login),
    path('plot/', views.ParkingLotList.get_plot_info),
    path('plot_list/', views.ParkingLotList.get_plot_list),
    path('marker/', views.get_marker),
    # /reservation/ 엔드포인트로 POST 요청이 들어오면 Reservation 클래스의 post 메서드 실행
    # GET 요청이 들어오면 Reservation 클래스의 get_queryset 메서드가 실행
    # 예약전 해당 주차장의 slot 보여주는 api
    path('get_slot_info/', views.Get_parkingslot_info.as_view(), name='get_slot_info'),
    path('update_reservation/', views.update_reservation, name='update_reservation'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
