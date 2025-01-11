from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import User
from .serializers import UserSerializer

class LeaderboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get overall leaderboard"""
        top_users = User.objects.order_by('-reward_points')[:10]
        
        # Get user's rank if not in top 10
        user = request.user
        user_rank = user.contribution_rank
        user_in_top = user in top_users
        
        response_data = {
            'top_users': [
                {
                    'id': u.id,
                    'username': u.username,
                    'reward_points': u.reward_points,
                    'rank': idx + 1,
                    'total_waste_reports': u.total_waste_reports,
                    'environmental_impact': {
                        'carbon_saved': float(u.carbon_saved),
                        'trees_saved': float(u.trees_saved),
                        'water_saved': float(u.water_saved)
                    }
                }
                for idx, u in enumerate(top_users)
            ],
            'user_stats': {
                'rank': user_rank,
                'percentile': user.contribution_percentile,
                'reward_points': user.reward_points,
                'total_waste_reports': user.total_waste_reports,
                'environmental_impact': {
                    'carbon_saved': float(user.carbon_saved),
                    'trees_saved': float(user.trees_saved),
                    'water_saved': float(user.water_saved)
                }
            } if not user_in_top else None
        }
        
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        """Get weekly leaderboard"""
        week_ago = timezone.now() - timedelta(days=7)
        
        # Get users with waste reports in the last week
        top_users = User.objects.filter(
            waste_reports__created_at__gte=week_ago,
            waste_reports__status='approved'
        ).annotate(
            weekly_points=Sum('waste_reports__points_awarded')
        ).order_by('-weekly_points')[:10]
        
        response_data = {
            'top_users': [
                {
                    'id': u.id,
                    'username': u.username,
                    'weekly_points': u.weekly_points or 0,
                    'rank': idx + 1
                }
                for idx, u in enumerate(top_users)
            ],
            'time_period': {
                'start': week_ago,
                'end': timezone.now()
            }
        }
        
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def impact(self, request):
        """Get total environmental impact"""
        all_users = User.objects.all()
        
        total_impact = {
            'total_waste_reports': sum(u.total_waste_reports for u in all_users),
            'total_waste_collected': float(sum(u.total_waste_collected for u in all_users)),
            'carbon_saved': float(sum(u.carbon_saved for u in all_users)),
            'trees_saved': float(sum(u.trees_saved for u in all_users)),
            'water_saved': float(sum(u.water_saved for u in all_users)),
            'total_participants': all_users.count(),
            'waste_by_type': {
                'cardboard': 0,
                'glass': 0,
                'metal': 0,
                'paper': 0,
                'plastic': 0,
                'trash': 0
            }
        }
        
        # Get waste distribution
        waste_distribution = User.objects.filter(
            waste_reports__status='approved'
        ).values(
            'waste_reports__waste_type'
        ).annotate(
            total=Sum('waste_reports__quantity')
        )
        
        for item in waste_distribution:
            waste_type = item['waste_reports__waste_type']
            if waste_type in total_impact['waste_by_type']:
                total_impact['waste_by_type'][waste_type] = float(item['total'])
        
        return Response(total_impact)
