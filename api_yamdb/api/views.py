from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, views, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import (HTTP_200_OK,
                                   HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND,
                                   HTTP_405_METHOD_NOT_ALLOWED)
from rest_framework.viewsets import ModelViewSet

from api.filters import TitleFilter
from api.mixins import ListCreateDestroyMixin
from api.paginators import StandardResultsSetPagination
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             IsAuthorOrModeratorOrReadOnly)
from api.serializers import (CategorySerializer,
                             CommentSerializer,
                             GenreSerializer,
                             ReviewSerializer,
                             SignupSerializer,
                             TitleCreateSerializer,
                             TitleSerializer,
                             TokenSerializer,
                             UserSerializer)
from reviews.models import Category, Comment, Genre, Review, Title, User
from django.conf import settings


class SignupView(views.APIView):
    """Модель подключения пользователей."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            list_resp_user = [username]
            list_resp_email = [email]
            if User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    return Response({'username': list_resp_user},
                                    status=status.HTTP_400_BAD_REQUEST)
                existing_user = User.objects.get(username=username)
                if existing_user.email != email:
                    return Response(
                        {'email': list_resp_email, 'username': list_resp_user},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            if User.objects.filter(email=email).exists():
                if not User.objects.filter(username=username).exists():
                    return Response({'email': list_resp_email},
                                    status=status.HTTP_400_BAD_REQUEST)
                existing_user = User.objects.get(email=email)
                if existing_user.username != username:
                    return Response(
                        {'email': list_resp_email, 'username': list_resp_user},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if existing_user.username != username:
                    return Response({'email': list_resp_email},
                                    status=HTTP_400_BAD_REQUEST)
            user, created = User.objects.get_or_create(
                username=username,
                email=email
            )
            confirmation_code = user.generate_confirmation_code()
            send_mail(
                'Confirmation code',
                f'Your confirmation code is {confirmation_code}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response(serializer.data, status=HTTP_200_OK)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


'''class SignupView(views.APIView):
    """Модель подключения пользователей."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        user, created = User.objects.get_or_create(
            username=username,
            email=email
        )
        confirmation_code = user.generate_confirmation_code()
        send_mail(
            'Confirmation code',
            f'Your confirmation code is {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=HTTP_200_OK)'''


class TokenView(viewsets.ViewSet):
    """Модель проверки токена пользователей."""

    permission_classes = [AllowAny]

    def get_token(self, request, validated_data):
        username = validated_data['username']
        if not User.objects.filter(username=username).exists():
            return Response({'username': username},
                            status=HTTP_404_NOT_FOUND)
        user = get_object_or_404(User, username=username)
        confirmation_code = validated_data.get('confirmation_code')
        user_confirmation_code = user.confirmation_code
        if not user_confirmation_code:
            user_confirmation_code = 0
        user_confirmation_code = str(user_confirmation_code)

        if user_confirmation_code == confirmation_code:
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)}, status=HTTP_200_OK)
        return Response(
            {'confirmation_code': 'Ошибка, неверный confirmation code'},
            status=HTTP_400_BAD_REQUEST
            )

    @action(methods=['POST'], detail=False, url_path='token')
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return self.get_token(request, serializer.validated_data)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


class UserInfoViewSet(ModelViewSet):
    """Пользователь смотрит о себе информацию (get) и меняеет ее (patch)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'
    http_method_names = ['get', 'patch']
    search_fields = ('username',)

    @action(methods=['get', 'patch'],
            detail=False,
            permission_classes=[IsAuthenticated],
            url_path='me')
    def get_current_user_info(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=HTTP_200_OK)
        serializer = UserSerializer(request.user, data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        if 'role' in request.data:
            return Response({'role': 'Cannot change role'},
                            status=HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class UsersViewSet(ModelViewSet):
    """По модели пользователей запросы 'get', 'post', 'patch', 'delete'."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class CategoryViewSet(ListCreateDestroyMixin):
    """Получаем список всех категорий. Создание/удаление администраторм."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = StandardResultsSetPagination


class GenreViewSet(ListCreateDestroyMixin):
    """Получаем список всех жанров. Создание/удаление администраторм."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = StandardResultsSetPagination


class TitleViewSet(ModelViewSet):
    """Модель по произведениям. Доступна всем, изменения - администратору."""

    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        queryset = super().get_queryset()
        for title in queryset:
            score = title.reviews.aggregate(Avg('score'))
            title.rating = score['score__avg']
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(ModelViewSet):
    """Модель отзывов по произведениям. Стандартные запросы кроме PUT."""

    permission_classes = (IsAuthorOrModeratorOrReadOnly,)
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = StandardResultsSetPagination

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        if Review.objects.filter(title=title,
                                 author=self.request.user).exists():
            raise ValidationError('Review already exists')
        serializer.save(title=title, author=self.request.user)


class CommentsViewSet(ModelViewSet):
    """Модель комментариев по отзывам. Стандартные запросы кроме PUT."""

    permission_classes = (IsAuthorOrModeratorOrReadOnly,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()
