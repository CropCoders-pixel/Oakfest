from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductReviewViewSet

# Create a router for products
router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

# Create a router for product reviews
product_router = DefaultRouter()
product_router.register(r'reviews', ProductReviewViewSet, basename='product-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:product_pk>/', include(product_router.urls)),
]
