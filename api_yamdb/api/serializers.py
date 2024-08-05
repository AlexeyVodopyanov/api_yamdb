from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.core.validators import RegexValidator

from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

REGEX_SIGNS = RegexValidator(r'^[\w.@+-]+\Z', 'Поддерживать знак.')
REGEX_ME = RegexValidator(r'[^m][^e]', 'Пользователя не должен быть "me".')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        error_messages={
            'invalid': 'Значение должны состоять только из буквы или цифры или символов подчёркивания или дефисов.',
        }
    )
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email')

    #def validate(self, data):
    #   if 'username' not in data:
    #        raise serializers.ValidationError({"username": "This field is required."})
    #    if 'email' not in data:
    #        raise serializers.ValidationError({"email": "This field is required."})
    #    return data

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError("Username 'me' is not allowed.")
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, validators=(REGEX_SIGNS, REGEX_ME))
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )

    def get_rating(self, obj):
        score = obj.reviews.aggregate(Avg('score'))
        return score['score__avg']


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
    rating = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=256)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )

    def get_rating(self, obj):
        score = obj.reviews.aggregate(Avg('score'))
        return score['score__avg']


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('review',)
