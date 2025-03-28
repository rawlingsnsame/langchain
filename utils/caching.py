from functools import wraps
import hashlib
import json


def cached_embedding(func):
    """
    Decorator for caching embeddings
    """
    cache = {}

    @wraps(func)
    def wrapper(self, texts):
        # Create a cache key
        cache_key = hashlib.md5(json.dumps(texts, sort_keys=True).encode()).hexdigest()

        # Check cache
        if cache_key in cache:
            return cache[cache_key]

        # Generate and cache embeddings
        embeddings = func(self, texts)
        cache[cache_key] = embeddings

        return embeddings

    return wrapper
