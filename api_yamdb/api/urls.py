from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewViewSet, SignupView, TitleViewSet, TokenView,
                    UsersViewSet)

router = SimpleRouter()

router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                CommentsViewSet,
                basename='comments')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet,
                basename='reviews')
router.register('users', UsersViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='title')
router.register(r'auth', TokenView, basename='auth')

app_name = 'api'


patterns_version_1 = [
    path('', include(router.urls)),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('users/me/',
         UsersViewSet.as_view({'get': 'get_current_user_info',
                               'patch': 'get_current_user_info'}),
         name='current_user'),
]

urlpatterns = [
    path('v1/', include(patterns_version_1)),
]
