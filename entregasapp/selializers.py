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
    events = EventDetailSerializer(many=True)

    class Meta:
        model = TrackingEventCA
        fields = ['tracking_number', 'quantity', 'country_id', 'service_type', 'events']

    def create(self, validated_data):
        events_data = validated_data.pop('events')
        tracking_event = TrackingEventCA.objects.create(**validated_data)
        for event_data in events_data:
            EventDetail.objects.create(tracking_event=tracking_event, **event_data)
        return tracking_event

    def update(self, instance, validated_data):
        events_data = validated_data.pop('events')
        instance.tracking_number = validated_data.get('tracking_number', instance.tracking_number)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.country_id = validated_data.get('country_id', instance.country_id)
        instance.service_type = validated_data.get('service_type', instance.service_type)
        instance.save()

        # Clear existing events and create new ones
        instance.events.all().delete()
        for event_data in events_data:
            EventDetail.objects.create(tracking_event=instance, **event_data)
        return instance