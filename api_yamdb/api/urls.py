from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api import views


router = SimpleRouter()
router.register('users', views.UsersViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', views.user_signup, name='user_signup'),
    path('v1/auth/token/', views.get_token, name='get_token'),
    path('v1/', include(router.urls)),
]
