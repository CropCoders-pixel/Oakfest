from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import hashlib

class CacheMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method != 'GET':
            return None

        # Don't cache admin or authenticated requests
        if request.path.startswith('/admin') or request.user.is_authenticated:
            return None

        cache_key = self._generate_cache_key(request)
        response = cache.get(cache_key)
        
        if response:
            return response
        
        return None

    def process_response(self, request, response):
        if request.method != 'GET':
            return response

        # Don't cache admin, authenticated requests, or error responses
        if (request.path.startswith('/admin') or 
            request.user.is_authenticated or 
            response.status_code != 200):
            return response

        cache_key = self._generate_cache_key(request)
        cache.set(cache_key, response, settings.CACHE_MIDDLEWARE_SECONDS)
        
        return response

    def _generate_cache_key(self, request):
        """Generate a cache key based on the full URL"""
        url = f"{request.scheme}://{request.get_host()}{request.get_full_path()}"
        return f"page_cache:{hashlib.md5(url.encode()).hexdigest()}"
