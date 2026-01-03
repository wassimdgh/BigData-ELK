"""
Redis Caching Utility
Provides decorators and functions for caching with Redis
"""
import redis
import json
from functools import wraps
from flask import request
from datetime import datetime, timedelta
import os

def get_redis_client():
    """Get Redis client instance"""
    redis_host = os.getenv('REDIS_HOST', 'redis')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_db = int(os.getenv('REDIS_DB', 0))
    
    return redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True
    )


def cache_key(*args, **kwargs):
    """Generate cache key from function arguments"""
    # Include request path and method for route caching
    path = request.path if hasattr(request, 'path') else ''
    method = request.method if hasattr(request, 'method') else ''
    
    # Include query parameters
    query_string = request.query_string.decode() if hasattr(request, 'query_string') else ''
    
    key_parts = [path, method, query_string] + list(args)
    return ':'.join(str(p) for p in key_parts if p)


def cached(ttl=300):
    """
    Decorator to cache function results in Redis
    
    Args:
        ttl (int): Time to live in seconds (default: 5 minutes)
    
    Usage:
        @cached(ttl=600)
        def expensive_function(param1, param2):
            return result
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                redis_client = get_redis_client()
                
                # Generate cache key
                key = f"cache:{f.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                
                # Try to get from cache
                cached_value = redis_client.get(key)
                if cached_value:
                    try:
                        return json.loads(cached_value)
                    except json.JSONDecodeError:
                        return cached_value
                
                # Call the function
                result = f(*args, **kwargs)
                
                # Store in cache
                try:
                    redis_client.setex(
                        key,
                        ttl,
                        json.dumps(result, default=str)
                    )
                except (TypeError, ValueError):
                    # If JSON serialization fails, store as string
                    redis_client.setex(key, ttl, str(result))
                
                return result
                
            except redis.ConnectionError:
                # If Redis is down, just call the function
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def cached_route(ttl=300):
    """
    Decorator to cache Flask route responses
    
    Only caches GET requests with status 200
    Includes request parameters and user info in cache key
    
    Args:
        ttl (int): Time to live in seconds (default: 5 minutes)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Only cache GET requests
                if request.method != 'GET':
                    return f(*args, **kwargs)
                
                redis_client = get_redis_client()
                
                # Generate cache key including query params and user
                from flask_login import current_user
                user_id = current_user.id if current_user.is_authenticated else 'anonymous'
                
                key_parts = [
                    f.__name__,
                    request.path,
                    request.query_string.decode(),
                    user_id
                ]
                cache_key_str = f"route:{':'.join(str(p) for p in key_parts if p)}"
                
                # Try to get from cache
                cached_value = redis_client.get(cache_key_str)
                if cached_value:
                    from flask import jsonify
                    try:
                        # Return as proper JSON response
                        data = json.loads(cached_value)
                        return jsonify(data), 200
                    except json.JSONDecodeError:
                        return cached_value, 200
                
                # Call the function
                result = f(*args, **kwargs)
                
                # Only cache successful responses
                if isinstance(result, tuple) and len(result) >= 2:
                    response_data, status_code = result[0], result[1]
                    if status_code == 200:
                        # If response is a Flask Response, extract JSON payload
                        payload = None
                        try:
                            # Flask Response has get_json in Flask >=1.0
                            if hasattr(response_data, 'get_json'):
                                payload = response_data.get_json(silent=True)
                            if payload is None and hasattr(response_data, 'get_data'):
                                raw = response_data.get_data(as_text=True)
                                payload = json.loads(raw)
                        except Exception:
                            payload = None

                        try:
                            if payload is not None:
                                redis_client.setex(
                                    cache_key_str,
                                    ttl,
                                    json.dumps(payload, default=str)
                                )
                        except (TypeError, ValueError):
                            pass
                else:
                    try:
                        redis_client.setex(
                            cache_key_str,
                            ttl,
                            json.dumps(result, default=str)
                        )
                    except (TypeError, ValueError):
                        pass
                
                return result
                
            except redis.ConnectionError:
                # If Redis is down, just call the function
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def clear_cache(pattern=None):
    """
    Clear cache entries
    
    Args:
        pattern (str): Redis key pattern to delete (e.g., "cache:*" or "route:*")
    """
    try:
        redis_client = get_redis_client()
        
        if pattern:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                return len(keys)
        else:
            redis_client.flushdb()
            return -1  # All keys deleted
        
        return 0
    except redis.ConnectionError:
        return None


def get_cache_stats():
    """Get Redis cache statistics"""
    try:
        redis_client = get_redis_client()
        
        info = redis_client.info()
        
        return {
            'connected': True,
            'memory_used': info.get('used_memory_human', 'N/A'),
            'memory_peak': info.get('used_memory_peak_human', 'N/A'),
            'keys_count': redis_client.dbsize(),
            'cache_keys': len(redis_client.keys('cache:*')),
            'route_keys': len(redis_client.keys('route:*')),
            'uptime_seconds': info.get('uptime_in_seconds', 0)
        }
    except redis.ConnectionError:
        return {
            'connected': False,
            'error': 'Cannot connect to Redis'
        }


class CacheManager:
    """Utility class for cache management"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
    
    def get(self, key):
        """Get value from cache"""
        try:
            value = self.redis_client.get(f"cache:{key}")
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except redis.ConnectionError:
            return None
    
    def set(self, key, value, ttl=300):
        """Set value in cache"""
        try:
            self.redis_client.setex(
                f"cache:{key}",
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except (redis.ConnectionError, TypeError, ValueError):
            return False
    
    def delete(self, key):
        """Delete value from cache"""
        try:
            return self.redis_client.delete(f"cache:{key}") > 0
        except redis.ConnectionError:
            return False
    
    def clear(self, pattern='*'):
        """Clear cache with pattern"""
        try:
            keys = self.redis_client.keys(f"cache:{pattern}")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except redis.ConnectionError:
            return False
    
    def exists(self, key):
        """Check if key exists"""
        try:
            return self.redis_client.exists(f"cache:{key}") > 0
        except redis.ConnectionError:
            return False
