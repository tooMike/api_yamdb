from django.urls import path


from api import views

urlpatterns = [
    path('v1/auth/signup/', views.user_signup, name='user_signup'),
    path('v1/auth/token/', views.get_token, name='get_token'),
]