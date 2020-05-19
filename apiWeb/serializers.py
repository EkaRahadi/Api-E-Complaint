from rest_framework import serializers
from apiMobile.models import rawComplaints

class RawComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = rawComplaints
        fields = '__all__'