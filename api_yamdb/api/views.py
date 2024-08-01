from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import (SignupSerializer,
                             TokenSerializer,
                             UserSerializer,
                             ReviewSerializer,
                             CommentSerializer,
                             CategorySerializer,
                             GenreSerializer)
from api.permissions import IsAdmin, IsAuthorOrReadOnly
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


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdmin]


class ReviewViewSet(ModelViewSet):

    permission_classes = (AllowAny,)  # AllowAny - временно
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Review.objects.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()  # type: ignore


class CommentsViewSet(ModelViewSet):

    permission_classes = (AllowAny,)  # AllowAny - временно
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
