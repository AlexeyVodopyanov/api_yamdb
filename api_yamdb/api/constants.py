from django.core.validators import RegexValidator

REGEX_SIGNS = RegexValidator(r'^[\w.@+-]+\Z',
                             'Поддерживать знак.')
REGEX_ME = RegexValidator(r'[^m][^e]',
                          'Пользователя не должен быть "me".')
