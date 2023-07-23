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


def impersonate_other_page(page, other, use_other_title):
    '''
        Modify the tree location data of `page` to resemble `other`.

        Args:
            page:               the page to modify
            other:              the page to impersonate
            use_control_title:  whether use to use the other's title

        Return:
            None
    '''

    page.path = other.path
    page.depth = other.depth
    page.url_path = other.url_path
    if use_other_title:
        page.title = other.title

def use_control_title(experiment, page):
    '''
        Determine whether to use the control page's title
        on an alternative page. If alternative page doesn't
        exists, then defaults to False.

        Args:
            experiment: the primary key for the experiment
            page:       the primary key for the page

        Return:
            True if control title should be used. Otherwise, False.
    '''

    try:
        alt = Alternative.objects.get(experiment=experiment, page=page)
        if alt:
            use_control_title = alt.use_control_title
        else:
            use_control_title = False

    except Alternative.DoesNotExist:
        use_control_title = False

    return use_control_title

