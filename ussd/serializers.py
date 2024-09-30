from rest_framework import serializers

class USSDRequestSerializer(serializers.Serializer):
    msisdn = serializers.CharField(max_length=255, allow_null=True, allow_blank=True)
    text = serializers.CharField(max_length=255, allow_null=True, allow_blank=True)
    sessionId = serializers.CharField(max_length=255)