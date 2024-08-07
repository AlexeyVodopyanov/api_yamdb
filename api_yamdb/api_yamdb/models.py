from django.db import models


class BaseModelCategoryGenre(models.Model):
    """Базовая модель жанров и категорий произведений."""

    name = models.CharField(
        max_length=256,
        default=None,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class BaseModelReviewComment(models.Model):
    """Модель отзывов и комментариев по отзывам"""

    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
