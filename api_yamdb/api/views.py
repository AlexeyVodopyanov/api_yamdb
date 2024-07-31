from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters, views, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title
from .filters import TitleFilter
from .mixins import ListCreateDestroyMixin
from .permissions import IsAdmin
from .serializers import (CategorySerializer, GenreSerializer,
                          SignupSerializer, TitleSerializer,
                          TokenSerializer, UserSerializer)

User = get_user_model()


class SignupView(views.APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user, created = User.objects.get_or_create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            )
            if created:
                confirmation_code = user.generate_confirmation_code()  # Implement this method
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
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, username=serializer.validated_data['username'])
            token = RefreshToken.for_user(user)
            return Response({'token': str(token.access_token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentsViewSet(ModelViewSet):
    pass


class CategoryViewSet(ListCreateDestroyMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdmin,)


class GenreViewSet(ListCreateDestroyMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination
