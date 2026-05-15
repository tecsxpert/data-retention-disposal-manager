from flask import request, jsonify
from functools import wraps
import time
from collections import defaultdict

# Simple in-memory rate limiter for testing
class SimpleRateLimiter:
    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, key):
        """Check if request is allowed for given key"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    def get_remaining(self, key):
        """Get remaining requests for key"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        return max(0, self.max_requests - len(self.requests[key]))

# Global rate limiter instance
rate_limiter = SimpleRateLimiter(max_requests=50, window_seconds=60)

def rate_limit(f):
    """Decorator to apply rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Use IP address as rate limit key
        key = request.remote_addr or 'unknown'
        
        if not rate_limiter.is_allowed(key):
            remaining = rate_limiter.get_remaining(key)
            return jsonify({
                'error': 'Rate limit exceeded',
                'code': 'RATE_LIMIT_EXCEEDED',
                'remaining': remaining
            }), 429
        
        return f(*args, **kwargs)
    
    return decorated_function
