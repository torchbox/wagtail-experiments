from __future__ import absolute_import, unicode_literals

import uuid


def get_user_id(request):
    return request.session.setdefault('experiment_user_id', str(uuid.uuid4()))


def percentage(fraction, population):
    try:
        return float(fraction) / float(population) * 100
    except (ValueError, ZeroDivisionError, TypeError):
        return 0.0


def impersonate_other_page(page, other):
    """Modify the title and tree location data of `page` to resemble `other`"""
    page.path = other.path
    page.depth = other.depth
    page.url_path = other.url_path
    page.title = other.title
