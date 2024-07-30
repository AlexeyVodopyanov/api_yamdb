from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import (CommentsViewSet,
                    )


router = SimpleRouter()

router.register('comments', CommentsViewSet, basename='comments')

app_name = 'api'


patterns_version_1 = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('v1/', include(patterns_version_1)),
]
