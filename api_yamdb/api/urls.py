from django.urls import include, path
from rest_framework import routers
from rest_framework.routers import SimpleRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       MeUserViewSet, ReviewViewSet, TitleViewSet,
                       UsersViewSet, get_token, user_signup)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path("v1/auth/signup/", user_signup, name="user_signup"),
    path("v1/auth/token/", get_token, name="get_token"),
    path(
        "v1/users/me/",
        MeUserViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update"}),
        name="me_user",
    ),
    path("v1/", include(router_v1.urls)),
]
