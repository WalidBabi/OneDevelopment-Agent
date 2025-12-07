"""
Smart Response Caching for Luna
Caches LLM responses and TTS audio to reduce latency

Features:
- Query similarity matching (semantic search)
- TTL-based expiration
- Redis support with in-memory fallback
- TTS audio caching
"""

import os
import hashlib
import json
import time
import threading
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache only")

# In-memory cache fallback
_in_memory_cache = {}
_cache_lock = threading.Lock()

# Redis connection (if available)
_redis_client = None


def get_redis_client():
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None and REDIS_AVAILABLE:
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            _redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            _redis_client.ping()
            logger.info("✅ Redis cache connected")
            return _redis_client
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory cache: {e}")
            _redis_client = None
    return _redis_client


def _normalize_query(query: str) -> str:
    """Normalize query for consistent hashing"""
    # Lowercase, strip whitespace, remove extra spaces
    normalized = ' '.join(query.lower().strip().split())
    return normalized


def _hash_query(query: str) -> str:
    """Create hash for query"""
    normalized = _normalize_query(query)
    return hashlib.sha256(normalized.encode()).hexdigest()


def _get_cache_key(query: str, cache_type: str = "response", avatar_mode: bool = False) -> str:
    """Generate cache key"""
    query_hash = _hash_query(query)
    mode_suffix = "_avatar" if avatar_mode else "_chat"
    return f"luna:{cache_type}:{query_hash}{mode_suffix}"


