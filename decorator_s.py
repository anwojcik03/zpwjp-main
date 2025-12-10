import time
from functools import wraps
import functools

def timer(func):
    @wraps(func)
    def wrapper(*a, **kw):
        start = time.time()
        out = func(*a, **kw)
        print(f"{func.__name__}: {time.time() - start:.3f}s")
        return out
    return wrapper


def cache(func):
    memo = {}
    @wraps(func)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        result = func(*args)
        memo[args] = result
        return result
    return wrapper