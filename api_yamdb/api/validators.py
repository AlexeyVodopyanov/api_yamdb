from datetime import datetime
from django.forms import ValidationError

def validate_year(value):
    if value > datetime.now().year:
        raise ValidationError('Проверьте год!')
    return value
