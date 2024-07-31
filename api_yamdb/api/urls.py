from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentsViewSet,
                       GenreViewSet, TitleViewSet)

router_v1 = DefaultRouter()
router_v1.register('comments', CommentsViewSet, basename='comments')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('genres', GenreViewSet, basename='genres')

app_name = 'api'

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
