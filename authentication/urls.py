from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from . import views
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('userinfo/', views.UserDetailAPIView.as_view(), name='userinfo'),
    path('profile-image/', views.ProfileImageView.as_view(), name='profile-image'),
    path('profile-image/<int:pk>/', views.ProfileImageView.as_view(), name='profile-image'),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('login/', views.LoginView.as_view(), name='login'),
]

