from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView, UserProfileView,
    LeaderboardView, WeeklyLeaderboardView, ImpactLeaderboardView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # Profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Leaderboard endpoints
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('leaderboard/weekly/', WeeklyLeaderboardView.as_view(), name='weekly_leaderboard'),
    path('leaderboard/impact/', ImpactLeaderboardView.as_view(), name='impact_leaderboard'),
]