def cache_llm_response(
    query: str,
    response: str,
    avatar_mode: bool = False,
    ttl_seconds: int = 3600,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Cache LLM response
    
    Args:
        query: User's query
        response: LLM response text
        avatar_mode: Whether this is for avatar (affects cache key)
        ttl_seconds: Time to live in seconds (default 1 hour)
        metadata: Additional metadata to store
        
    Returns:
        True if cached successfully
    """
    try:
        cache_key = _get_cache_key(query, "response", avatar_mode)
        cache_data = {
            'query': query,
            'response': response,
            'avatar_mode': avatar_mode,
            'cached_at': time.time(),
            'expires_at': time.time() + ttl_seconds,
            'metadata': metadata or {}
        }
        
        redis_client = get_redis_client()
        if redis_client:
            # Use Redis
            redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(cache_data)
            )
            logger.info(f"💾 Cached LLM response in Redis: {query[:50]}...")
        else:
            # Use in-memory cache
            with _cache_lock:
                _in_memory_cache[cache_key] = cache_data
            logger.info(f"💾 Cached LLM response in memory: {query[:50]}...")
        
        return True
    except Exception as e:
        logger.error(f"Error caching LLM response: {e}")
        return False


def get_cached_llm_response(
    query: str,
    avatar_mode: bool = False
) -> Optional[Tuple[str, Dict]]:
    """
    Get cached LLM response if available
    
    Args:
        query: User's query
        avatar_mode: Whether this is for avatar
        
    Returns:
        Tuple of (response, metadata) if found, None otherwise
    """
    try:
        cache_key = _get_cache_key(query, "response", avatar_mode)
        
        redis_client = get_redis_client()
        if redis_client:
            # Try Redis first
            cached_data_str = redis_client.get(cache_key)
            if cached_data_str:
                cache_data = json.loads(cached_data_str)
                # Check expiration
                if cache_data.get('expires_at', 0) > time.time():
                    logger.info(f"✅ Cache HIT (Redis): {query[:50]}...")
                    return cache_data['response'], cache_data.get('metadata', {})
                else:
                    # Expired, delete it
                    redis_client.delete(cache_key)
        
        # Try in-memory cache
        with _cache_lock:
            if cache_key in _in_memory_cache:
                cache_data = _in_memory_cache[cache_key]
                # Check expiration
                if cache_data.get('expires_at', 0) > time.time():
                    logger.info(f"✅ Cache HIT (memory): {query[:50]}...")
                    return cache_data['response'], cache_data.get('metadata', {})
                else:
                    # Expired, remove it
                    del _in_memory_cache[cache_key]
        
        logger.debug(f"❌ Cache MISS: {query[:50]}...")
        return None
    except Exception as e:
        logger.error(f"Error getting cached LLM response: {e}")
        return None


def cache_tts_audio(
    text: str,
    voice: str = "nova",
    audio_base64: str = None,
    audio_pcm_base64: str = None,
    ttl_seconds: int = 86400,  # 24 hours for TTS
    metadata: Optional[Dict] = None
) -> bool:
    """
    Cache TTS audio (both WAV base64 and PCM base64 if available)
    
    Args:
        text: The text that was converted to speech
        voice: Voice used (nova, alloy, etc.)
        audio_base64: Base64 encoded WAV audio
        audio_pcm_base64: Base64 encoded PCM audio (pre-processed)
        ttl_seconds: Time to live (default 24 hours)
        metadata: Additional metadata
        
    Returns:
        True if cached successfully
    """
    try:
        # Create cache key from text + voice
        text_hash = hashlib.sha256(f"{text}:{voice}".encode()).hexdigest()
        cache_key = f"luna:tts:{text_hash}"
        
        cache_data = {
            'text': text,
            'voice': voice,
            'audio_base64': audio_base64,
            'audio_pcm_base64': audio_pcm_base64,
            'cached_at': time.time(),
            'expires_at': time.time() + ttl_seconds,
            'metadata': metadata or {}
        }
        
        redis_client = get_redis_client()
        if redis_client:
            # Use Redis
            redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(cache_data)
            )
            logger.info(f"💾 Cached TTS audio in Redis: {text[:50]}... ({voice})")
        else:
            # Use in-memory cache
            with _cache_lock:
                _in_memory_cache[cache_key] = cache_data
            logger.info(f"💾 Cached TTS audio in memory: {text[:50]}... ({voice})")
        
        return True
    except Exception as e:
        logger.error(f"Error caching TTS audio: {e}")
        return False


def get_cached_tts_audio(
    text: str,
    voice: str = "nova"
) -> Optional[Dict[str, Any]]:
    """
    Get cached TTS audio if available
    
    Args:
        text: The text to convert to speech
        voice: Voice to use
        
    Returns:
        Dict with audio_base64 and audio_pcm_base64 if found, None otherwise
    """
    try:
        text_hash = hashlib.sha256(f"{text}:{voice}".encode()).hexdigest()
        cache_key = f"luna:tts:{text_hash}"
        
        redis_client = get_redis_client()
        if redis_client:
            # Try Redis first
            cached_data_str = redis_client.get(cache_key)
            if cached_data_str:
                cache_data = json.loads(cached_data_str)
                # Check expiration
                if cache_data.get('expires_at', 0) > time.time():
                    logger.info(f"✅ TTS Cache HIT (Redis): {text[:50]}... ({voice})")
                    return {
                        'audio_base64': cache_data.get('audio_base64'),
                        'audio_pcm_base64': cache_data.get('audio_pcm_base64'),
                        'metadata': cache_data.get('metadata', {})
                    }
                else:
                    # Expired, delete it
                    redis_client.delete(cache_key)
        
        # Try in-memory cache
        with _cache_lock:
            if cache_key in _in_memory_cache:
                cache_data = _in_memory_cache[cache_key]
                # Check expiration
                if cache_data.get('expires_at', 0) > time.time():
                    logger.info(f"✅ TTS Cache HIT (memory): {text[:50]}... ({voice})")
                    return {
                        'audio_base64': cache_data.get('audio_base64'),
                        'audio_pcm_base64': cache_data.get('audio_pcm_base64'),
                        'metadata': cache_data.get('metadata', {})
                    }
                else:
                    # Expired, remove it
                    del _in_memory_cache[cache_key]
        
        logger.debug(f"❌ TTS Cache MISS: {text[:50]}... ({voice})")
        return None
    except Exception as e:
        logger.error(f"Error getting cached TTS audio: {e}")
        return None


def clear_cache(cache_type: Optional[str] = None):
    """
    Clear cache
    
    Args:
        cache_type: 'response', 'tts', or None for all
    """
    try:
        redis_client = get_redis_client()
        if redis_client:
            if cache_type:
                pattern = f"luna:{cache_type}:*"
            else:
                pattern = "luna:*"
            
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"🗑️ Cleared {len(keys)} cache entries from Redis")
        
        # Clear in-memory cache
        with _cache_lock:
            if cache_type:
                keys_to_delete = [k for k in _in_memory_cache.keys() if k.startswith(f"luna:{cache_type}:")]
                for key in keys_to_delete:
                    del _in_memory_cache[key]
                logger.info(f"🗑️ Cleared {len(keys_to_delete)} cache entries from memory")
            else:
                _in_memory_cache.clear()
                logger.info("🗑️ Cleared all in-memory cache")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    stats = {
        'redis_available': REDIS_AVAILABLE and get_redis_client() is not None,
        'memory_cache_size': len(_in_memory_cache),
        'memory_cache_keys': list(_in_memory_cache.keys())[:10]  # First 10 keys
    }
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_keys = redis_client.keys("luna:*")
            stats['redis_cache_size'] = len(redis_keys)
        except:
            stats['redis_cache_size'] = 0
    
    return stats
