from django.db import router
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register('auth', views.AuthViewSet, basename='auth')
router.register('apartments', views.ApartmentViewSet)
router.register('users', views.UserViewSet, basename='users')
router.register('bills', views.BillViewSet)
router.register('parking-cards', views.ParkingCardViewSet)
router.register('card-requests', views.CardRequestViewSet)
router.register('relative-cards', views.RelativeCardViewSet)
router.register('lockers', views.LockerViewSet)
router.register('feedbacks', views.FeedbackViewSet)
router.register('surveys', views.SurveyViewSet)
router.register('survey-results', views.SurveyResultViewSet)
router.register('notifications', views.NotificationViewSet)
router.register('chat-messages', views.ChatMessageViewSet)
router.register('payment-accounts', views.PaymentAccountViewSet)
router.register('card-requests', views.CardRequestViewSet, basename='card-request')
router.register('upload-avatar', views.UploadAvatarViewSet, basename='upload-avatar')

# router.register(r'users/(?P<user_id>\d+)/bills', views.BillViewSet, basename='user-bills')
# router.register(r'users/(?P<user_id>\d+)/parking-cards', views.ParkingCardViewSet, basename='user-parking-cards')
# router.register(r'users/(?P<user_id>\d+)/relative-cards', views.RelativeCardViewSet, basename='user-relative-cards')
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
    # path('', include('user.urls')),
    # path('accounts/', include('allauth.urls'))
]

