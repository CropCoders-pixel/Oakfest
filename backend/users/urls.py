from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserRegistrationView

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('', include(router.urls)),
]
