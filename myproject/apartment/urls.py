from django.db import router
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('auth', views.AuthViewSet, basename='auth')
router.register('apartments', views.ApartmentViewSet, basename='apartment')
router.register('users', views.UserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),
]

