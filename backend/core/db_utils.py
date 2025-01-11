from django.core.cache import cache
from django.db import transaction
from functools import wraps
import phonenumbers
from django.core.exceptions import ValidationError

def validate_phone_number(phone):
    """Validate phone number format"""
    try:
        phone_number = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError("Invalid phone number")
    except phonenumbers.NumberParseException:
        raise ValidationError("Invalid phone number format")

def cached_queryset(timeout=300):
    """Cache queryset results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def atomic_transaction(func):
    """Ensure atomic database transactions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with transaction.atomic():
            return func(*args, **kwargs)
    return wrapper

def update_inventory(product_id, quantity, operation='decrease'):
    """Update product inventory with locking"""
    with transaction.atomic():
        from products.models import Product
        product = Product.objects.select_for_update().get(id=product_id)
        
        if operation == 'decrease':
            if product.stock < quantity:
                raise ValidationError("Insufficient stock")
            product.stock -= quantity
        else:
            product.stock += quantity
        
        product.save()
        return product.stock

def calculate_reward_points(order_total):
    """Calculate reward points for an order"""
    base_points = int(order_total * 10)  # 10 points per currency unit
    return base_points
