from django.db import router
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register('auth', views.AuthViewSet, basename='auth')
router.register('apartments', views.ApartmentViewSet, basename='apartment')
router.register('users', views.UserViewSet, basename='user')
router.register('bills', views.BillViewSet, basename='bill')
router.register('parking-cards', views.ParkingCardViewSet, basename='parking-card')
router.register('relative-cards', views.RelativeCardViewSet, basename='relative-card')
router.register('lockers', views.LockerViewSet, basename='locker')
router.register('feedbacks', views.FeedbackViewSet, basename='feedback')
router.register('surveys', views.SurveyViewSet, basename='survey')
router.register('survey-results', views.SurveyResultViewSet, basename='survey-result')
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('chat-messages', views.ChatMessageViewSet, basename='chat-message')
router.register('payment-accounts', views.PaymentAccountViewSet, basename='payment-account')

# router.register(r'users/(?P<user_id>\d+)/bills', views.BillViewSet, basename='user-bills')
# router.register(r'users/(?P<user_id>\d+)/parking-cards', views.ParkingCardViewSet, basename='user-parking-cards')
# router.register(r'users/(?P<user_id>\d+)/relative-cards', views.RelativeCardViewSet, basename='user-relative-cards')
# router.register(r'users/(?P<user_id>\d+)/lockers', views.LockerViewSet, basename='user-lockers')
# router.register(r'users/(?P<user_id>\d+)/feedbacks', views.FeedbackViewSet, basename='user-feedbacks')
router.register(r'users/(?P<user_id>\d+)/bills', views.BillViewSet, basename='user-bills')
router.register(r'users/(?P<user_id>\d+)/parking-cards', views.ParkingCardViewSet, basename='user-parking-cards')
router.register(r'users/(?P<user_id>\d+)/relative-cards', views.RelativeCardViewSet, basename='user-relative-cards')
router.register(r'users/(?P<user_id>\d+)/lockers', views.LockerViewSet, basename='user-lockers')
router.register(r'users/(?P<user_id>\d+)/feedbacks', views.FeedbackViewSet, basename='user-feedbacks')
router.register(r'users/(?P<user_id>\d+)/notifications', views.NotificationViewSet, basename='user-notifications')

#apartment-nested
router.register(r'apartments/(?P<apartment_id>\d+)/residents', views.UserViewSet, basename='apartment-residents')
# router.register(r'apartments/(?P<apartment_id>\d+)/bills', views.BillViewSet, basename='apartment-bills')

#survey-nested
router.register(r'surveys/(?P<survey_id>\d+)/results', views.SurveyResultViewSet, basename='survey-results')



urlpatterns = [
    path('', include(router.urls)),
]

