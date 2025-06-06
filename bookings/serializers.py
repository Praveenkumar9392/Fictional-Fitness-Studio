# serializers.py
from rest_framework import serializers
from .models import FitnessClass, Booking

class FitnessClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessClass
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class BookingRequestSerializer(serializers.Serializer):
    class_id = serializers.IntegerField()
    client_name = serializers.CharField()
    client_email = serializers.EmailField()