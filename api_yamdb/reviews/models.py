import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ], default='user')
    confirmation_code = models.CharField(max_length=36, blank=True, null=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def generate_confirmation_code(self):
        self.confirmation_code = str(uuid.uuid4())
        self.save()
        return self.confirmation_code


class Category(models.Model):
    """"Модель категории произведений"""
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
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model): 
    """Модель Жанров произведений"""
    name = models.CharField(
        max_length=100,
        default=None,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name
    

class Title(models.Model):
    """Модель произведений"""
    name = models.CharField(max_length=200, verbose_name='Название')
    year = models.IntegerField(verbose_name='год')
    description = models.TextField(
        max_length=200,
        blank=True,null=True,
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
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """Связующая модель произведений и жанров."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='title_genres',
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='title_genres',
        verbose_name='Жанр'
    )

    def __str__(self):
        return f'Жанр - {self.genre}, произведение - {self.title}'


class Review(models.Model):
    """Модель отзывов на произведения"""
    text = models.TextField(verbose_name='Текст')
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
    pub_date = models.DateTimeField(
        'Дата публикации отзыва', auto_now_add=True, db_index=True)
    score = models.IntegerField(
        verbose_name='Оценка произведения',
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(models.Model):
    """Модель комментариев по отзывам"""
    text = models.TextField(verbose_name='Текст')
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
    pub_date = models.DateTimeField(
        'Дата добавления комментария', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'