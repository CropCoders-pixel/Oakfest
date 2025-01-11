from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import CategoryViewSet, ProductViewSet, ProductReviewViewSet, ReviewViewSet, WasteReportViewSet

# Create a router for categories, waste reports, and products
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'waste', WasteReportViewSet)
router.register(r'', ProductViewSet, basename='product')

# Create a nested router for product reviews
product_router = routers.NestedSimpleRouter(router, r'', lookup='product')
product_router.register(r'reviews', ProductReviewViewSet, basename='product-reviews')

# Create a router for reviews
review_router = DefaultRouter()
review_router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(review_router.urls)),
]
