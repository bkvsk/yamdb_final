from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuthEmailView,
    AuthTokenView,
    CategoriesViewSet,
    CommentViewSet,
    GenresViewSet,
    ReviewViewSet,
    TitlesViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register('categories', CategoriesViewSet, basename='categories')
router.register('genres', GenresViewSet, basename='genres')
router.register('titles', TitlesViewSet, basename='titles')
router.register('users', UserViewSet, basename='users')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

auth_urls = [
    path('email/', AuthEmailView.as_view(), name='auth_email'),
    path('token/', AuthTokenView.as_view(), name='auth_token'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urls)),
]
