from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from apartment.views import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Apartment Management API",
        default_version='v1',
        description="API documentation for Apartment Management System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@apartment.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('apartments', ApartmentViewSet, basename='apartments')
router.register('bills', BillViewSet, basename='bills')
router.register('parking-cards', ParkingCardViewSet, basename='parking-cards')
router.register('relative-cards', RelativeCardViewSet, basename='relative-cards')
router.register('lockers', LockerViewSet, basename='lockers')
router.register('feedbacks', FeedbackViewSet, basename='feedbacks')
router.register('notifications', NotificationViewSet, basename='notifications')
router.register('chat-messages', ChatMessageViewSet, basename='chat-messages')

# Nested routers
users_router = routers.NestedSimpleRouter(router, 'users', lookup='user')
users_router.register('bills', BillViewSet, basename='user-bills')
users_router.register('parking-cards', ParkingCardViewSet, basename='user-parking-cards')
users_router.register('relative-cards', RelativeCardViewSet, basename='user-relative-cards')
users_router.register('lockers', LockerViewSet, basename='user-lockers')
users_router.register('feedbacks', FeedbackViewSet, basename='user-feedbacks')
users_router.register('notifications', NotificationViewSet, basename='user-notifications')
users_router.register('chat-messages', ChatMessageViewSet, basename='user-chat-messages')

apartments_router = routers.NestedSimpleRouter(router, 'apartments', lookup='apartment')
apartments_router.register('residents', UserViewSet, basename='apartment-residents')
apartments_router.register('bills', BillViewSet, basename='apartment-bills')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/v1/', include(router.urls)),
    path('api/v1/', include(users_router.urls)),
    path('api/v1/', include(apartments_router.urls)),
    path('api/v1/auth/', include('apartment.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


