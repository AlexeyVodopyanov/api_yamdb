from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

REGEX_SIGNS = RegexValidator(r'^[\w.@+-]+\Z', 'Поддерживать знак.')
REGEX_ME = RegexValidator(r'[^m][^e]', 'Пользователя не должен быть "me".')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.SlugField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError("Username 'me' is not allowed.")
        return value

    def validate_email(self, value):
        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        user_with_same_username = User.objects.filter(username=username).first()
        user_with_same_email = User.objects.filter(email=email).first()

        if user_with_same_username and user_with_same_username.email != email:
            raise serializers.ValidationError(
                {"email": "Этот email уже используется другим пользователем."}
            )

        if user_with_same_email and user_with_same_email.username != username:
            raise serializers.ValidationError(
                {"username": "Этот username уже используется другим пользователем."}
            )

        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,
                                     validators=(REGEX_SIGNS, REGEX_ME))
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )

    def validate_year(self, value):
        current_year = datetime.date.today().year
        if not settings.TITLES_MIN_YEAR <= value <= current_year:
            raise serializers.ValidationError(
                'Invalid year. Year must be between {} and {}'.format(settings.TITLES_MIN_YEAR, current_year))
        return value


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    name = serializers.CharField(max_length=256)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category',
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('review',)
