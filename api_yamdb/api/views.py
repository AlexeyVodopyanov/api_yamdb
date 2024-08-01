from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters, views, mixins, viewsets
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title
from .filters import TitleFilter
from .mixins import ListCreateDestroyMixin
from .serializers import (SignupSerializer,
                          TitleCreateSerializer,
                          TokenSerializer,
                          UserSerializer,
                          ReviewSerializer,
                          CommentSerializer,
                          CategorySerializer,
                          TitleSerializer,
                          GenreSerializer)
from .permissions import IsAdmin, IsAuthorOrReadOnly, IsAdminOrReadOnly
from reviews.models import Review, Title, Comment, Category, Genre

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SignupView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user, created = User.objects.get_or_create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            )
            if created:
                confirmation_code = user.generate_confirmation_code()
                send_mail(
                    'Confirmation code',
                    f'Your confirmation code is {confirmation_code}',
                    'from@example.com',
                    [user.email],
                    fail_silently=False,
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, username=serializer.validated_data['username'])
            if user.check_confirmation_code(serializer.validated_data['confirmation_code']):
                token = RefreshToken.for_user(user)
                return Response({'token': str(token.access_token)}, status=status.HTTP_200_OK)
            return Response({'confirmation_code': 'Invalid confirmation code'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(methods=['get', 'patch'], detail=False, permission_classes=[IsAuthenticated], url_path='me')
    def get_current_user_info(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(ListCreateDestroyMixin):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination


class GenreViewSet(ListCreateDestroyMixin):

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination


class TitleViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(ModelViewSet):

    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly,)  # AllowAny - временно
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Review.objects.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()  # type: ignore

#    def update(self, request, *args, **kwargs):
#        return Response(data='PUT-запрос не предусмотрен', status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentsViewSet(ModelViewSet):

    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly,)  # AllowAny - временно
    serializer_class = CommentSerializer
    pagination_class = None
    pagination_class = StandardResultsSetPagination
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()  # type: ignore

    def update(self, request, *args, **kwargs):
        return Response(data='PUT-запрос не предусмотрен',
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
