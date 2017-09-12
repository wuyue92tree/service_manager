# encoding=utf-8

from threading import local

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object


_thread_locals = local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


class ThreadLocals(MiddlewareMixin):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""

    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
