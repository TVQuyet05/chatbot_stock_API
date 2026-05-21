import time
from src.auth.rate_limiter import RateLimiter

def test_rate_limiter_basic():
    limiter = RateLimiter(max_tokens=2, window=60)
    client = "client1"
    
    assert limiter.is_allowed(client) is True
    assert limiter.is_allowed(client) is True
    assert limiter.is_allowed(client) is False

def test_rate_limiter_refill():
    # Use a very short window for refilling
    limiter = RateLimiter(max_tokens=1, window=1) 
    client = "client2"
    
    assert limiter.is_allowed(client) is True
    assert limiter.is_allowed(client) is False
    
    time.sleep(1.1)
    assert limiter.is_allowed(client) is True
