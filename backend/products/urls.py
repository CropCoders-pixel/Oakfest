from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ReviewViewSet, WasteReportViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'waste', WasteReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
