from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Category, Product, Review, WasteReport, ProductReview
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductListSerializer,
    ReviewSerializer,
    WasteReportSerializer,
    WasteStatisticsSerializer,
    ProductReviewSerializer
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

class IsFarmer(permissions.BasePermission):
    """Custom permission to only allow farmers to create/edit products"""
    
    def has_permission(self, request, view):
        # Allow read operations for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is authenticated and is a farmer
        return request.user.is_authenticated and request.user.user_type == 'farmer'
    
    def has_object_permission(self, request, view, obj):
        # Allow read operations for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only allow farmers to modify their own products
        return obj.farmer == request.user

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsFarmer]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by farmer
        farmer_id = self.request.query_params.get('farmer', None)
        if farmer_id:
            queryset = queryset.filter(farmer_id=farmer_id)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def manage_stock(self, request, pk=None):
        product = self.get_object()
        action = request.data.get('action')
        quantity = int(request.data.get('quantity', 0))
        
        if action not in ['add', 'remove']:
            return Response(
                {'error': 'Invalid action. Use "add" or "remove"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action == 'remove' and product.stock < quantity:
            return Response(
                {'error': 'Insufficient stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action == 'add':
            product.stock += quantity
        else:
            product.stock -= quantity
        
        product.save()
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Get all products for the current farmer"""
        if request.user.user_type != 'farmer':
            return Response(
                {'error': 'Only farmers can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        products = Product.objects.filter(farmer=request.user, is_active=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a product by setting is_active to False"""
        product = self.get_object()
        product.is_active = False
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return ProductReview.objects.filter(product_id=self.kwargs['product_pk'])
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            product_id=self.kwargs['product_pk']
        )
