from random import randint

from django.contrib.auth.models import User

from api.models import RedirectUrl


__author__ = 'schien'


def generate_url_key():
    """
    Generate a random key of a specific length
    """
    n = 10
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def generate_redirect_url(target_url=None, username=None, display_text=None):
    users = User.objects.filter(username__exact=username)
    if len(users) != 1:
        raise Exception('user not found')
    user = users[0]

    max_attempts = 50
    for _ in range(0, max_attempts):
        key = generate_url_key()
        if len(RedirectUrl.objects.filter(redirect_key__exact=key)) > 0:
            continue
        else:
            redirect, created = RedirectUrl.objects.get_or_create(target_url=target_url, user=user)
            redirect.display_text = display_text
            redirect.redirect_key = key
            redirect.save()
            return redirect

    raise Exception('Could not find a unique random key.')


