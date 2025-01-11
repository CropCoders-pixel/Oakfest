from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from .models import Product, ProductReview
from .serializers import ProductSerializer, ProductReviewSerializer
from users.permissions import IsFarmer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'farmer']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'manage_stock', 'my_products']:
            return [IsFarmer()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.action == 'my_products':
            return Product.objects.filter(farmer=self.request.user, is_active=True)
        return Product.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)

    @action(detail=True, methods=['post'])
    def manage_stock(self, request, pk=None):
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        try:
            quantity = int(quantity)
            product.stock += quantity
            if product.stock < 0:
                return Response(
                    {'error': 'Cannot reduce stock below 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            product.save()
            return Response({'stock': product.stock})
        except ValueError:
            return Response(
                {'error': 'Quantity must be a number'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
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
