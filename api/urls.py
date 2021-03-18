from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import CouriersViewSet

router = DefaultRouter()
router.register('couriers', CouriersViewSet, basename='CouriersView')

urlpatterns = [
    path('v1/', include(router.urls)),
]