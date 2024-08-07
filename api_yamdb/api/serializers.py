from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers

from api.constants import REGEX_SIGNS, REGEX_ME
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=['user', 'moderator', 'admin',],
                                   required=False)

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

        user_with_same_username = (User.objects
                                   .filter(username=username).first())
        user_with_same_email = (User.objects
                                .filter(email=email).first())

        if user_with_same_username and user_with_same_username.email != email:
            raise serializers.ValidationError(
                {"email": "Этот email уже используется другим пользователем."}
            )

        if user_with_same_email and user_with_same_email.username != username:
            raise serializers.ValidationError(
                {"username": "Этот username уже используется "
                             "другим пользователем."}
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

    class Meta:
        model = Title
        fields = '__all__'


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
