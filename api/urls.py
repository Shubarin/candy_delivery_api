from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CouriersViewSet, OrdersViewSet

router = DefaultRouter()
router.register('couriers', CouriersViewSet, basename='CouriersView')
router.register('orders', OrdersViewSet, basename='OrdersView')

urlpatterns = [
    path('v1/', include(router.urls)),
]
