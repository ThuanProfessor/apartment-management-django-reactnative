from django.db import router
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('apartments', views.ApartmentViewSet, basename='apartment')
router.register('users', views.UserViewSet, basename='user')
router.register('bills', views.BillViewSet, basename='bill')
router.register(r'users/(?P<user_id>\d+)/bills', views.BillViewSet, basename='user-bills')

urlpatterns = [
    path('', include(router.urls)),
]

