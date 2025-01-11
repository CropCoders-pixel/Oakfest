from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

# Create your views here.

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)
    
    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        cart_item = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            cart_item.quantity = quantity
            cart_item.save()
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Quantity must be a number'},
                status=status.HTTP_400_BAD_REQUEST
            )
