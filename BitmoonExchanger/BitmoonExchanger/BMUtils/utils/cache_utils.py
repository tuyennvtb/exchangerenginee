from django.core.cache import cache
class CacheUtils:

    @classmethod
    def cache_key(cls,key,value,ttl=30):
        cache.set(key, value , ttl)
    
    @classmethod
    def get_key(cls,key):
        
        return cache.get(key)

    @classmethod
    def remove_key(cls,key):
        cache.delete(key)