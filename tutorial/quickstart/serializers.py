from rest_framework import serializers
from .models import ParkingLot, ParkingSlot, User, Reservation

class ParkingLotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ['plotid', 'plotname', 'location', 'latitude', 'longitude', 'fee', 'total_space', 'available_space']

class ParkingSlotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = ['plotid', 'slotid', 'ptime', 'available']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userid', 'password', 'carnum', 'username', 'address', 'phone']

# 예약 정보
class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['resnum', 'plotid', 'slotid', 'userid', 'carnum', 'intime', 'outtime', 'usagetime']