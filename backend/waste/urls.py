from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WasteReportViewSet, WasteCategoryViewSet

router = DefaultRouter()
router.register(r'reports', WasteReportViewSet, basename='waste-reports')
router.register(r'categories', WasteCategoryViewSet, basename='waste-categories')

urlpatterns = [
    path('', include(router.urls)),
]
