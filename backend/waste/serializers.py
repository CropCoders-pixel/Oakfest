from rest_framework import serializers
from .models import WasteReport, WasteCategory

class WasteCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteCategory
        fields = '__all__'

class WasteReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteReport
        fields = [
            'id', 'category', 'waste_type', 'quantity',
            'description', 'location', 'image',
            'points_awarded', 'created_at', 'status'
        ]
        read_only_fields = ['points_awarded', 'status']

    def create(self, validated_data):
        # Ensure user is set from context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
