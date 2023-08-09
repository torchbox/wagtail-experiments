import uuid

from .models import Alternative


def get_user_id(request):
    '''
        Get user id for this request. A user ID is assigned randomly
        for each request session.

        Args:
            request:  django HttpRequest.

        Return:
            User ID for the request as a str.

        To do:
            Require unique user ID for each session.
    '''

    return request.session.setdefault('experiment_user_id', str(uuid.uuid4()))


def percentage(fraction, population):
    '''
        Calc percentage.

        Args:
            fraction:  Portion of population.
            population: Population count.

        Return:
            Percentage as float.
    '''

    try:
        return float(fraction) / float(population) * 100
    except (ValueError, ZeroDivisionError, TypeError):
        return 0.0


def impersonate_other_page(page, other):
    '''
        Modify the tree location data of `page` to resemble `other`.

        Args:
            page:               the page to modify
            other:              the page to impersonate

        Return:
            None
    '''

    page.path = other.path
    page.depth = other.depth
    page.url_path = other.url_path
    page.title = other.title
