# This will make celery auto-discovery work for Django projects.
# Import celery only when needed to avoid Django setup conflicts.
try:
    from .celery import celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not available or Django not ready
    __all__ = ()
