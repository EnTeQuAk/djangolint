from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.functional import memoize


_downloaders_cache = {}


def clear_downloaders_cache():
    global _downloaders_cache
    _downloaders_cache.clear()


def load_downloader(downloader_name):
    module_name, attr = downloader_name.rsplit('.', 1)
    try:
        module = import_module(module_name)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error importing downloader %s: "%s"' % (downloader_name, e))
    try:
        downloader = getattr(module, attr)
    except AttributeError, e:
        raise ImproperlyConfigured(
            'Error importing downloader %s: "%s"' % (downloader_name, e))
    return downloader


def get_downloaders():
    downloaders = []
    for downloader_name in getattr(settings, 'LINT_DOWNLOADERS', ()):
        downloaders.append(load_downloader(downloader_name))
    return downloaders
get_downloaders = memoize(get_downloaders, _downloaders_cache, 0)
