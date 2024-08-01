from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import (CommentsViewSet,
                    ReviewViewSet, TitleViewSet,
                    UsersViewSet,
                    SignupView,
                    TokenView,
                    CategoryViewSet,
                    GenreViewSet)


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

app_name = 'api'

patterns_version_1 = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token'),
    path('v1/users/me/',
         UsersViewSet.as_view({'get': 'get_current_user_info',
                               'patch': 'get_current_user_info'}),
         name='current_user'),
]
