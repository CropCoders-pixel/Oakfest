from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import hashlib

class CacheMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method != 'GET':
            return None

        # Don't cache admin or API requests
        if request.path.startswith('/admin') or request.path.startswith('/api/'):
            return None

        # Don't cache if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return None

        cache_key = self._generate_cache_key(request)
        response = cache.get(cache_key)
        
        if response:
            return response
        
        return None

    def process_response(self, request, response):
        if request.method != 'GET':
            return response

        # Don't cache admin or API requests
        if request.path.startswith('/admin') or request.path.startswith('/api/'):
            return response

        # Don't cache if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return response

        # Don't cache error responses
        if response.status_code != 200:
            return response

        cache_key = self._generate_cache_key(request)
        cache.set(cache_key, response, settings.CACHE_MIDDLEWARE_SECONDS)
        return response

    def _generate_cache_key(self, request):
        """Generate a cache key based on the full URL"""
        url = f"{request.scheme}://{request.get_host()}{request.get_full_path()}"
        return f"page_cache_{hashlib.md5(url.encode()).hexdigest()}"
