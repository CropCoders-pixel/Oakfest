from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from .models import WasteReport, WasteCategory
from .serializers import WasteReportSerializer, WasteCategorySerializer
from .ml_utils import WasteClassifier
import os
import logging

logger = logging.getLogger(__name__)

# Initialize waste classifier lazily to avoid startup errors
waste_classifier = None

def get_waste_classifier():
    global waste_classifier
    if waste_classifier is None:
        try:
            MODEL_PATH = os.path.join(settings.BASE_DIR, 'waste', 'ml_model')
            waste_classifier = WasteClassifier(MODEL_PATH)
        except Exception as e:
            logger.error(f"Failed to load waste classifier: {e}")
            return None
    return waste_classifier

class WasteReportViewSet(viewsets.ModelViewSet):
    queryset = WasteReport.objects.all()
    serializer_class = WasteReportSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return WasteReport.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def classify(self, request):
        image = request.FILES.get('image')
        
        if not image:
            return Response(
                {'error': 'Image is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        classifier = get_waste_classifier()
        if not classifier:
            return Response(
                {'error': 'Waste classifier is not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            waste_type = classifier.classify_image(image)
            return Response({
                'waste_type': waste_type,
                'confidence': classifier.get_confidence()
            })
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return Response(
                {'error': 'Failed to classify image'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        # Add the user to the request data
        data = request.data.copy()
        data['user'] = request.user.id

        # Get the image and waste type
        image = request.FILES.get('image')
        waste_type = data.get('waste_type')
        
        if not image:
            return Response(
                {'error': 'Image is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not waste_type:
            return Response(
                {'error': 'Waste type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate waste type
        allowed_types = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
        if waste_type not in allowed_types:
            return Response(
                {'error': f'Invalid waste type. Must be one of: {", ".join(allowed_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the waste report
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # Save the report
            report = serializer.save()
            
            # Update user points
            user = request.user
            user.total_points += report.points
            user.save()
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Waste report created successfully',
                    'report': serializer.data,
                    'points_earned': report.points,
                    'total_points': user.total_points
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WasteCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WasteCategory.objects.all()
    serializer_class = WasteCategorySerializer
    permission_classes = [IsAuthenticated]
