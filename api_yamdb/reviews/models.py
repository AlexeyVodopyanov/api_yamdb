import uuid

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _

from api.validators import validate_year
from api_yamdb.models import BaseModelCategoryGenre, BaseModelReviewComment


class User(AbstractUser):
    """Модель пользователей"""

    class Role(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')

    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    confirmation_code = models.CharField(max_length=36, blank=True, null=True)
    groups = models.ManyToManyField(
        Group,
        related_name='reviews_users',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='reviews_users',
        blank=True
    )

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def generate_confirmation_code(self):
        """Генерирует новый код подтверждения и возвращает его."""
        self.confirmation_code = str(uuid.uuid4())
        return self.confirmation_code

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('role', 'id')


class Category(BaseModelCategoryGenre):
    """Модель категории произведений"""

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('name', 'slug')


class Genre(BaseModelCategoryGenre):
    """Модель жанров произведений"""

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name', 'slug')


class Title(models.Model):
    """Модель произведений"""

    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[validate_year],
        verbose_name='Год'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('id', 'name', 'year')

    def __str__(self):
        return self.name

    def get_rating(self):
        """Вычисляет средний рейтинг произведения."""
        return self.reviews.aggregate(Avg('score'))['score__avg']


class Review(BaseModelReviewComment):
    """Модель отзывов на произведения"""

    author = models.ForeignKey(
        User,
        verbose_name='Автор отзыва',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Отзыв произведения',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        verbose_name='Оценка произведения',
        default=1,
        validators=[
            MinValueValidator(1, message=('Оценка должна быть '
                                          'больше или равна 1.')),
            MaxValueValidator(10, message=('Оценка не может '
                                           'быть больше 10.'))
        ]
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=('author', 'title'),
                                    name='unique_author_title')
        ]
        ordering = ('pub_date', 'author')


class Comment(BaseModelReviewComment):
    """Модель комментариев по отзывам"""

    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        verbose_name='Комментируемый отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date', 'author')
