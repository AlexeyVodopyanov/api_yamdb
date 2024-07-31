from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


from reviews.models import Category, Genre, Title


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if not user:
            raise serializers.ValidationError('User not found')
        return data


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
    category = CategorySerializer(many=False)
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        year = timezone.now().year
        if value not in range(settings.TITLES_MIN_YEAR, year):
            raise serializers.ValidationError('Не верно указан год!')
        return value

