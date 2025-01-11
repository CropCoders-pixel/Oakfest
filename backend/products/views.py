from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Category, Product, Review, WasteReport
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductListSerializer,
    ReviewSerializer,
    WasteReportSerializer,
    WasteStatisticsSerializer
)
from users.permissions import IsFarmer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_organic', 'is_featured', 'farmer']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsFarmer]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        product = self.get_object()
        stats = {
            'average_rating': Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0,
            'review_count': Review.objects.filter(product=product).count(),
            'rating_distribution': Review.objects.filter(product=product).values('rating').annotate(count=Count('rating'))
        }
        return Response(stats)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WasteReportViewSet(viewsets.ModelViewSet):
    queryset = WasteReport.objects.all()
    serializer_class = WasteReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['waste_type', 'user']
    ordering_fields = ['created_at', 'quantity']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return WasteReport.objects.all()
        return WasteReport.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        # Get the date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Calculate total waste and points
        total_stats = WasteReport.objects.filter(user=request.user).aggregate(
            total_waste=Sum('quantity'),
            total_points=Sum('points_awarded')
        )
        
        # Get waste by type
        waste_by_type = WasteReport.objects.filter(user=request.user).values('waste_type').annotate(
            total=Sum('quantity')
        )
        
        # Get monthly statistics
        monthly_stats = WasteReport.objects.filter(
            user=request.user,
            created_at__range=(start_date, end_date)
        ).values('waste_type').annotate(
            total=Sum('quantity')
        ).order_by('waste_type')
        
        serializer = WasteStatisticsSerializer(data={
            'total_waste': total_stats['total_waste'] or 0,
            'total_points': total_stats['total_points'] or 0,
            'waste_by_type': {
                item['waste_type']: item['total']
                for item in waste_by_type
            },
            'monthly_stats': monthly_stats
        })
        serializer.is_valid()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        top_users = WasteReport.objects.values(
            'user__email',
            'user__first_name',
            'user__last_name'
        ).annotate(
            total_points=Sum('points_awarded'),
            total_waste=Sum('quantity')
        ).order_by('-total_points')[:10]
        
        return Response(list(top_users))
