from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewViewSet, SignupView, TitleViewSet, TokenView,
                    UsersViewSet, UserInfoViewSet)

r = SimpleRouter()

r.register(r'titles/(?P<title_id>\d+)'
           r'/reviews/(?P<review_id>\d+)/comments',
           CommentsViewSet,
           basename='comments')
r.register(r'titles/(?P<title_id>\d+)/reviews',
           ReviewViewSet,
           basename='reviews')
r.register('users', UsersViewSet, basename='users')
r.register('categories', CategoryViewSet, basename='categories')
r.register('genres', GenreViewSet, basename='genres')
r.register('titles', TitleViewSet, basename='title')
r.register(r'auth', TokenView, basename='auth')

app_name = 'api'


patterns_version_1 = [
    path('users/me/',
         UserInfoViewSet.as_view({'get': 'get_current_user_info',
                                  'patch': 'get_current_user_info'}),
         name='current_user'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('', include(r.urls)),

]

urlpatterns = [
    path('v1/', include(patterns_version_1)),
]
