# serializers.py
from rest_framework import serializers
from .models import TrackingEventCA, EventDetail

class EventDetailSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M", input_formats=["%d-%m-%Y %H:%M"])
    status_id = serializers.CharField()

    class Meta:
        model = EventDetail
        fields = ['facility_code', 'status_id', 'status', 'date', 'sign', 'facility']

class TrackingEventCASerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEventCA
        fields = ['tracking_number', 'raw_data']