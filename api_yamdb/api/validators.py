from django.utils import timezone
from django.forms import ValidationError


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError('Проверьте год!')
    return value
