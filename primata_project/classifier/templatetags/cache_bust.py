"""Template tags untuk cache-busting aset statis secara otomatis.

Menghasilkan query string `?v=<mtime>` berdasarkan waktu modifikasi file,
sehingga browser selalu mengambil versi terbaru setiap kali file berubah,
tanpa perlu menaikkan versi manual di template.
"""
import os

from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

_mtime_cache = {}


@register.simple_tag
def versioned_static(path):
    """Return {% static %} URL dengan parameter ?v=<mtime file>.

    Contoh pemakaian::

        <link rel="stylesheet" href="{% versioned_static 'classifier/style.css' %}">
    """
    url = static(path)
    relative = path.lstrip('/')
    for root in settings.STATICFILES_DIRS:
        candidate = os.path.join(str(root), relative)
        if os.path.exists(candidate):
            mtime = int(os.path.getmtime(candidate))
            key = (candidate, mtime)
            if key not in _mtime_cache:
                _mtime_cache[key] = f"{url}?v={mtime:x}"
            return _mtime_cache[key]
    return url
