from django import template
from django.utils import timezone

register = template.Library()


def print_timestamp(timestamp):
    try:
        parsed_ago = (timezone.now() - timestamp)
        return f'{parsed_ago.days * 1440 + int(parsed_ago.seconds / 60)} minutes ago'
    except ValueError:
        return None


register.filter(print_timestamp)
