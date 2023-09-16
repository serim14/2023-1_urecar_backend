from rest_framework import serializers
from .models import ParkingLot, ParkingSlot, User, Reservation, ParkingStats, RecommendedPlace

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

        

class ParkingStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingStats
        fields = ['time', 'plotid', 'numofslot', 'numofcar', 'stats', 'count']

class RecommendedPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedPlace
        fields = ['place_name', 'nearby_parking_lot', 'place_address', 'place_latitude', 'place_longitude', 'place_property']