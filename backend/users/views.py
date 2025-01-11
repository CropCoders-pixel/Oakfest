from django.contrib.auth import authenticate, login, logout
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .serializers import UserSerializer, UserRegistrationSerializer
from .models import User

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Logged in successfully'
            })
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class LeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        users = User.objects.annotate(
            total_points=Sum('wastereport__points_awarded')
        ).order_by('-total_points')[:10]
        
        return Response([{
            'username': user.username,
            'points': user.total_points or 0
        } for user in users])

class WeeklyLeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        week_ago = timezone.now() - timedelta(days=7)
        users = User.objects.filter(
            wastereport__created_at__gte=week_ago
        ).annotate(
            weekly_points=Sum('wastereport__points_awarded')
        ).order_by('-weekly_points')[:10]
        
        return Response([{
            'username': user.username,
            'points': user.weekly_points or 0
        } for user in users])

class ImpactLeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        users = User.objects.annotate(
            reports_count=Count('wastereport')
        ).order_by('-reports_count')[:10]
        
        return Response([{
            'username': user.username,
            'reports': user.reports_count or 0
        } for user in users])
